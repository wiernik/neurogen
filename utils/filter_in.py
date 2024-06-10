from pathlib import Path
import pandas as pd
import shutil
from tqdm import tqdm
its_folder = Path('/gpfsscratch/rech/xdz/uow84uh/DATA/neurogen/L3_HIPAA_LENA/its')
wav_folder = Path('/gpfsscratch/rech/xdz/uow84uh/DATA/neurogen/L3_HIPAA_LENA/wav')
csv_path = Path('/gpfsscratch/rech/xdz/uow84uh/DATA/neurogen/LENA/LENADataset_Full.csv')
output_path = Path('/gpfsscratch/rech/xdz/uow84uh/DATA/neurogen/L3_HIPAA_LENA_cleaned')

its_filenames = pd.read_csv(csv_path, encoding='ISO-8859-1')
its_filenames = its_filenames[~its_filenames['Location'].isin(['asmt', 'amst'])]
its_filenames = its_filenames[~its_filenames['Study'].isin(['TraCS', 'PANDA_LatinX'])]
its_filenames = its_filenames['ITS_File_Name']

for its_filename in tqdm(its_filenames):
    its_path = its_folder / its_filename
    wav_path = wav_folder / (its_filename.replace('.its', '.wav'))

    has_its = False
    if its_path.is_file():
        has_its = True

    has_wav = False
    if wav_path.is_file():
        has_wav = True

    if has_its and has_wav:
        shutil.copy(its_path, output_path / 'its' / its_path.name)
        shutil.copy(wav_path, output_path / 'wav' / wav_path.name)