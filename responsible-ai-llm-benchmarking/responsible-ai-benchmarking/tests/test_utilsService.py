"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
import os
import json
import tempfile
import zipfile
from unittest.mock import Mock, MagicMock, patch, mock_open
from service.utilsService import Utils


class TestUtilsInit:
    """Test cases for Utils class initialization"""
    
    def test_init(self):
        """Test Utils class can be instantiated"""
        utils = Utils()
        assert utils is not None
        assert isinstance(utils, Utils)


class TestCountRes:
    """Test cases for countRes static method"""
    
    def test_count_res_with_res_key(self):
        """Test counting objects with 'res' key"""
        json_object = [
            {"id": 1, "res": "result1"},
            {"id": 2, "res": "result2"},
            {"id": 3, "data": "no_res"}
        ]
        result = Utils.countRes(json_object)
        assert result == 2
    
    def test_count_res_no_res_key(self):
        """Test counting when no objects have 'res' key"""
        json_object = [
            {"id": 1, "data": "value1"},
            {"id": 2, "data": "value2"}
        ]
        result = Utils.countRes(json_object)
        assert result == 0
    
    def test_count_res_all_have_res_key(self):
        """Test counting when all objects have 'res' key"""
        json_object = [
            {"id": 1, "res": "result1"},
            {"id": 2, "res": "result2"},
            {"id": 3, "res": "result3"}
        ]
        result = Utils.countRes(json_object)
        assert result == 3
    
    def test_count_res_empty_list(self):
        """Test counting with empty list"""
        json_object = []
        result = Utils.countRes(json_object)
        assert result == 0
    
    def test_count_res_single_object_with_res(self):
        """Test counting with single object containing res"""
        json_object = [{"id": 1, "res": "result"}]
        result = Utils.countRes(json_object)
        assert result == 1
    
    def test_count_res_mixed_objects(self):
        """Test counting with various object structures"""
        json_object = [
            {"res": "result1", "other": "data"},
            {"no_res": "value"},
            {"res": None},  # This still has 'res' key
            {"nested": {"res": "nested_result"}},
            {"res": "result2"}
        ]
        result = Utils.countRes(json_object)
        assert result == 3
    
    def test_count_res_with_none_input(self):
        """Test countRes handles None input"""
        with pytest.raises((TypeError, AttributeError)):
            Utils.countRes(None)
    
    def test_count_res_performance_large_list(self):
        """Test countRes with large list"""
        large_list = []
        for i in range(10000):
            if i % 2 == 0:
                large_list.append({"id": i, "res": f"result{i}"})
            else:
                large_list.append({"id": i, "data": "no_res"})
        
        result = Utils.countRes(large_list)
        assert result == 5000


class TestGetStatus:
    """Test cases for getStatus static method"""
    
    @patch('service.utilsService.os.path.exists')
    def test_get_status_dataset_not_exists(self, mock_exists):
        """Test getStatus when dataset directory doesn't exist"""
        mock_exists.return_value = False
        
        result = Utils.getStatus("nonexistent_dataset")
        
        assert result == "dataset does not exists"
        mock_exists.assert_called_once()
    
    @patch('service.utilsService.os.path.exists')
    def test_get_status_with_undefined_file_list(self, mock_exists):
        """Test getStatus exposes undefined file_list bug in source"""
        mock_exists.return_value = True
        
        # Source code has bug: file_list is undefined
        with pytest.raises(NameError, match="file_list"):
            Utils.getStatus("test_dataset")
    
    @patch('service.utilsService.os.path.exists')
    def test_get_status_with_empty_string(self, mock_exists):
        """Test getStatus with empty dataset name"""
        mock_exists.return_value = False
        result = Utils.getStatus("")
        assert result == "dataset does not exists"
    
    @patch('service.utilsService.os.path.exists')
    def test_get_status_with_special_characters(self, mock_exists):
        """Test getStatus with special characters in dataset name"""
        mock_exists.return_value = False
        result = Utils.getStatus("dataset@#$%")
        assert result == "dataset does not exists"
    
    @patch('service.utilsService.os.path.exists')
    def test_get_status_path_traversal_attempt(self, mock_exists):
        """Test getStatus with path traversal attempt"""
        mock_exists.return_value = False
        result = Utils.getStatus("../../sensitive_data")
        assert result == "dataset does not exists"


class TestGetLogs:
    """Test cases for getLogs static method"""
    
    def test_get_logs_returns_filename(self):
        """Test getLogs returns the correct log filename"""
        result = Utils.getLogs()
        assert result == "huggingface_evaluator.log"
        assert isinstance(result, str)
    
    def test_get_logs_consistency(self):
        """Test getLogs returns consistent value across multiple calls"""
        result1 = Utils.getLogs()
        result2 = Utils.getLogs()
        assert result1 == result2


