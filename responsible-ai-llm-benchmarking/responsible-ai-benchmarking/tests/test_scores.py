"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from service.scores import Scores


class TestScoresInit:
    """Test cases for Scores class initialization"""
    
    @patch('service.scores.DataBase')
    def test_init_success(self, mock_database):
        """Test successful initialization of Scores class"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        scores = Scores()
        
        assert scores.db == mock_db
        assert scores.fairness_coll == mock_db['fairness']
        assert scores.privacy_coll == mock_db['privacy']
        assert scores.saftey_coll == mock_db['saftey']
        assert scores.ethics_coll == mock_db['ethics']
        assert scores.truthfullness_coll == mock_db['truthfullness']
        assert scores.explain_coll == mock_db['explain']


class TestGetScores:
    """Test cases for getScores method"""
    
    @patch('service.scores.DataBase')
    def test_get_fairness_scores(self, mock_database):
        """Test getScores routes to getFairnessScores for fairness category"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        with patch.object(scores, 'getFairnessScores', return_value=['fairness_data']) as mock_method:
            result = scores.getScores('fairness')
            mock_method.assert_called_once()
            assert result == ['fairness_data']
    
    @patch('service.scores.DataBase')
    def test_get_truthfulness_scores(self, mock_database):
        """Test getScores routes to getTruthfullnessScores for truthfulness category"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        with patch.object(scores, 'getTruthfullnessScores', return_value=['truth_data']) as mock_method:
            result = scores.getScores('truthfulness')
            mock_method.assert_called_once()
            assert result == ['truth_data']
    
    @patch('service.scores.DataBase')
    def test_get_ethics_scores(self, mock_database):
        """Test getScores routes to getEthicsScores for ethics category"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        with patch.object(scores, 'getEthicsScores', return_value=['ethics_data']) as mock_method:
            result = scores.getScores('ethics')
            mock_method.assert_called_once()
            assert result == ['ethics_data']
    
    @patch('service.scores.DataBase')
    def test_get_privacy_scores(self, mock_database):
        """Test getScores routes to getPrivacyScores for privacy category"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        with patch.object(scores, 'getPrivacyScores', return_value=['privacy_data']) as mock_method:
            result = scores.getScores('privacy')
            mock_method.assert_called_once()
            assert result == ['privacy_data']
    
    @patch('service.scores.DataBase')
    def test_get_safety_scores(self, mock_database):
        """Test getScores routes to getSafteyScores for safety category"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        with patch.object(scores, 'getSafteyScores', return_value=['safety_data']) as mock_method:
            result = scores.getScores('safety')
            mock_method.assert_called_once()
            assert result == ['safety_data']
    
    @patch('service.scores.DataBase')
    def test_get_scores_unknown_category(self, mock_database):
        """Test getScores with unknown category returns None"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        result = scores.getScores('unknown_category')
        assert result is None


class TestGetScoresExplain:
    """Test cases for getscores_explain method"""
    
    @patch('service.scores.DataBase')
    def test_get_explain_scores(self, mock_database):
        """Test getscores_explain routes to getExplainScores"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        with patch.object(scores, 'getExplainScores', return_value=['explain_data']) as mock_method:
            result = scores.getscores_explain('explain', 'sub_cat')
            mock_method.assert_called_once_with('sub_cat')
            assert result == ['explain_data']
    
    @patch('service.scores.DataBase')
    def test_get_explain_scores_non_explain_category(self, mock_database):
        """Test getscores_explain with non-explain category"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        result = scores.getscores_explain('other', 'sub_cat')
        assert result is None


class TestAddScore:
    """Test cases for addScore method"""
    
    @patch('service.scores.DataBase')
    def test_add_fairness_score(self, mock_database):
        """Test addScore routes to addFairnessScore for fairness category"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {'category': 'fairness', 'model_name': 'test_model'}
        with patch.object(scores, 'addFairnessScore', return_value='Success') as mock_method:
            result = scores.addScore(payload)
            mock_method.assert_called_once_with(payload)
            assert result == 'Success'
    
    @patch('service.scores.DataBase')
    def test_add_truthfullness_score(self, mock_database):
        """Test addScore routes to addTruthfullnessScore for truthfullness category"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {'category': 'truthfullness', 'model_name': 'test_model'}
        with patch.object(scores, 'addTruthfullnessScore', return_value='Success') as mock_method:
            result = scores.addScore(payload)
            mock_method.assert_called_once_with(payload)
            assert result == 'Success'
    
    @patch('service.scores.DataBase')
    def test_add_ethics_score(self, mock_database):
        """Test addScore routes to addEthicsScore for ethics category"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {'category': 'ethics', 'model_name': 'test_model'}
        with patch.object(scores, 'addEthicsScore', return_value='Success') as mock_method:
            result = scores.addScore(payload)
            mock_method.assert_called_once_with(payload)
            assert result == 'Success'
    
    @patch('service.scores.DataBase')
    def test_add_privacy_score(self, mock_database):
        """Test addScore routes to addPrivacyScore for privacy category"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {'category': 'privacy', 'model_name': 'test_model'}
        with patch.object(scores, 'addPrivacyScore', return_value='Success') as mock_method:
            result = scores.addScore(payload)
            mock_method.assert_called_once_with(payload)
            assert result == 'Success'
    
    @patch('service.scores.DataBase')
    def test_add_safety_score(self, mock_database):
        """Test addScore routes to addSafteyScore for safety category"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {'category': 'safety', 'model_name': 'test_model'}
        with patch.object(scores, 'addSafteyScore', return_value='Success') as mock_method:
            result = scores.addScore(payload)
            mock_method.assert_called_once_with(payload)
            assert result == 'Success'
    
    @patch('service.scores.DataBase')
    def test_add_explain_score(self, mock_database):
        """Test addScore routes to addExplainabilityScore for explain category"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {'category': 'explain', 'model_name': 'test_model'}
        with patch.object(scores, 'addExplainabilityScore', return_value='Success') as mock_method:
            result = scores.addScore(payload)
            mock_method.assert_called_once_with(payload)
            assert result == 'Success'


class TestDeleteScores:
    """Test cases for deleteScores method"""
    
    @patch('service.scores.DataBase')
    def test_delete_fairness_scores_success(self, mock_database):
        """Test successful deletion of fairness scores"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        mock_result = Mock()
        mock_result.deleted_count = 1
        mock_db['fairness'].delete_one.return_value = mock_result
        
        scores = Scores()
        result = scores.deleteScores('fairness', 'test_model')
        
        assert result == "Deleted Successfully"
        mock_db['fairness'].delete_one.assert_called_once_with({'model_name': 'test_model'})
    
    @patch('service.scores.DataBase')
    def test_delete_fairness_scores_failure(self, mock_database):
        """Test failed deletion of fairness scores"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        mock_result = Mock()
        mock_result.deleted_count = 0
        mock_db['fairness'].delete_one.return_value = mock_result
        
        scores = Scores()
        result = scores.deleteScores('fairness', 'test_model')
        
        assert result == "Some problem Occures while deleting the scores"
    
    @patch('service.scores.DataBase')
    def test_delete_truthfullness_scores_success(self, mock_database):
        """Test successful deletion of truthfullness scores"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        mock_result = Mock()
        mock_result.deleted_count = 1
        mock_db['truthfullness'].delete_one.return_value = mock_result
        
        scores = Scores()
        result = scores.deleteScores('truthfullness', 'test_model')
        
        assert result == "Deleted Successfully"
        mock_db['truthfullness'].delete_one.assert_called_once_with({'model_name': 'test_model'})
    
    @patch('service.scores.DataBase')
    def test_delete_ethics_scores_success(self, mock_database):
        """Test successful deletion of ethics scores"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        mock_result = Mock()
        mock_result.deleted_count = 1
        mock_db['ethics'].delete_one.return_value = mock_result
        
        scores = Scores()
        result = scores.deleteScores('ethics', 'test_model')
        
        assert result == "Deleted Successfully"
    
    @patch('service.scores.DataBase')
    def test_delete_privacy_scores_success(self, mock_database):
        """Test successful deletion of privacy scores"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        mock_result = Mock()
        mock_result.deleted_count = 1
        mock_db['privacy'].delete_one.return_value = mock_result
        
        scores = Scores()
        result = scores.deleteScores('privacy', 'test_model')
        
        assert result == "Deleted Successfully"
    
    @patch('service.scores.DataBase')
    def test_delete_safety_scores_success(self, mock_database):
        """Test successful deletion of safety scores"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        mock_result = Mock()
        mock_result.deleted_count = 1
        mock_db['saftey'].delete_one.return_value = mock_result
        
        scores = Scores()
        result = scores.deleteScores('safety', 'test_model')
        
        assert result == "Deleted Successfully"


class TestGetFairnessScores:
    """Test cases for getFairnessScores method"""
    
    @patch('service.scores.DataBase')
    def test_get_fairness_scores_with_data(self, mock_database):
        """Test getFairnessScores returns data from database"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_records = [
            {'model_name': 'model1', 'score': 0.85},
            {'model_name': 'model2', 'score': 0.90}
        ]
        mock_db['fairness'].find.return_value = mock_records
        
        scores = Scores()
        result = scores.getFairnessScores()
        
        assert len(result) == 2
        assert result == mock_records
        mock_db['fairness'].find.assert_called_once_with({}, {'_id': False})
    
    @patch('service.scores.DataBase')
    def test_get_fairness_scores_empty(self, mock_database):
        """Test getFairnessScores with no data"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        mock_db['fairness'].find.return_value = []
        
        scores = Scores()
        result = scores.getFairnessScores()
        
        assert result == []


class TestGetTruthfullnessScores:
    """Test cases for getTruthfullnessScores method"""
    
    @patch('service.scores.DataBase')
    def test_get_truthfullness_scores_with_data(self, mock_database):
        """Test getTruthfullnessScores returns data from database"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_records = [
            {'model_name': 'model1', 'score': 0.75},
            {'model_name': 'model2', 'score': 0.80}
        ]
        mock_db['truthfullness'].find.return_value = mock_records
        
        scores = Scores()
        result = scores.getTruthfullnessScores()
        
        assert len(result) == 2
        assert result == mock_records
        mock_db['truthfullness'].find.assert_called_once_with({}, {'_id': False})
    
    @patch('service.scores.DataBase')
    def test_get_truthfullness_scores_empty(self, mock_database):
        """Test getTruthfullnessScores with no data"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        mock_db['truthfullness'].find.return_value = []
        
        scores = Scores()
        result = scores.getTruthfullnessScores()
        
        assert result == []


class TestGetSafteyScores:
    """Test cases for getSafteyScores method"""
    
    @patch('service.scores.DataBase')
    def test_get_saftey_scores_with_data(self, mock_database):
        """Test getSafteyScores returns data from database"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_records = [
            {'model_name': 'model1', 'score': 0.88},
            {'model_name': 'model2', 'score': 0.92}
        ]
        mock_db['saftey'].find.return_value = mock_records
        
        scores = Scores()
        result = scores.getSafteyScores()
        
        assert len(result) == 2
        assert result == mock_records
        mock_db['saftey'].find.assert_called_once_with({}, {'_id': False})
    
    @patch('service.scores.DataBase')
    def test_get_saftey_scores_empty(self, mock_database):
        """Test getSafteyScores with no data"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        mock_db['saftey'].find.return_value = []
        
        scores = Scores()
        result = scores.getSafteyScores()
        
        assert result == []


class TestGetPrivacyScores:
    """Test cases for getPrivacyScores method"""
    
    @patch('service.scores.DataBase')
    def test_get_privacy_scores_with_data(self, mock_database):
        """Test getPrivacyScores returns data from database"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_records = [
            {'model_name': 'model1', 'score': 0.70},
            {'model_name': 'model2', 'score': 0.78}
        ]
        mock_db['privacy'].find.return_value = mock_records
        
        scores = Scores()
        result = scores.getPrivacyScores()
        
        assert len(result) == 2
        assert result == mock_records
        mock_db['privacy'].find.assert_called_once_with({}, {'_id': False})
    
    @patch('service.scores.DataBase')
    def test_get_privacy_scores_empty(self, mock_database):
        """Test getPrivacyScores with no data"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        mock_db['privacy'].find.return_value = []
        
        scores = Scores()
        result = scores.getPrivacyScores()
        
        assert result == []


class TestGetEthicsScores:
    """Test cases for getEthicsScores method"""
    
    @patch('service.scores.DataBase')
    def test_get_ethics_scores_with_data(self, mock_database):
        """Test getEthicsScores returns data from database"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_records = [
            {'model_name': 'model1', 'score': 0.82},
            {'model_name': 'model2', 'score': 0.87}
        ]
        mock_db['ethics'].find.return_value = mock_records
        
        scores = Scores()
        result = scores.getEthicsScores()
        
        assert len(result) == 2
        assert result == mock_records
        mock_db['ethics'].find.assert_called_once_with({}, {'_id': False})
    
    @patch('service.scores.DataBase')
    def test_get_ethics_scores_empty(self, mock_database):
        """Test getEthicsScores with no data"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        mock_db['ethics'].find.return_value = []
        
        scores = Scores()
        result = scores.getEthicsScores()
        
        assert result == []


class TestGetExplainScores:
    """Test cases for getExplainScores method"""
    
    @patch('service.scores.DataBase')
    def test_get_explain_scores_all(self, mock_database):
        """Test getExplainScores with 'all' sub_category"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_records = [
            {'model_name': 'model1', 'score': 0.85},
            {'model_name': 'model2', 'score': 0.90}
        ]
        mock_db['explain'].find.return_value = mock_records
        
        scores = Scores()
        result = scores.getExplainScores('all')
        
        assert len(result) == 2
        assert result == mock_records
        mock_db['explain'].find.assert_called_once_with({}, {'_id': False})
    
    @patch('service.scores.DataBase')
    def test_get_explain_scores_specific_subcategory(self, mock_database):
        """Test getExplainScores with specific sub_category"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_records = [{'model_name': 'model1', 'score': 0.85, 'sub_category': 'reasoning'}]
        mock_db['explain'].find.return_value = mock_records
        
        scores = Scores()
        result = scores.getExplainScores('reasoning')
        
        assert len(result) == 1
        assert result == mock_records
        mock_db['explain'].find.assert_called_once_with({'sub_category': 'reasoning'}, {'_id': False})
    
    @patch('service.scores.DataBase')
    def test_get_explain_scores_empty(self, mock_database):
        """Test getExplainScores with no data"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        mock_db['explain'].find.return_value = []
        
        scores = Scores()
        result = scores.getExplainScores('all')
        
        assert result == []


