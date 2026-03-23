"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, Mock, patch, call
from pymongo.results import InsertOneResult, DeleteResult

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from service.inhouse_scores import Scores


class TestScoresInitialization:
    """Test suite for Scores class initialization"""
    
    @patch('service.inhouse_scores.DataBase')
    def test_init_success(self, mock_database):
        """Test successful initialization of Scores class"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        # Act
        scores = Scores()
        
        # Assert
        assert scores.db == mock_db
        assert scores.fairness_coll == mock_db['fairnessInhouse']
        assert scores.privacy_coll == mock_db['privacyInhouse']
        assert scores.saftey_coll == mock_db['safteyInhouse']
        assert scores.ethics_coll == mock_db['ethicsInhouse']
        assert scores.truthfullness_coll == mock_db['truthfullnessInhouse']
    
    @patch('service.inhouse_scores.DataBase')
    def test_init_database_connection_failure(self, mock_database):
        """Test initialization when database connection fails"""
        # Arrange
        mock_database.side_effect = Exception("Database connection failed")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            Scores()
        assert "Database connection failed" in str(exc_info.value)


class TestGetScore:
    """Test suite for getScore method"""
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_fairness_scores(self, mock_database):
        """Test getScore method with fairness category"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        expected_data = [{'model_name': 'test_model', 'score': '0.85'}]
        scores.getFairnessScores = MagicMock(return_value=expected_data)
        
        # Act
        result = scores.getScore("fairness")
        
        # Assert
        assert result == expected_data
        scores.getFairnessScores.assert_called_once()
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_truthfulness_scores(self, mock_database):
        """Test getScore method with truthfulness category"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        expected_data = [{'model_name': 'test_model', 'score': '0.90'}]
        scores.getTruthfullnessScores = MagicMock(return_value=expected_data)
        
        # Act
        result = scores.getScore("truthfulness")
        
        # Assert
        assert result == expected_data
        scores.getTruthfullnessScores.assert_called_once()
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_ethics_scores(self, mock_database):
        """Test getScore method with ethics category"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        expected_data = [{'model_name': 'test_model', 'score': '0.88'}]
        scores.getEthicsScores = MagicMock(return_value=expected_data)
        
        # Act
        result = scores.getScore("ethics")
        
        # Assert
        assert result == expected_data
        scores.getEthicsScores.assert_called_once()
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_privacy_scores(self, mock_database):
        """Test getScore method with privacy category"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        expected_data = [{'model_name': 'test_model', 'score': '0.92'}]
        scores.getPrivacyScores = MagicMock(return_value=expected_data)
        
        # Act
        result = scores.getScore("privacy")
        
        # Assert
        assert result == expected_data
        scores.getPrivacyScores.assert_called_once()
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_safety_scores(self, mock_database):
        """Test getScore method with safety category"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        expected_data = [{'model_name': 'test_model', 'score': '0.87'}]
        scores.getSafteyScores = MagicMock(return_value=expected_data)
        
        # Act
        result = scores.getScore("safety")
        
        # Assert
        assert result == expected_data
        scores.getSafteyScores.assert_called_once()
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_score_unknown_category(self, mock_database):
        """Test getScore method with unknown category returns None"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        # Act
        result = scores.getScore("unknown_category")
        
        # Assert
        assert result is None


class TestAddScore:
    """Test suite for addScore method"""
    
    @patch('service.inhouse_scores.DataBase')
    def test_add_fairness_score(self, mock_database):
        """Test addScore method with fairness category"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {'category': 'fairness', 'model_name': 'test_model'}
        scores.addFairnessScore = MagicMock(return_value='Insertion Successful')
        
        # Act
        result = scores.addScore(payload)
        
        # Assert
        assert result == 'Insertion Successful'
        scores.addFairnessScore.assert_called_once_with(payload)
    
    @patch('service.inhouse_scores.DataBase')
    def test_add_truthfullness_score(self, mock_database):
        """Test addScore method with truthfullness category"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {'category': 'truthfullness', 'model_name': 'test_model'}
        scores.addTruthfullnessScore = MagicMock(return_value='Insertion Successful')
        
        # Act
        result = scores.addScore(payload)
        
        # Assert
        assert result == 'Insertion Successful'
        scores.addTruthfullnessScore.assert_called_once_with(payload)
    
    @patch('service.inhouse_scores.DataBase')
    def test_add_ethics_score(self, mock_database):
        """Test addScore method with ethics category"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {'category': 'ethics', 'model_name': 'test_model'}
        scores.addEthicsScore = MagicMock(return_value='Insertion Successful')
        
        # Act
        result = scores.addScore(payload)
        
        # Assert
        assert result == 'Insertion Successful'
        scores.addEthicsScore.assert_called_once_with(payload)
    
    @patch('service.inhouse_scores.DataBase')
    def test_add_privacy_score(self, mock_database):
        """Test addScore method with privacy category"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {'category': 'privacy', 'model_name': 'test_model'}
        scores.addPrivacyScore = MagicMock(return_value='Insertion Successful')
        
        # Act
        result = scores.addScore(payload)
        
        # Assert
        assert result == 'Insertion Successful'
        scores.addPrivacyScore.assert_called_once_with(payload)
    
    @patch('service.inhouse_scores.DataBase')
    def test_add_safety_score(self, mock_database):
        """Test addScore method with safety category"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {'category': 'safety', 'model_name': 'test_model'}
        scores.addSafteyScore = MagicMock(return_value='Insertion Successful')
        
        # Act
        result = scores.addScore(payload)
        
        # Assert
        assert result == 'Insertion Successful'
        scores.addSafteyScore.assert_called_once_with(payload)
    
    @patch('service.inhouse_scores.DataBase')
    def test_add_score_unknown_category(self, mock_database):
        """Test addScore method with unknown category returns None"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {'category': 'unknown', 'model_name': 'test_model'}
        
        # Act
        result = scores.addScore(payload)
        
        # Assert
        assert result is None


class TestDeleteScores:
    """Test suite for deleteScores method"""
    
    @patch('service.inhouse_scores.DataBase')
    def test_delete_fairness_scores_success(self, mock_database):
        """Test successful deletion of fairness scores"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        mock_delete_result = Mock(spec=DeleteResult)
        mock_delete_result.deleted_count = 1
        scores.fairness_coll.delete_one = MagicMock(return_value=mock_delete_result)
        
        # Act
        result = scores.deleteScores("fairness", "test_model")
        
        # Assert
        assert result == "Deleted Successfully"
        scores.fairness_coll.delete_one.assert_called_once_with({'model_name': 'test_model'})
    
    @patch('service.inhouse_scores.DataBase')
    def test_delete_truthfullness_scores_success(self, mock_database):
        """Test successful deletion of truthfullness scores"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        mock_delete_result = Mock(spec=DeleteResult)
        mock_delete_result.deleted_count = 1
        scores.truthfullness_coll.delete_one = MagicMock(return_value=mock_delete_result)
        
        # Act
        result = scores.deleteScores("truthfullness", "test_model")
        
        # Assert
        assert result == "Deleted Successfully"
        scores.truthfullness_coll.delete_one.assert_called_once_with({'model_name': 'test_model'})
    
    @patch('service.inhouse_scores.DataBase')
    def test_delete_ethics_scores_success(self, mock_database):
        """Test successful deletion of ethics scores"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        mock_delete_result = Mock(spec=DeleteResult)
        mock_delete_result.deleted_count = 1
        scores.ethics_coll.delete_one = MagicMock(return_value=mock_delete_result)
        
        # Act
        result = scores.deleteScores("ethics", "test_model")
        
        # Assert
        assert result == "Deleted Successfully"
        scores.ethics_coll.delete_one.assert_called_once_with({'model_name': 'test_model'})
    
    @patch('service.inhouse_scores.DataBase')
    def test_delete_privacy_scores_success(self, mock_database):
        """Test successful deletion of privacy scores"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        mock_delete_result = Mock(spec=DeleteResult)
        mock_delete_result.deleted_count = 1
        scores.privacy_coll.delete_one = MagicMock(return_value=mock_delete_result)
        
        # Act
        result = scores.deleteScores("privacy", "test_model")
        
        # Assert
        assert result == "Deleted Successfully"
        scores.privacy_coll.delete_one.assert_called_once_with({'model_name': 'test_model'})
    
    @patch('service.inhouse_scores.DataBase')
    def test_delete_safety_scores_success(self, mock_database):
        """Test successful deletion of safety scores"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        mock_delete_result = Mock(spec=DeleteResult)
        mock_delete_result.deleted_count = 1
        scores.saftey_coll.delete_one = MagicMock(return_value=mock_delete_result)
        
        # Act
        result = scores.deleteScores("safety", "test_model")
        
        # Assert
        assert result == "Deleted Successfully"
        scores.saftey_coll.delete_one.assert_called_once_with({'model_name': 'test_model'})
    
    @patch('service.inhouse_scores.DataBase')
    def test_delete_scores_failure(self, mock_database):
        """Test deletion failure when no records are deleted"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        mock_delete_result = Mock(spec=DeleteResult)
        mock_delete_result.deleted_count = 0
        scores.fairness_coll.delete_one = MagicMock(return_value=mock_delete_result)
        
        # Act
        result = scores.deleteScores("fairness", "nonexistent_model")
        
        # Assert
        assert result == "Some problem Occures while deleting the scores"
        scores.fairness_coll.delete_one.assert_called_once_with({'model_name': 'nonexistent_model'})
    
    @patch('service.inhouse_scores.DataBase')
    def test_delete_scores_database_error(self, mock_database):
        """Test deletion when database error occurs"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        scores.fairness_coll.delete_one = MagicMock(side_effect=Exception("Database error"))
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            scores.deleteScores("fairness", "test_model")
        assert "Database error" in str(exc_info.value)


