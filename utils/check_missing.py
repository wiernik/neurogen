from pathlib import Path
import pandas as pd

its_folder = Path('/gpfsscratch/rech/xdz/uow84uh/DATA/neurogen/L3_HIPAA_LENA/its')
wav_folder = Path('/gpfsscratch/rech/xdz/uow84uh/DATA/neurogen/L3_HIPAA_LENA/wav')
csv_path = Path('/gpfsscratch/rech/xdz/uow84uh/DATA/neurogen/LENA/LENADataset_Full.csv')
its_filenames = pd.read_csv(csv_path, encoding='ISO-8859-1')
its_filenames = its_filenames[~its_filenames['Location'].isin(['asmt', 'amst'])]
its_filenames = its_filenames[~its_filenames['Study'].isin(['TraCS', 'PANDA_LatinX'])]

print(its_filenames['Study'].unique())
its_filenames = its_filenames[['ITS_File_Name', 'Study']]

missing_its = []
missing_wav = []
retrieved_its = 0
retrieved_wav = 0

has_its_but_missing_wav = []
has_wav_but_missing_its = []

for its_filename, its_study in zip(its_filenames['ITS_File_Name'], its_filenames['Study']):
    its_path = its_folder / its_filename
    wav_path = wav_folder / (its_filename.replace('.its', '.wav'))

    if not its_path.is_file():
        missing_its.append((its_path.stem, its_study))
        has_its = False
    else:
        retrieved_its += 1
        has_its = True

    if not wav_path.is_file():
        missing_wav.append((wav_path.stem, its_study))
        has_wav = False
    else:
        retrieved_wav += 1
        has_wav = True

    if has_its and not has_wav:
        has_its_but_missing_wav.append((its_path.stem, its_study))
    if has_wav and not has_its:
        has_wav_but_missing_its.append((wav_path.stem, its_study))

def write(filename, L):
    with open(filename, 'w') as fin:
        for line in L:
            fin.write(f'{line[0]} {line[1]}\n')

write('missing_its.txt', missing_its)
write('missing_wav.txt', missing_wav)


if len(has_its_but_missing_wav) > 0:
    write('has_its_but_missing_wav.txt', has_its_but_missing_wav)
if len(has_wav_but_missing_its) > 0:
    write('has_wav_but_missing_its.txt', has_wav_but_missing_its)

print(f"Could retrieve {retrieved_its}/{len(its_filenames)} its files and {retrieved_wav}/{len(its_filenames)} wav files.")
print(f"{len(missing_its)} missing its files.")
print(f"{len(missing_wav)} missing wav files.")
print("Done.")
