#!/usr/bin/env python3
import argparse
import pandas as pd
from pathlib import Path

def extract_onset_from_filename(filename):
    """Extract onset from filename (second-to-last underscore part)"""
    parts = Path(filename).stem.split('_')
    return int(parts[-2]) / 1000.0  # Convert ms to seconds

def process_file(file_path, output_path, file_onset):
    """Add file onset to utterance onsets in 4th column"""
    try:
        # Check if file is empty
        if file_path.stat().st_size == 0:
            # Copy empty file as-is
            output_path.touch()
            return

        df = pd.read_csv(file_path, sep=' ', header=None, na_filter=False)
        if df.empty or df.shape[1] < 4:
            # Copy empty or insufficient column files as-is
            df.to_csv(output_path, sep=' ', header=False, index=False, na_rep='<NA>')
        else:
            df.iloc[:, 3] = pd.to_numeric(df.iloc[:, 3]) + file_onset
            df.to_csv(output_path, sep=' ', header=False, index=False, na_rep='<NA>')
    except Exception:
        # Copy file as-is if reading fails
        with open(file_path, 'r') as f_in, open(output_path, 'w') as f_out:
            f_out.write(f_in.read())

def main():
    parser = argparse.ArgumentParser(description='Add file onset to utterance onsets in VCM files')
    parser.add_argument('--folder_path', help='Path to folder containing VCM files')
    parser.add_argument('--output_path', help='Path to output folder')

    args = parser.parse_args()
    folder_path = Path(args.folder_path)
    output_path = Path(args.output_path)

    if not folder_path.is_dir():
        print(f"Error: {folder_path} is not a valid directory")
        return 1

    output_path.mkdir(exist_ok=True)
    csv_files = folder_path.glob('*.vcm')

    for csv_file in csv_files:
        print(f"Processing {csv_file}")
        file_onset = extract_onset_from_filename(csv_file.name)
        output_file = output_path / csv_file.name
        process_file(csv_file, output_file, file_onset)
        print(f"Updated {csv_file.name}")

    return 0

if __name__ == "__main__":
    exit(main())