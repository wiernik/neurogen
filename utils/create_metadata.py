import sys
from pathlib import Path
import argparse
from tqdm import tqdm
import pandas as pd
import re
def create_annotations_metadata(data_path, duration):
    metadata = []
    for its_path in (data_path / 'annotations' / 'its' / 'raw').glob('*.its'):
        recording_filename =  its_path.stem+'.wav'
        # Create entry for its file
        metadata.append({'set': 'its',
                         'recording_filename': recording_filename,
                         'time_seek': 0,
                         'range_onset': 0,
                         'range_offset': int(duration[recording_filename]*1000),
                         'raw_filename': its_path.name,
                         'format': 'its',
                         'filter': '',
                         'annotation_filename':its_path.stem+'.csv',
                         'imported_at':'2024-07-10',
                         'error': '',
                         'package_version': 'custom'})
        # Create entry for rttm files
        metadata.append({'set': 'vtc',
                         'recording_filename': recording_filename,
                         'time_seek': 0,
                         'range_onset': 0,
                         'range_offset': int(duration[recording_filename]*1000),
                         'raw_filename': its_path.stem+'.rttm',
                         'format': 'vtc_rttm',
                         'filter': '',
                         'annotation_filename':its_path.stem+'.csv',
                         'imported_at':'2024-07-10',
                         'error': '',
                         'package_version': 'custom'})
        # Create entry for alice files
        metadata.append({'set': 'alice',
                         'recording_filename': recording_filename,
                         'time_seek': 0,
                         'range_onset': 0,
                         'range_offset': int(duration[recording_filename] * 1000),
                         'raw_filename': its_path.stem + '.txt',
                         'format': 'alice',
                         'filter': '',
                         'annotation_filename': its_path.stem + '.csv',
                         'imported_at': '2024-07-10',
                         'error': '',
                         'package_version': 'custom'})
    metadata = pd.DataFrame(metadata)
    metadata.drop_duplicates(inplace=True)
    metadata.sort_values(by='set', inplace=True)
    metadata.to_csv(data_path / 'metadata' / 'annotations.csv', index=False)

def create_children_metadata(data_path, csv_data):
    its_files = list((data_path / 'annotations' / 'its' / 'raw').glob('*.its'))
    its_files = [f.name for f in its_files]
    csv_data = csv_data[csv_data['ITS_File_Name'].isin(its_files)]
    metadata = []

    for idx, row in csv_data.iterrows():
        child_sex = row['child_sex'].strip()
        if child_sex == 'Male':
            child_sex = 'm'
        elif child_sex == 'Female':
            child_sex = 'f'
        else:
            raise ValueError(f"Cannot find the sex for child_sex = {child_sex}")
        group_id = row['group'].strip().replace(' ', '_').lower()
        mm, dd, yy = row['child_dob'].split('/')  # YYYY-MM-DD
        if len(yy) == 2:
            yy = f'20{yy}'
        child_dob = '%d-%02d-%02d' % (int(yy), int(mm), int(dd))
        metadata.append({'experiment': 'neurogen',
                         'child_id': row['child_id'],
                         'child_dob': child_dob,
                         'child_sex': child_sex,
                         'group_id': group_id})

    metadata = pd.DataFrame(metadata)
    metadata.drop_duplicates(inplace=True)
    metadata.sort_values(by='child_id', inplace=True)
    metadata.to_csv(data_path / 'metadata' / 'children.csv', index=False)

def create_recordings_metadata(data_path, csv_data, duration):
    its_files = list((data_path / 'annotations' / 'its' / 'raw').glob('*.its'))
    its_files = [f.name for f in its_files]
    csv_data = csv_data[csv_data['ITS_File_Name'].isin(its_files)]
    metadata = []
    for idx, row in csv_data.iterrows():
        mm, dd, yy = row['StartTime'].split(' ')[0].split('/')
        if len(yy) == 2:
            yy = f'20{yy}'
        recording_date = '%d-%02d-%02d' % (int(yy), int(mm), int(dd)) # YYYY-MM-DD
        start_time = re.sub(' +', ' ', row['StartTime']).split(' ')[1] # HH:MM:SS
        recording_filename = row['ITS_File_Name'].replace('.its', '.wav')
        group_id = row['group'].strip().replace(' ', '_').lower()
        metadata.append({'child_id': row['child_id'],
                         'experiment': 'neurogen',
                         'date_iso': recording_date,
                         'start_time': start_time,
                         'recording_device_type': 'lena',
                         'recording_filename': recording_filename,
                         'duration': int(duration[recording_filename]*1000),
                         'its_filename': row['ITS_File_Name']})
    metadata = pd.DataFrame(metadata)
    metadata.drop_duplicates(inplace=True)
    metadata.sort_values(by='duration', inplace=True)
    metadata.to_csv(data_path / 'metadata' / 'recordings.csv', index=False)

def main(argv):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--data_path', type=str, default='/home/engaclew/DATA/neurogen/L3_HIPAA_LENA_cleaned',
                        help='Path to the data folder')
    args = parser.parse_args(argv)
    data_path = Path(args.data_path)
    csv_path = data_path / 'LENADataset_Full.csv'
    duration_path = data_path / 'wav_duration.csv'
    csv_data = pd.read_csv(csv_path, encoding='ISO-8859-1')
    duration = pd.read_csv(duration_path, encoding='ISO-8859-1', header=None, sep=' ')
    duration.columns = ['filename', 'duration']
    duration = {k:v for k,v in zip(duration['filename'], duration['duration'])}

    create_annotations_metadata(data_path, duration)
    create_recordings_metadata(data_path, csv_data, duration)
    create_children_metadata(data_path, csv_data)

if __name__ == "__main__":
    # execute only if run as a script
    args = sys.argv[1:]
    main(args)