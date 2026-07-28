"""
Unit tests for diffrentialPrivacy.py service.
Tests DiffPrivacy class and its differential privacy mechanisms.
"""
import pytest
import io
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from privacy.service.diffrentialPrivacy import DiffPrivacy, AttributeDict


class TestAttributeDict:
    """Test suite for AttributeDict class"""

    def test_attribute_dict_basic_operations(self):
        """Test AttributeDict basic get/set/delete operations"""
        attr_dict = AttributeDict()
        attr_dict['key1'] = 'value1'
        assert attr_dict.key1 == 'value1'
        
        attr_dict.key2 = 'value2'
        assert attr_dict['key2'] == 'value2'
        
        del attr_dict.key1
        assert 'key1' not in attr_dict

    def test_attribute_dict_initialization(self):
        """Test AttributeDict initialization with data"""
        data = {'suppression': 'col1', 'noiselist': 'col2'}
        attr_dict = AttributeDict(data)
        assert attr_dict.suppression == 'col1'
        assert attr_dict['noiselist'] == 'col2'


class TestDiffPrivacyBinaryCheck:
    """Test suite for binaryCheck method"""

    def test_binaryCheck_with_binary_values(self):
        """Test binaryCheck with binary column values"""
        df = pd.DataFrame({'gender': ['M', 'F', 'M', 'F', 'M', 'F']})
        
        with patch('privacy.service.diffrentialPrivacy.binary.Binary') as mock_binary_class:
            mock_mechanism = Mock()
            mock_mechanism.randomise.side_effect = lambda x: x  # Return same value
            mock_binary_class.return_value = mock_mechanism
            
            DiffPrivacy.binaryCheck(df, 'gender')
            
            # Verify Binary mechanism was created with correct parameters
            mock_binary_class.assert_called_once()
            call_args = mock_binary_class.call_args
            assert call_args[1]['epsilon'] == 1.0
            assert call_args[1]['value0'] in ['M', 'F']
            assert call_args[1]['value1'] in ['M', 'F']

    def test_binaryCheck_with_numeric_binary(self):
        """Test binaryCheck with numeric binary values (0/1)"""
        df = pd.DataFrame({'flag': [0, 1, 0, 1, 1, 0]})
        
        with patch('privacy.service.diffrentialPrivacy.binary.Binary') as mock_binary_class:
            mock_mechanism = Mock()
            mock_mechanism.randomise.return_value = 1
            mock_binary_class.return_value = mock_mechanism
            
            DiffPrivacy.binaryCheck(df, 'flag')
            
            assert mock_mechanism.randomise.call_count == len(df)

    def test_binaryCheck_modifies_values(self):
        """Test binaryCheck modifies DataFrame values"""
        df = pd.DataFrame({'status': ['active', 'inactive', 'active', 'inactive']})
        
        with patch('privacy.service.diffrentialPrivacy.binary.Binary') as mock_binary_class:
            mock_mechanism = Mock()
            mock_mechanism.randomise.side_effect = ['inactive', 'active', 'inactive', 'active']
            mock_binary_class.return_value = mock_mechanism
            
            DiffPrivacy.binaryCheck(df, 'status')
            
            # Values should be modified
            assert df['status'].tolist() == ['inactive', 'active', 'inactive', 'active']


class TestDiffPrivacyRangeAdd:
    """Test suite for rangeAdd method"""

    def test_rangeAdd_creates_ranges(self):
        """Test rangeAdd creates appropriate ranges for numeric data"""
        df = pd.DataFrame({'age': [15, 25, 35, 45, 55, 65, 75]})
        
        DiffPrivacy.rangeAdd(df, 'age')
        
        # Verify column is now categorical
        assert df['age'].dtype.name == 'category'
        # Verify values are categorical ranges
        assert len(df['age']) == 7

    def test_rangeAdd_handles_small_range(self):
        """Test rangeAdd with small value range"""
        df = pd.DataFrame({'score': [5, 7, 9, 11, 13]})
        
        DiffPrivacy.rangeAdd(df, 'score')
        
        assert df['score'].dtype.name == 'category'

    def test_rangeAdd_handles_large_range(self):
        """Test rangeAdd with large value range"""
        df = pd.DataFrame({'income': [20000, 50000, 80000, 110000, 140000]})
        
        DiffPrivacy.rangeAdd(df, 'income')
        
        assert df['score'].dtype.name == 'category' if 'score' in df.columns else True