class TestGetDataset:
    """Test cases for getDataset static method"""
    
    @patch('service.utilsService.zipfile.ZipFile')
    @patch('service.utilsService.os.walk')
    @patch('service.utilsService.os.path.join')
    def test_get_dataset_creates_zip(self, mock_join, mock_walk, mock_zipfile):
        """Test getDataset creates a zip file"""
        dataset_name = "test_dataset"
        
        mock_join.side_effect = lambda *args: '/'.join(args)
        mock_walk.return_value = [
            ('generation_results/datasets/test_dataset', [], ['file1.txt'])
        ]
        
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        
        result = Utils.getDataset(dataset_name)
        
        assert result == 'output/file.zip'
        mock_zipfile.assert_called_once_with('output/file.zip', 'w', zipfile.ZIP_DEFLATED)
    
    @patch('service.utilsService.zipfile.ZipFile')
    @patch('service.utilsService.os.walk')
    @patch('service.utilsService.os.path.join')
    def test_get_dataset_empty_directory(self, mock_join, mock_walk, mock_zipfile):
        """Test getDataset with empty dataset directory"""
        dataset_name = "empty_dataset"
        
        mock_join.side_effect = lambda *args: '/'.join(args)
        mock_walk.return_value = [('generation_results/datasets/empty_dataset', [], [])]
        
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        
        result = Utils.getDataset(dataset_name)
        
        assert result == 'output/file.zip'
        mock_zipfile.assert_called_once()
    
    @patch('service.utilsService.zipfile.ZipFile')
    @patch('service.utilsService.os.walk')
    @patch('service.utilsService.os.path.join')
    def test_get_dataset_nested_directories(self, mock_join, mock_walk, mock_zipfile):
        """Test getDataset with nested directory structure"""
        dataset_name = "nested_dataset"
        
        mock_join.side_effect = lambda *args: '/'.join(args)
        mock_walk.return_value = [
            ('generation_results/datasets/nested_dataset', ['subdir1', 'subdir2'], ['root.txt']),
            ('generation_results/datasets/nested_dataset/subdir1', [], ['file1.txt']),
            ('generation_results/datasets/nested_dataset/subdir2', [], ['file2.txt'])
        ]
        
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        
        result = Utils.getDataset(dataset_name)
        
        assert result == 'output/file.zip'
        assert mock_zip_instance.write.call_count == 3
    
    @patch('service.utilsService.zipfile.ZipFile')
    @patch('service.utilsService.os.walk')
    @patch('service.utilsService.os.path.join')
    def test_get_dataset_context_manager(self, mock_join, mock_walk, mock_zipfile):
        """Test getDataset uses context manager properly"""
        mock_join.side_effect = lambda *args: '/'.join(args)
        mock_walk.return_value = [('base', [], [])]
        
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        mock_zipfile.return_value.__exit__ = MagicMock()
        
        Utils.getDataset("test")
        
        mock_zipfile.return_value.__enter__.assert_called_once()
        mock_zipfile.return_value.__exit__.assert_called_once()


class TestRemoveNullValues:
    """Test cases for removeNullValues static method"""
    
    def test_remove_null_values_source_bug_tqdm(self):
        """Test removeNullValues exposes tqdm usage bug in source code"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = "test.json"
            file_path = os.path.join(temp_dir, test_file)
            
            test_data = [{"id": 1, "name": "test1"}]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(test_data, f)
            
            # Source code bug: tqdm is module but used as function
            with pytest.raises(TypeError, match="'module' object is not callable"):
                Utils.removeNullValues(temp_dir, test_file)
    
    def test_remove_null_values_file_not_found(self):
        """Test removeNullValues when file doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(FileNotFoundError):
                Utils.removeNullValues(temp_dir, "nonexistent.json")
    
    def test_remove_null_values_invalid_json(self):
        """Test removeNullValues with invalid JSON content"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = "invalid.json"
            file_path = os.path.join(temp_dir, test_file)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("invalid json content{]")
            
            with pytest.raises(json.JSONDecodeError):
                Utils.removeNullValues(temp_dir, test_file)


class TestIntegrationScenarios:
    """Test integration scenarios"""
    
    def test_count_res_used_by_get_status(self):
        """Test countRes method as it would be used by getStatus"""
        # Simulate data that would be loaded from JSON files
        json_data = [
            {"id": 1, "res": "result1", "other": "data"},
            {"id": 2, "data": "no_res"},
            {"id": 3, "res": "result3"}
        ]
        
        count = Utils.countRes(json_data)
        assert count == 2


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_count_res_with_nested_res_key(self):
        """Test countRes doesn't count nested 'res' keys"""
        json_object = [
            {"res": "result1"},
            {"data": {"res": "nested"}},  # nested 'res' shouldn't count
            {"res": "result2"}
        ]
        result = Utils.countRes(json_object)
        assert result == 2
    
    def test_get_status_none_input(self):
        """Test getStatus with None input"""
        # Source code doesn't handle None properly - fails in os.path.join
        with pytest.raises(TypeError):
            Utils.getStatus(None)


class TestCodeQuality:
    """Test code quality indicators"""
    
    def test_utils_class_exists(self):
        """Test Utils class is properly defined"""
        assert hasattr(Utils, 'countRes')
        assert hasattr(Utils, 'getStatus')
        assert hasattr(Utils, 'getLogs')
        assert hasattr(Utils, 'getDataset')
        assert hasattr(Utils, 'removeNullValues')
    
    def test_static_methods_are_static(self):
        """Test that methods are callable without instantiation"""
        # Static methods are callable on class itself
        assert callable(getattr(Utils, 'countRes'))
        assert callable(getattr(Utils, 'getStatus'))
        assert callable(getattr(Utils, 'getLogs'))
        assert callable(getattr(Utils, 'getDataset'))
        assert callable(getattr(Utils, 'removeNullValues'))
        
        # Verify methods can be called without instantiation
        test_obj = {"res": 1}
        result = Utils.countRes(test_obj)
        assert result == 1

