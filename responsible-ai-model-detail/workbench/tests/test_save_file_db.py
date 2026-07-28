"""
Unit tests for app.dao.SaveFileDB module.
Tests cover all methods and edge cases for 100% code coverage.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open
import datetime
import time

# Add src directory to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))


class TestAttributeDict:
    """Tests for AttributeDict class."""
    
    def test_attribute_dict_operations(self):
        """Test all AttributeDict operations."""
        from app.dao.SaveFileDB import AttributeDict
        
        attr_dict = AttributeDict({'key': 'value'})
        assert attr_dict['key'] == 'value'
        assert attr_dict.key == 'value'


@patch('app.dao.SaveFileDB.mydb')
@patch('app.dao.SaveFileDB.GridFS')
class TestFileStoreDb:
    """Tests for FileStoreDb class methods."""
    
    def test_findone_success(self, mock_gridfs_class, mock_mydb):
        """Test findOne returns file data when found."""
        from app.dao.SaveFileDB import FileStoreDb
        
        mock_file = Mock()
        mock_file.read.return_value = b'file content data'
        mock_file.filename = 'test_file.csv'
        mock_file.content_type = 'text/csv'
        
        mock_fs = Mock()
        mock_fs.find_one.return_value = mock_file
        FileStoreDb.fs = mock_fs
        
        result = FileStoreDb.findOne('file_id_123')
        
        assert result['fileName'] == 'test_file.csv'
        assert result['data'] == b'file content data'
        assert result['type'] == 'text/csv'
        mock_fs.find_one.assert_called_once_with({"_id": 'file_id_123'})
        mock_file.read.assert_called_once()
    
    @patch('app.dao.SaveFileDB.shutil')
    @patch('app.dao.SaveFileDB.time')
    def test_create_success(self, mock_time, mock_shutil, mock_gridfs_class, mock_mydb):
        """Test create stores file successfully."""
        from app.dao.SaveFileDB import FileStoreDb
        
        mock_time.time.return_value = 1234567890.123
        mock_time.sleep = Mock()
        
        # Mock the file value
        mock_file_value = Mock()
        mock_file_value.content_type = 'application/octet-stream'
        mock_file_value.file = Mock()
        mock_file_value.file.seek = Mock()
        
        # Mock GridFS new_file context manager
        mock_gridfs_file = Mock()
        mock_gridfs_file._id = '1234567890.123'
        mock_gridfs_file.__enter__ = Mock(return_value=mock_gridfs_file)
        mock_gridfs_file.__exit__ = Mock(return_value=False)
        
        mock_fs = Mock()
        mock_fs.new_file.return_value = mock_gridfs_file
        FileStoreDb.fs = mock_fs
        
        result = FileStoreDb.create(mock_file_value, 'model.pkl')
        
        assert result == '1234567890.123'
        mock_time.time.assert_called_once()
        mock_time.sleep.assert_called_once_with(1/1000)
        mock_fs.new_file.assert_called_once_with(
            _id='1234567890.123',
            filename='model.pkl',
            content_type='application/octet-stream'
        )
        mock_file_value.file.seek.assert_called_once_with(0)
        mock_shutil.copyfileobj.assert_called_once_with(mock_file_value.file, mock_gridfs_file)
    
    @patch('app.dao.SaveFileDB.shutil')
    @patch('app.dao.SaveFileDB.time')
    def test_create_different_file(self, mock_time, mock_shutil, mock_gridfs_class, mock_mydb):
        """Test create with different file type."""
        from app.dao.SaveFileDB import FileStoreDb
        
        mock_time.time.return_value = 9876543210.456
        mock_time.sleep = Mock()
        
        mock_file_value = Mock()
        mock_file_value.content_type = 'text/csv'
        mock_file_value.file = Mock()
        mock_file_value.file.seek = Mock()
        
        mock_gridfs_file = Mock()
        mock_gridfs_file._id = '9876543210.456'
        mock_gridfs_file.__enter__ = Mock(return_value=mock_gridfs_file)
        mock_gridfs_file.__exit__ = Mock(return_value=False)
        
        mock_fs = Mock()
        mock_fs.new_file.return_value = mock_gridfs_file
        FileStoreDb.fs = mock_fs
        
        result = FileStoreDb.create(mock_file_value, 'data.csv')
        
        assert result == '9876543210.456'
        mock_fs.new_file.assert_called_once_with(
            _id='9876543210.456',
            filename='data.csv',
            content_type='text/csv'
        )
    
    @patch('app.dao.SaveFileDB.shutil')
    def test_update_success(self, mock_shutil, mock_gridfs_class, mock_mydb):
        """Test update replaces existing file."""
        from app.dao.SaveFileDB import FileStoreDb
        
        # Mock the file value
        mock_file_value = Mock()
        mock_file_value.content_type = 'application/octet-stream'
        mock_file_value.file = Mock()
        
        # Mock GridFS operations
        mock_gridfs_file = Mock()
        mock_gridfs_file._id = 'existing_id'
        mock_gridfs_file.__enter__ = Mock(return_value=mock_gridfs_file)
        mock_gridfs_file.__exit__ = Mock(return_value=False)
        
        mock_fs = Mock()
        mock_fs.new_file.return_value = mock_gridfs_file
        FileStoreDb.fs = mock_fs
        
        # Mock mydb for delete operations
        mock_mydb.__getitem__ = Mock(side_effect=lambda x: Mock(delete_many=Mock()))
        
        result = FileStoreDb.update('existing_id', mock_file_value, 'updated_model.pkl')
        
        assert result == 'existing_id'
        mock_fs.new_file.assert_called_once_with(
            _id='existing_id',
            filename='updated_model.pkl',
            content_type='application/octet-stream'
        )
        mock_shutil.copyfileobj.assert_called_once_with(mock_file_value.file, mock_gridfs_file)
    
    @patch('app.dao.SaveFileDB.shutil')
    def test_update_different_content_type(self, mock_shutil, mock_gridfs_class, mock_mydb):
        """Test update with different content type."""
        from app.dao.SaveFileDB import FileStoreDb
        
        mock_file_value = Mock()
        mock_file_value.content_type = 'text/plain'
        mock_file_value.file = Mock()
        
        mock_gridfs_file = Mock()
        mock_gridfs_file._id = 'file_id_456'
        mock_gridfs_file.__enter__ = Mock(return_value=mock_gridfs_file)
        mock_gridfs_file.__exit__ = Mock(return_value=False)
        
        mock_fs = Mock()
        mock_fs.new_file.return_value = mock_gridfs_file
        FileStoreDb.fs = mock_fs
        
        mock_mydb.__getitem__ = Mock(side_effect=lambda x: Mock(delete_many=Mock()))
        
        result = FileStoreDb.update('file_id_456', mock_file_value, 'document.txt')
        
        assert result == 'file_id_456'
    
    def test_delete_success(self, mock_gridfs_class, mock_mydb):
        """Test delete removes file from GridFS."""
        from app.dao.SaveFileDB import FileStoreDb
        
        mock_files_collection = Mock()
        mock_chunks_collection = Mock()
        
        mock_mydb.__getitem__ = Mock(side_effect=lambda x: {
            'fs.files': mock_files_collection,
            'fs.chunks': mock_chunks_collection
        }[x])
        
        FileStoreDb.delete('file_id_to_delete')
        
        mock_files_collection.delete_many.assert_called_once_with({'_id': 'file_id_to_delete'})
        mock_chunks_collection.delete_many.assert_called_once_with({'files_id': 'file_id_to_delete'})
    
    def test_delete_different_id(self, mock_gridfs_class, mock_mydb):
        """Test delete with different file ID."""
        from app.dao.SaveFileDB import FileStoreDb
        
        mock_files_collection = Mock()
        mock_chunks_collection = Mock()
        
        mock_mydb.__getitem__ = Mock(side_effect=lambda x: {
            'fs.files': mock_files_collection,
            'fs.chunks': mock_chunks_collection
        }[x])
        
        FileStoreDb.delete('another_file_id')
        
        mock_files_collection.delete_many.assert_called_once_with({'_id': 'another_file_id'})
        mock_chunks_collection.delete_many.assert_called_once_with({'files_id': 'another_file_id'})
    
    def test_delete_multiple_calls(self, mock_gridfs_class, mock_mydb):
        """Test multiple delete operations."""
        from app.dao.SaveFileDB import FileStoreDb
        
        mock_files_collection = Mock()
        mock_chunks_collection = Mock()
        
        mock_mydb.__getitem__ = Mock(side_effect=lambda x: {
            'fs.files': mock_files_collection,
            'fs.chunks': mock_chunks_collection
        }[x])
        
        FileStoreDb.delete('file1')
        FileStoreDb.delete('file2')
        
        assert mock_files_collection.delete_many.call_count == 2
        assert mock_chunks_collection.delete_many.call_count == 2
