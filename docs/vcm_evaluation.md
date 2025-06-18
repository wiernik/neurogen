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
2. `annotations/eaf/an1/converted` which contains the manual annotation with human vocal maturity labels
3. `annotations/vcm/converted_from_human_timestamps` which contains automatic vocal maturity labels (VCMNet) based on ground truth diarization

To run the vocal maturity classifiers, please follow [these instructions](vcm_inference).

# A. 

# References 

```
Al Futaisi, N., Zhang, Z., Cristia, A., Warlaumont, A., & Schuller, B. (2019). VCMNet: Weakly supervised learning for automatic infant vocalisation maturity analysis. International Conference on Multimodal Interaction (pp. 205-209).
Zhang, T., Suresh, A., Warlaumont, A., Hitczenko, K., Cristia, A., Cychosz, M. (2025) Employing self-supervised learning models for cross-linguistic child speech maturity classification. In review in Interspeech.
```

