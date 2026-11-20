"""
Comprehensive test suite for Video_service.py

Tests cover:
- frame_anonymization: Frame processing with PII detection and anonymization
- video_privacy: Full video processing pipeline with chunking and threading
- Error handling and edge cases
- File cleanup and resource management
"""

import pytest
import base64
import os
import numpy as np
from unittest.mock import Mock, MagicMock, patch, AsyncMock, call
import cv2

# Standard imports following project convention
from privacy.service.Video_service import VideoService
from privacy.service.imagePrivacy import AttributeDict


class TestVideoServiceframe_anonymization:
    """Tests for VideoService.frame_anonymization static method"""

    @patch('privacy.service.Video_service.request_id_var')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.os.remove')
    @patch('privacy.service.Video_service.os.path.exists')
    @patch('privacy.service.Video_service.cv2.imdecode')
    @patch('privacy.service.Video_service.cv2.cvtColor')
    @patch('privacy.service.Video_service.Image.fromarray')
    @patch('privacy.service.Video_service.ImagePrivacy.image_anonymize')
    def test_frame_anonymization_success(
        self, mock_image_anonymize, mock_fromarray, mock_cvtColor,
        mock_imdecode, mock_exists, mock_remove, mock_makedirs, mock_request_id
    ):
        """Test successful frame_anonymization"""
        # Setup
        payload = {'entity_types': ['PERSON']}
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        indx = 0
        results_dict = {}
        main_request_id = 'test-main-id'
        video_temp_path = '/tmp/video_temp'
        
        # Mock setup - token needs to be truthy for reset to be called
        mock_token = object()  # truthy object
        mock_request_id.set.return_value = mock_token
        
        mock_pil_image = MagicMock()
        mock_fromarray.return_value = mock_pil_image
        
        # Mock anonymized image return
        processed_frame = np.ones((480, 640, 3), dtype=np.uint8)
        mock_imdecode.return_value = processed_frame
        
        encoded_img = base64.b64encode(b'processed_image_data').decode('utf-8')
        mock_image_anonymize.return_value = encoded_img
        
        mock_exists.return_value = True
        
        # Execute
        VideoService.frame_anonymization(
            payload, frame, indx, results_dict, main_request_id, video_temp_path
        )
        
        # Assert
        assert indx in results_dict
        assert results_dict[indx] is not None
        # Verify the processed frame matches (handle both numpy arrays and potential mocks)
        result_frame = results_dict[indx]
        if hasattr(result_frame, '__array__') and hasattr(processed_frame, '__array__'):
            assert (result_frame == processed_frame).all(), "Processed frame doesn't match"
        else:
            assert result_frame is processed_frame or result_frame == processed_frame
        mock_makedirs.assert_called_once()
        mock_pil_image.save.assert_called_once()
        mock_image_anonymize.assert_called_once()
        mock_remove.assert_called_once()

    @patch('privacy.service.Video_service.request_id_var')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.os.remove')
    @patch('privacy.service.Video_service.os.path.exists')
    @patch('privacy.service.Video_service.cv2.imdecode')
    @patch('privacy.service.Video_service.cv2.cvtColor')
    @patch('privacy.service.Video_service.Image.fromarray')
    @patch('privacy.service.Video_service.ImagePrivacy.image_anonymize')
    def test_frame_anonymization_decode_failure(
        self, mock_image_anonymize, mock_fromarray, mock_cvtColor,
        mock_imdecode, mock_exists, mock_remove, mock_makedirs, mock_request_id
    ):
        """Test frame_anonymization when cv2.imdecode fails"""
        # Setup
        payload = {'entity_types': ['PERSON']}
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        indx = 1
        results_dict = {}
        main_request_id = 'test-id'
        video_temp_path = '/tmp/test'
        
        mock_token = object()  # truthy object
        mock_request_id.set.return_value = mock_token
        
        mock_pil_image = MagicMock()
        mock_fromarray.return_value = mock_pil_image
        
        encoded_img = base64.b64encode(b'data').decode('utf-8')
        mock_image_anonymize.return_value = encoded_img
        mock_imdecode.return_value = None  # Decode failure
        mock_exists.return_value = True
        
        # Execute
        VideoService.frame_anonymization(
            payload, frame, indx, results_dict, main_request_id, video_temp_path
        )
        
        # Assert
        assert indx in results_dict
        assert results_dict[indx] is None
        mock_remove.assert_called_once()

    @patch('privacy.service.Video_service.request_id_var')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.os.remove')
    @patch('privacy.service.Video_service.os.path.exists')
    @patch('privacy.service.Video_service.cv2.cvtColor')
    @patch('privacy.service.Video_service.Image.fromarray')
    @patch('privacy.service.Video_service.ImagePrivacy.image_anonymize')
    def test_frame_anonymization_exception_handling(
        self, mock_image_anonymize, mock_fromarray, mock_cvtColor,
        mock_exists, mock_remove, mock_makedirs, mock_request_id
    ):
        """Test frame_anonymization handles exceptions gracefully"""
        # Setup
        payload = {'entity_types': ['PERSON']}
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        indx = 2
        results_dict = {}
        main_request_id = 'test-id'
        video_temp_path = '/tmp/test'
        
        mock_token = object()  # truthy object
        mock_request_id.set.return_value = mock_token
        
        # Simulate exception during processing
        mock_image_anonymize.side_effect = Exception("Anonymization failed")
        mock_exists.return_value = True
        
        # Execute
        VideoService.frame_anonymization(
            payload, frame, indx, results_dict, main_request_id, video_temp_path
        )
        
        # Assert
        assert indx in results_dict
        assert results_dict[indx] is None
        mock_remove.assert_called_once()

    @patch('privacy.service.Video_service.request_id_var')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.os.remove')
    @patch('privacy.service.Video_service.os.path.exists')
    @patch('privacy.service.Video_service.cv2.imdecode')
    @patch('privacy.service.Video_service.cv2.cvtColor')
    @patch('privacy.service.Video_service.Image.fromarray')
    @patch('privacy.service.Video_service.ImagePrivacy.image_anonymize')
    def test_frame_anonymization_file_cleanup_error(
        self, mock_image_anonymize, mock_fromarray, mock_cvtColor,
        mock_imdecode, mock_exists, mock_remove, mock_makedirs, mock_request_id
    ):
        """Test frame_anonymization continues despite cleanup errors"""
        # Setup
        payload = {'entity_types': ['PERSON']}
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        indx = 3
        results_dict = {}
        
        mock_token = object()  # truthy object
        mock_request_id.set.return_value = mock_token
        
        mock_pil_image = MagicMock()
        mock_fromarray.return_value = mock_pil_image
        
        processed_frame = np.ones((480, 640, 3), dtype=np.uint8)
        mock_imdecode.return_value = processed_frame
        
        encoded_img = base64.b64encode(b'data').decode('utf-8')
        mock_image_anonymize.return_value = encoded_img
        
        mock_exists.return_value = True
        mock_remove.side_effect = OSError("Permission denied")
        
        # Execute - should not raise exception
        VideoService.frame_anonymization(
            payload, frame, indx, results_dict, 'test-id', '/tmp/test'
        )
        
        # Assert - processing should succeed despite cleanup error
        assert indx in results_dict
        assert results_dict[indx] is not None


