import argparse, json
from nexora.data.synthetic import prepare

def main():
    parser=argparse.ArgumentParser(description='NEXORA local research tools')
    sub=parser.add_subparsers(dest='command',required=True)
    data=sub.add_parser('data').add_subparsers(dest='action',required=True)
    gen=data.add_parser('generate'); gen.add_argument('--seed',type=int,default=42); gen.add_argument('--profile',default='demo')
    wesad=data.add_parser('import-wesad'); wesad.add_argument('--path',required=True); wesad.add_argument('--trusted-original',action='store_true')
    training=sub.add_parser('train'); training.add_argument('kind',choices=['baseline','neural']); training.add_argument('--dataset',choices=['synthetic','wesad'],default='synthetic'); training.add_argument('--seed',type=int,default=42)
    experiment=sub.add_parser('experiment').add_subparsers(dest='action',required=True)
    run=experiment.add_parser('run'); run.add_argument('--mode',choices=['federated','private-federated'],required=True); run.add_argument('--dataset',choices=['synthetic','wesad'],default='synthetic'); run.add_argument('--rounds',type=int,default=5)
    args=parser.parse_args()
    if args.command=='data' and args.action=='generate': result=prepare(seed=args.seed)
    elif args.command=='data':
        from nexora.data.wesad import import_directory
        result=import_directory(args.path,trusted_original=args.trusted_original)
    elif args.command=='train':
        from nexora.ml.train import train
        result=train(args.kind, dataset_name=args.dataset, seed=args.seed)
    else:
        from nexora.federation.experiment import run
        result=run(rounds=args.rounds,private=args.mode=='private-federated',dataset=args.dataset)
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
