"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from transformers import BartForSequenceClassification, BartTokenizer
import torch
from fairness.constants.llm_constants import *
from fairness.config.logger import CustomLogger
log = CustomLogger()
class BartService:
    def __init__(self): 
        self.model = BartForSequenceClassification.from_pretrained(MODEL_PATH)
        self.tokenizer = BartTokenizer.from_pretrained(TOKENIZER_PATH)
        # self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # self.model.to(self.device)
        self.model.eval()

    def predict(self, text: str):
         # Tokenize the input text
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding='max_length', max_length=128)

        # Perform inference
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Get the predicted label
        logits = outputs.logits
        predicted_class_id = torch.argmax(logits, dim=-1).item()

        # Map the predicted class ID to the corresponding label
        label_mapping = {0: "Stereotype", 1: "Non-Stereotype", 2: "Negated Stereotype"}
        predicted_label = label_mapping[predicted_class_id]
        return predicted_label