import argparse
import os
import re
import sys
from pathlib import Path

import contractions
import pandas as pd
from ChildProject.converters import AnnotationConverter, ItsConverter, VtcConverter, AliceConverter, EafConverter, \
    VcmConverter
from tqdm import tqdm

AnnotationConverter.SPEAKER_ID_TO_TYPE = {
        "C1": "OCH",
        "C2": "OCH",
        "CHI": "CHI",
        "CHI*": "CHI",
        "FA0": "FEM",
        "FA1": "FEM",
        "FA2": "FEM",
        "FA3": "FEM",
        "FA4": "FEM",
        "FA5": "FEM",
        "FA6": "FEM",
        "FA7": "FEM",
        "FA8": "FEM",
        "FC1": "OCH",
        "FC2": "OCH",
        "FC3": "OCH",
        "MA0": "MAL",
        "MA1": "MAL",
        "MA2": "MAL",
        "MA3": "MAL",
        "MA4": "MAL",
        "MA5": "MAL",
        "MC1": "OCH",
        "MC2": "OCH",
        "MC3": "OCH",
        "MC4": "OCH",
        "MC5": "OCH",
        "MI1": "OCH",
        "MOT*": "FEM",
        "OC0": "OCH",
        "UC1": "OCH",
        "UC2": "OCH",
        "UC3": "OCH",
        "UC4": "OCH",
        "UC5": "OCH",
        "UC6": "OCH",
        "UA1": "NA",
        "UA2": "NA",
        "UA3": "NA",
        "UA4": "NA",
        "UA5": "NA",
        "UA6": "NA",
        "EE1": "NA",
        "EE2": "NA",
        "FAE": "NA",
        "MAE": "NA",
        "FCE": "NA",
        "MCE": "NA",
        "OCHI": "OCH", # I'm adding this one extra label (specific to Amanda Seidl)
        }

def write_data(data, output_path):
    if len(data.columns) == 0:
        data = pd.DataFrame([], columns=['segment_onset', 'segment_offset', 'speaker_id', 'speaker_type',
       'vcm_type', 'lex_type', 'mwu_type', 'addressee', 'transcription',
       'words'])
    data.to_csv(output_path, index=False)

def load_alice(count_file, diarization_file):
    # Load count
    count = pd.read_csv(count_file, sep='\t', header=None)
    count.columns = ['segment_path', 'phonemes', 'syllables', 'words']
    count['filename'] = count['segment_path'].map(lambda x: '_'.join(os.path.basename(x).split('_')[:-2]))
    count['onset'] = count['segment_path'].map(lambda x: int(os.path.basename(x).split('_')[-2]))
    count['offset'] = count['segment_path'].map(lambda x: int(os.path.basename(x).split('_')[-1].replace('.wav', '')))
    # Load diarization
    diarization = pd.read_csv(diarization_file, sep=' ', header=None)[[1,3,4,7]]
    diarization.columns = ['filename', 'onset', 'duration', 'speaker_type']
    diarization = diarization[diarization.speaker_type.isin(['MAL', 'FEM'])]
    diarization['onset'] = (10000*diarization['onset']).astype(int)
    diarization['duration'] = (10000*diarization['duration']).astype(int)
    diarization['offset'] = diarization['onset'] + diarization['duration']
    # Round to nearest multiple of ten (as ALICE) to avoid loosing rows
    diarization['onset'] = round(diarization['onset'], -1)
    diarization['offset'] = round(diarization['offset'], -1)

    # Merge and use childproject naming convention
    data = count.merge(diarization, on=['filename', 'onset', 'offset'], how='right')
    data = data[['filename', 'onset', 'offset', 'speaker_type', 'phonemes', 'syllables', 'words']]
    data['filename'] = data['filename'] + '.txt'
    data.columns = ['raw_filename', 'segment_onset', 'segment_offset', 'speaker_type', 'phonemes', 'syllables', 'words']
    data = data[['segment_onset', 'segment_offset', 'speaker_type', 'phonemes', 'syllables', 'words', 'raw_filename']]
    data['segment_onset'] = (data['segment_onset'] / 10).astype(int)
    data['segment_offset'] = (data['segment_offset'] / 10).astype(int)
    if len(data) < len(count):
        raise ValueError("Something went wrong when merging VTC & ALICE")
    return data

def count_words(transcription):
    '''
    This function derives the number of words produced by adult speakers from human transcription.
    It is adapted for Amanda Seidl's transcription scheme but should be refined for more complex schemes (e.g., the ACLEW one)
    '''
    # Remove 0.
    transcription = transcription.replace('0.', '')
    # 1. I noticed one typo } instead of ]
    transcription = transcription.replace('}', ']').replace('{', '[')
    # 2. Remove everything that's between brackets
    transcription = re.sub(r'\[.*?\]', '', transcription)
    # 3. Remove leading < and trailing >
    transcription = transcription.strip('<>')
    # 4. Remove double space
    transcription = re.sub(r' +', ' ', transcription)
    # 5. Transform contractions (isn't --> is not)
    transcription = contractions.fix(transcription)
    # 6. Remove leading/trailing whitespace
    transcription = transcription.strip(' ')
    return len(re.findall(r'\w+', transcription))

def main(argv):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--data_path', type=str, default='/home/engaclew/DATA/neurogen/L3_HIPAA_LENA_cleaned/annotations/its/raw',
                        help='Path to the folder containing its or rttm files')
    parser.add_argument('--algo', type=str, default='vtc', choices=['vtc', 'lena', 'alice', 'vcm', 'eaf'],
                        help='Extension of the files to be processed')
    args = parser.parse_args(argv)
    data_path = Path(args.data_path)

    if args.algo == 'vtc':
        converter = VtcConverter()
        ext = '.rttm'
    elif args.algo == 'vcm':
        converter = VcmConverter()
        ext = '.vcm'
    elif args.algo == 'lena':
        converter = ItsConverter()
        ext = '.its'
    elif args.algo == 'alice':
        converter = AliceConverter()
        ext = '.txt'
    elif args.algo == 'eaf':
        converter = EafConverter()
        ext = '.eaf'
    else:
        raise ValueError(f'Unknown algo {args.algo}. Please choose among [vtc, lena, alice, eaf].')

    output_folder = data_path.parent / data_path.stem.replace('raw', 'converted')

    output_folder.mkdir(parents=True, exist_ok=True)
    if args.algo in ['vtc', 'vcm', 'lena', 'eaf']:
        for file_path in tqdm(data_path.glob(f'*{ext}')):
            print(file_path)
            output_path = output_folder / (file_path.stem + '.csv')
            data = converter.convert(file_path)
            if args.algo == 'eaf' and len(data) > 0:
                splitted = file_path.stem.split('_')
                onset = int(splitted[-2])
                data['segment_onset'] += onset
                data['segment_offset'] += onset
                data.sort_values(by=['segment_onset'], inplace=True)
                data['words'] = data['transcription'].map(count_words)
            write_data(data, output_path)
    elif args.algo == 'alice':
        data = load_alice(count_file=data_path / 'ALICE_output.txt', diarization_file=data_path / 'diarization_output.rttm')
        filenames = data['raw_filename'].unique()
        for filename in tqdm(filenames):
            subdata = data[data.raw_filename == filename]
            stem = filename.replace('.txt', '')
            output_path = output_folder / (stem + '.csv')
            write_data(subdata, output_path)


if __name__ == "__main__":
    # execute only if run as a script
    args = sys.argv[1:]
    main(args)