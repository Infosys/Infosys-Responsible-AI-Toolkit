---
tags:
- generated_from_trainer
metrics:
- accuracy
- f1
- recall
- precision
model-index:
- name: codebert-base-Malicious_URLs
  results: []
language:
- en
pipeline_tag: text-classification
---

# codebert-base-Malicious_URLs

This model is a fine-tuned version of [microsoft/codebert-base](https://huggingface.co/microsoft/codebert-base).
It achieves the following results on the evaluation set:
- Loss: 0.8225
- Accuracy: 0.7279
- Weighted f1: 0.6508
- Micro f1: 0.7279
- Macro f1: 0.4611
- Weighted recall: 0.7279
- Micro recall: 0.7279
- Macro recall: 0.4422
- Weighted precision: 0.6256
- Micro precision: 0.7279
- Macro precision: 0.5436

## Model description

For more information on how it was created, check out the following link: https://github.com/DunnBC22/NLP_Projects/blob/main/Multiclass%20Classification/Malicious%20URLs/Malicious%20URLs%20-%20CodeBERT.ipynb

## Intended uses & limitations

This model is intended to demonstrate my ability to solve a complex problem using technology.

## Training and evaluation data

Dataset Source: https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset

_Input Word Length:_

![Length of Input Text (in Words)](https://github.com/DunnBC22/NLP_Projects/raw/main/Multiclass%20Classification/Malicious%20URLs/Images/Context%20Word%20Length.png)

_Input Word Length By Class:_

![Length of Input Text (in Words) By Class](https://github.com/DunnBC22/NLP_Projects/raw/main/Multiclass%20Classification/Malicious%20URLs/Images/Context%20Word%20Length%20By%20Class.png)

_Class Distribution:_

![Length of Input Text (in Words)](https://github.com/DunnBC22/NLP_Projects/raw/main/Sentiment%20Analysis/Sentiment%20Analysis%20of%20Commodity%20News%20-%20Gold%20(Transformer%20Comparison)/Images/Class%20Distribution.png)

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 2e-05
- train_batch_size: 64
- eval_batch_size: 64
- seed: 42
- optimizer: Adam with betas=(0.9,0.999) and epsilon=1e-08
- lr_scheduler_type: linear
- num_epochs: 1

### Training results

| Training Loss | Epoch | Step | Validation Loss | Accuracy | Weighted f1 | Micro f1 | Macro f1 | Weighted recall | Micro recall | Macro recall | Weighted precision | Micro precision | Macro precision |
|:-------------:|:-----:|:----:|:---------------:|:--------:|:-----------:|:--------:|:--------:|:---------------:|:------------:|:------------:|:------------------:|:---------------:|:---------------:|
| 0.8273        | 1.0   | 6450 | 0.8225          | 0.7279   | 0.6508      | 0.7279   | 0.4611   | 0.7279          | 0.7279       | 0.4422       | 0.6256             | 0.7279          | 0.5436          |

### Framework versions

- Transformers 4.27.4
- Pytorch 2.0.0
- Datasets 2.11.0
- Tokenizers 0.13.3