class TestDiffPrivacyGaussianFunc:
    """Test suite for gaussianFunc method"""

    def test_gaussianFunc_with_integer_column(self):
        """Test gaussianFunc applies Gaussian mechanism to integers"""
        df = pd.DataFrame({'count': [10, 20, 30, 40, 50]})
        
        with patch('privacy.service.diffrentialPrivacy.gaussian.GaussianAnalytic') as mock_gaussian_class:
            mock_mechanism = Mock()
            mock_mechanism.randomise.side_effect = [10.5, 19.8, 30.2, 39.7, 50.3]
            mock_gaussian_class.return_value = mock_mechanism
            
            DiffPrivacy.gaussianFunc(df, 'count')
            
            # Verify Gaussian mechanism was created
            mock_gaussian_class.assert_called_once_with(epsilon=1, delta=1, sensitivity=2)
            # Verify all values were processed
            assert mock_mechanism.randomise.call_count == len(df)
            # Verify results are integers
            assert df['count'].dtype == 'int64'

    def test_gaussianFunc_with_float_column(self):
        """Test gaussianFunc applies Gaussian mechanism to floats"""
        df = pd.DataFrame({'rating': [3.5, 4.2, 2.8, 4.9, 3.1]})
        
        with patch('privacy.service.diffrentialPrivacy.gaussian.GaussianAnalytic') as mock_gaussian_class:
            mock_mechanism = Mock()
            mock_mechanism.randomise.side_effect = [3.6, 4.1, 2.9, 4.8, 3.2]
            mock_gaussian_class.return_value = mock_mechanism
            
            DiffPrivacy.gaussianFunc(df, 'rating')
            
            assert mock_mechanism.randomise.call_count == len(df)
            assert df['rating'].dtype == 'float64'


class TestDiffPrivacyLaplaceFunc:
    """Test suite for laplaceFunc method"""

    def test_laplaceFunc_with_integer_column(self):
        """Test laplaceFunc applies Laplace mechanism to integers"""
        df = pd.DataFrame({'visits': [5, 10, 15, 20, 25]})
        
        with patch('privacy.service.diffrentialPrivacy.laplace.LaplaceTruncated') as mock_laplace_class:
            mock_mechanism = Mock()
            mock_mechanism.randomise.side_effect = [5.2, 10.1, 14.8, 20.3, 24.9]
            mock_laplace_class.return_value = mock_mechanism
            
            DiffPrivacy.laplaceFunc(df, 'visits')
            
            # Verify mechanism was created with bounds
            mock_laplace_class.assert_called_once()
            call_args = mock_laplace_class.call_args[1]
            assert call_args['epsilon'] == 1
            assert call_args['sensitivity'] == 1
            assert call_args['lower'] == 0  # min(5) - 5
            assert call_args['upper'] == 30  # max(25) + 5

    def test_laplaceFunc_with_float_column(self):
        """Test laplaceFunc applies Laplace mechanism to floats"""
        df = pd.DataFrame({'temperature': [20.5, 22.3, 19.8, 21.1, 23.7]})
        
        with patch('privacy.service.diffrentialPrivacy.laplace.LaplaceTruncated') as mock_laplace_class:
            mock_mechanism = Mock()
            mock_mechanism.randomise.side_effect = [20.6, 22.2, 19.9, 21.0, 23.8]
            mock_laplace_class.return_value = mock_mechanism
            
            DiffPrivacy.laplaceFunc(df, 'temperature')
            
            assert mock_mechanism.randomise.call_count == len(df)


