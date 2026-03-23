import io
import json
import datetime
import os
import zipfile
import pytest

import src.service.utility as utility_mod
from src.service.utility import Utility


def test_combineReportFile_error_path(monkeypatch, tmp_path):
    # Stub SecReport to return a report list
    class SecReportStub:
        @staticmethod
        def findall(q):
            return [{'SecReportId': 'r1', 'ReportName': 'AttackX.zip', 'CreatedDateTime': datetime.datetime.now()}]
    monkeypatch.setattr(utility_mod, 'SecReport', SecReportStub)

    # Cause FileStoreDb.findOne to raise inside combineReportFile
    class FileStoreDbStub:
        @staticmethod
        def findOne(_id):
            raise RuntimeError('boom')
    monkeypatch.setattr(utility_mod, 'FileStoreDb', FileStoreDbStub)

    # Ensure directory exists
    folder = tmp_path / 'report'
    folder.mkdir()

    with pytest.raises(Exception):
        Utility.combineReportFile({'batchid': 1.0, 'modelName': 'm', 'report_path': str(folder), 'attackList': ['AttackX']})


def test_update_and_sort_reports_list():
    now = datetime.datetime.now()
    reports = [
        {'ReportName': 'A.zip', 'CreatedDateTime': now - datetime.timedelta(seconds=10)},
        {'ReportName': 'A.zip', 'CreatedDateTime': now},
        {'ReportName': 'B.zip', 'CreatedDateTime': now - datetime.timedelta(seconds=5)},
        {'ReportName': 'm.zip', 'CreatedDateTime': now},  # model zip ignored
    ]
    latest = Utility.updateReportsList({'reportList': reports, 'modelName': 'm', 'attackList': ['A', 'B']})
    assert [r['ReportName'] for r in latest] == ['A.zip', 'B.zip']

    sorted_list = Utility.sortReportsList(latest)
    assert sorted_list[0]['CreatedDateTime'] >= sorted_list[1]['CreatedDateTime']
