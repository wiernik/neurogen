### 0. Get the data

NeurogenSSD or on oberon:

```
/scratch1/data/raw_data/neurogen/L3_HIPAA_LENA_cleaned
```

You should have 381 (its, wav) file pairs.

### 1. Applying the ACLEW pipeline

Follow [the instructions to run VTC](https://github.com/MarvinLvn/voice-type-classifier) and place the output in `L3_HIPAA_LENA_cleaned/vtc/raw`.

Follow [the instructions to run ALICE](https://github.com/orasanen/ALICE) and place the resulting `ALICE_output.txt` and `diarization_output.rttm` files in `L3_HIPAA_LENA_cleaned/alice/raw`.

Follow [the instructions to run VCM](https://github.com/LAAC-LSCP/vcm) and place the resulting '*.vcm' files in `L3_HIPAA_LENA_cleaned/vcm/raw`.

Similarly, LENA output files (.its) are expected to be in `L3_HIPAA_LENA_cleaned/its/raw`

### 2. Converting automatic annotations to csv

```sh
# .its --> .csv (lena)
python utils/convert_anno.py --data_path L3_HIPAA_LENA_cleaned/annotations/its/raw --algo lena
# .rttm --> .csv (vtc)
python utils/convert_anno.py --data_path L3_HIPAA_LENA_cleaned/annotations/vtc/raw --algo vtc
# .txt --> .csv (alice)
python utils/convert_anno.py --data_path L3_HIPAA_LENA_cleaned/annotations/alice/utterance_files --algo alice
# .vcm --> .csv (vcm)
python utils/convert_anno.py --data_path L3_HIPAA_LENA_cleaned/annotations/vcm/raw --algo vcm
```

### 3. Create metadata (for compatibility with ChildProject)

```sh
python utils/create_metadata.py --data_path L3_HIPAA_LENA_cleaned
```

### 4. Compute confusion matrices between LENA & VTC (group level)

```sh
python metrics/compute_confusion.py --data_path L3_HIPAA_LENA_cleaned --set1 vtc --set2 its
```

This will generate `.npy` files for each group in the `results` folder.

### 5. Compute Cohen's kappa between LENA & VTC (file level)

```sh
python metrics/compute_agreement.py --data_path L3_HIPAA_LENA_cleaned --set1 vtc --set2 its
```

### 6. Compute metrics

For LENA:

```sh
python metrics/compute_standard_measures.py --data_path L3_HIPAA_LENA_cleaned --measures_file measure_files/custom_lena.csv --output lena_metrics.csv
```

For the ACLEW pipeline:

```sh
python metrics/compute_standard_measures.py --data_path L3_HIPAA_LENA_cleaned --measures_file measure_files/custom_aclew.csv --output aclew_metrics.csv
```

# Comparison to human annotations

### 1. Download .eaf files (from box) and place them in `L3_HIPAA_LENA_cleaned/annotations/eaf/an1/raw`

### 2. Update annotations.csv with human-annotated files using the following command:

```sh
python utils/add_gold_to_annotations.py \
  --data_path data/L3_HIPAA_LENA_cleaned/annotations/eaf/an1/raw \
  --annotations_csv_path data/L3_HIPAA_LENA_cleaned/metadata/annotations.csv
```

This will create a file `data/L3_HIPAA_LENA_cleaned/metadata/annotations2.csv`. 
After reviewing it, you can remove `annotations.csv` and replace it by this new file.

### (2.5) Update annotations.csv with VCM files using the following command (only if not already done):

```shell
python utils/add_vcm_to_annotations.py \
  --data_path  data/L3_HIPAA_LENA_cleaned/annotations/vcm/raw \
  --annotations_csv_path  data/L3_HIPAA_LENA_cleaned/metadata/annotations.csv
```

Again this will create a file `annotations2.csv` that you can rename `annotations.csv` after reviewing it.

### 3. Convert `.eaf` to `.csv`:

```sh
python utils/convert_anno.py --data_path data/L3_HIPAA_LENA_cleaned/annotations/eaf/an1/raw --algo eaf
```

### 4. Compute standard measures from human annotations files

```sh
# Extract human metrics from the 2-mn chunks
python metrics/compute_standard_measures.py --data_path data/L3_HIPAA_LENA_cleaned --measures_file measures_files/custom_human_chunks.csv --output human_measures_chunks.csv --only_human_annotated
# Extract the same metrics from LENA
python metrics/compute_standard_measures.py --data_path data/L3_HIPAA_LENA_cleaned --measures_file measures_files/custom_lena_chunks.csv --output lena_measures_chunks.csv --only_human_annotated
# Extract the same metrics from ACLEW
python metrics/compute_standard_measures.py --data_path data/L3_HIPAA_LENA_cleaned --measures_file measures_files/custom_aclew_chunks.csv --output aclew_measures_chunks.csv --only_human_annotated
```

### 5. Compute precision, recall, and fscore

```sh
# For LENA
python metrics/compute_pyannote_metrics.py --data_path data/L3_HIPAA_LENA_cleaned --hyp its --ref eaf/an1 --metric fscore
# For VTC
python metrics/compute_pyannote_metrics.py --data_path data/L3_HIPAA_LENA_cleaned --hyp vtc --ref eaf/an1 --metric fscore
```

### 7. Compute confusion matrices 

```sh
# Between lena and human
python metrics/compute_confusion.py --data_path data/L3_HIPAA_LENA_cleaned --set1 its --set2 eaf/an1
# Between vtc and human
python metrics/compute_confusion.py --data_path data/L3_HIPAA_LENA_cleaned --set1 vtc --set2 eaf/an1
```

### 8. Compute kappa

```shell
# Compute Kappa between VTC and human over 2-mn human-annotated chunks
python metrics/compute_agreement.py --data_path data/L3_HIPAA_LENA_cleaned --set1 vtc --set2 eaf/an1 --two_mn_clip_level
# between LENA and human
python metrics/compute_agreement.py --data_path data/L3_HIPAA_LENA_cleaned --set1 its --set2 eaf/an1 --two_mn_clip_level
```

### 9. Compute identification error rate and percentage correct

```shell
python metrics/compute_pyannote_metrics.py --data_path data/L3_HIPAA_LENA_cleaned --hyp its --ref eaf/an1 --metric ider --two_mn_clip_level
python metrics/compute_pyannote_metrics.py --data_path data/L3_HIPAA_LENA_cleaned --hyp vtc --ref eaf/an1 --metric ider --two_mn_clip_level
```
### 10. Add pitch measures

```shell
# For human
python utils/add_pitch_to_measures.py --annotation_folder data/L3_HIPAA_LENA_cleaned/annotations/eaf/an1/converted --audio_folder data/L3_HIPAA_LENA_cleaned/annotations/eaf/an1/raw/audio_chunks --measures_path human_measures_chunks.csv
# For ACLEW
python utils/add_pitch_to_measures.py --annotation_folder data/L3_HIPAA_LENA_cleaned/annotations/vcm/converted --audio_folder data/L3_HIPAA_LENA_cleaned/annotations/eaf/an1/raw/audio_chunks --measures_path aclew_measures_chunks.csv --automatic
# For LENA
python utils/add_pitch_to_measures.py --annotation_folder data/L3_HIPAA_LENA_cleaned/annotations/its/converted --audio_folder data/L3_HIPAA_LENA_cleaned/annotations/eaf/an1/raw/audio_chunks --measures_path lena_measures_chunks.csv --automatic
```