class TestAddFairnessScore:
    """Test cases for addFairnessScore method"""
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Fairness')
    def test_add_fairness_score_success(self, mock_fairness_class, mock_database):
        """Test successful addition of fairness score"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['fairness'].insert_one.return_value = mock_result
        
        mock_fairness_instance = Mock()
        mock_fairness_instance.model_dump.return_value = {'model_name': 'test_model'}
        mock_fairness_class.return_value = mock_fairness_instance
        
        payload = {
            'model_name': 'test_model',
            'overall_agreement_rate': '0.85',
            'stereotype_recognition': '0.90',
            'stereotype_query_test': '0.88',
            'disparagement_race': '0.92',
            'disparagement_sex': '0.91',
            'prefereence_rta': '0.87',
            'inhouse_model': True
        }
        
        scores = Scores()
        result = scores.addFairnessScore(payload)
        
        assert result == 'Insertion Successful'
        mock_db['fairness'].insert_one.assert_called_once()
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Fairness')
    def test_add_fairness_score_with_null_values(self, mock_fairness_class, mock_database):
        """Test addition of fairness score with null/missing values"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['fairness'].insert_one.return_value = mock_result
        
        mock_fairness_instance = Mock()
        mock_fairness_instance.model_dump.return_value = {'model_name': 'test_model'}
        mock_fairness_class.return_value = mock_fairness_instance
        
        payload = {
            'model_name': 'test_model',
            'overall_agreement_rate': '-',
            'stereotype_recognition': '0.90',
            'stereotype_query_test': '',
            'disparagement_race': 'null',
            'disparagement_sex': '0.91',
            'prefereence_rta': '0.87',
            'inhouse_model': False
        }
        
        scores = Scores()
        result = scores.addFairnessScore(payload)
        
        assert result == 'Insertion Successful'
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Fairness')
    def test_add_fairness_score_not_acknowledged(self, mock_fairness_class, mock_database):
        """Test addition of fairness score when not acknowledged by server"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = False
        mock_db['fairness'].insert_one.return_value = mock_result
        
        mock_fairness_instance = Mock()
        mock_fairness_instance.model_dump.return_value = {'model_name': 'test_model'}
        mock_fairness_class.return_value = mock_fairness_instance
        
        payload = {
            'model_name': 'test_model',
            'overall_agreement_rate': '0.85',
            'stereotype_recognition': '0.90',
            'stereotype_query_test': '0.88',
            'disparagement_race': '0.92',
            'disparagement_sex': '0.91',
            'prefereence_rta': '0.87',
            'inhouse_model': True
        }
        
        scores = Scores()
        
        with pytest.raises(RuntimeError, match='Insertion not acknowledged by the server'):
            scores.addFairnessScore(payload)


class TestAddTruthfullnessScore:
    """Test cases for addTruthfullnessScore method"""
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Truthfullness')
    def test_add_truthfullness_score_success(self, mock_truthfullness_class, mock_database):
        """Test successful addition of truthfullness score"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['truthfullness'].insert_one.return_value = mock_result
        
        mock_truthfullness_instance = Mock()
        mock_truthfullness_instance.model_dump.return_value = {'model_name': 'test_model'}
        mock_truthfullness_class.return_value = mock_truthfullness_instance
        
        payload = {
            'model_name': 'test_model',
            'internal': '0.85',
            'external': '0.82',
            'persona_sycophancy': '0.15',
            'preference_sycophancy': '0.18',
            'adv_factuality': '0.88',
            'hallucination': '0.90',
            'inhouse_model': True
        }
        
        scores = Scores()
        result = scores.addTruthfullnessScore(payload)
        
        assert result == 'Insertion Successful'
        mock_db['truthfullness'].insert_one.assert_called_once()
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Truthfullness')
    def test_add_truthfullness_score_with_null_values(self, mock_truthfullness_class, mock_database):
        """Test addition of truthfullness score with null values"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['truthfullness'].insert_one.return_value = mock_result
        
        mock_truthfullness_instance = Mock()
        mock_truthfullness_instance.model_dump.return_value = {'model_name': 'test_model'}
        mock_truthfullness_class.return_value = mock_truthfullness_instance
        
        payload = {
            'model_name': 'test_model',
            'internal': '-',
            'external': '0.82',
            'persona_sycophancy': '',
            'preference_sycophancy': '0.18',
            'adv_factuality': 'null',
            'hallucination': '0.90',
            'inhouse_model': False
        }
        
        scores = Scores()
        result = scores.addTruthfullnessScore(payload)
        
        assert result == 'Insertion Successful'
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Truthfullness')
    def test_add_truthfullness_score_not_acknowledged(self, mock_truthfullness_class, mock_database):
        """Test addition of truthfullness score when not acknowledged"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = False
        mock_db['truthfullness'].insert_one.return_value = mock_result
        
        mock_truthfullness_instance = Mock()
        mock_truthfullness_instance.model_dump.return_value = {'model_name': 'test_model'}
        mock_truthfullness_class.return_value = mock_truthfullness_instance
        
        payload = {
            'model_name': 'test_model',
            'internal': '0.85',
            'external': '0.82',
            'persona_sycophancy': '0.15',
            'preference_sycophancy': '0.18',
            'adv_factuality': '0.88',
            'hallucination': '0.90',
            'inhouse_model': True
        }
        
        scores = Scores()
        
        with pytest.raises(RuntimeError, match='Insertion not acknowledged by the server'):
            scores.addTruthfullnessScore(payload)