class TestVideoServicevideo_privacy:
    """Tests for VideoService.video_privacy async method"""

    @pytest.mark.asyncio
    @patch('privacy.service.Video_service.shutil.rmtree')
    @patch('privacy.service.Video_service.os.path.exists')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.request_id_var')
    @patch('privacy.service.Video_service.cv2.VideoWriter')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    @patch('privacy.service.Video_service.VideoService.frame_anonymization')
    async def test_video_privacy_basic_success(
        self, mock_frame_anon, mock_video_capture, mock_video_writer,
        mock_request_id, mock_makedirs, mock_exists, mock_rmtree
    ):
        """Test basic successful video_privacy processing"""
        # Setup
        service = VideoService()
        
        mock_token = object()  # truthy object
        mock_request_id.set.return_value = mock_token
        
        # Create mock video file
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = 'test_video.mp4'
        test_video_data = b'fake_video_data'
        mock_upload_file.read = AsyncMock(return_value=test_video_data)
        
        payload = {
            'video': mock_upload_file,
            'entity_types': ['PERSON'],
            'max_threads': 4
        }
        
        # Mock VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 640,
            cv2.CAP_PROP_FRAME_HEIGHT: 480,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 10
        }.get(prop, 0)
        
        # Use generator to provide infinite False after frames
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        def read_side_effect():
            for _ in range(10):
                yield (True, frame)
            while True:
                yield (False, None)
        
        mock_cap.read = MagicMock(side_effect=read_side_effect())
        mock_video_capture.return_value = mock_cap
        
        # Mock VideoWriter
        mock_writer = MagicMock()
        mock_writer.isOpened.return_value = True
        mock_video_writer.return_value = mock_writer
        
        mock_exists.return_value = True
        
        # Mock frame anonymization
        def mock_anon_side_effect(payload, frame, idx, results_dict, req_id, temp_path):
            results_dict[idx] = np.ones((480, 640, 3), dtype=np.uint8)
        
        mock_frame_anon.side_effect = mock_anon_side_effect
        
        # Mock open for file operations
        with patch('builtins.open', create=True) as mock_open:
            def open_side_effect(path, mode='r', *args, **kwargs):
                mock_file = MagicMock()
                if 'w' in mode or 'a' in mode:
                    # For write operations, return a mock that does nothing
                    mock_file.write = MagicMock()
                    mock_file.__enter__ = Mock(return_value=mock_file)
                    mock_file.__exit__ = Mock(return_value=False)
                else:
                    # For read operations, return actual bytes
                    mock_file.read = Mock(return_value=b'output_video_data')
                    mock_file.__enter__ = Mock(return_value=mock_file)
                    mock_file.__exit__ = Mock(return_value=False)
                return mock_file
            
            mock_open.side_effect = open_side_effect
            
            # Execute
            result = await service.video_privacy(payload)
            
            # Assert
            assert result is not None
            assert isinstance(result, str)
            # Verify it's base64 encoded
            try:
                decoded = base64.b64decode(result)
                assert isinstance(decoded, bytes)
            except Exception:
                pytest.fail("Result is not valid base64")
            
            mock_video_capture.assert_called_once()
            mock_video_writer.assert_called_once()
            assert mock_writer.write.call_count == 10
            mock_rmtree.assert_called_once()

    @pytest.mark.asyncio
    @patch('privacy.service.Video_service.shutil.rmtree')
    @patch('privacy.service.Video_service.os.path.exists')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.request_id_var')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    async def test_video_privacy_cannot_open_video(
        self, mock_video_capture, mock_request_id, mock_makedirs, mock_exists, mock_rmtree
    ):
        """Test video_privacy when VideoCapture cannot open video"""
        # Setup
        service = VideoService()
        
        mock_token = object()  # truthy object
        mock_request_id.set.return_value = mock_token
        
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = 'bad_video.mp4'
        mock_upload_file.read = AsyncMock(return_value=b'bad_video_data')
        
        payload = {'video': mock_upload_file, 'entity_types': ['PERSON']}
        
        # Mock VideoCapture to fail opening
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap
        
        mock_exists.return_value = True
        
        with patch('builtins.open', create=True):
            # Execute and assert exception
            with pytest.raises(Exception, match="could not open video file"):
                await service.video_privacy(payload)
        
        # Cleanup should still happen
        mock_rmtree.assert_called_once()

    @pytest.mark.asyncio
    @patch('privacy.service.Video_service.shutil.rmtree')
    @patch('privacy.service.Video_service.os.path.exists')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.request_id_var')
    @patch('privacy.service.Video_service.cv2.VideoWriter')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    async def test_video_privacy_cannot_open_writer(
        self, mock_video_capture, mock_video_writer,
        mock_request_id, mock_makedirs, mock_exists, mock_rmtree
    ):
        """Test video_privacy when VideoWriter cannot be opened"""
        # Setup
        service = VideoService()
        
        mock_token = object()  # truthy object
        mock_request_id.set.return_value = mock_token
        
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = 'test.mp4'
        mock_upload_file.read = AsyncMock(return_value=b'video_data')
        
        payload = {'video': mock_upload_file}
        
        # Mock VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 640,
            cv2.CAP_PROP_FRAME_HEIGHT: 480,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 5
        }.get(prop, 0)
        mock_video_capture.return_value = mock_cap
        
        # Mock VideoWriter to fail opening
        mock_writer = MagicMock()
        mock_writer.isOpened.return_value = False
        mock_video_writer.return_value = mock_writer
        
        mock_exists.return_value = True
        
        with patch('builtins.open', create=True):
            # Execute and assert exception
            with pytest.raises(Exception, match="could not open VideoWriter"):
                await service.video_privacy(payload)
        
        mock_rmtree.assert_called_once()

    @pytest.mark.asyncio
    @patch('privacy.service.Video_service.shutil.rmtree')
    @patch('privacy.service.Video_service.os.path.exists')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.request_id_var')
    @patch('privacy.service.Video_service.cv2.VideoWriter')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    @patch('privacy.service.Video_service.VideoService.frame_anonymization')
    async def test_video_privacy_with_zero_fps(
        self, mock_frame_anon, mock_video_capture, mock_video_writer,
        mock_request_id, mock_makedirs, mock_exists, mock_rmtree
    ):
        """Test video_privacy handles zero FPS gracefully (uses default 30.0)"""
        # Setup
        service = VideoService()
        
        mock_token = object()  # truthy object
        mock_request_id.set.return_value = mock_token
        
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = 'test.mp4'
        mock_upload_file.read = AsyncMock(return_value=b'video_data')
        
        payload = {'video': mock_upload_file, 'max_threads': 2}
        
        # Mock VideoCapture with FPS = 0
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 640,
            cv2.CAP_PROP_FRAME_HEIGHT: 480,
            cv2.CAP_PROP_FPS: 0.0,  # Zero FPS
            cv2.CAP_PROP_FRAME_COUNT: 5
        }.get(prop, 0)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        def read_side_effect():
            for _ in range(5):
                yield (True, frame)
            while True:
                yield (False, None)
        
        mock_cap.read = MagicMock(side_effect=read_side_effect())
        mock_video_capture.return_value = mock_cap
        
        # Mock VideoWriter
        mock_writer = MagicMock()
        mock_writer.isOpened.return_value = True
        mock_video_writer.return_value = mock_writer
        
        mock_exists.return_value = True
        
        def mock_anon_side_effect(payload, frame, idx, results_dict, req_id, temp_path):
            results_dict[idx] = np.ones((480, 640, 3), dtype=np.uint8)
        
        mock_frame_anon.side_effect = mock_anon_side_effect
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_file.read.return_value = b'output'
            mock_open.return_value.__enter__.return_value = mock_file
            
            # Execute
            result = await service.video_privacy(payload)
            
            # Assert - should use default FPS of 30.0
            assert result is not None
            # Verify VideoWriter was called with 30.0 FPS
            mock_video_writer.assert_called_once()
            call_args = mock_video_writer.call_args
            assert call_args[0][2] == 30.0  # FPS parameter

    @pytest.mark.asyncio
    @patch('privacy.service.Video_service.shutil.rmtree')
    @patch('privacy.service.Video_service.os.path.exists')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.request_id_var')
    @patch('privacy.service.Video_service.cv2.VideoWriter')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    @patch('privacy.service.Video_service.VideoService.frame_anonymization')
    async def test_video_privacy_multiple_chunks(
        self, mock_frame_anon, mock_video_capture, mock_video_writer,
        mock_request_id, mock_makedirs, mock_exists, mock_rmtree
    ):
        """Test video_privacy processes multiple chunks correctly"""
        # Setup
        service = VideoService()
        
        mock_token = object()  # truthy object
        mock_request_id.set.return_value = mock_token
        
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = 'long_video.mp4'
        mock_upload_file.read = AsyncMock(return_value=b'video_data')
        
        payload = {'video': mock_upload_file, 'max_threads': 4}
        
        # Mock VideoCapture with 30 frames (will be processed in chunks)
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 640,
            cv2.CAP_PROP_FRAME_HEIGHT: 480,
            cv2.CAP_PROP_FPS: 10.0,  # Low FPS for easier chunk calculation
            cv2.CAP_PROP_FRAME_COUNT: 30
        }.get(prop, 0)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        def read_side_effect():
            for _ in range(30):
                yield (True, frame)
            while True:
                yield (False, None)
        
        mock_cap.read = MagicMock(side_effect=read_side_effect())
        mock_video_capture.return_value = mock_cap
        
        # Mock VideoWriter
        mock_writer = MagicMock()
        mock_writer.isOpened.return_value = True
        mock_video_writer.return_value = mock_writer
        
        mock_exists.return_value = True
        
        def mock_anon_side_effect(payload, frame, idx, results_dict, req_id, temp_path):
            results_dict[idx] = np.ones((480, 640, 3), dtype=np.uint8) * (idx % 255)
        
        mock_frame_anon.side_effect = mock_anon_side_effect
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_file.read.return_value = b'output_video'
            mock_open.return_value.__enter__.return_value = mock_file
            
            # Execute
            result = await service.video_privacy(payload)
            
            # Assert
            assert result is not None
            # All 30 frames should be written
            assert mock_writer.write.call_count == 30
            mock_rmtree.assert_called_once()

    @pytest.mark.asyncio
    @patch('privacy.service.Video_service.shutil.rmtree')
    @patch('privacy.service.Video_service.os.path.exists')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.request_id_var')
    @patch('privacy.service.Video_service.cv2.VideoWriter')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    async def test_video_privacy_exception_in_processing(
        self, mock_video_capture, mock_video_writer,
        mock_request_id, mock_makedirs, mock_exists, mock_rmtree
    ):
        """Test video_privacy handles exceptions during processing"""
        # Setup
        service = VideoService()
        
        mock_token = object()  # truthy object
        mock_request_id.set.return_value = mock_token
        
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = 'test.mp4'
        mock_upload_file.read = AsyncMock(side_effect=Exception("File read error"))
        
        payload = {'video': mock_upload_file}
        
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        
        mock_writer = MagicMock()
        mock_video_writer.return_value = mock_writer
        
        mock_exists.return_value = True
        
        # Execute and assert exception is raised
        with pytest.raises(Exception, match="File read error"):
            await service.video_privacy(payload)
        
        # Cleanup should still happen
        mock_rmtree.assert_called_once()

    @pytest.mark.asyncio
    @patch('privacy.service.Video_service.shutil.rmtree')
    @patch('privacy.service.Video_service.os.path.exists')
    @patch('privacy.service.Video_service.os.makedirs')
    @patch('privacy.service.Video_service.request_id_var')
    @patch('privacy.service.Video_service.cv2.VideoWriter')
    @patch('privacy.service.Video_service.cv2.VideoCapture')
    @patch('privacy.service.Video_service.VideoService.frame_anonymization')
    async def test_video_privacy_cleanup_on_success(
        self, mock_frame_anon, mock_video_capture, mock_video_writer,
        mock_request_id, mock_makedirs, mock_exists, mock_rmtree
    ):
        """Test video_privacy cleans up temp directory on success"""
        # Setup
        service = VideoService()
        
        mock_token = object()  # truthy object
        mock_request_id.set.return_value = mock_token
        
        mock_upload_file = AsyncMock()
        mock_upload_file.filename = 'test.mp4'
        mock_upload_file.read = AsyncMock(return_value=b'video_data')
        
        payload = {'video': mock_upload_file}
        
        # Mock VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 640,
            cv2.CAP_PROP_FRAME_HEIGHT: 480,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 3
        }.get(prop, 0)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        def read_side_effect():
            for _ in range(3):
                yield (True, frame)
            while True:
                yield (False, None)
        
        mock_cap.read = MagicMock(side_effect=read_side_effect())
        mock_video_capture.return_value = mock_cap
        
        # Mock VideoWriter
        mock_writer = MagicMock()
        mock_writer.isOpened.return_value = True
        mock_video_writer.return_value = mock_writer
        
        mock_exists.return_value = True
        
        def mock_anon_side_effect(payload, frame, idx, results_dict, req_id, temp_path):
            results_dict[idx] = np.ones((480, 640, 3), dtype=np.uint8)
        
        mock_frame_anon.side_effect = mock_anon_side_effect
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_file.read.return_value = b'output'
            mock_open.return_value.__enter__.return_value = mock_file
            
            # Execute
            result = await service.video_privacy(payload)
            
            # Assert cleanup was called
            mock_rmtree.assert_called_once()
            assert result is not None