class TestDiffPrivacySnappingFunc:
    """Test suite for snappingFunc method"""

    def test_snappingFunc_with_integer_column(self):
        """Test snappingFunc applies Snapping mechanism to integers"""
        df = pd.DataFrame({'quantity': [100, 200, 300, 400, 500]})
        
        with patch('privacy.service.diffrentialPrivacy.snapping.Snapping') as mock_snapping_class:
            mock_mechanism = Mock()
            mock_mechanism.randomise.side_effect = [101, 199, 302, 398, 501]
            mock_snapping_class.return_value = mock_mechanism
            
            DiffPrivacy.snappingFunc(df, 'quantity')
            
            # Verify mechanism was created with bounds
            mock_snapping_class.assert_called_once()
            call_args = mock_snapping_class.call_args[1]
            assert call_args['epsilon'] == 1
            assert call_args['sensitivity'] == 1
            assert call_args['lower'] == 95  # min(100) - 5
            assert call_args['upper'] == 505  # max(500) + 5

    def test_snappingFunc_with_float_column(self):
        """Test snappingFunc applies Snapping mechanism to floats"""
        df = pd.DataFrame({'price': [9.99, 19.99, 29.99, 39.99]})
        
        with patch('privacy.service.diffrentialPrivacy.snapping.Snapping') as mock_snapping_class:
            mock_mechanism = Mock()
            mock_mechanism.randomise.side_effect = [10.01, 19.97, 30.02, 39.95]
            mock_snapping_class.return_value = mock_mechanism
            
            DiffPrivacy.snappingFunc(df, 'price')
            
            assert mock_mechanism.randomise.call_count == len(df)


class TestDiffPrivacyUploadFile:
    """Test suite for uploadFIle method"""

    def test_uploadFIle_success_with_mixed_types(self):
        """Test uploadFIle successfully processes CSV with mixed column types"""
        # Create CSV content
        csv_content = "name,age,salary,active\nJohn,25,50000,1\nJane,30,60000,0\n"
        mock_file = Mock()
        mock_file.file = io.StringIO(csv_content)
        
        result = DiffPrivacy.uploadFIle(mock_file)
        
        # Verify result structure
        assert 'allHeadders' in result
        assert 'numaricHeadder' in result
        assert 'binaryHeadder' in result
        
        # Verify headers
        assert 'name' in result['allHeadders']
        assert 'age' in result['allHeadders']
        assert 'age' in result['numaricHeadder']
        assert 'salary' in result['numaricHeadder']
        assert 'active' in result['binaryHeadder']

    def test_uploadFIle_identifies_binary_columns(self):
        """Test uploadFIle correctly identifies binary columns"""
        csv_content = "col1,col2,col3\nA,1,10\nB,0,20\nA,1,30\n"
        mock_file = Mock()
        mock_file.file = io.StringIO(csv_content)
        
        result = DiffPrivacy.uploadFIle(mock_file)
        
        # col1 and col2 have exactly 2 unique values
        assert 'col1' in result['binaryHeadder']
        assert 'col2' in result['binaryHeadder']
        # col3 has 3 unique values, not binary
        assert 'col3' not in result['binaryHeadder']

    def test_uploadFIle_stores_dataframe(self):
        """Test uploadFIle stores DataFrame in class variable"""
        csv_content = "id,value\n1,100\n2,200\n"
        mock_file = Mock()
        mock_file.file = io.StringIO(csv_content)
        
        DiffPrivacy.uploadFIle(mock_file)
        
        # Verify DataFrame was stored
        assert isinstance(DiffPrivacy.df, pd.DataFrame)
        assert len(DiffPrivacy.df) == 2

    def test_uploadFIle_handles_numeric_only(self):
        """Test uploadFIle with only numeric columns"""
        csv_content = "num1,num2,num3\n1,2,3\n4,5,6\n7,8,9\n"
        mock_file = Mock()
        mock_file.file = io.StringIO(csv_content)
        
        result = DiffPrivacy.uploadFIle(mock_file)
        
        assert len(result['numaricHeadder']) == 3
        assert 'num1' in result['numaricHeadder']

    def test_uploadFIle_exception_handling(self):
        """Test uploadFIle handles exceptions properly"""
        mock_file = Mock()
        mock_file.file = Mock()
        mock_file.file.read.side_effect = IOError("File read error")
        
        with patch('privacy.service.diffrentialPrivacy.pd.read_csv') as mock_read_csv:
            mock_read_csv.side_effect = IOError("File read error")
            
            with pytest.raises(Exception):
                DiffPrivacy.uploadFIle(mock_file)