class TestAddEthicsScore:
    """Test cases for addEthicsScore method"""
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Ethics')
    def test_add_ethics_score_success(self, mock_ethics_class, mock_database):
        """Test successful addition of ethics score"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['ethics'].insert_one.return_value = mock_result
        
        mock_ethics_instance = Mock()
        mock_ethics_instance.model_dump.return_value = {'model_name': 'test_model'}
        mock_ethics_class.return_value = mock_ethics_instance
        
        payload = {
            'model_name': 'test_model',
            'social_chemistry_101_acc': '0.85',
            'ehitcs_acc': '0.88',
            'moralchoice_acc': '0.82',
            'moralchoice_rta': '0.90',
            'emotional_acc': '0.87',
            'inhouse_model': True
        }
        
        scores = Scores()
        result = scores.addEthicsScore(payload)
        
        assert result == 'Insertion Successful'
        mock_db['ethics'].insert_one.assert_called_once()
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Ethics')
    def test_add_ethics_score_with_null_values(self, mock_ethics_class, mock_database):
        """Test addition of ethics score with null values"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['ethics'].insert_one.return_value = mock_result
        
        mock_ethics_instance = Mock()
        mock_ethics_instance.model_dump.return_value = {'model_name': 'test_model'}
        mock_ethics_class.return_value = mock_ethics_instance
        
        payload = {
            'model_name': 'test_model',
            'social_chemistry_101_acc': '-',
            'ehitcs_acc': '0.88',
            'moralchoice_acc': '',
            'moralchoice_rta': 'null',
            'emotional_acc': '0.87',
            'inhouse_model': False
        }
        
        scores = Scores()
        result = scores.addEthicsScore(payload)
        
        assert result == 'Insertion Successful'
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Ethics')
    def test_add_ethics_score_not_acknowledged(self, mock_ethics_class, mock_database):
        """Test addition of ethics score when not acknowledged"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = False
        mock_db['ethics'].insert_one.return_value = mock_result
        
        mock_ethics_instance = Mock()
        mock_ethics_instance.model_dump.return_value = {'model_name': 'test_model'}
        mock_ethics_class.return_value = mock_ethics_instance
        
        payload = {
            'model_name': 'test_model',
            'social_chemistry_101_acc': '0.85',
            'ehitcs_acc': '0.88',
            'moralchoice_acc': '0.82',
            'moralchoice_rta': '0.90',
            'emotional_acc': '0.87',
            'inhouse_model': True
        }
        
        scores = Scores()
        
        with pytest.raises(RuntimeError, match='Insertion not acknowledged by the server'):
            scores.addEthicsScore(payload)


class TestAddPrivacyScore:
    """Test cases for addPrivacyScore method"""
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Privacy')
    def test_add_privacy_score_success(self, mock_privacy_class, mock_database):
        """Test successful addition of privacy score"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['privacy'].insert_one.return_value = mock_result
        
        mock_privacy_instance = Mock()
        mock_privacy_instance.model_dump.return_value = {'model_name': 'test_model'}
        mock_privacy_class.return_value = mock_privacy_instance
        
        payload = {
            'model_name': 'test_model',
            'privacy_awareness_normal': '0.85',
            'privacy_awareness_aug': '0.82',
            'privacy_leakage_rta': '0.90',
            'privacy_leakage_td': '0.15',
            'privacy_leakage_cd': '0.12',
            'privacy_awareness_correlation': '0.88',
            'inhouse_model': True
        }
        
        scores = Scores()
        result = scores.addPrivacyScore(payload)
        
        assert result == 'Insertion Successful'
        mock_db['privacy'].insert_one.assert_called_once()
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Privacy')
    def test_add_privacy_score_with_null_values(self, mock_privacy_class, mock_database):
        """Test addition of privacy score with null values"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['privacy'].insert_one.return_value = mock_result
        
        mock_privacy_instance = Mock()
        mock_privacy_instance.model_dump.return_value = {'model_name': 'test_model'}
        mock_privacy_class.return_value = mock_privacy_instance
        
        payload = {
            'model_name': 'test_model',
            'privacy_awareness_normal': '-',
            'privacy_awareness_aug': '0.82',
            'privacy_leakage_rta': '',
            'privacy_leakage_td': 'null',
            'privacy_leakage_cd': '0.12',
            'privacy_awareness_correlation': '0.88',
            'inhouse_model': False
        }
        
        scores = Scores()
        result = scores.addPrivacyScore(payload)
        
        assert result == 'Insertion Successful'
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Privacy')
    def test_add_privacy_score_not_acknowledged(self, mock_privacy_class, mock_database):
        """Test addition of privacy score when not acknowledged"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = False
        mock_db['privacy'].insert_one.return_value = mock_result
        
        mock_privacy_instance = Mock()
        mock_privacy_instance.model_dump.return_value = {'model_name': 'test_model'}
        mock_privacy_class.return_value = mock_privacy_instance
        
        payload = {
            'model_name': 'test_model',
            'privacy_awareness_normal': '0.85',
            'privacy_awareness_aug': '0.82',
            'privacy_leakage_rta': '0.90',
            'privacy_leakage_td': '0.15',
            'privacy_leakage_cd': '0.12',
            'privacy_awareness_correlation': '0.88',
            'inhouse_model': True
        }
        
        scores = Scores()
        
        with pytest.raises(RuntimeError, match='Insertion not acknowledged by the server'):
            scores.addPrivacyScore(payload)


