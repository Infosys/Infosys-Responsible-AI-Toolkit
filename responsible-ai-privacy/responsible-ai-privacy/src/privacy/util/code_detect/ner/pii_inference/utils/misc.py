'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


import numpy as np
from scipy.special import softmax
from sklearn.metrics import average_precision_score
from privacy.util.code_detect.ner.pii_inference.utils.seqevel_metric import Seqeval

LABEL2ID = {'O': 0,
            'B-AMBIGUOUS': 1,
            'I-AMBIGUOUS': 2,
            'B-EMAIL': 3,
            'I-EMAIL': 4,
            'B-IP_ADDRESS': 5,
            'I-IP_ADDRESS': 6,
            'B-KEY': 7,
            'I-KEY': 8,
            'B-NAME': 9,
            'I-NAME': 10,
            'B-PASSWORD': 11,
            'I-PASSWORD': 12,
            'B-USERNAME': 13,
            'I-USERNAME': 14}

ID2LABEL = ['O',
            'B-AMBIGUOUS',
            'I-AMBIGUOUS',
            'B-EMAIL',
            'I-EMAIL',
            'B-IP_ADDRESS',
            'I-IP_ADDRESS',
            'B-KEY',
            'I-KEY',
            'B-NAME',
            'I-NAME',
            'B-PASSWORD',
            'I-PASSWORD',
            'B-USERNAME',
            'I-USERNAME']

_seqeval_metric = Seqeval()


def compute_ap(pred, truth):
    pred_proba = 1 - softmax(pred, axis=-1)[..., 0]
    pred_proba, truth = pred_proba.flatten(), np.array(truth).flatten()
    pred_proba = pred_proba[truth != -100]
    truth = truth[truth != -100]

    return average_precision_score(truth != 0, pred_proba)


def compute_metrics(p):
    predictions, labels = p
    avg_prec = compute_ap(predictions, labels)
    predictions = np.argmax(predictions, axis=2)

    # Remove ignored index (special tokens)
    true_predictions = [
        [ID2LABEL[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [ID2LABEL[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]

    results = _seqeval_metric.compute(predictions=true_predictions, references=true_labels)
    agg_metrics = {
        "Avg.Precision": avg_prec,
        "precision": results.pop("overall_precision"),
        "recall": results.pop("overall_recall"),
        "f1": results.pop("overall_f1"),
    }
    results.pop("overall_accuracy")
    per_cat_metrics = {name: metrics['f1'] for name, metrics in results.items()}

    return dict(**agg_metrics, **per_cat_metrics)
