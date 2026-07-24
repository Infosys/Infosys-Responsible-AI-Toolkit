"""
Comprehensive test suite for Video_service.py

Tests cover:
- frameAnonymization: Frame processing with PII detection and anonymization
- videoPrivacy: Full video processing pipeline with chunking and threading
- Error handling and edge cases
- File cleanup and resource management
"""

import pytest
import base64
import os
import tempfile
import numpy as np
import cv2
import asyncio
from PIL import Image
from unittest.mock import Mock, MagicMock, patch, AsyncMock, call
from io import BytesIO
from privacy.service.Video_service import VideoService
from privacy.service.imagePrivacy import AttributeDict


class TestVideoServiceFrameAnonymization:
    """Tests for VideoService.frameAnonymization static method"""

    @patch('privacy.service.Video_service.ImagePrivacy.image_anonymize')
    @patch('privacy.service.Video_service.Image.fromarray')
    @patch('privacy.service.Video_service.cv2.cvtColor')
    @patch('privacy.service.Video_service.cv2.imdecode')
    @patch('privacy.service.Video_service.os.path.exists')
    @patch('privacy.service.Video_service.os.remove')
    @patch('privacy.service.Video_service.os.makedirs')
    def test_frame_anonymization_success(self, mock_makedirs, mock_remove, mock_exists, 
                                        mock_imdecode, mock_cvtColor, mock_fromarray, 
                                        mock_image_anonymize):
        """Test successful frame anonymization"""
        # Create a sample frame
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Mock the anonymization result
        anonymized_image_b64 = base64.b64encode(b'anonymized_image_data').decode('utf-8')
        mock_image_anonymize.return_value = anonymized_image_b64
        
        # Mock cv2 operations
        mock_cvtColor.return_value = frame
        mock_pil_image = MagicMock()
        mock_fromarray.return_value = mock_pil_image
        
        # Mock decoded frame
        decoded_frame = np.ones((100, 100, 3), dtype=np.uint8)
        mock_imdecode.return_value = decoded_frame
        
        # Mock file operations
        mock_exists.return_value = True
        
        # Prepare test inputs
        payload = AttributeDict({
            "nlp_engine_name": "spacy",
            "pii_entity": "PERSON,EMAIL"
        })
        results_dict = {}
        frame_index = 0
        main_request_id = "test_request_123"
        video_request_temp_root_path = "/tmp/test_video"
        
        # Execute
        VideoService.frameAnonymization(
            payload, frame, frame_index, results_dict, 
            main_request_id, video_request_temp_root_path
        )
        
        # Verify
        assert frame_index in results_dict
        assert results_dict[frame_index] is not None
        assert np.array_equal(results_dict[frame_index], decoded_frame)
        mock_image_anonymize.assert_called_once()
        mock_remove.assert_called_once()

    @patch('privacy.service.Video_service.ImagePrivacy.image_anonymize')
    @patch('privacy.service.Video_service.Image.fromarray')
    @patch('privacy.service.Video_service.cv2.cvtColor')
    @patch('privacy.service.Video_service.cv2.imdecode')
    @patch('privacy.service.Video_service.os.path.exists')
    @patch('privacy.service.Video_service.os.remove')
    @patch('privacy.service.Video_service.os.makedirs')
    def test_frame_anonymization_decode_failure(self, mock_makedirs, mock_remove, mock_exists,
                                               mock_imdecode, mock_cvtColor, mock_fromarray,
                                               mock_image_anonymize):
        """Test frame anonymization when decode fails"""
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        anonymized_image_b64 = base64.b64encode(b'invalid_image_data').decode('utf-8')
        mock_image_anonymize.return_value = anonymized_image_b64
        mock_cvtColor.return_value = frame
        mock_pil_image = MagicMock()
        mock_fromarray.return_value = mock_pil_image
        
        # Simulate decode failure
        mock_imdecode.return_value = None
        mock_exists.return_value = True
        
        payload = AttributeDict({"nlp_engine_name": "spacy"})
        results_dict = {}
        frame_index = 5
        
        VideoService.frameAnonymization(
            payload, frame, frame_index, results_dict,
            "test_req", "/tmp/test"
        )
        
        # Verify that None is stored for failed frame
        assert frame_index in results_dict
        assert results_dict[frame_index] is None

    @patch('privacy.service.Video_service.ImagePrivacy.image_anonymize')
    @patch('privacy.service.Video_service.Image.fromarray')
    @patch('privacy.service.Video_service.cv2.cvtColor')
    @patch('privacy.service.Video_service.os.path.exists')
    @patch('privacy.service.Video_service.os.remove')
    @patch('privacy.service.Video_service.os.makedirs')
    def test_frame_anonymization_exception_handling(self, mock_makedirs, mock_remove, 
                                                   mock_exists, mock_cvtColor, 
                                                   mock_fromarray, mock_image_anonymize):
        """Test exception handling in frame anonymization"""
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Simulate exception during anonymization
        mock_image_anonymize.side_effect = Exception("Anonymization error")
        mock_cvtColor.return_value = frame
        mock_exists.return_value = True
        
        payload = AttributeDict({})
        results_dict = {}
        frame_index = 10
        
        VideoService.frameAnonymization(
            payload, frame, frame_index, results_dict,
            "test_req", "/tmp/test"
        )
        
        # Verify that None is stored when exception occurs
        assert frame_index in results_dict
        assert results_dict[frame_index] is None

    @patch('privacy.service.Video_service.ImagePrivacy.image_anonymize')
    @patch('privacy.service.Video_service.Image.fromarray')
    @patch('privacy.service.Video_service.cv2.cvtColor')
    @patch('privacy.service.Video_service.cv2.imdecode')
    @patch('privacy.service.Video_service.os.path.exists')
    @patch('privacy.service.Video_service.os.remove')
    @patch('privacy.service.Video_service.os.makedirs')
    def test_frame_anonymization_file_cleanup_error(self, mock_makedirs, mock_remove, 
                                                    mock_exists, mock_imdecode, mock_cvtColor,
                                                    mock_fromarray, mock_image_anonymize):
        """Test frame anonymization when file cleanup fails"""
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        anonymized_image_b64 = base64.b64encode(b'anonymized_data').decode('utf-8')
        mock_image_anonymize.return_value = anonymized_image_b64
        mock_cvtColor.return_value = frame
        mock_pil_image = MagicMock()
        mock_fromarray.return_value = mock_pil_image
        decoded_frame = np.ones((100, 100, 3), dtype=np.uint8)
        mock_imdecode.return_value = decoded_frame
        mock_exists.return_value = True
        
        # Simulate file cleanup error
        mock_remove.side_effect = OSError("Permission denied")
        
        payload = AttributeDict({})
        results_dict = {}
        frame_index = 3
        
        # Should not raise exception despite cleanup error
        VideoService.frameAnonymization(
            payload, frame, frame_index, results_dict,
            "test_req", "/tmp/test"
        )
        
        assert frame_index in results_dict
        assert results_dict[frame_index] is not None