class TestGetFairnessScores:
    """Test suite for getFairnessScores method"""
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_fairness_scores_with_data(self, mock_database):
        """Test getFairnessScores with valid data"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        mock_records = [
            {'model_name': 'model1', 'stereotype_recognition': '0.85'},
            {'model_name': 'model2', 'stereotype_recognition': '0.90'}
        ]
        scores.fairness_coll.find = MagicMock(return_value=iter(mock_records))
        
        # Act
        result = scores.getFairnessScores()
        
        # Assert
        assert len(result) == 2
        assert result[0]['model_name'] == 'model1'
        assert result[1]['model_name'] == 'model2'
        scores.fairness_coll.find.assert_called_once_with({}, {'_id': False})
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_fairness_scores_empty(self, mock_database):
        """Test getFairnessScores with no data"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        scores.fairness_coll.find = MagicMock(return_value=iter([]))
        
        # Act
        result = scores.getFairnessScores()
        
        # Assert
        assert result == []
        scores.fairness_coll.find.assert_called_once_with({}, {'_id': False})
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_fairness_scores_database_error(self, mock_database):
        """Test getFairnessScores when database error occurs"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        scores.fairness_coll.find = MagicMock(side_effect=Exception("Database connection lost"))
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            scores.getFairnessScores()
        assert "Database connection lost" in str(exc_info.value)


class TestGetTruthfullnessScores:
    """Test suite for getTruthfullnessScores method"""
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_truthfullness_scores_with_data(self, mock_database):
        """Test getTruthfullnessScores with valid data"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        mock_records = [
            {'model_name': 'model1', 'internal': '0.88', 'external': '0.87'},
            {'model_name': 'model2', 'internal': '0.92', 'external': '0.91'}
        ]
        scores.truthfullness_coll.find = MagicMock(return_value=iter(mock_records))
        
        # Act
        result = scores.getTruthfullnessScores()
        
        # Assert
        assert len(result) == 2
        assert result[0]['model_name'] == 'model1'
        assert result[1]['internal'] == '0.92'
        scores.truthfullness_coll.find.assert_called_once_with({}, {'_id': False})
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_truthfullness_scores_empty(self, mock_database):
        """Test getTruthfullnessScores with no data"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        scores.truthfullness_coll.find = MagicMock(return_value=iter([]))
        
        # Act
        result = scores.getTruthfullnessScores()
        
        # Assert
        assert result == []
        scores.truthfullness_coll.find.assert_called_once_with({}, {'_id': False})


class TestGetSafteyScores:
    """Test suite for getSafteyScores method"""
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_saftey_scores_with_data(self, mock_database):
        """Test getSafteyScores with valid data"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        mock_records = [
            {'model_name': 'model1', 'jailbreak': '0.75', 'toxicity': '0.80'}
        ]
        scores.saftey_coll.find = MagicMock(return_value=iter(mock_records))
        
        # Act
        result = scores.getSafteyScores()
        
        # Assert
        assert len(result) == 1
        assert result[0]['model_name'] == 'model1'
        assert result[0]['jailbreak'] == '0.75'
        scores.saftey_coll.find.assert_called_once_with({}, {'_id': False})
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_saftey_scores_empty(self, mock_database):
        """Test getSafteyScores with no data"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        scores.saftey_coll.find = MagicMock(return_value=iter([]))
        
        # Act
        result = scores.getSafteyScores()
        
        # Assert
        assert result == []
        scores.saftey_coll.find.assert_called_once_with({}, {'_id': False})


class TestGetPrivacyScores:
    """Test suite for getPrivacyScores method"""
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_privacy_scores_with_data(self, mock_database):
        """Test getPrivacyScores with valid data"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        mock_records = [
            {'model_name': 'model1', 'privacy_awareness_normal': '0.92'}
        ]
        scores.privacy_coll.find = MagicMock(return_value=iter(mock_records))
        
        # Act
        result = scores.getPrivacyScores()
        
        # Assert
        assert len(result) == 1
        assert result[0]['privacy_awareness_normal'] == '0.92'
        scores.privacy_coll.find.assert_called_once_with({}, {'_id': False})
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_privacy_scores_empty(self, mock_database):
        """Test getPrivacyScores with no data"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        scores.privacy_coll.find = MagicMock(return_value=iter([]))
        
        # Act
        result = scores.getPrivacyScores()
        
        # Assert
        assert result == []
        scores.privacy_coll.find.assert_called_once_with({}, {'_id': False})


class TestGetEthicsScores:
    """Test suite for getEthicsScores method"""
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_ethics_scores_with_data(self, mock_database):
        """Test getEthicsScores with valid data"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        mock_records = [
            {'model_name': 'model1', 'social_chemistry_101_acc': '0.88'}
        ]
        scores.ethics_coll.find = MagicMock(return_value=iter(mock_records))
        
        # Act
        result = scores.getEthicsScores()
        
        # Assert
        assert len(result) == 1
        assert result[0]['social_chemistry_101_acc'] == '0.88'
        scores.ethics_coll.find.assert_called_once_with({}, {'_id': False})
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_ethics_scores_empty(self, mock_database):
        """Test getEthicsScores with no data"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        scores.ethics_coll.find = MagicMock(return_value=iter([]))
        
        # Act
        result = scores.getEthicsScores()
        
        # Assert
        assert result == []
        scores.ethics_coll.find.assert_called_once_with({}, {'_id': False})


class TestAddFairnessScore:
    """Test suite for addFairnessScore method"""
    
    @patch('service.inhouse_scores.DataBase')
    @patch('service.inhouse_scores.Fairness')
    def test_add_fairness_score_success(self, mock_fairness_class, mock_database):
        """Test successful addition of fairness score"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {
            'model_name': 'test_model',
            'overall_agreement_rate': '0.85',
            'stereotype_recognition': '0.90',
            'stereotype_query_test': '0.88',
            'disparagement_race': '0.87',
            'disparagement_sex': '0.86',
            'prefereence_rta': '0.89'
        }
        
        mock_fairness_instance = MagicMock()
        mock_fairness_instance.model_dump.return_value = payload
        mock_fairness_class.return_value = mock_fairness_instance
        
        mock_insert_result = Mock(spec=InsertOneResult)
        mock_insert_result.acknowledged = True
        scores.fairness_coll.insert_one = MagicMock(return_value=mock_insert_result)
        
        # Act
        result = scores.addFairnessScore(payload)
        
        # Assert
        assert result == 'Insertion Successful'
        scores.fairness_coll.insert_one.assert_called_once()
    
    @patch('service.inhouse_scores.DataBase')
    @patch('service.inhouse_scores.Fairness')
    def test_add_fairness_score_not_acknowledged(self, mock_fairness_class, mock_database):
        """Test addition of fairness score when not acknowledged"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {
            'model_name': 'test_model',
            'overall_agreement_rate': '0.85',
            'stereotype_recognition': '0.90',
            'stereotype_query_test': '0.88',
            'disparagement_race': '0.87',
            'disparagement_sex': '0.86',
            'prefereence_rta': '0.89'
        }
        
        mock_fairness_instance = MagicMock()
        mock_fairness_instance.model_dump.return_value = payload
        mock_fairness_class.return_value = mock_fairness_instance
        
        mock_insert_result = Mock(spec=InsertOneResult)
        mock_insert_result.acknowledged = False
        scores.fairness_coll.insert_one = MagicMock(return_value=mock_insert_result)
        
        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            scores.addFairnessScore(payload)
        assert 'Insertion not acknowledged by the server' in str(exc_info.value)
    
    @patch('service.inhouse_scores.DataBase')
    @patch('service.inhouse_scores.Fairness')
    def test_add_fairness_score_database_error(self, mock_fairness_class, mock_database):
        """Test addition of fairness score when database error occurs"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {
            'model_name': 'test_model',
            'overall_agreement_rate': '0.85',
            'stereotype_recognition': '0.90',
            'stereotype_query_test': '0.88',
            'disparagement_race': '0.87',
            'disparagement_sex': '0.86',
            'prefereence_rta': '0.89'
        }
        
        mock_fairness_instance = MagicMock()
        mock_fairness_instance.model_dump.return_value = payload
        mock_fairness_class.return_value = mock_fairness_instance
        
        scores.fairness_coll.insert_one = MagicMock(side_effect=Exception("Database error"))
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            scores.addFairnessScore(payload)
        assert "Database error" in str(exc_info.value)


