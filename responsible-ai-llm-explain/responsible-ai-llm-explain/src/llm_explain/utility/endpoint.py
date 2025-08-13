'''
Copyright 2024 Infosys Ltd.

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

from llm_explain.config.logger import CustomLogger
import requests
import json
import re
import copy

log = CustomLogger()

class APIEndpoint:

    def convert_path_to_list(param_str):
        # Use regular expressions to find keys and indices
        parts = re.findall(r'\[([^\]]+)\]', param_str)
        
        # Convert numeric parts to integers and strip quotes from strings
        result = [int(part) if part.isdigit() else part.strip("'").strip('"') for part in parts]
    
        return result

    def endpoint_calling(prompt, modelEndpointUrl, endpointInputParam, endpointOutputParam):
        try:
            # Create a copy of the endpointInputParam dictionary
            endpointInputParamCopy = copy.deepcopy(endpointInputParam)
            # Create a copy of the dictionary items for safe iteration
            for key, value in list(endpointInputParamCopy.items()):
                if key == "input_parameter":
                    # Assign the value to the new key and delete the old one
                    endpointInputParamCopy[value] = prompt
                    del endpointInputParamCopy[key]
    
            # Convert the endpointInputParam to JSON
            payload = json.dumps(endpointInputParamCopy)
            headers = {
                'Content-Type': 'application/json'
            }
            result = requests.request("POST", modelEndpointUrl, headers=headers, data=payload, verify=False).json()
            explanation = result
            # Parse the endpointOutputParam string into a list of keys/indices
            parsed_output_param = APIEndpoint.convert_path_to_list(endpointOutputParam)
            # Traverse the explanation dictionary using the parsed_output_param list
            for key in parsed_output_param:
                explanation = explanation[key]
            return explanation
        except requests.exceptions.RequestException as e:
            log.error(f"API endpoint error: {e}")
            

    
        
    