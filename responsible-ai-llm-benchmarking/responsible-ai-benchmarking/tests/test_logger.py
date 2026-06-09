import pytest
from unittest.mock import patch, MagicMock
import logging
from config.logger import CustomLogger

def test_basic():
    with patch('config.logger.readConfig') as mc, \
         patch('config.logger.os.path.dirname') as md, \
         patch('config.logger.os.path.abspath') as ma:
        ma.return_value = '/f'
        md.return_value = '/f'
        mc.return_value = {'file_name': 't', 'verbose': 'True', 'log_dir': ''}
        logger = CustomLogger()
        assert logger.name == 't'


class TestInit:
    def test_verbose_true(self):
        with patch('config.logger.readConfig') as mc, \
             patch('config.logger.os.path.dirname') as md, \
             patch('config.logger.os.path.abspath') as ma:
            ma.return_value = '/f'
            md.return_value = '/f'
            mc.return_value = {'file_name': 'test', 'verbose': 'True', 'log_dir': ''}
            logger = CustomLogger()
            assert logger.verbose is True
            assert logger.level == logging.DEBUG

    def test_verbose_false(self):
        with patch('config.logger.readConfig') as mc, \
             patch('config.logger.os.path.dirname') as md, \
             patch('config.logger.os.path.abspath') as ma:
            ma.return_value = '/f'
            md.return_value = '/f'
            mc.return_value = {'file_name': 'test', 'verbose': False, 'log_dir': ''}
            logger = CustomLogger()
            assert logger.verbose is False

    def test_verbose_exception(self):
        with patch('config.logger.readConfig') as mc, \
             patch('config.logger.os.path.dirname') as md, \
             patch('config.logger.os.path.abspath') as ma:
            ma.return_value = '/f'
            md.return_value = '/f'
            mc.return_value = {'file_name': 'test', 'verbose': None, 'log_dir': ''}
            logger = CustomLogger()
            assert logger.verbose is False

    @patch('config.logger.logging.FileHandler')
    @patch('config.logger.os.path.exists')
    def test_init_with_log_dir(self, me, mfh):
        with patch('config.logger.readConfig') as mc, \
             patch('config.logger.os.path.dirname') as md, \
             patch('config.logger.os.path.abspath') as ma:
            ma.return_value = '/f'
            md.return_value = '/f'
            mc.return_value = {'file_name': 'test', 'verbose': 'True', 'log_dir': '/log'}
            me.return_value = True
            mfh.return_value = MagicMock()
            logger = CustomLogger()
            assert logger.file_handler is not None
