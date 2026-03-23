'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import io
import sys
import types
import pytest


class FakeResult:
    def __init__(self, inserted_id=None, acknowledged=True, deleted_count=0):
        self.inserted_id = inserted_id
        self.acknowledged = acknowledged
        self.deleted_count = deleted_count


class FakeCollection:
    def __init__(self):
        self._docs = {}

    def distinct(self, field_name):
        vals = set()
        for d in self._docs.values():
            if field_name in d:
                vals.add(d[field_name])
        return list(vals)

    def find_one(self, query, projection=None):
        if "_id" in query:
            return self._docs.get(query["_id"]) or None
        # naive matcher
        for d in self._docs.values():
            ok = all(d.get(k) == v for k, v in query.items())
            if ok:
                return d
        return None

    def find(self, query, projection=None):
        for d in list(self._docs.values()):
            ok = all(d.get(k) == v for k, v in query.items())
            if ok:
                yield d

    def insert_one(self, doc):
        _id = doc.get("_id")
        self._docs[_id] = dict(doc)
        return FakeResult(inserted_id=_id)

    def update_one(self, query, update):
        d = self.find_one(query)
        if not d:
            return FakeResult(acknowledged=False)
        if "$set" in update:
            d.update(update["$set"])
        return FakeResult(acknowledged=True)

    def delete_many(self, query):
        keys = []
        for k, d in list(self._docs.items()):
            ok = all(d.get(f) == v for f, v in query.items())
            if ok:
                keys.append(k)
        for k in keys:
            self._docs.pop(k, None)
        return FakeResult(deleted_count=len(keys))


class _GridFile:
    def __init__(self, _id, filename, content_type, data=b""):
        self._id = _id
        self.filename = filename
        self.content_type = content_type
        self._buf = io.BytesIO(data)

    def write(self, b):
        self._buf.write(b)

    def read(self):
        pos = self._buf.tell()
        self._buf.seek(0)
        data = self._buf.read()
        self._buf.seek(pos)
        return data

    # context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeGridFS:
    def __init__(self, db):
        self._store = {}

    def new_file(self, _id=None, filename=None, content_type=None):
        gf = _GridFile(_id, filename, content_type)
        # upon exit, persist
        class Ctx:
            def __enter__(_self):
                return gf
            def __exit__(_self, exc_type, exc, tb):
                self._store[_id] = gf
                return False
        return Ctx()

    def find_one(self, query):
        _id = query.get("_id") if isinstance(query, dict) else query
        return self._store.get(_id)

    def get(self, _id):
        return self._store.get(_id)


class FakeDB:
    def __init__(self):
        self._cols = {
            'AttackConfiguration': FakeCollection(),
            'AttackModel': FakeCollection(),
            'JudgeModel': FakeCollection(),
            'TargetModel': FakeCollection(),
            'RedTeamingReport': FakeCollection(),
            'fs.files': FakeCollection(),
            'fs.chunks': FakeCollection(),
        }

    def __getitem__(self, name):
        return self._cols[name]


def _prep_db_stubs(monkeypatch):
    # Patch DB.connect to return fake DB and gridfs.GridFS to FakeGridFS
    # Import the module first so we can patch the attribute before DAO modules import it
    import app.dao.DatabaseConnection as DC
    monkeypatch.setattr(DC.DB, 'connect', classmethod(lambda cls: FakeDB()), raising=False)
    # monkeypatch actual gridfs module
    import gridfs as real_gridfs
    monkeypatch.setattr(real_gridfs, 'GridFS', FakeGridFS, raising=True)


def test_attack_configuration_crud_pair_tap(monkeypatch):
    _prep_db_stubs(monkeypatch)
    # Fresh import ensures class attributes bind to fakes
    sys.modules.pop('app.dao.AttackConfiguration', None)
    import app.dao.AttackConfiguration as AC

    # PAIR create
    id1 = AC.AttackConfiguration.create({
        'userId': 'u1', 'redTeamingType': 'PAIR', 'retryLimit': 2, 'objectiveFileId': 'obj'
    })
    assert id1
    # TAP create
    id2 = AC.AttackConfiguration.create({
        'userId': 'u2', 'redTeamingType': 'TAP', 'depth': 1, 'width': 2, 'branchingFactor': 1, 'objectiveFileId': 'obj2'
    })
    assert id2 and id2 != id1
    # get_all
    users = AC.AttackConfiguration.get_all('UserId')
    assert 'u1' in users and 'u2' in users
    # find_one
    doc = AC.AttackConfiguration.find_one(id1)
    assert doc.UserId == 'u1'
    # update
    ok = AC.AttackConfiguration.update(id1, {'retryLimit': 3})
    assert ok is True
    # findall
    lst = AC.AttackConfiguration.findall({'UserId': 'u2'})
    assert len(lst) == 1
    # delete
    cnt = AC.AttackConfiguration.delete({'UserId': 'u1'})
    assert cnt == 1