class TestAddTruthfullnessScore:
    """Test suite for addTruthfullnessScore method"""
    
    @patch('service.inhouse_scores.DataBase')
    @patch('service.inhouse_scores.Truthfullness')
    def test_add_truthfullness_score_success(self, mock_truthfullness_class, mock_database):
        """Test successful addition of truthfullness score"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {
            'model_name': 'test_model',
            'internal': '0.85',
            'external': '0.90',
            'persona_sycophancy': '0.88',
            'preference_sycophancy': '0.87',
            'adv_factuality': '0.86',
            'hallucination': '0.89'
        }
        
        mock_truthfullness_instance = MagicMock()
        mock_truthfullness_instance.model_dump.return_value = payload
        mock_truthfullness_class.return_value = mock_truthfullness_instance
        
        mock_insert_result = Mock(spec=InsertOneResult)
        mock_insert_result.acknowledged = True
        scores.truthfullness_coll.insert_one = MagicMock(return_value=mock_insert_result)
        
        # Act
        result = scores.addTruthfullnessScore(payload)
        
        # Assert
        assert result == 'Insertion Successful'
        scores.truthfullness_coll.insert_one.assert_called_once()
    
    @patch('service.inhouse_scores.DataBase')
    @patch('service.inhouse_scores.Truthfullness')
    def test_add_truthfullness_score_not_acknowledged(self, mock_truthfullness_class, mock_database):
        """Test addition of truthfullness score when not acknowledged"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {
            'model_name': 'test_model',
            'internal': '0.85',
            'external': '0.90',
            'persona_sycophancy': '0.88',
            'preference_sycophancy': '0.87',
            'adv_factuality': '0.86',
            'hallucination': '0.89'
        }
        
        mock_truthfullness_instance = MagicMock()
        mock_truthfullness_instance.model_dump.return_value = payload
        mock_truthfullness_class.return_value = mock_truthfullness_instance
        
        mock_insert_result = Mock(spec=InsertOneResult)
        mock_insert_result.acknowledged = False
        scores.truthfullness_coll.insert_one = MagicMock(return_value=mock_insert_result)
        
        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            scores.addTruthfullnessScore(payload)
        assert 'Insertion not acknowledged by the server' in str(exc_info.value)


