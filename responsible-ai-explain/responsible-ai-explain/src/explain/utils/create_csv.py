'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from explain.config.logger import CustomLogger
import pandas as pd
import os

log = CustomLogger()

class CreateCSV:

    def json_to_csv(json_response: list):
        try:
            for item in json_response:
                data = []
                if item['scope'] == 'LOCAL':
                    explanations = item.get('anchors') or item.get('featureImportance') or item.get('timeSeriesForecast') or item.get('shapImportanceText')
                    if explanations is not None:
                        for exp in explanations:
                            features = {}
                            if exp.inputRow is not None:
                                features = {ele['featureName']: ele['featureValue'] for ele in exp.inputRow}
                            elif exp.inputText is not None:
                                features['input'] = exp.inputText

                            features['prediction'] = exp.modelPrediction
                            if isinstance(exp.explanation[0], dict):
                                features['explanation'] = exp.explanation
                            else:
                                features['explanation'] = '; '.join(exp.explanation)

                            data.append(features)

                    if data:
                        df = pd.DataFrame(data)
                        output_dir = '../output'
                        output_file = os.path.join(output_dir, "local_explanation.csv")
                        os.makedirs(output_dir, exist_ok=True)
                        df.to_csv(output_file, index=False)
        
        except Exception as e:
            log.error(e, exc_info=True)
            raise