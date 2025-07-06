####################### packages & setup #######################

import os
from pathlib import Path
import pandas as pd

# hardcoded path
base_dir = Path(r'C:\Users\lydia\L3_HIPAA_LENA') 

# relative path
# base_dir = Path('L3_HIPAA_LENA/annotations') 

human_files = list(base_dir.glob('annotations/eaf/an1/converted/*.csv'))
vcm_files = list(base_dir.glob('annotations/vcm/converted_from_human_timestamps/*.csv'))
meg_files = list(base_dir.glob('annotations/meg_vcm/converted_from_human_timestamps/*.csv'))

####################### pd dataframe / merge approach #######################

def files_to_dataframe(files, source):
    dfs = []
    for file_path in files:
        df = pd.read_csv(file_path)

        df = df[(df['speaker_type'] == 'CHI') &                         # filter for speaker type
                (df['vcm_type'] != 'U') &                               # filter out unsure labels
                (df['vcm_type'] != ' ') &                               # filter out blanks
                (pd.notna(df['vcm_type'])) &                            # filter out n/a labels
                ((df['segment_offset'] - df['segment_onset']) >= 60)]   # remove segments < 60ms
        
        df['source'] = source
        df['filename'] = os.path.basename(file_path)
        dfs.append(df)
    
    return pd.concat(dfs, ignore_index=True)

human_files = files_to_dataframe(human_files, 'human_annotations')
vcm_files = files_to_dataframe(vcm_files, 'VCMNet')
# meg_files = files_to_dataframe(meg_files, 'meg_classifier')

csv_files = human_files.merge(vcm_files, on=['segment_onset', 'segment_offset', 'filename'], 
                             suffixes=('_human', '_vcmnet'), how='inner')  # add suffixes for clarity

# below for when adding in meg_classifier
# csv_files = human_files.merge(vcm_files, on=['segment_onset', 'segment_offset', 'filename'], 
#                              suffixes=('_human', '_vcmnet'))\
#                        .merge(meg_files, on=['segment_onset', 'segment_offset', 'filename'], 
#                              suffixes=('', '_meg'), how='inner')

csv_files = csv_files[['filename', 'segment_onset', 'segment_offset', 
                       'vcm_type_human', 'vcm_type_vcmnet']]

# csv_files.to_csv("merge_csv_files_check.csv")

####################### concat approach #######################

# csv_files = []

# for annotation, file_list in [('human_annotations', human_files), 
#                               ('VCMNet', vcm_files), 
#                               ('meg_classifier', meg_files)]:
#     for file_path in file_list:
#         df = pd.read_csv(file_path, dtype={'segment_onset': int, 'segment_offset': int}) # make sure segments show up as ints

#         df = df[(df['speaker_type'] == 'CHI') &                         # filter for speaker type
#                 (df['vcm_type'] != 'U') &                               # filter out unsure labels
#                 (pd.notna(df['vcm_type'])) &                            # filter out n/a labels
#                 ((df['segment_offset'] - df['segment_onset']) >= 60)]   # remove segments < 60ms

#         df['source'] = annotation
#         df['filename'] = os.path.basename(file_path)
#         csv_files.append(df)

# csv_files = pd.concat(csv_files, ignore_index=True)

# csv_files = csv_files.pivot_table(
#     index=['filename', 'segment_onset', 'segment_offset'], 
#     columns='source', 
#     values='vcm_type',
#     aggfunc='first'
# ).reset_index()

# # csv_files.to_csv("csv_files_check.csv")

# ####################### confusion matrix #######################

labels = sorted(list(set(csv_files['vcm_type_human']) | 
                     set(csv_files['vcm_type_vcmnet'])))

VCMNet_human_confusion_matrix = pd.DataFrame(0, index=labels, columns=labels)

for human_label, vcm_label in zip(csv_files['vcm_type_human'], csv_files['vcm_type_vcmnet']):                          
    if pd.notna(human_label) and pd.notna(vcm_label):                        # robustness checks but maybe unnecessary?
        if human_label in labels and vcm_label in labels:                    # robustness checks but maybe unnecessary?
            VCMNet_human_confusion_matrix.loc[human_label, vcm_label] += 1              

# print(VCMNet_human_confusion_matrix)

# VCMNet_human_confusion_matrix.to_csv("no_unsure_vcmnet_human_matrix.csv")

# confusion_normalized = VCMNet_human_confusion_matrix.div(VCMNet_human_confusion_matrix.sum(axis=1), axis=0) * 100 # normalize by row and multiply by 100 for percentage
# confusion_normalized.to_csv("no_unsure_vcmnet_human_matrix_normalised.csv")