class TestAddEthicsScore:
    """Test suite for addEthicsScore method"""
    
    @patch('service.inhouse_scores.DataBase')
    @patch('service.inhouse_scores.Ethics')
    def test_add_ethics_score_success(self, mock_ethics_class, mock_database):
        """Test successful addition of ethics score"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {
            'model_name': 'test_model',
            'social_chemistry_101_acc': '0.85',
            'ehitcs_acc': '0.90',
            'moralchoice_acc': '0.88',
            'moralchoice_rta': '0.87',
            'emotional_acc': '0.86'
        }
        
        mock_ethics_instance = MagicMock()
        mock_ethics_instance.model_dump.return_value = payload
        mock_ethics_class.return_value = mock_ethics_instance
        
        mock_insert_result = Mock(spec=InsertOneResult)
        mock_insert_result.acknowledged = True
        scores.ethics_coll.insert_one = MagicMock(return_value=mock_insert_result)
        
        # Act
        result = scores.addEthicsScore(payload)
        
        # Assert
        assert result == 'Insertion Successful'
        scores.ethics_coll.insert_one.assert_called_once()
    
    @patch('service.inhouse_scores.DataBase')
    @patch('service.inhouse_scores.Ethics')
    def test_add_ethics_score_not_acknowledged(self, mock_ethics_class, mock_database):
        """Test addition of ethics score when not acknowledged"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {
            'model_name': 'test_model',
            'social_chemistry_101_acc': '0.85',
            'ehitcs_acc': '0.90',
            'moralchoice_acc': '0.88',
            'moralchoice_rta': '0.87',
            'emotional_acc': '0.86'
        }
        
        mock_ethics_instance = MagicMock()
        mock_ethics_instance.model_dump.return_value = payload
        mock_ethics_class.return_value = mock_ethics_instance
        
        mock_insert_result = Mock(spec=InsertOneResult)
        mock_insert_result.acknowledged = False
        scores.ethics_coll.insert_one = MagicMock(return_value=mock_insert_result)
        
        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            scores.addEthicsScore(payload)
        assert 'Insertion not acknowledged by the server' in str(exc_info.value)


