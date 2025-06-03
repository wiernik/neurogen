#!/usr/bin/env python3
"""
Convert CSV files in a folder to RTTM format.

Example usage:
python utils/extract_rttm_KCHI.py --data data/L3_HIPAA_LENA_cleaned/annotations/eaf/an1/converted --output data/L3_HIPAA_LENA_cleaned/annotations/eaf/an1/rttm
"""

import argparse
import csv
import os
from pathlib import Path
import pandas as pd
from tqdm import tqdm

def read_csv(path):
    data = pd.read_csv(path, sep=',')
    data['filename'] = path.stem
    file_onset = int(path.stem.split('_')[-2])
    data['segment_onset'] = data['segment_onset'] - file_onset
    data['segment_offset'] = data['segment_offset'] - file_onset
    return data

def csv2rttm(csv_data):
    cols = csv_data.columns
    assert 'segment_onset' in cols and 'segment_offset' in cols and 'speaker_type' in colsx
    rttm = pd.DataFrame(index=csv_data.index)
    rttm['first'] = 'SPEAKER'
    rttm['second'] = csv_data['filename']
    rttm['third'] = 1
    rttm['fourth'] = csv_data['segment_onset'] / 1000
    rttm['fifth'] = (csv_data['segment_offset'] - csv_data['segment_onset'])/1000
    rttm['sixth'] = '<NA>'
    rttm['seventh'] = '<NA>'
    rttm['eigth'] = csv_data['speaker_type']
    rttm['ninth'] ='<NA>'
    rttm['tenth'] = '<NA>'

    # Remove voc < 0.06 s since VCM will return an error for them
    rttm = rttm[rttm['fifth'] > .06]

    # Replace ACLEW convention to VTC convention
    speaker_map = {'CHI': 'KCHI',
                   'OCH': 'CHI',
                   'MAL': 'MAL',
                   'FEM': 'FEM'}
    rttm['eigth'] = rttm['eigth'].map(lambda x: speaker_map[x])
    rttm = rttm[rttm['eigth'] == 'KCHI']
    return rttm

def write_rttm(rttm_data, rttm_path):
    rttm_data.to_csv(rttm_path, sep=' ', index=False, header=False)

def main():
    parser = argparse.ArgumentParser(description="Convert CSV files to RTTM format")
    parser.add_argument('--data', required=True, help='Path to the folder containing human annotation .csv files.')
    parser.add_argument('--output', required=True, help='Path to the output folder where rttm will be generated.')
    args = parser.parse_args()

    if args.data == args.output:
        raise ValueError("--output cannot be the same as --data.")

    args.data = Path(args.data)
    args.output = Path(args.output)
    args.output.mkdir(parents=True, exist_ok=True)

    csv_files = list(args.data.glob('*.csv'))
    if len(csv_files) == 0:
        raise ValueError(f"Cannot find .csv files in {args.data}")

    for csv_file in tqdm(csv_files):
        output_file = args.output / (csv_file.stem + '.rttm')
        csv_data = read_csv(csv_file)
        rttm_data = csv2rttm(csv_data)
        write_rttm(rttm_data, output_file)

if __name__ == '__main__':
    main()