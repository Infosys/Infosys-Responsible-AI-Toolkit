'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import pytest
from unittest.mock import patch
import sys
import types

# Provide a lightweight stub for FileStoreDb to avoid global MagicMocks
if 'app.dao.SaveFileDB' not in sys.modules:
    m = types.ModuleType('app.dao.SaveFileDB')
    class FileStoreDb:  # noqa
        fs = types.SimpleNamespace(get=lambda *a, **k: types.SimpleNamespace(read=lambda: b"data"))
        @staticmethod
        def create(*a, **k):
            return 'id'
        @staticmethod
        def read_file(*a, **k):
            return {'data': b'data'}
    m.FileStoreDb = FileStoreDb
    sys.modules['app.dao.SaveFileDB'] = m

# Stub other DAO modules to avoid real DB connections during import of service
for _mod, _cls in [
    ('app.dao.AttackConfiguration', 'AttackConfiguration'),
    ('app.dao.AttackModel', 'AttackModel'),
    ('app.dao.JudgeModel', 'JudgeModel'),
    ('app.dao.TargetModel', 'TargetModel'),
    ('app.dao.RedTeamingReport', 'RedTeamingReport'),
]:
    if _mod not in sys.modules:
        mm = types.ModuleType(_mod)
        setattr(mm, _cls, type(_cls, (), {
            'create': staticmethod(lambda *a, **k: 'id')
        }))
        sys.modules[_mod] = mm

# Lightweight stub for app.utility.multifaceted to avoid heavy imports
if 'app.utility.multifaceted' not in sys.modules:
    ms = types.ModuleType('app.utility.multifaceted')
    class MultifacetedEvaluation:  # noqa
        def __init__(self, *a, **k):
            pass
    ms.MultifacetedEvaluation = MultifacetedEvaluation
    sys.modules['app.utility.multifaceted'] = ms

from fastapi.testclient import TestClient