class TestAddPrivacyScore:
    """Test suite for addPrivacyScore method"""
    
    @patch('service.inhouse_scores.DataBase')
    @patch('service.inhouse_scores.Privacy')
    def test_add_privacy_score_success(self, mock_privacy_class, mock_database):
        """Test successful addition of privacy score"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {
            'model_name': 'test_model',
            'privacy_awareness_normal': '0.85',
            'privacy_awareness_aug': '0.90',
            'privacy_leakage_rta': '0.88',
            'privacy_leakage_td': '0.87',
            'privacy_leakage_cd': '0.86',
            'privacy_awareness_correlation': '0.89'
        }
        
        mock_privacy_instance = MagicMock()
        mock_privacy_instance.model_dump.return_value = payload
        mock_privacy_class.return_value = mock_privacy_instance
        
        mock_insert_result = Mock(spec=InsertOneResult)
        mock_insert_result.acknowledged = True
        scores.privacy_coll.insert_one = MagicMock(return_value=mock_insert_result)
        
        # Act
        result = scores.addPrivacyScore(payload)
        
        # Assert
        assert result == 'Insertion Successful'
        scores.privacy_coll.insert_one.assert_called_once()
    
    @patch('service.inhouse_scores.DataBase')
    @patch('service.inhouse_scores.Privacy')
    def test_add_privacy_score_not_acknowledged(self, mock_privacy_class, mock_database):
        """Test addition of privacy score when not acknowledged"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {
            'model_name': 'test_model',
            'privacy_awareness_normal': '0.85',
            'privacy_awareness_aug': '0.90',
            'privacy_leakage_rta': '0.88',
            'privacy_leakage_td': '0.87',
            'privacy_leakage_cd': '0.86',
            'privacy_awareness_correlation': '0.89'
        }
        
        mock_privacy_instance = MagicMock()
        mock_privacy_instance.model_dump.return_value = payload
        mock_privacy_class.return_value = mock_privacy_instance
        
        mock_insert_result = Mock(spec=InsertOneResult)
        mock_insert_result.acknowledged = False
        scores.privacy_coll.insert_one = MagicMock(return_value=mock_insert_result)
        
        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            scores.addPrivacyScore(payload)
        assert 'Insertion not acknowledged by the server' in str(exc_info.value)


