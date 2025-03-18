import sys
from pathlib import Path
import pandas as pd
import argparse
from datetime import date

def main(argv):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--data_path', type=str, default='/home/engaclew/DATA/neurogen/L3_HIPAA_LENA_cleaned/annotations/vcm/raw',
                        help='Path to the folder containing VCM files (.vcm)')
    parser.add_argument('--annotations_csv_path', type=str,
                        default='/home/engaclew/DATA/neurogen/L3_HIPAA_LENA_cleaned/metadata/annotations.csv',
                        help='Path to the .csv file containing the list of annotations')
    args = parser.parse_args(argv)
    data_path = Path(args.data_path)
    metadata_path = Path(args.annotations_csv_path)

    # Load annotation
    annotations = pd.read_csv(metadata_path, sep=',')
    annotations = annotations[annotations.set != 'vcm']

    vcm_annotations = annotations[annotations.set == 'vtc'].copy(deep=True)
    vcm_annotations['set'] = 'vcm'
    vcm_annotations['format'] = 'vcm_rttm'
    vcm_annotations['raw_filename'] = vcm_annotations['raw_filename'].apply(lambda x: x.replace('.rttm', '.vcm'))
    current_date = date.today().strftime('%Y-%m-%d')
    vcm_annotations['imported_at'] = current_date

    merged_annotations = pd.concat([annotations, vcm_annotations], ignore_index=True)
    merged_annotations.to_csv(metadata_path.parent / 'annotations2.csv', index=False)
    print("Done.")

if __name__ == "__main__":
    # execute only if run as a script
    args = sys.argv[1:]
    main(args)