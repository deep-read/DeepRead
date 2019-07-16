""" Creates the folder containing the configurations for training """

import argparse
from pathlib import Path

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--out-dir',
        type=str,
        help='Directory to place files. Dir does not need to exist',
    )
    parser.add_argument(
        '--n-classes',
        type=int,
        required=True,
        help='The number of classes in your data set',
    )
    parser.add_argument(
        '--label-dir',
        type=str,
        required=True,
        help='Path to dir containing YOLO labels for images'
    )

    args = parser.parse_args()
    print(args)

    out_dir = Path(args.out_dir)
    if not out_dir.is_dir():
        out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir/'classes.txt', 'w') as _:
        pass

    with open(out_dir/'custom.data', 'w') as out_f:
        out_f.write(f'classes={args.n_classes}\n')
        out_f.write(f'train={out_dir}/train.txt\n')
        out_f.write(f'valid={out_dir}/valid.txt\n')
        out_f.write(f'names={out_dir}/classes.txt\n')
        out_f.write(f'boxes={args.label_dir}\n')