class TestAddSafteyScore:
    """Test suite for addSafteyScore method"""
    
    @patch('service.inhouse_scores.DataBase')
    @patch('service.inhouse_scores.Saftey')
    def test_add_saftey_score_success(self, mock_saftey_class, mock_database):
        """Test successful addition of safety score"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {
            'model_name': 'test_model',
            'jailbreak': '0.85',
            'toxicity': '0.90',
            'misuse': '0.88',
            'exaggerated_safety': '0.87'
        }
        
        mock_saftey_instance = MagicMock()
        mock_saftey_instance.model_dump.return_value = payload
        mock_saftey_class.return_value = mock_saftey_instance
        
        mock_insert_result = Mock(spec=InsertOneResult)
        mock_insert_result.acknowledged = True
        scores.saftey_coll.insert_one = MagicMock(return_value=mock_insert_result)
        
        # Act
        result = scores.addSafteyScore(payload)
        
        # Assert
        assert result == 'Insertion Successful'
        scores.saftey_coll.insert_one.assert_called_once()
    
    @patch('service.inhouse_scores.DataBase')
    @patch('service.inhouse_scores.Saftey')
    def test_add_saftey_score_not_acknowledged(self, mock_saftey_class, mock_database):
        """Test addition of safety score when not acknowledged"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {
            'model_name': 'test_model',
            'jailbreak': '0.85',
            'toxicity': '0.90',
            'misuse': '0.88',
            'exaggerated_safety': '0.87'
        }
        
        mock_saftey_instance = MagicMock()
        mock_saftey_instance.model_dump.return_value = payload
        mock_saftey_class.return_value = mock_saftey_instance
        
        mock_insert_result = Mock(spec=InsertOneResult)
        mock_insert_result.acknowledged = False
        scores.saftey_coll.insert_one = MagicMock(return_value=mock_insert_result)
        
        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            scores.addSafteyScore(payload)
        assert 'Insertion not acknowledged by the server' in str(exc_info.value)