class TestVideoServiceExceptionHandling:
    """Tests for exception handling in video processing"""
    
    @patch('privacy.service.Video_service.log')
    def test_frame_anonymization_with_exception_in_processing(self, mock_log):
        """Test frame_anonymization when an exception occurs during processing"""
        # This tests the try-except block in frame_anonymization
        with patch('privacy.service.Video_service.request_id_var') as mock_request_id, \
             patch('privacy.service.Video_service.os.makedirs'), \
             patch('privacy.service.Video_service.os.remove'), \
             patch('privacy.service.Video_service.os.path.exists') as mock_exists, \
             patch('privacy.service.Video_service.cv2.cvtColor') as mock_cvtColor:
            
            # Setup
            payload = {'entity_types': ['PERSON']}
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            indx = 0
            results_dict = {}
            main_request_id = 'test-id'
            video_temp_path = '/tmp/video_temp'
            
            mock_token = object()
            mock_request_id.set.return_value = mock_token
            mock_exists.return_value = True
            
            # Make cvtColor raise an exception to test error handling
            mock_cvtColor.side_effect = RuntimeError("cvtColor failed")
            
            # Execute
            VideoService.frame_anonymization(
                payload, frame, indx, results_dict, main_request_id, video_temp_path
            )
            
            # Assert - should set None in results_dict on error
            assert indx in results_dict
            assert results_dict[indx] is None
            
            # Verify error was logged
            assert any('error' in str(call).lower() or 'fail' in str(call).lower() 
                      for call in mock_log.error.call_args_list)