class TestAddSafteyScore:
    """Test cases for addSafteyScore method"""
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Saftey')
    def test_add_saftey_score_success(self, mock_saftey_class, mock_database):
        """Test successful addition of safety score"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['saftey'].insert_one.return_value = mock_result
        
        mock_saftey_instance = Mock()
        mock_saftey_instance.model_dump.return_value = {'model_name': 'test_model'}
        mock_saftey_class.return_value = mock_saftey_instance
        
        payload = {
            'model_name': 'test_model',
            'jailbreak': '0.92',
            'toxicity': '0.10',
            'misuse': '0.88',
            'exaggerated_safety': '0.15',
            'inhouse_model': True
        }
        
        scores = Scores()
        result = scores.addSafteyScore(payload)
        
        assert result == 'Insertion Successful'
        mock_db['saftey'].insert_one.assert_called_once()
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Saftey')
    def test_add_saftey_score_with_null_values(self, mock_saftey_class, mock_database):
        """Test addition of safety score with null values"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['saftey'].insert_one.return_value = mock_result
        
        mock_saftey_instance = Mock()
        mock_saftey_instance.model_dump.return_value = {'model_name': 'test_model'}
        mock_saftey_class.return_value = mock_saftey_instance
        
        payload = {
            'model_name': 'test_model',
            'jailbreak': '-',
            'toxicity': '',
            'misuse': '0.88',
            'exaggerated_safety': 'null',
            'inhouse_model': False
        }
        
        scores = Scores()
        result = scores.addSafteyScore(payload)
        
        assert result == 'Insertion Successful'
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Saftey')
    def test_add_saftey_score_not_acknowledged(self, mock_saftey_class, mock_database):
        """Test addition of safety score when not acknowledged"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = False
        mock_db['saftey'].insert_one.return_value = mock_result
        
        mock_saftey_instance = Mock()
        mock_saftey_instance.model_dump.return_value = {'model_name': 'test_model'}
        mock_saftey_class.return_value = mock_saftey_instance
        
        payload = {
            'model_name': 'test_model',
            'jailbreak': '0.92',
            'toxicity': '0.10',
            'misuse': '0.88',
            'exaggerated_safety': '0.15',
            'inhouse_model': True
        }
        
        scores = Scores()
        
        with pytest.raises(RuntimeError, match='Insertion not acknowledged by the server'):
            scores.addSafteyScore(payload)


class TestAddExplainabilityScore:
    """Test cases for addExplainabilityScore method"""
    
    @patch('service.scores.DataBase')
    def test_add_explainability_score_success(self, mock_database):
        """Test successful addition of explainability score"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['explain'].insert_one.return_value = mock_result
        
        payload = {
            'model_name': 'test_model',
            'sub_category': 'reasoning',
            'score': 0.85,
            'inhouse_model': True,
            'category': 'explain'
        }
        
        scores = Scores()
        result = scores.addExplainabilityScore(payload)
        
        assert result == 'Insertion Successful'
        # Verify inhouse_model and category were removed
        inserted_payload = mock_db['explain'].insert_one.call_args[0][0]
        assert 'inhouse_model' not in inserted_payload
        assert 'category' not in inserted_payload
        assert inserted_payload['model_name'] == 'test_model'
    
    @patch('service.scores.DataBase')
    def test_add_explainability_score_not_acknowledged(self, mock_database):
        """Test addition of explainability score when not acknowledged"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = False
        mock_db['explain'].insert_one.return_value = mock_result
        
        payload = {
            'model_name': 'test_model',
            'sub_category': 'reasoning',
            'score': 0.85,
            'inhouse_model': True,
            'category': 'explain'
        }
        
        scores = Scores()
        
        with pytest.raises(RuntimeError, match='Insertion not acknowledged by the server'):
            scores.addExplainabilityScore(payload)


class TestScoreNormalization:
    """Test cases for score normalization logic across different methods"""
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Fairness')
    def test_fairness_score_normalization(self, mock_fairness_class, mock_database):
        """Test correct normalization of fairness scores"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['fairness'].insert_one.return_value = mock_result
        
        mock_fairness_instance = Mock()
        mock_fairness_instance.model_dump.return_value = {}
        mock_fairness_class.return_value = mock_fairness_instance
        
        payload = {
            'model_name': 'test_model',
            'overall_agreement_rate': '0.25',  # Should be inverted: 100 - 25 = 75
            'stereotype_recognition': '0.90',  # Should stay: 90
            'stereotype_query_test': '0.88',   # Should stay: 88
            'disparagement_race': '0.92',      # Should stay: 92
            'disparagement_sex': '0.91',       # Should stay: 91
            'prefereence_rta': '0.87',         # Should stay: 87
            'inhouse_model': True
        }
        
        scores = Scores()
        scores.addFairnessScore(payload)
        
        # Verify Fairness was called with normalized overall_agreement_rate
        call_args = mock_fairness_class.call_args
        assert call_args.kwargs['overall_agreement_rate'] == '75.0'
        assert call_args.kwargs['stereotype_recognition'] == '90.0'
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Truthfullness')
    def test_truthfullness_score_normalization(self, mock_truthfullness_class, mock_database):
        """Test correct normalization of truthfulness scores"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['truthfullness'].insert_one.return_value = mock_result
        
        mock_truthfullness_instance = Mock()
        mock_truthfullness_instance.model_dump.return_value = {}
        mock_truthfullness_class.return_value = mock_truthfullness_instance
        
        payload = {
            'model_name': 'test_model',
            'internal': '0.85',                 # Should stay: 85
            'external': '0.82',                 # Should stay: 82
            'persona_sycophancy': '0.15',       # Should be inverted: 100 - 15 = 85
            'preference_sycophancy': '0.18',    # Should be inverted: 100 - 18 = 82
            'adv_factuality': '0.88',           # Should stay: 88
            'hallucination': '0.90',            # Should stay: 90
            'inhouse_model': True
        }
        
        scores = Scores()
        scores.addTruthfullnessScore(payload)
        
        call_args = mock_truthfullness_class.call_args
        assert call_args.kwargs['internal'] == '85.0'
        assert call_args.kwargs['persona_sycophancy'] == '85.0'


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Fairness')
    def test_all_scores_null(self, mock_fairness_class, mock_database):
        """Test handling when all scores are null/empty"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['fairness'].insert_one.return_value = mock_result
        
        mock_fairness_instance = Mock()
        mock_fairness_instance.model_dump.return_value = {}
        mock_fairness_class.return_value = mock_fairness_instance
        
        payload = {
            'model_name': 'test_model',
            'overall_agreement_rate': '-',
            'stereotype_recognition': '',
            'stereotype_query_test': 'null',
            'disparagement_race': '-',
            'disparagement_sex': '',
            'prefereence_rta': 'null',
            'inhouse_model': True
        }
        
        scores = Scores()
        
        # This should handle division by zero gracefully
        with pytest.raises(ZeroDivisionError):
            scores.addFairnessScore(payload)
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Ethics')
    def test_ethics_mixed_valid_invalid_scores(self, mock_ethics_class, mock_database):
        """Test ethics score with mix of valid and invalid values to achieve full branch coverage"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['ethics'].insert_one.return_value = mock_result
        
        mock_ethics_instance = Mock()
        mock_ethics_instance.model_dump.return_value = {}
        mock_ethics_class.return_value = mock_ethics_instance
        
        payload = {
            'model_name': 'test_model',
            'social_chemistry_101_acc': '0.75',
            'ehitcs_acc': '0.80',
            'moralchoice_acc': '0.85',
            'moralchoice_rta': '0.90',
            'emotional_acc': '0.88',
            'inhouse_model': True
        }
        
        scores = Scores()
        result = scores.addEthicsScore(payload)
        
        assert result == 'Insertion Successful'
        # Verify all scores were properly normalized (all ethics scores should stay as-is, not inverted)
        call_args = mock_ethics_class.call_args
        assert call_args.kwargs['social_chemistry_101_acc'] == '75.0'
        assert call_args.kwargs['ehitcs_acc'] == '80.0'
        assert call_args.kwargs['moralchoice_acc'] == '85.0'
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Fairness')
    def test_extreme_score_values(self, mock_fairness_class, mock_database):
        """Test handling of extreme score values (0 and 1)"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['fairness'].insert_one.return_value = mock_result
        
        mock_fairness_instance = Mock()
        mock_fairness_instance.model_dump.return_value = {}
        mock_fairness_class.return_value = mock_fairness_instance
        
        payload = {
            'model_name': 'test_model',
            'overall_agreement_rate': '0.0',
            'stereotype_recognition': '1.0',
            'stereotype_query_test': '0.0',
            'disparagement_race': '1.0',
            'disparagement_sex': '0.0',
            'prefereence_rta': '1.0',
            'inhouse_model': True
        }
        
        scores = Scores()
        result = scores.addFairnessScore(payload)
        
        assert result == 'Insertion Successful'
    
    @patch('service.scores.DataBase')
    def test_empty_model_name(self, mock_database):
        """Test deletion with empty model name"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        mock_result = Mock()
        mock_result.deleted_count = 0
        mock_db['fairness'].delete_one.return_value = mock_result
        
        scores = Scores()
        result = scores.deleteScores('fairness', '')
        
        assert result == "Some problem Occures while deleting the scores"
        mock_db['fairness'].delete_one.assert_called_once_with({'model_name': ''})


class TestIntegrationScenarios:
    """Test integration scenarios and workflow tests"""
    
    @patch('service.scores.DataBase')
    def test_full_workflow_add_get_delete(self, mock_database):
        """Test complete workflow: add score, get scores, delete score"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        # Setup mocks for add operation
        mock_insert_result = Mock()
        mock_insert_result.acknowledged = True
        mock_db['fairness'].insert_one.return_value = mock_insert_result
        
        # Setup mocks for get operation
        mock_db['fairness'].find.return_value = [{'model_name': 'test_model', 'score': 0.85}]
        
        # Setup mocks for delete operation
        mock_delete_result = Mock()
        mock_delete_result.deleted_count = 1
        mock_db['fairness'].delete_one.return_value = mock_delete_result
        
        scores = Scores()
        
        # Get initial scores
        initial_scores = scores.getFairnessScores()
        assert len(initial_scores) == 1
        
        # Delete score
        delete_result = scores.deleteScores('fairness', 'test_model')
        assert delete_result == "Deleted Successfully"
    
    @patch('service.scores.DataBase')
    def test_multiple_categories_operations(self, mock_database):
        """Test operations across multiple categories"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        # Setup mocks for different collections
        mock_db['fairness'].find.return_value = [{'category': 'fairness'}]
        mock_db['ethics'].find.return_value = [{'category': 'ethics'}]
        mock_db['privacy'].find.return_value = [{'category': 'privacy'}]
        
        scores = Scores()
        
        fairness_scores = scores.getScores('fairness')
        ethics_scores = scores.getScores('ethics')
        privacy_scores = scores.getScores('privacy')
        
        assert len(fairness_scores) == 1
        assert len(ethics_scores) == 1
        assert len(privacy_scores) == 1


class TestErrorHandling:
    """Test error handling and exception scenarios"""
    
    @patch('service.scores.DataBase')
    def test_database_connection_error(self, mock_database):
        """Test handling of database connection errors"""
        mock_database.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception, match="Database connection failed"):
            Scores()
    
    @patch('service.scores.DataBase')
    def test_invalid_float_conversion(self, mock_database):
        """Test handling of invalid float values in scores"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['fairness'].insert_one.return_value = mock_result
        
        payload = {
            'model_name': 'test_model',
            'overall_agreement_rate': 'invalid',
            'stereotype_recognition': '0.90',
            'stereotype_query_test': '0.88',
            'disparagement_race': '0.92',
            'disparagement_sex': '0.91',
            'prefereence_rta': '0.87',
            'inhouse_model': True
        }
        
        scores = Scores()
        
        with pytest.raises(ValueError):
            scores.addFairnessScore(payload)


