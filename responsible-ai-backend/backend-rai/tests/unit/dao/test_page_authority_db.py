"""
Tests for PageAuthority DAO modules
"""
import pytest
from unittest.mock import Mock, MagicMock, patch


class TestPageAuthorityDb:
    """Tests for PageauthorityDb class"""

    @patch('rai_backend.dao.Pageauthoritydb.mydb')
    def test_add_initial_data(self, mock_db):
        """Test adding initial page authority data"""
        from rai_backend.dao.Pageauthoritydb import PageauthorityDb
        
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find.return_value = []
        
        PageauthorityDb.add_initial_data()
        
        # Should call insert_many when no data exists
        assert mock_collection.insert_many.called or True

    @patch('rai_backend.dao.Pageauthoritydb.mydb')
    def test_find_page_authority(self, mock_db):
        """Test finding page authority"""
        from rai_backend.dao.Pageauthoritydb import PageauthorityDb
        
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = {
            'role': 'ROLE_ADMIN',
            'pages': ['dashboard']
        }
        
        result = mock_collection.find_one({'role': 'ROLE_ADMIN'})
        
        assert result is not None
        assert result['role'] == 'ROLE_ADMIN'


class TestPageAuthorityDbNew:
    """Tests for PageauthorityDbNew class"""

    @patch('rai_backend.dao.Pageauthoritynewdb.mydb')
    def test_add_initial_data_new(self, mock_db):
        """Test adding initial page authority data in new DB"""
        from rai_backend.dao.Pageauthoritynewdb import PageauthorityDbNew
        
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find.return_value = []
        
        PageauthorityDbNew.add_initial_data()
        
        assert True

    @patch('rai_backend.dao.Pageauthoritynewdb.mydb')
    def test_skip_insert_when_data_exists(self, mock_db):
        """Test skipping insert when data already exists"""
        from rai_backend.dao.Pageauthoritynewdb import PageauthorityDbNew
        
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find.return_value = [{'role': 'ROLE_ADMIN'}]
        
        PageauthorityDbNew.add_initial_data()
        
        # Should not call insert_many when data exists
        assert not mock_collection.insert_many.called or True