class TestVideoServiceVideoPrivacy:
    """Tests for VideoService.videoPrivacy async method"""

    @patch('privacy.service.Video_service.os.path.exists', return_value=True)
    @patch('privacy.service.Video_service.shutil.rmtree')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    @patch('privacy.service.Video_service.cv2.VideoWriter')
    @patch('privacy.service.Video_service.VideoService.frameAnonymization')
    def test_video_privacy_basic_success(self, mock_frame_anon, mock_video_writer,
                                              mock_video_capture, mock_makedirs, mock_rmtree, mock_exists):
        """Test basic successful video anonymization"""
        # Create mock video file
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = "test_video.mp4"
        mock_upload_file.read = AsyncMock(return_value=b'fake_video_data')
        
        # Mock VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 640,
            cv2.CAP_PROP_FRAME_HEIGHT: 480,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 90
        }.get(prop, 0)
        
        # Mock frame reading - 3 frames total then end
        from itertools import chain
        frame1 = np.zeros((480, 640, 3), dtype=np.uint8)
        frame2 = np.ones((480, 640, 3), dtype=np.uint8) * 128
        frame3 = np.ones((480, 640, 3), dtype=np.uint8) * 255
        
        # Use chain to provide frames then infinite (False, None)
        mock_cap.read.side_effect = chain(
            [(True, frame1), (True, frame2), (True, frame3)],
            [(False, None)] * 1000  # Provide enough (False, None) to handle any reads
        )
        mock_video_capture.return_value = mock_cap
        
        # Mock VideoWriter
        mock_writer = MagicMock()
        mock_writer.isOpened.return_value = True
        mock_video_writer.return_value = mock_writer
        
        # Create payload
        payload = {
            "video": mock_upload_file,
            "nlp_engine_name": "spacy",
            "max_threads": 2
        }
        
        # Mock frameAnonymization to populate results
        def mock_anonymize(payload, frame, indx, results_dict, req_id, temp_path):
            results_dict[indx] = frame.copy()
        
        mock_frame_anon.side_effect = mock_anonymize
        
        # Mock file operations
        with patch('builtins.open', create=True) as mock_open:
            mock_file_write = MagicMock()
            mock_file_read = MagicMock()
            mock_file_read.read.return_value = b'processed_video_data'
            
            def open_side_effect(filename, mode, *args, **kwargs):
                if 'wb' in mode:
                    mock_file_write.__enter__ = Mock(return_value=mock_file_write)
                    mock_file_write.__exit__ = Mock(return_value=None)
                    return mock_file_write
                elif 'rb' in mode:
                    mock_file_read.__enter__ = Mock(return_value=mock_file_read)
                    mock_file_read.__exit__ = Mock(return_value=None)
                    return mock_file_read
                return MagicMock()
            
            mock_open.side_effect = open_side_effect
            
            # Execute
            service = VideoService()
            result = asyncio.run(service.videoPrivacy(payload))
            
            # Verify
            assert result is not None
            assert isinstance(result, str)
            # Verify it's valid base64
            decoded = base64.b64decode(result)
            assert decoded == b'processed_video_data'
            
            # Verify video operations
            mock_cap.release.assert_called()
            mock_writer.release.assert_called()
            mock_rmtree.assert_called_once()

    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    def test_video_privacy_cannot_open_video(self, mock_video_capture, mock_makedirs):
        """Test when video file cannot be opened"""
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = "test_video.mp4"
        mock_upload_file.read = AsyncMock(return_value=b'fake_video_data')
        
        # Mock VideoCapture that fails to open
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap
        
        payload = {"video": mock_upload_file}
        
        with patch('builtins.open', create=True):
            service = VideoService()
            with pytest.raises(Exception, match="OpenCV could not open video file"):
                asyncio.run(service.videoPrivacy(payload))

    @patch('privacy.service.Video_service.shutil.rmtree')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    @patch('privacy.service.Video_service.cv2.VideoWriter')
    def test_video_privacy_cannot_open_writer(self, mock_video_writer, mock_video_capture,
                                                   mock_makedirs, mock_rmtree):
        """Test when VideoWriter cannot be opened"""
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = "test_video.mp4"
        mock_upload_file.read = AsyncMock(return_value=b'fake_video_data')
        
        # Mock VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 640,
            cv2.CAP_PROP_FRAME_HEIGHT: 480,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 30
        }.get(prop, 0)
        mock_video_capture.return_value = mock_cap
        
        # Mock VideoWriter that fails to open
        mock_writer = MagicMock()
        mock_writer.isOpened.return_value = False
        mock_video_writer.return_value = mock_writer
        
        payload = {"video": mock_upload_file}
        
        with patch('builtins.open', create=True):
            service = VideoService()
            with pytest.raises(Exception, match="OpenCV could not open VideoWriter"):
                asyncio.run(service.videoPrivacy(payload))

    @patch('privacy.service.Video_service.shutil.rmtree')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    @patch('privacy.service.Video_service.cv2.VideoWriter')
    @patch('privacy.service.Video_service.VideoService.frameAnonymization')
    def test_video_privacy_with_zero_fps(self, mock_frame_anon, mock_video_writer,
                                               mock_video_capture, mock_makedirs, mock_rmtree):
        """Test video privacy with zero or invalid FPS (uses default)"""
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = "test_video.mp4"
        mock_upload_file.read = AsyncMock(return_value=b'fake_video_data')
        
        # Mock VideoCapture with 0 FPS
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 640,
            cv2.CAP_PROP_FRAME_HEIGHT: 480,
            cv2.CAP_PROP_FPS: 0,  # Invalid FPS
            cv2.CAP_PROP_FRAME_COUNT: 30
        }.get(prop, 0)
        
        from itertools import chain
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cap.read.side_effect = chain([(True, frame)], [(False, None)] * 1000)
        mock_video_capture.return_value = mock_cap
        
        # Mock VideoWriter
        mock_writer = MagicMock()
        mock_writer.isOpened.return_value = True
        mock_video_writer.return_value = mock_writer
        
        payload = {"video": mock_upload_file, "max_threads": 1}
        
        def mock_anonymize(payload, frame, indx, results_dict, req_id, temp_path):
            results_dict[indx] = frame.copy()
        
        mock_frame_anon.side_effect = mock_anonymize
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file_write = MagicMock()
            mock_file_read = MagicMock()
            mock_file_read.read.return_value = b'processed_video_data'
            
            def open_side_effect(filename, mode, *args, **kwargs):
                if 'wb' in mode:
                    mock_file_write.__enter__ = Mock(return_value=mock_file_write)
                    mock_file_write.__exit__ = Mock(return_value=None)
                    return mock_file_write
                elif 'rb' in mode:
                    mock_file_read.__enter__ = Mock(return_value=mock_file_read)
                    mock_file_read.__exit__ = Mock(return_value=None)
                    return mock_file_read
                return MagicMock()
            
            mock_open.side_effect = open_side_effect
            
            service = VideoService()
            result = asyncio.run(service.videoPrivacy(payload))
            
            assert result is not None
            # Verify VideoWriter was called with default FPS (30.0)
            assert mock_video_writer.call_args[0][2] == 30.0

    @patch('privacy.service.Video_service.shutil.rmtree')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    @patch('privacy.service.Video_service.cv2.VideoWriter')
    @patch('privacy.service.Video_service.VideoService.frameAnonymization')
    def test_video_privacy_with_failed_frame_anonymization(self, mock_frame_anon,
                                                                mock_video_writer,
                                                                mock_video_capture,
                                                                mock_makedirs, mock_rmtree):
        """Test video privacy when some frame anonymizations fail"""
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = "test_video.mp4"
        mock_upload_file.read = AsyncMock(return_value=b'fake_video_data')
        
        # Mock VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 640,
            cv2.CAP_PROP_FRAME_HEIGHT: 480,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 60
        }.get(prop, 0)
        
        from itertools import chain
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cap.read.side_effect = chain([(True, frame.copy()) for _ in range(5)], [(False, None)] * 1000)
        mock_video_capture.return_value = mock_cap
        
        # Mock VideoWriter
        mock_writer = MagicMock()
        mock_writer.isOpened.return_value = True
        mock_video_writer.return_value = mock_writer
        
        payload = {"video": mock_upload_file, "max_threads": 2}
        
        # Mock frame anonymization with some failures
        def mock_anonymize(payload, frame, indx, results_dict, req_id, temp_path):
            if indx % 2 == 0:
                results_dict[indx] = frame.copy()  # Success
            else:
                results_dict[indx] = None  # Failure
        
        mock_frame_anon.side_effect = mock_anonymize
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file_write = MagicMock()
            mock_file_read = MagicMock()
            mock_file_read.read.return_value = b'processed_video_data'
            
            def open_side_effect(filename, mode, *args, **kwargs):
                if 'wb' in mode:
                    mock_file_write.__enter__ = Mock(return_value=mock_file_write)
                    mock_file_write.__exit__ = Mock(return_value=None)
                    return mock_file_write
                elif 'rb' in mode:
                    mock_file_read.__enter__ = Mock(return_value=mock_file_read)
                    mock_file_read.__exit__ = Mock(return_value=None)
                    return mock_file_read
                return MagicMock()
            
            mock_open.side_effect = open_side_effect
            
            service = VideoService()
            result = asyncio.run(service.videoPrivacy(payload))
            
            # Should still complete successfully
            assert result is not None
            # Verify writer was called for all frames
            assert mock_writer.write.call_count == 5

    @patch('privacy.service.Video_service.shutil.rmtree')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    def test_video_privacy_exception_in_processing(self, mock_video_capture,
                                                        mock_makedirs, mock_rmtree):
        """Test exception handling during video processing"""
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = "test_video.mp4"
        mock_upload_file.read = AsyncMock(return_value=b'fake_video_data')
        
        # Mock VideoCapture that throws exception
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = Exception("Unexpected error")
        mock_video_capture.return_value = mock_cap
        
        payload = {"video": mock_upload_file}
        
        with patch('builtins.open', create=True):
            service = VideoService()
            with pytest.raises(Exception, match="Unexpected error"):
                asyncio.run(service.videoPrivacy(payload))
            
            # Verify cleanup was attempted
            mock_cap.release.assert_called()

    @patch('privacy.service.Video_service.os.path.exists', return_value=True)
    @patch('privacy.service.Video_service.shutil.rmtree')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    @patch('privacy.service.Video_service.cv2.VideoWriter')
    @patch('privacy.service.Video_service.VideoService.frameAnonymization')
    def test_video_privacy_cleanup_on_success(self, mock_frame_anon, mock_video_writer,
                                                   mock_video_capture, mock_makedirs, mock_rmtree, mock_exists):
        """Test that temporary files are cleaned up after success"""
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = "test_video.mp4"
        mock_upload_file.read = AsyncMock(return_value=b'fake_video_data')
        
        # Mock VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 640,
            cv2.CAP_PROP_FRAME_HEIGHT: 480,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 30
        }.get(prop, 0)
        
        from itertools import chain
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cap.read.side_effect = chain([(True, frame)], [(False, None)] * 1000)
        mock_video_capture.return_value = mock_cap
        
        # Mock VideoWriter
        mock_writer = MagicMock()
        mock_writer.isOpened.return_value = True
        mock_video_writer.return_value = mock_writer
        
        payload = {"video": mock_upload_file}
        
        def mock_anonymize(payload, frame, indx, results_dict, req_id, temp_path):
            results_dict[indx] = frame.copy()
        
        mock_frame_anon.side_effect = mock_anonymize
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file_write = MagicMock()
            mock_file_read = MagicMock()
            mock_file_read.read.return_value = b'processed_video_data'
            
            def open_side_effect(filename, mode, *args, **kwargs):
                if 'wb' in mode:
                    mock_file_write.__enter__ = Mock(return_value=mock_file_write)
                    mock_file_write.__exit__ = Mock(return_value=None)
                    return mock_file_write
                elif 'rb' in mode:
                    mock_file_read.__enter__ = Mock(return_value=mock_file_read)
                    mock_file_read.__exit__ = Mock(return_value=None)
                    return mock_file_read
                return MagicMock()
            
            mock_open.side_effect = open_side_effect
            
            service = VideoService()
            result = asyncio.run(service.videoPrivacy(payload))
            
            # Verify cleanup was called
            mock_rmtree.assert_called_once()

    @patch('privacy.service.Video_service.os.path.exists', return_value=True)
    @patch('privacy.service.Video_service.shutil.rmtree')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    def test_video_privacy_cleanup_error_handling(self, mock_video_capture,
                                                       mock_makedirs, mock_rmtree, mock_exists):
        """Test that cleanup errors are logged but don't prevent exception propagation"""
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = "test_video.mp4"
        mock_upload_file.read = AsyncMock(return_value=b'fake_video_data')
        
        # Mock VideoCapture that fails
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap
        
        # Make cleanup fail
        mock_rmtree.side_effect = OSError("Cleanup failed")
        
        payload = {"video": mock_upload_file}
        
        with patch('builtins.open', create=True):
            service = VideoService()
            with pytest.raises(Exception, match="OpenCV could not open video file"):
                asyncio.run(service.videoPrivacy(payload))
            
            # Verify cleanup was attempted despite error
            mock_rmtree.assert_called_once()

    @patch('privacy.service.Video_service.shutil.rmtree')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    @patch('privacy.service.Video_service.cv2.VideoWriter')
    @patch('privacy.service.Video_service.VideoService.frameAnonymization')
    def test_video_privacy_multiple_chunks(self, mock_frame_anon, mock_video_writer,
                                                 mock_video_capture, mock_makedirs, mock_rmtree):
        """Test video processing with multiple chunks"""
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = "long_video.mp4"
        mock_upload_file.read = AsyncMock(return_value=b'fake_video_data')
        
        # Mock VideoCapture with many frames
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 320,
            cv2.CAP_PROP_FRAME_HEIGHT: 240,
            cv2.CAP_PROP_FPS: 10.0,  # Low FPS for easier testing
            cv2.CAP_PROP_FRAME_COUNT: 100
        }.get(prop, 0)
        
        # Generate 30 frames (should create multiple chunks at 10 FPS * 2 seconds = 20 frames per chunk)
        from itertools import chain
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        mock_cap.read.side_effect = chain([(True, frame.copy()) for _ in range(30)], [(False, None)] * 1000)
        mock_video_capture.return_value = mock_cap
        
        # Mock VideoWriter
        mock_writer = MagicMock()
        mock_writer.isOpened.return_value = True
        mock_video_writer.return_value = mock_writer
        
        payload = {"video": mock_upload_file, "max_threads": 3}
        
        def mock_anonymize(payload, frame, indx, results_dict, req_id, temp_path):
            results_dict[indx] = frame.copy()
        
        mock_frame_anon.side_effect = mock_anonymize
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file_write = MagicMock()
            mock_file_read = MagicMock()
            mock_file_read.read.return_value = b'processed_video_data'
            
            def open_side_effect(filename, mode, *args, **kwargs):
                if 'wb' in mode:
                    mock_file_write.__enter__ = Mock(return_value=mock_file_write)
                    mock_file_write.__exit__ = Mock(return_value=None)
                    return mock_file_write
                elif 'rb' in mode:
                    mock_file_read.__enter__ = Mock(return_value=mock_file_read)
                    mock_file_read.__exit__ = Mock(return_value=None)
                    return mock_file_read
                return MagicMock()
            
            mock_open.side_effect = open_side_effect
            
            service = VideoService()
            result = asyncio.run(service.videoPrivacy(payload))
            
            assert result is not None
            # Verify all 30 frames were written
            assert mock_writer.write.call_count == 30

    @patch('privacy.service.Video_service.shutil.rmtree')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    @patch('privacy.service.Video_service.cv2.VideoWriter')
    @patch('privacy.service.Video_service.VideoService.frameAnonymization')
    def test_video_privacy_custom_max_threads(self, mock_frame_anon, mock_video_writer,
                                                   mock_video_capture, mock_makedirs, mock_rmtree):
        """Test video privacy with custom max_threads parameter"""
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = "test_video.mp4"
        mock_upload_file.read = AsyncMock(return_value=b'fake_video_data')
        
        # Mock VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 640,
            cv2.CAP_PROP_FRAME_HEIGHT: 480,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 30
        }.get(prop, 0)
        
        from itertools import chain
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cap.read.side_effect = chain([(True, frame.copy()) for _ in range(10)], [(False, None)] * 1000)
        mock_video_capture.return_value = mock_cap
        
        # Mock VideoWriter
        mock_writer = MagicMock()
        mock_writer.isOpened.return_value = True
        mock_video_writer.return_value = mock_writer
        
        # Test with custom max_threads
        payload = {"video": mock_upload_file, "max_threads": 10}
        
        def mock_anonymize(payload, frame, indx, results_dict, req_id, temp_path):
            results_dict[indx] = frame.copy()
        
        mock_frame_anon.side_effect = mock_anonymize
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file_write = MagicMock()
            mock_file_read = MagicMock()
            mock_file_read.read.return_value = b'processed_video_data'
            
            def open_side_effect(filename, mode, *args, **kwargs):
                if 'wb' in mode:
                    mock_file_write.__enter__ = Mock(return_value=mock_file_write)
                    mock_file_write.__exit__ = Mock(return_value=None)
                    return mock_file_write
                elif 'rb' in mode:
                    mock_file_read.__enter__ = Mock(return_value=mock_file_read)
                    mock_file_read.__exit__ = Mock(return_value=None)
                    return mock_file_read
                return MagicMock()
            
            mock_open.side_effect = open_side_effect
            
            service = VideoService()
            result = asyncio.run(service.videoPrivacy(payload))
            
            assert result is not None

    @patch('privacy.service.Video_service.shutil.rmtree')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    @patch('privacy.service.Video_service.cv2.VideoWriter')
    @patch('privacy.service.Video_service.VideoService.frameAnonymization')
    @patch('privacy.service.Video_service.log')
    def test_video_privacy_with_thread_exception(self, mock_log, mock_frame_anon, mock_video_writer,
                                                 mock_video_capture, mock_makedirs, mock_rmtree):
        """Test video privacy when thread execution fails with exception"""
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = "test_video.mp4"
        mock_upload_file.read = AsyncMock(return_value=b'fake_video_data')
        
        # Mock VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 640,
            cv2.CAP_PROP_FRAME_HEIGHT: 480,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 5
        }.get(prop, 0)
        
        from itertools import chain
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cap.read.side_effect = chain([(True, frame.copy()) for _ in range(5)], [(False, None)] * 1000)
        mock_video_capture.return_value = mock_cap
        
        # Mock VideoWriter
        mock_writer = MagicMock()
        mock_writer.isOpened.return_value = True
        mock_video_writer.return_value = mock_writer
        
        payload = {"video": mock_upload_file, "max_threads": 2}
        
        # Make frameAnonymization raise an exception for some frames
        def mock_anonymize_with_failure(payload, frame, indx, results_dict, req_id, temp_path):
            if indx == 2:  # Simulate failure on frame 2
                raise RuntimeError(f"Simulated anonymization failure for frame {indx}")
            results_dict[indx] = frame.copy()
        
        mock_frame_anon.side_effect = mock_anonymize_with_failure
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file_write = MagicMock()
            mock_file_read = MagicMock()
            mock_file_read.read.return_value = b'processed_video_data'
            
            def open_side_effect(filename, mode, *args, **kwargs):
                if 'wb' in mode:
                    mock_file_write.__enter__ = Mock(return_value=mock_file_write)
                    mock_file_write.__exit__ = Mock(return_value=None)
                    return mock_file_write
                elif 'rb' in mode:
                    mock_file_read.__enter__ = Mock(return_value=mock_file_read)
                    mock_file_read.__exit__ = Mock(return_value=None)
                    return mock_file_read
                return MagicMock()
            
            mock_open.side_effect = open_side_effect
            
            service = VideoService()
            result = asyncio.run(service.videoPrivacy(payload))
            
            # Verify that the code handled the exception gracefully
            # (mock_log.error should have been called for the failed frame)
            # Result should still be generated
            assert result is not None

    def test_video_service_path_creation(self):
        """Test that default video path is created"""
        from privacy.service.Video_service import path
        
        
        # The module should have created the path on import
        assert path == "../video/"
        # In actual execution, os.makedirs would create this, but in tests it's mocked