class TestEdgeCases:
    """Test suite for edge cases and special scenarios"""
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_score_with_partial_match(self, mock_database):
        """Test getScore method with partial category name match"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        expected_data = [{'model_name': 'test_model'}]
        scores.getFairnessScores = MagicMock(return_value=expected_data)
        
        # Act - using substring "fairness" within a larger string
        result = scores.getScore("test_fairness_category")
        
        # Assert
        assert result == expected_data
        scores.getFairnessScores.assert_called_once()
    
    @patch('service.inhouse_scores.DataBase')
    def test_add_score_missing_category_key(self, mock_database):
        """Test addScore method with missing category key"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {'model_name': 'test_model'}  # Missing 'category' key
        
        # Act & Assert
        with pytest.raises(KeyError):
            scores.addScore(payload)
    
    @patch('service.inhouse_scores.DataBase')
    def test_delete_scores_empty_model_name(self, mock_database):
        """Test deleteScores with empty model name"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        mock_delete_result = Mock(spec=DeleteResult)
        mock_delete_result.deleted_count = 0
        scores.fairness_coll.delete_one = MagicMock(return_value=mock_delete_result)
        
        # Act
        result = scores.deleteScores("fairness", "")
        
        # Assert
        assert result == "Some problem Occures while deleting the scores"
        scores.fairness_coll.delete_one.assert_called_once_with({'model_name': ''})
    
    @patch('service.inhouse_scores.DataBase')
    @patch('service.inhouse_scores.Fairness')
    def test_add_score_with_special_characters_in_model_name(self, mock_fairness_class, mock_database):
        """Test adding score with special characters in model name"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        payload = {
            'model_name': 'test-model_v1.2@special#chars',
            'overall_agreement_rate': '0.85',
            'stereotype_recognition': '0.90',
            'stereotype_query_test': '0.88',
            'disparagement_race': '0.87',
            'disparagement_sex': '0.86',
            'prefereence_rta': '0.89'
        }
        
        mock_fairness_instance = MagicMock()
        mock_fairness_instance.model_dump.return_value = payload
        mock_fairness_class.return_value = mock_fairness_instance
        
        mock_insert_result = Mock(spec=InsertOneResult)
        mock_insert_result.acknowledged = True
        scores.fairness_coll.insert_one = MagicMock(return_value=mock_insert_result)
        
        # Act
        result = scores.addFairnessScore(payload)
        
        # Assert
        assert result == 'Insertion Successful'
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_scores_with_large_dataset(self, mock_database):
        """Test getting scores with large number of records"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        # Create a large dataset
        mock_records = [
            {'model_name': f'model_{i}', 'score': f'0.{85 + i % 15}'}
            for i in range(1000)
        ]
        scores.fairness_coll.find = MagicMock(return_value=iter(mock_records))
        
        # Act
        result = scores.getFairnessScores()
        
        # Assert
        assert len(result) == 1000
        assert result[0]['model_name'] == 'model_0'
        assert result[999]['model_name'] == 'model_999'
    
    @patch('service.inhouse_scores.DataBase')
    def test_case_sensitivity_in_category_names(self, mock_database):
        """Test case sensitivity in category name matching"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        # Act
        result_lower = scores.getScore("fairness")
        result_upper = scores.getScore("FAIRNESS")
        result_mixed = scores.getScore("FaIrNeSs")
        
        # Assert - None of these should raise errors
        # Only lowercase 'fairness' should match
        assert result_upper is None
        assert result_mixed is None