def test_attack_and_judge_model_crud(monkeypatch):
    _prep_db_stubs(monkeypatch)
    sys.modules.pop('app.dao.AttackModel', None)
    sys.modules.pop('app.dao.JudgeModel', None)
    import app.dao.AttackModel as AM
    import app.dao.JudgeModel as JM

    vals = {'userId': 'u', 'modelName': 'm', 'maxToken': 10, 'attack_configuration_id': 'cfg'}
    vals['attackConfigurationId'] = vals['attack_configuration_id']
    aid = AM.AttackModel.create(vals)
    assert aid
    got = AM.AttackModel.find_one(aid)
    assert got.modelName == 'm'
    assert AM.AttackModel.update(aid, {'maxToken': 20}) is True
    assert len(AM.AttackModel.findall({'UserId': 'u'})) == 1
    assert AM.AttackModel.delete({'UserId': 'u'}) == 1

    jvals = {'userId': 'u', 'modelName': 'jm', 'maxToken': 5, 'attack_configuration_id': 'cfg'}
    jvals['attackConfigurationId'] = jvals['attack_configuration_id']
    jid = JM.JudgeModel.create(jvals)
    assert jid
    assert JM.JudgeModel.get_all('UserId') == ['u']
    assert JM.JudgeModel.findOne(jid).modelName == 'jm'
    assert JM.JudgeModel.update(jid, {'maxToken': 7}) is True
    assert JM.JudgeModel.delete({'UserId': 'u'}) == 1


def test_target_model_and_report_crud(monkeypatch):
    _prep_db_stubs(monkeypatch)
    sys.modules.pop('app.dao.TargetModel', None)
    sys.modules.pop('app.dao.RedTeamingReport', None)
    import app.dao.TargetModel as TM
    import app.dao.RedTeamingReport as RR

    # endpoint variant create
    tvals = {'userId': 'u', 'endPointUrl': 'http://e', 'headers': {'A':'B'}, 'payload': {'x':1}, 'promptVariable': 'q', 'attack_configuration_id': 'cfg'}
    tvals['attackConfigurationId'] = tvals['attack_configuration_id']
    tid1 = TM.TargetModel.create(tvals)
    assert tid1
    # local variant create
    tvals2 = {'userId': 'u', 'modelName': 'm', 'maxToken': 10, 'temperature': 0.1, 'attack_configuration_id': 'cfg'}
    tvals2['attackConfigurationId'] = tvals2['attack_configuration_id']
    tid2 = TM.TargetModel.create(tvals2)
    assert tid2
    # reads
    assert TM.TargetModel.findOne(tid1).endPointUrl == 'http://e'
    assert TM.TargetModel.update(tid2, {'temperature': 0.2}) is True
    assert TM.TargetModel.delete({'UserId': 'u'}) >= 1

    rval = {'userId': 'u', 'report_id': 'R', 'reportName': 'n', 'attack_configuration_id': 'cfg'}
    rval['attackConfigurationId'] = rval['attack_configuration_id']
    # Provide camelCase reportId expected by DAO implementation
    rval['reportId'] = rval.get('report_id')
    rid = RR.RedTeamingReport.create(rval)
    assert rid
    assert RR.RedTeamingReport.findOne(rid).reportName == 'n'
    assert RR.RedTeamingReport.update(rid, {'reportName': 'x'}) is True
    assert RR.RedTeamingReport.delete({'UserId': 'u'}) == 1


def test_file_store_db_mongo_and_blob(monkeypatch):
    _prep_db_stubs(monkeypatch)
    sys.modules.pop('app.dao.SaveFileDB', None)
    import app.dao.SaveFileDB as FS
    # mongo path: create, get_file, read_file
    obj = types.SimpleNamespace(filename='t.txt', content_type='text/plain', file=io.BytesIO(b'hello'))
    fid = FS.FileStoreDb.create(obj)
    one = FS.FileStoreDb.get_file(fid)
    assert one['fileName'] == 't.txt' and one['data'] == b'hello'
    got = FS.FileStoreDb.read_file(fid, None)
    assert got['data'] == b'hello'
    # update
    obj2 = types.SimpleNamespace(filename='t.txt', content_type='text/plain', file=io.BytesIO(b'world'))
    FS.FileStoreDb.update(fid, obj2)
    one2 = FS.FileStoreDb.get_file(fid)
    assert one2['data'] == b'world'

    # cosmos/blob path: switch db_type and mock requests
    FS.FileStoreDb.db_type = 'cosmos'
    monkeypatch.setenv('AZURE_GET_API', 'http://example.test/get')
    class Resp:
        def __init__(self, code, content=b'blob'):
            self.status_code = code
            self.content = content
    import requests as real_req
    monkeypatch.setattr(real_req, 'get', lambda **k: Resp(200, b'blob'))
    out = FS.FileStoreDb.read_file('blob-id', 'cont')
    assert out['data'] == b'blob'
    # error branch
    monkeypatch.setattr(real_req, 'get', lambda **k: Resp(500))
    with pytest.raises(RuntimeError):
        FS.FileStoreDb.read_file('blob-id', 'cont')
