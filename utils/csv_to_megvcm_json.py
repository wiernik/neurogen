#!/usr/bin/env python3
"""
Convert CSV files in a folder to RTTM format. Keep only KCHI segments

Example usage:
python utils/csv_to_megvcm_json.py --input /home/engaclew/neurogen/data/L3_HIPAA_LENA_cleaned/chunks/eaf_an1/chunks_20250613_205715.csv
"""

import argparse
import os
from pathlib import Path
import pandas as pd
import json

def convert_df_to_json(df, output_file=None):
    result_dict = {}

    for idx, row in df.iterrows():
        # Extract filename without extension from wav path
        wav_path = row['wav']
        filename = os.path.splitext(os.path.basename(wav_path))[0]

        # Create entry for this file
        result_dict[filename] = {
            "wav": row['wav'],
            "label": row['label'],
            "child_ID": str(row['child_ID']),  # Ensure it's a string
            "hyp_pr": row['hyp_pr']
        }

    # Save to file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)
        print(f"JSON saved to {output_file}")

    return result_dict

def main():
    parser = argparse.ArgumentParser(description="Convert CSV files to JSON format for Meg's VM")
    parser.add_argument('--input', required=True, help='Path to the .csv file containing 500-ms chunks')
    args = parser.parse_args()

    args.input = Path(args.input).resolve()
    data = pd.read_csv(args.input)[['wav']]
    data['wav'] = str(args.input.parent) + '/chunks/' + data['wav']
    data['label'] = 'Junk'
    data['child_ID'] = '0'
    data['hyp_pr'] = "o\u028a"

    output_file = args.input.parent / f'{args.input.stem}_meg_vcm.json'
    convert_df_to_json(data, output_file)
    print("Saving resulting json to {}".format(output_file))

if __name__ == '__main__':
    main()