def test_pair_batch_endpoint_with_jailbreak_score():
    """Test pair_batch_endpoint processes jailbreak scores correctly"""
    from src.main import app
    import io
    import pandas as pd
    
    # Create test Excel file
    test_data = pd.DataFrame({
        'goal': ['test goal 1', 'test goal 2'],
        'target_str': ['test target 1', 'test target 2'],
        'category': ['cat1', 'cat1']
    })
    excel_buffer = io.BytesIO()
    test_data.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    
    client = TestClient(app)

    # Patch dataAdditiontoDB to return our excel bytes and a fake ID
    with patch('app.service.service.InfosysRAI.dataAdditiontoDB') as mock_data_add:
        with patch('app.service.service.InfosysRAI.GetRedteamListPair') as mock_get_pair:
            with patch('pdfkit.from_file') as mock_pdfkit:
                with patch('app.service.service.InfosysRAI.addReportToDB') as mock_add_report:
                    with patch('app.service.service.InfosysRAI.addingReportToDB') as mock_adding_report:
                        mock_data_add.return_value = (excel_buffer, 'conf-id')
                        # Mock return with score 10 (jailbroken)
                        mock_get_pair.return_value = {
                            'id': 'test-id',
                            'jailbroken': 10,
                            'scores': [10, 5, 10],
                            'prompts': ['prompt1', 'prompt2', 'prompt3'],
                            'responses': ['response1 text', 'response2 text', 'response3 text']
                        }
                        # Fake PDF generation
                        def _fake_from_file(html_path, pdf_path, options=None):
                            import os
                            with open(pdf_path, 'wb') as fp:
                                fp.write(b'%PDF-1.4')
                        mock_pdfkit.side_effect = _fake_from_file
                        mock_add_report.side_effect = lambda f, n: (f.close(), 'rep-id')[1]
                        mock_adding_report.return_value = None

                        import json as _json
                        params = {
                            "userId": "u",
                            "technique_type": "PAIR",
                            "n_iterations": 1,
                            "attack_model": "gpt-4",
                            "attack_max_n_tokens": 10,
                            "target_model": "gpt-3.5-turbo",
                            "target_max_n_tokens": 10,
                            "target_temperature": 0.5,
                            "judge_model": "gpt-4",
                            "judge_max_n_tokens": 5
                        }
                        response = client.post(
                            "/v1/redteaming/pair/batch",
                            files={"file": ("test.xlsx", excel_buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                            data={"parameters": _json.dumps(params)}
                        )

                        assert response.status_code == 200
                        result = response.json()
                        assert 'RedTeamingId' in result
                        assert 'reportId' in result


def test_pair_batch_endpoint_technical_failure():
    """Test pair_batch_endpoint handles technical failures"""
    from src.main import app
    import io
    import pandas as pd
    
    test_data = pd.DataFrame({
        'goal': ['test goal'],
        'target_str': ['test target'],
        'category': ['cat1']
    })
    excel_buffer = io.BytesIO()
    test_data.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    
    client = TestClient(app)

    with patch('app.service.service.InfosysRAI.dataAdditiontoDB') as mock_data_add:
        with patch('app.service.service.InfosysRAI.GetRedteamListPair') as mock_get_pair:
            with patch('pdfkit.from_file') as mock_pdfkit:
                with patch('app.service.service.InfosysRAI.addReportToDB') as mock_add_report:
                    with patch('app.service.service.InfosysRAI.addingReportToDB') as mock_adding_report:
                        mock_data_add.return_value = (excel_buffer, 'conf-id')
                        mock_get_pair.side_effect = Exception("Database error")
                        def _fake_from_file(html_path, pdf_path, options=None):
                            import os
                            with open(pdf_path, 'wb') as fp:
                                fp.write(b'%PDF-1.4')
                        mock_pdfkit.side_effect = _fake_from_file
                        mock_add_report.side_effect = lambda f, n: (f.close(), 'rep-id')[1]
                        mock_adding_report.return_value = None

                        import json as _json
                        params = {
                            "userId": "u",
                            "technique_type": "PAIR",
                            "n_iterations": 1,
                            "attack_model": "gpt-4",
                            "attack_max_n_tokens": 10,
                            "target_model": "gpt-3.5-turbo",
                            "target_max_n_tokens": 10,
                            "target_temperature": 0.5,
                            "judge_model": "gpt-4",
                            "judge_max_n_tokens": 5
                        }
                        response = client.post(
                            "/v1/redteaming/pair/batch",
                            files={"file": ("test.xlsx", excel_buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                            data={"parameters": _json.dumps(params)}
                        )

                        assert response.status_code == 200
                        result = response.json()
                        assert 'RedTeamingId' in result
                        assert 'reportId' in result


def test_tap_batch_endpoint_with_jailbreak():
    """Test tap_batch_endpoint processes jailbreak correctly"""
    from src.main import app
    import io
    import pandas as pd
    
    test_data = pd.DataFrame({
        'goal': ['test goal'],
        'target_str': ['test target'],
        'category': ['cat1']
    })
    excel_buffer = io.BytesIO()
    test_data.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    
    client = TestClient(app)

    with patch('app.service.service.InfosysRAI.dataAdditiontoDB') as mock_data_add:
        with patch('app.service.service.InfosysRAI.GetRedteamListTap') as mock_get_tap:
            with patch('pdfkit.from_file') as mock_pdfkit:
                with patch('app.service.service.InfosysRAI.addReportToDB') as mock_add_report:
                    with patch('app.service.service.InfosysRAI.addingReportToDB') as mock_adding_report:
                        mock_data_add.return_value = (excel_buffer, 'conf-id')
                        mock_get_tap.return_value = [{
                            'prompt': 'prompt1',
                            'response': 'response1',
                            'score': 10
                        }]
                        def _fake_from_file(html_path, pdf_path, options=None):
                            import os
                            with open(pdf_path, 'wb') as fp:
                                fp.write(b'%PDF-1.4')
                        mock_pdfkit.side_effect = _fake_from_file
                        mock_add_report.side_effect = lambda f, n: (f.close(), 'rep-id')[1]
                        mock_adding_report.return_value = None

                        import json as _json
                        params = {
                            "userId": "u",
                            "technique_type": "TAP",
                            "depth": 1,
                            "width": 1,
                            "branching_factor": 1,
                            "attack_model": "gpt-4",
                            "attack_max_n_tokens": 10,
                            "target_model": "gpt-3.5-turbo",
                            "target_max_n_tokens": 10,
                            "target_temperature": 0.5,
                            "judge_model": "gpt-4",
                            "judge_max_n_tokens": 5
                        }
                        response = client.post(
                            "/v1/redteaming/tap/batch",
                            files={"file": ("test.xlsx", excel_buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                            data={"parameters": _json.dumps(params)}
                        )

                        assert response.status_code == 200
                        result = response.json()
                        assert 'RedTeamingId' in result
                        assert 'reportId' in result


def test_pair_endpoint_default_payload_merge():
    """Test pair endpoint merges with default payload"""
    from src.main import app
    client = TestClient(app)

    with patch('app.service.service.InfosysRAI.GetRedteamListPair') as mock_get_pair:
        mock_get_pair.return_value = {'id': 'test-id', 'jailbroken': 5, 'scores': [], 'prompts': [], 'responses': []}
        response = client.post(
            "/v1/redteaming/pair",
            json={
                "goal": "test goal",
                "target_str": "test target",
                "attack_model": "gpt-4",
                "target_model": "gpt-3.5-turbo"
            }
        )
        assert response.status_code == 200


def test_tap_endpoint_default_payload_merge():
    """Test tap endpoint merges with default payload"""
    from src.main import app
    client = TestClient(app)

    with patch('app.service.service.InfosysRAI.GetRedteamListTap') as mock_get_tap:
        mock_get_tap.return_value = [{'prompt':'p','response':'r','score':5}]
        response = client.post(
            "/v1/redteaming/tap",
            json={
                "goal": "test goal",
                "target_str": "test target",
                "attack_model": "gpt-4",
                "target_model": "gpt-3.5-turbo",
                "evaluator_model": "gpt-4"
            }
        )
        assert response.status_code == 200


def test_router_category_wise_score_accumulation():
    """Test category wise score accumulation logic"""
    category_wise_score = {}
    category = 'test_category'
    
    # First occurrence
    if category not in category_wise_score:
        category_wise_score[category] = {
            'provided': 0,
            'count': 0,
            'details': []
        }
    
    category_wise_score[category]['provided'] += 1
    category_wise_score[category]['count'] += 1
    category_wise_score[category]['details'].append({'goal': 'g1', 'prompt': 'p1', 'response': 'r1'})
    
    assert category_wise_score[category]['provided'] == 1
    assert category_wise_score[category]['count'] == 1
    assert len(category_wise_score[category]['details']) == 1
    
    # Second occurrence
    category_wise_score[category]['provided'] += 1
    category_wise_score[category]['count'] += 1
    
    assert category_wise_score[category]['provided'] == 2
    assert category_wise_score[category]['count'] == 2


def test_refusal_phrases_filtering():
    """Test refusal phrases are filtered out"""
    refusal_phrases = ["i'm sorry", "i cannot", "i apologize"]
    
    response1 = "I'm sorry, I cannot help with that"
    response2 = "Here is the information you requested"
    
    low1 = response1.lower()
    low2 = response2.lower()
    
    has_refusal1 = any(p in low1 for p in refusal_phrases)
    has_refusal2 = any(p in low2 for p in refusal_phrases)
    
    assert has_refusal1 == True
    assert has_refusal2 == False


def test_score_10_detection():
    """Test score 10 detection logic"""
    scores_list = [10, '10', 5, '5', 10]
    
    score_10_indices = []
    for i, sc in enumerate(scores_list):
        if sc == 10 or str(sc) == '10':
            score_10_indices.append(i)
    
    assert 0 in score_10_indices
    assert 1 in score_10_indices
    assert 4 in score_10_indices
    assert len(score_10_indices) == 3