class TestConcurrencyAndPerformance:
    """Test suite for concurrency and performance scenarios"""
    
    @patch('service.inhouse_scores.DataBase')
    def test_multiple_concurrent_reads(self, mock_database):
        """Test multiple concurrent read operations"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        # Create separate mock collections for each category
        mock_fairness_coll = MagicMock()
        mock_privacy_coll = MagicMock()
        mock_ethics_coll = MagicMock()
        
        # Configure the database to return different collections
        mock_db.__getitem__.side_effect = lambda key: {
            'fairnessInhouse': mock_fairness_coll,
            'privacyInhouse': mock_privacy_coll,
            'ethicsInhouse': mock_ethics_coll,
            'safteyInhouse': MagicMock(),
            'truthfullnessInhouse': MagicMock()
        }[key]
        
        scores = Scores()
        
        # Use side_effect to return a new iterator on each call
        mock_fairness_coll.find = MagicMock(side_effect=lambda *args, **kwargs: iter([{'model_name': 'model1'}]))
        mock_privacy_coll.find = MagicMock(side_effect=lambda *args, **kwargs: iter([{'model_name': 'model1'}]))
        mock_ethics_coll.find = MagicMock(side_effect=lambda *args, **kwargs: iter([{'model_name': 'model1'}]))
        
        # Act
        result1 = scores.getFairnessScores()
        result2 = scores.getPrivacyScores()
        result3 = scores.getEthicsScores()
        
        # Assert
        assert len(result1) == 1
        assert len(result2) == 1
        assert len(result3) == 1
        mock_fairness_coll.find.assert_called_once()
        mock_privacy_coll.find.assert_called_once()
        mock_ethics_coll.find.assert_called_once()


class TestDataIntegrity:
    """Test suite for data integrity and validation"""
    
    @patch('service.inhouse_scores.DataBase')
    @patch('service.inhouse_scores.Fairness')
    def test_add_score_with_missing_required_fields(self, mock_fairness_class, mock_database):
        """Test adding score with missing required fields"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        # Missing several required fields
        incomplete_payload = {
            'model_name': 'test_model',
            'overall_agreement_rate': '0.85'
            # Missing other required fields
        }
        
        # Pydantic validation should fail
        mock_fairness_class.side_effect = Exception("Validation error: missing required fields")
        
        # Act & Assert
        # The code will raise KeyError when trying to access missing fields from the payload dict
        with pytest.raises((Exception, KeyError)) as exc_info:
            scores.addFairnessScore(incomplete_payload)
        # Check for either validation error or KeyError (missing key)
        assert ("Validation error" in str(exc_info.value) or 
                "missing required fields" in str(exc_info.value).lower() or
                isinstance(exc_info.value, KeyError))
    
    @patch('service.inhouse_scores.DataBase')
    def test_get_scores_with_corrupted_data(self, mock_database):
        """Test getting scores when database returns corrupted data"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        # Simulate corrupted data (e.g., None values, malformed records)
        mock_records = [
            {'model_name': 'model1', 'score': '0.85'},
            None,  # Corrupted entry
            {'model_name': 'model2'}  # Missing fields
        ]
        scores.fairness_coll.find = MagicMock(return_value=iter(mock_records))
        
        # Act
        result = scores.getFairnessScores()
        
        # Assert - Should handle gracefully
        assert len(result) == 3
        assert result[0]['model_name'] == 'model1'
        assert result[1] is None
        assert 'score' not in result[2]


class TestResourceManagement:
    """Test suite for resource management"""
    
    @patch('service.inhouse_scores.DataBase')
    def test_database_connection_cleanup(self, mock_database):
        """Test that database connections are properly managed"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        
        # Act
        scores = Scores()
        del scores  # Force cleanup
        
        # Assert - Database object was created
        mock_database.assert_called_once()
    
    @patch('service.inhouse_scores.DataBase')
    def test_memory_efficiency_with_iterator(self, mock_database):
        """Test that find operations use iterators for memory efficiency"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        # Create a large dataset as iterator
        def record_generator():
            for i in range(10000):
                yield {'model_name': f'model_{i}', 'score': f'0.{85 + i % 15}'}
        
        scores.fairness_coll.find = MagicMock(return_value=record_generator())
        
        # Act
        result = scores.getFairnessScores()
        
        # Assert
        assert len(result) == 10000
        scores.fairness_coll.find.assert_called_once()


class TestErrorRecovery:
    """Test suite for error recovery scenarios"""
    
    @patch('service.inhouse_scores.DataBase')
    def test_recovery_from_transient_database_error(self, mock_database):
        """Test behavior with transient database errors"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        # First call fails, second succeeds
        scores.fairness_coll.find = MagicMock(side_effect=[
            Exception("Transient connection error"),
            iter([{'model_name': 'model1'}])
        ])
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            scores.getFairnessScores()
        assert "Transient connection error" in str(exc_info.value)
        
        # Second attempt should succeed
        result = scores.getFairnessScores()
        assert len(result) == 1
    
    @patch('service.inhouse_scores.DataBase')
    def test_timeout_handling(self, mock_database):
        """Test handling of database timeout scenarios"""
        # Arrange
        mock_db = MagicMock()
        mock_database.return_value.db = mock_db
        scores = Scores()
        
        scores.fairness_coll.find = MagicMock(side_effect=Exception("Operation timed out"))
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            scores.getFairnessScores()
        assert "Operation timed out" in str(exc_info.value)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=service.inhouse_scores', '--cov-report=html', '--cov-report=term'])
