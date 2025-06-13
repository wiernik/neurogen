#!/usr/bin/env python3
"""
Convert CSV files in a folder to RTTM format. Keep only KCHI segments

Example usage:
python utils/anonymize_human_annotations.py --data data/L3_HIPAA_LENA_cleaned/annotations/eaf/an1_with_transcript/converted --output data/L3_HIPAA_LENA_cleaned/annotations/eaf/an1/converted
"""

import argparse
import csv
import os
from pathlib import Path
import pandas as pd
from tqdm import tqdm

def read_csv(path):
    data = pd.read_csv(path, sep=',', keep_default_na=False)
    return data


def write_csv(csv_data, csv_path):
    csv_data.to_csv(csv_path, sep=',', index=False, header=True)

def main():
    parser = argparse.ArgumentParser(description="Convert CSV files to RTTM format")
    parser.add_argument('--data', required=True, help='Path to the folder containing human annotation .csv files.')
    parser.add_argument('--output', required=True, help='Path to the output folder where anonymized .csv files will be saved')
    args = parser.parse_args()
    args.data = Path(args.data)

    if args.data == args.output:
        raise ValueError("--output cannot be the same as --data.")

    csv_files = list(args.data.glob('*.csv'))
    if len(csv_files) == 0:
        raise ValueError(f"Cannot find .csv files in {args.data}")

    args.data = Path(args.data)
    args.output = Path(args.output)
    args.output.mkdir(parents=True, exist_ok=True)

    for csv_file in tqdm(csv_files):
        output_file = args.output / (csv_file.stem + '.csv')
        csv_data = read_csv(csv_file)
        csv_data['transcription'] = 'xxx'
        write_csv(csv_data, output_file)

if __name__ == '__main__':
    main()