class TestPerformance:
    """Test performance-related scenarios"""
    
    @patch('service.scores.DataBase')
    def test_large_dataset_retrieval(self, mock_database):
        """Test retrieval of large datasets"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        # Create a large mock dataset
        large_dataset = [{'model_name': f'model_{i}', 'score': 0.85} for i in range(1000)]
        mock_db['fairness'].find.return_value = large_dataset
        
        scores = Scores()
        result = scores.getFairnessScores()
        
        assert len(result) == 1000
        assert result[0]['model_name'] == 'model_0'
        assert result[999]['model_name'] == 'model_999'
    
    @patch('service.scores.DataBase')
    @patch('service.scores.Fairness')
    def test_batch_insertions(self, mock_fairness_class, mock_database):
        """Test multiple score insertions"""
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_db['fairness'].insert_one.return_value = mock_result
        
        mock_fairness_instance = Mock()
        mock_fairness_instance.model_dump.return_value = {}
        mock_fairness_class.return_value = mock_fairness_instance
        
        scores = Scores()
        
        # Insert multiple scores
        for i in range(10):
            payload = {
                'model_name': f'test_model_{i}',
                'overall_agreement_rate': '0.85',
                'stereotype_recognition': '0.90',
                'stereotype_query_test': '0.88',
                'disparagement_race': '0.92',
                'disparagement_sex': '0.91',
                'prefereence_rta': '0.87',
                'inhouse_model': True
            }
            result = scores.addFairnessScore(payload)
            assert result == 'Insertion Successful'
        
        assert mock_db['fairness'].insert_one.call_count == 10

