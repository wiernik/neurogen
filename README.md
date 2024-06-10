### 0. Get the data

NeurogenSSD or on oberon:

```
/scratch1/data/raw_data/neurogen/L3_HIPAA_LENA_cleaned
```

You should have 381 (its, wav) file pairs.

### 1. Applying the Voice Type Classifier (VTC)

Follow instructions at https://github.com/MarvinLvn/voice-type-classifier
and place the output in `L3_HIPAA_LENA_cleaned/vtc/raw`.

Similarly, LENA output files (.its) are expected to be in `L3_HIPAA_LENA_cleaned/its/raw`

### 2. Converting automatic annotations to csv

```sh
# .its --> .csv (lena)
python utils/convert_anno.py --data_path L3_HIPAA_LENA_cleaned/its/raw --ext .its
# .rttm --> .csv (vtc)
python utils/convert_anno.py --data_path L3_HIPAA_LENA_cleaned/vtc/raw --ext .rttm
```

### 3. Create metadata (for compatibility with ChildProject)

```sh
python utils/create_metadata.py --data_path L3_HIPAA_LENA_cleaned
```

### 4. Compute confusion matrices between LENA & VTC (group level)

```sh
python compute_confusion.py --data_path L3_HIPAA_LENA_cleaned
```

This will generate `.npy` files for each group in the `results` folder.

### 5. Compute gamma agreement rates between LENA & VTC (file level)

```sh
WIP
```