"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from pydantic import BaseModel
from typing import  Optional

class TrainingDataset(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    fileType: Optional[str] = None 
    path: Optional[dict] = None
    label: Optional[str] = None
    extension: Optional[str] = None


class Mitigation(BaseModel):
    method: Optional[str] = None
    mitigationType: Optional[str] = None ,
    mitigationTechnique: Optional[str] = None,
    biasType: Optional[str] = None
    taskType: Optional[str] = None
    trainingDataset: Optional[TrainingDataset] = None
    features: Optional[str] = None
    categoricalAttributes: Optional[str] = None
    ca_dict : Optional[dict] = None
    favourableOutcome: Optional[list] = []
    labelmaps: Optional[dict] = {}
    facet: Optional[list] = None
    outputPath: Optional[dict] = {
    "storage": "INFY_AICLD_NUTANIX",
    "uri": "responsible-ai//responsible-ai-fairness//output_api.json"
  }