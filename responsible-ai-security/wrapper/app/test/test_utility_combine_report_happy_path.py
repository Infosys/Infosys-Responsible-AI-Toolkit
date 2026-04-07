import io
import zipfile
import datetime
import os

import src.service.utility as utility_mod
from src.service.utility import Utility


def make_zip_bytes():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        # HTML with style tag to be stripped
        z.writestr('attack.html', '<html><style>body{}</style><body>ok</body></html>')
        # CSV content
        z.writestr('attack.csv', 'col1,col2\n1,2\n3,4')
        # Image-like entry
        z.writestr('img.png', b'fakeimg')
    buf.seek(0)
    return buf.read()


def test_combineReportFile_happy(monkeypatch, tmp_path):
    # Stub SecReport to provide one entry
    class SecReportStub:
        @staticmethod
        def findall(q):
            return [{'SecReportId': 'id1', 'ReportName': 'AttackX.zip', 'CreatedDateTime': datetime.datetime.now()}]
    monkeypatch.setattr(utility_mod, 'SecReport', SecReportStub)

    # Stub FileStoreDb.findOne to return zip bytes
    class FileStoreDbStub:
        @staticmethod
        def findOne(_id):
            return {'fileName': 'AttackX.zip', 'data': make_zip_bytes(), 'type': 'zip'}
    monkeypatch.setattr(utility_mod, 'FileStoreDb', FileStoreDbStub)

    folder = tmp_path / 'report'
    folder.mkdir()

    count = Utility.combineReportFile({'batchid': 1.0, 'modelName': 'm', 'report_path': str(folder), 'attackList': ['AttackX']})
    assert count == 1
    # Files laid out
    assert (folder / 'report.html').exists()
    assert (folder / 'AttackX.csv').exists()