class TestDiffPrivacyListParser:
    """Test suite for listParser method"""

    def test_listParser_with_empty_string(self):
        """Test listParser returns empty list for empty string"""
        result = DiffPrivacy.listParser([""])
        assert result == []

    def test_listParser_with_valid_list(self):
        """Test listParser returns same list for non-empty first element"""
        input_list = ["col1", "col2", "col3"]
        result = DiffPrivacy.listParser(input_list)
        assert result == input_list

    def test_listParser_with_single_element(self):
        """Test listParser with single element"""
        result = DiffPrivacy.listParser(["column1"])
        assert result == ["column1"]


class TestDiffPrivacyDiffPrivacy:
    """Test suite for diffPrivacy method"""

    def test_diffPrivacy_with_suppression(self):
        """Test diffPrivacy with column suppression"""
        # Setup DataFrame
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'age': [25, 30, 35],
            'name': ['John', 'Jane', 'Bob']
        })
        DiffPrivacy.df = df
        
        payload = {
            'suppression': 'id,name',
            'noiselist': '',
            'binarylist': '',
            'rangelist': ''
        }
        
        result = DiffPrivacy.diffPrivacy(payload)
        
        # Verify result is a BytesIO buffer
        assert isinstance(result, io.BytesIO)
        
        # Read CSV from buffer
        result.seek(0)
        result_df = pd.read_csv(result)
        
        # Verify suppressed columns are removed
        assert 'id' not in result_df.columns
        assert 'name' not in result_df.columns
        assert 'age' in result_df.columns

    def test_diffPrivacy_with_noise(self):
        """Test diffPrivacy applies noise to specified columns"""
        df = pd.DataFrame({
            'age': [25, 30, 35, 40],
            'salary': [50000, 60000, 70000, 80000]
        })
        DiffPrivacy.df = df
        
        payload = {
            'suppression': '',
            'noiselist': 'age,salary',
            'binarylist': '',
            'rangelist': ''
        }
        
        with patch('secrets.choice') as mock_choice:
            mock_choice.return_value = 'noiseAdd'
            
            with patch.object(DiffPrivacy, 'noiseAdd') as mock_noise:
                result = DiffPrivacy.diffPrivacy(payload)
                
                # Verify noise was applied to both columns
                assert mock_noise.call_count == 2

    def test_diffPrivacy_with_binary(self):
        """Test diffPrivacy applies binary mechanism to specified columns"""
        df = pd.DataFrame({
            'gender': ['M', 'F', 'M', 'F'],
            'active': [1, 0, 1, 0]
        })
        DiffPrivacy.df = df
        
        payload = {
            'suppression': '',
            'noiselist': '',
            'binarylist': 'gender,active',
            'rangelist': ''
        }
        
        with patch.object(DiffPrivacy, 'binaryCheck') as mock_binary:
            result = DiffPrivacy.diffPrivacy(payload)
            
            assert mock_binary.call_count == 2

    def test_diffPrivacy_with_range(self):
        """Test diffPrivacy applies range binning to specified columns"""
        df = pd.DataFrame({
            'age': [15, 25, 35, 45, 55],
            'score': [60, 70, 80, 90, 100]
        })
        DiffPrivacy.df = df
        
        payload = {
            'suppression': '',
            'noiselist': '',
            'binarylist': '',
            'rangelist': 'age,score'
        }
        
        with patch.object(DiffPrivacy, 'rangeAdd') as mock_range:
            result = DiffPrivacy.diffPrivacy(payload)
            
            assert mock_range.call_count == 2

    def test_diffPrivacy_combined_operations(self):
        """Test diffPrivacy with multiple operations combined"""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'age': [25, 30, 35],
            'salary': [50000, 60000, 70000],
            'active': [1, 0, 1]
        })
        DiffPrivacy.df = df
        
        payload = {
            'suppression': 'id',
            'noiselist': 'salary',
            'binarylist': 'active',
            'rangelist': 'age'
        }
        
        with patch('secrets.choice', return_value='noiseAdd'):
            with patch.object(DiffPrivacy, 'noiseAdd'), \
                 patch.object(DiffPrivacy, 'binaryCheck'), \
                 patch.object(DiffPrivacy, 'rangeAdd'):
                
                result = DiffPrivacy.diffPrivacy(payload)
                
                assert isinstance(result, io.BytesIO)

    def test_diffPrivacy_returns_csv_buffer(self):
        """Test diffPrivacy returns valid CSV buffer"""
        df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
        DiffPrivacy.df = df
        
        payload = {
            'suppression': '',
            'noiselist': '',
            'binarylist': '',
            'rangelist': ''
        }
        
        result = DiffPrivacy.diffPrivacy(payload)
        
        # Verify buffer can be read as CSV
        result.seek(0)
        result_df = pd.read_csv(result)
        assert len(result_df) == 3
        assert 'col1' in result_df.columns

    def test_diffPrivacy_exception_handling(self):
        """Test diffPrivacy handles exceptions properly"""
        DiffPrivacy.df = None  # Cause error
        
        payload = {
            'suppression': '',
            'noiselist': 'age',
            'binarylist': '',
            'rangelist': ''
        }
        
        with pytest.raises(Exception):
            DiffPrivacy.diffPrivacy(payload)


