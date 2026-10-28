"""Standalone preceptor reads and consent controls via the canonical ledger API."""
import argparse
import json
import re
from pathlib import Path
from . import ledger, gates


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True,help='Explicit ledger directory; no automatic recording')
    s=p.add_subparsers(dest='operation',required=True)
    s.add_parser('status');s.add_parser('cues')
    q=s.add_parser('observations');q.add_argument('--session');q.add_argument('--limit',type=int,default=20)
    q=s.add_parser('why');q.add_argument('session')
    q=s.add_parser('gate');q.add_argument('assessment',type=Path)
    q=s.add_parser('forget');q.add_argument('--since',required=True);q.add_argument('--confirm-root',type=Path,required=True)
    a=p.parse_args(argv)
    try:
        if getattr(a,'session',None) and not re.fullmatch(r'[A-Za-z0-9_-]{1,128}',a.session):raise ValueError('Session ID must be a simple identifier')
        if a.operation=='status':out=ledger.read_status(a.root)
        elif a.operation=='cues':out=ledger.list_cues(a.root)
        elif a.operation=='observations':
            if not 1<=a.limit<=1000:raise ValueError('Limit must be 1..1000 files')
            out=ledger.summarize_observations(a.root,a.session,a.limit)
        elif a.operation=='why':out=ledger.read_manifest(a.root,a.session)
        elif a.operation=='gate':
            assessment=json.loads(a.assessment.read_text())
            out={'promote':gates.promote(assessment),'retire':gates.retire(assessment),'minimum_n_per_arm':gates.MIN_N_PER_ARM,'applied':False}
        else:
            if a.confirm_root.resolve()!=a.root.resolve():raise ValueError('Confirmation must match the explicit ledger root')
            out=ledger.forget(a.root,a.since)
        print(json.dumps(out,indent=2));return 0
    except (ValueError,OSError,ledger.LedgerError) as exc:p.exit(2,f'{type(exc).__name__}: {exc}\n')

if __name__=='__main__':raise SystemExit(main())
