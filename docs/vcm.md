We will compare two algorithms: 
- VCMNet from Futaisi et al. (2019)
- Meg's algorithm from Suresh et al. (2025)

To do so, we will work with our 25 hours of audio annotated by a single human expert (5 hours per diagnostic group).
Both classifiers will be applied exclusively on KCHI utterances.

To get the data, install ChildProject and datalad via:

```shell
conda env create -f env.yml
```

And then follow the instructions in the [L3_LENA_HIPAA](https://gin.g-node.org/MarvinLvn/L3_HIPAA_LENA) gin repository.
We'll be working from:

1. `metadata` which contains useful metadata including the child's diagnostic group and age
2. `annotations/eaf/an1/converted` which contains the manual annotation containing vocal maturity labels
3. `annotations/vcm/converted_from_human_timestamps` which contains automatic vocal maturity labels based on ground truth diarization

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
Zhang, T., Suresh, A., Warlaumont, A., Hitczenko, K., Cristia, A., Cychosz, M. (2025) Employing self-supervised learning models for cross-linguistic child speech maturity classification. In review in Interspeech.
```

