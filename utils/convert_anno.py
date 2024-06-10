from ChildProject.converters import ItsConverter, VtcConverter
import sys
from pathlib import Path
import argparse
from tqdm import tqdm

def write_data(data, output_path):
    data.to_csv(output_path, index=False)

def main(argv):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--data_path', type=str, default='/home/engaclew/DATA/neurogen/L3_HIPAA_LENA_cleaned/its/raw',
                        help='Path to the folder containing itFs or rttm files')
    parser.add_argument('--ext', type=str, default='.its', choices=['.rttm', '.its'],
                        help='Extension of the files to be processed')
    args = parser.parse_args(argv)
    data_path = Path(args.data_path)

    converter = ItsConverter() if args.ext == '.its' else VtcConverter()
    output_folder = data_path.parent / 'converted'
    output_folder.mkdir(exist_ok=True)

    for file_path in tqdm(data_path.glob(f'*{args.ext}')):
        output_path = output_folder / (file_path.stem + '.csv')
        data = converter.convert(file_path)
        write_data(data, output_path)


if __name__ == "__main__":
    # execute only if run as a script
    args = sys.argv[1:]
    main(args)