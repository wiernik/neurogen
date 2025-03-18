import sys
from pathlib import Path
import pandas as pd
import argparse
from datetime import date

def main(argv):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--data_path', type=str, default='/home/engaclew/DATA/neurogen/L3_HIPAA_LENA_cleaned/annotations/eaf/an1/raw',
                        help='Path to the folder containing human annotation files (.eaf)')
    parser.add_argument('--annotations_csv_path', type=str,
                        default='/home/engaclew/DATA/neurogen/L3_HIPAA_LENA_cleaned/metadata/annotations.csv',
                        help='Path to the .csv file containing the list of annotations')
    args = parser.parse_args(argv)
    data_path = Path(args.data_path)
    metadata_path = Path(args.annotations_csv_path)

    # Load annotation
    annotations = pd.read_csv(metadata_path, sep=',')
    annotations = annotations[annotations.set != 'eaf/an1']

    current_date = date.today().strftime('%Y-%m-%d')
    out = []
    for cha_file in data_path.glob('*.eaf'):
        stem = cha_file.stem
        splitted = stem.split('_')
        onset = int(splitted[-2])
        offset = int(splitted[-1])
        original_audio = '_'.join(splitted[:-2])
        row = {'set': 'eaf/an1',
               'recording_filename': f'{original_audio}.wav',
               'time_seek': -3418598,
               'range_onset':onset,
               'range_offset': offset,
               'raw_filename': cha_file.name,
               'format': 'eaf',
               'filter': None,
               'annotation_filename': f'{stem}.csv',
               'imported_at': current_date,
               'error': None,
               'package_version': '42.42.42'}
        out.append(row)
    out = pd.DataFrame(out)
    print(f"Found {len(out)} 2-mn clips.")
    merged_annotations = pd.concat([annotations, out], ignore_index=True)
    merged_annotations.to_csv(metadata_path.parent / 'annotations2.csv', index=False)
    print("Done.")

if __name__ == "__main__":
    # execute only if run as a script
    args = sys.argv[1:]
    main(args)