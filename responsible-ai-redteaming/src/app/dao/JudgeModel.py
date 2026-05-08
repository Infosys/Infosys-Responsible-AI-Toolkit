'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


from __future__ import annotations
from gridfs import GridFS
import pymongo
from pymongo.collection import Collection
from pymongo.database import Database
import datetime, time
from dotenv import load_dotenv
from app.config.logger import CustomLogger
from app.dao.DatabaseConnection import DB
from typing import Any, Mapping, List, Dict, Optional, TypeAlias, Callable
from datetime import timezone  # aware timestamps

load_dotenv()
log = CustomLogger()

mydb_conn: Optional[Database] = DB.connect()
if mydb_conn is None:
    raise RuntimeError("Database connection failed for JudgeModel")
mydb: Database = mydb_conn  

try:  
    AttributeDict  
except NameError:  
    class AttributeDict(dict):
        __getattr__ = dict.__getitem__
        __setattr__ = dict.__setitem__
        __delattr__ = dict.__delitem__


def _crud_get_all(col: Collection, field_name: str) -> List[Any]:
    if not isinstance(field_name, str):
        raise TypeError("field_name must be a string")
    return list(col.distinct(field_name))


def _crud_find_one(col: Collection, doc_id: Any, not_found_msg: str) -> 'AttributeDict':
    values = col.find_one({"_id": doc_id}, {})
    if values is None:
        raise ValueError(f"{not_found_msg} id={doc_id}")
    return AttributeDict(values)


def _crud_find_all(col: Collection, query: Mapping[str, Any]) -> List['AttributeDict']:
    return [AttributeDict(v) for v in col.find(dict(query), {})]


def _crud_update(col: Collection, doc_id: Any, update_values: Mapping[str, Any], logger: Callable[[str], None]) -> bool:
    result = col.update_one({"_id": doc_id}, {"$set": dict(update_values)})
    logger(f"Updated id={doc_id} acknowledged={result.acknowledged}")
    return result.acknowledged


def _crud_delete(col: Collection, query: Mapping[str, Any], logger: Callable[[str], None]) -> int:
    result = col.delete_many(dict(query))
    logger(f"Deleted {result.deleted_count} documents")
    return result.deleted_count


class JudgeModel:
    mycol: Collection = mydb["JudgeModel"]  
    fs: GridFS = GridFS(mydb)
    judge_doc: TypeAlias = Dict[str, Any]  

    @classmethod
    def get_all(cls, field_name: str) -> List[Any]:
        return _crud_get_all(cls.mycol, field_name)

    @classmethod
    def findOne(cls, doc_id: Any) -> 'AttributeDict':
        return _crud_find_one(cls.mycol, doc_id, "JudgeModel not found for")

    
    find_one = findOne

    @classmethod
    def findall(cls, query: Mapping[str, Any]) -> List['AttributeDict']:
        return _crud_find_all(cls.mycol, query)

    @classmethod
    def create(cls, values: Mapping[str, Any]) -> Any:
        data = AttributeDict(dict(values))
        timestamp = time.time()
        time.sleep(1/1000)
        doc: Dict[str, Any] = {
            "_id": timestamp,
            "UserId": data.userId,
            "judgeModelId": timestamp,
            "modelName": data.modelName,
            "maxToken": data.maxToken,
            "judgeModelRedTeamingId": data.attackConfigurationId,
            "CreatedDateTime": datetime.datetime.now(timezone.utc),
            "LastUpdatedDateTime": datetime.datetime.now(timezone.utc),
        }
        result = cls.mycol.insert_one(doc)
        log.debug(f"Inserted JudgeModel id={result.inserted_id}")
        return result.inserted_id

    @classmethod
    def update(cls, doc_id: Any, update_values: Mapping[str, Any]) -> bool:
        return _crud_update(cls.mycol, doc_id, update_values, lambda m: log.debug(f"JudgeModel {m}"))

    @classmethod
    def delete(cls, query: Mapping[str, Any]) -> int:
        return _crud_delete(cls.mycol, query, lambda m: log.debug(f"JudgeModel {m}"))