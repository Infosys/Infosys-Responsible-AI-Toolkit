'''
MIT License
https://mit-license.org/
Copyright © 2025 - 2026 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import logging
import sys
from io import StringIO


from privacy.mappers.mappers import PIIAnonymizeRequest, PIIAnonymizeResponse
from privacy.service.textPrivacy import TextPrivacy
logger = logging.getLogger(__name__)

def textAnonymize(input_text: str) -> str:
    try:
        request = PIIAnonymizeRequest(
            inputText=input_text,
            nlp="basic",
            portfolio=None,
            piiEntitiesToBeRedacted=None,
            exclusionList="",  
            scoreThreshold=0.7,
            fakeData=False  
        )
        
        
        
        result = TextPrivacy.anonymize(request)
        return result.anonymizedText
            
            
    except Exception as e:
        logger.error(f"Anonymization error: {e}")
        return input_text 