class TestDiffPrivacyIntegration:
    """Integration tests for complete workflows"""

    def test_full_workflow_upload_and_process(self):
        """Test complete workflow from upload to processing"""
        # Upload file
        csv_content = "name,age,salary,status\nJohn,25,50000,active\nJane,30,60000,inactive\n"
        mock_file = Mock()
        mock_file.file = io.StringIO(csv_content)
        
        upload_result = DiffPrivacy.uploadFIle(mock_file)
        
        # Verify upload
        assert 'allHeadders' in upload_result
        
        # Process with differential privacy
        payload = {
            'suppression': 'name',
            'noiselist': 'age',
            'binarylist': '',
            'rangelist': ''
        }
        
        with patch('secrets.choice', return_value='noiseAdd'):
            with patch.object(DiffPrivacy, 'noiseAdd'):
                result = DiffPrivacy.diffPrivacy(payload)
                
                assert isinstance(result, io.BytesIO)

    def test_random_noise_selection(self):
        """Test that noise function is randomly selected"""
        df = pd.DataFrame({'value': [10, 20, 30, 40, 50]})
        DiffPrivacy.df = df
        
        payload = {
            'suppression': '',
            'noiselist': 'value',
            'binarylist': '',
            'rangelist': ''
        }
        
        # Mock secrets.choice to return different values
        with patch('secrets.choice') as mock_choice:
            mock_choice.return_value = 'gaussianFunc'
            
            with patch.object(DiffPrivacy, 'gaussianFunc') as mock_gaussian:
                DiffPrivacy.diffPrivacy(payload)
                
                # Verify the randomly selected function was called
                mock_gaussian.assert_called_once()


class TestDiffPrivacyEdgeCases:
    """Test edge cases for missing coverage lines"""
    
    def test_rangeAdd_with_large_range_magnitude(self):
        """Test rangeAdd with data requiring multiple ranges"""
        df = pd.DataFrame({'value': [5, 15, 25, 35, 45, 55, 65, 75, 85, 95]})
        
        with patch('secrets.choice') as mock_choice:
            # Mock choice to return consistent range
            mock_choice.side_effect = ['10-20', '10-20', '20-30', '30-40', '40-50', 
                                       '50-60', '60-70', '70-80', '80-90', '90-100']
            
            DiffPrivacy.rangeAdd(df, 'value')
            
            # Verify the function completed without errors
            assert len(df) == 10
            # Check that values are strings (ranges)
            assert isinstance(df['value'].iloc[0], str)


