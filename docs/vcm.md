We will compare two algorithms: 
- VCMNet from Futaisi et al. (2019)
- Meg's algorithm from Suresh et al. (2025)

To do so, we will work with our 25 hours of audio annotated by a single human expert (5 hours per diagnostic group).
Both classifiers will be applied exclusively on KCHI utterances.

# A. Applying [VCMNet](https://github.com/LAAC-LSCP/vcm)

1. First, we need to extract KCHI utterances from annotation files:

```sh
python utils/extract_rttm_KCHI.py --data data/L3_HIPAA_LENA_cleaned/annotations/eaf/an1/converted --output data/L3_HIPAA_LENA_cleaned/annotations/eaf/an1/rttm
```

This will create a folder containing .rttm files with KCHI utterances such as found by the human annotator. 

2. We can then apply VCM following the instructions in this [git](https://github.com/LAAC-LSCP/vcm).

# B. Applying [Meg's algorithm](https://github.com/spoglab-stanford/w2v2-pro-sm/tree/main/speechbrain/recipes/W2V2-LL4300-Pro-SM)

1. Install the dependencies:

```shell
git clone https://github.com/spoglab-stanford/w2v2-pro-sm
cd w2v2-pro-sm/speechbrain/recipes/W2V2-LL4300-Pro-SM
conda create -n megvcm python=3.10 -y
pip install -r requirements.txt
```

2. a

# C. 

# References 

```
Al Futaisi, N., Zhang, Z., Cristia, A., Warlaumont, A., & Schuller, B. (2019). VCMNet: Weakly supervised learning for automatic infant vocalisation maturity analysis. International Conference on Multimodal Interaction (pp. 205-209).
Zhang, T., Suresh, A., Warlaumont, A., Hitczenko, K., Cristia, A., Cychosz, M. (2025) Employing self-supervised learning models for cross-linguistic child speech maturity classification. In review in Intersspech.
```

