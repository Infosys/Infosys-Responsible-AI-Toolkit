'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from cov_llama import CovLlama
import pytest
import os

@pytest.fixture(scope="session", autouse=True)
def set_env():
    os.environ["LLAMA_ENDPOINT"]="https://api-aicloud.ad.infosys.com/v1/language/generate/models/llama2-7b/versions/1/infer"

@pytest.mark.filterwarnings("ignore")
def test_cov(): 
    '''unit test for service.py method cov()'''
    text = "Which is the largest country?"
    complexity = "simple"
    keys = ['original_question','baseline_response','verification_question','verification_answers','final_answer','timetaken']
    response=CovLlama.cov(text,complexity)

    assert list(response.keys())==keys
    assert response.get(keys[0])==text
    assert response.get(keys[1]) is not None
    assert response.get(keys[2]) is not None
    assert response.get(keys[3]) is not None
    assert response.get(keys[4]) is not None

    complexity = "medium"
    response=CovLlama.cov(text,complexity)
    assert list(response.keys())==keys
    assert response.get(keys[0])==text
    assert response.get(keys[1]) is not None
    assert response.get(keys[2]) is not None
    assert response.get(keys[3]) is not None
    assert response.get(keys[4]) is not None
    complexity = "complex"
    response=CovLlama.cov(text,complexity)
    assert list(response.keys())==keys
    assert response.get(keys[0])==text
    assert response.get(keys[1]) is not None
    assert response.get(keys[2]) is not None
    assert response.get(keys[3]) is not None
    assert response.get(keys[4]) is not None
