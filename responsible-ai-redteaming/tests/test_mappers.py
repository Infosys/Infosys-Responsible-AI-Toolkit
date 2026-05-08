'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import pytest


def test_excel_upload_response_pair_creation():
    """Test ExcelUploadResponsePAIR model creation"""
    from app.mappers.mappers import ExcelUploadResponsePAIR
    
    response = ExcelUploadResponsePAIR(
        total_rows=10,
        processed_rows=8,
        jailbroken_rows=2,
        technical_failed_rows=[3, 7],
        category_wise_score={"category1": {"score": 0.8}},
        technique_type="PAIR",
        target_endpoint_url="http://test.com",
        usecase_name="test_usecase",
        results=[{"test": "data"}],
        target_model="gpt-4",
        target_temperature=0.7,
        n_iterations=5,
        enable_moderation=True
    )
    
    assert response.total_rows == 10
    assert response.technique_type == "PAIR"
    assert response.jailbroken_rows == 2


def test_redteam_payload_request_pair_defaults():
    """Test RedteamPayloadRequestPair default values"""
    from app.mappers.mappers import RedteamPayloadRequestPair
    
    payload = RedteamPayloadRequestPair(
        goal="test goal",
        target_str="test target"
    )
    
    assert payload.goal == "test goal"
    assert payload.target_str == "test target"
    assert payload.attack_model is not None
    assert payload.n_streams > 0


def test_redteam_payload_request_tap_defaults():
    """Test RedteamPayloadRequestTap default values"""
    from app.mappers.mappers import RedteamPayloadRequestTap
    
    payload = RedteamPayloadRequestTap(
        goal="tap goal",
        target_str="tap target"
    )
    
    assert payload.goal == "tap goal"
    assert payload.target_str == "tap target"
    assert payload.attack_model is not None
    assert payload.branching_factor > 0
    assert payload.width > 0
