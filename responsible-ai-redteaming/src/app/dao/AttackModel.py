'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''



from gridfs import GridFS
import pymongo
import datetime,time
from dotenv import load_dotenv
from app.config.logger import CustomLogger
from app.dao.DatabaseConnection import DB
from typing import Any, Mapping, List, Dict, Optional, TypeAlias  
from pymongo.database import Database as MongoDatabase  
from pymongo.collection import Collection as MongoCollection  
from datetime import timezone

load_dotenv()
log = CustomLogger()

mydb_conn: Optional[MongoDatabase] = DB.connect()
if mydb_conn is None:
    raise RuntimeError("Database connection failed for AttackModel")
mydb: MongoDatabase = mydb_conn

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class AttackModel:
    mycol: MongoCollection = mydb["AttackModel"]  
    fs: GridFS = GridFS(mydb)
    attack_model_doc: TypeAlias = Dict[str, Any]  
   

    @classmethod
    def get_all(cls, field_name: str) -> List[Any]:
        """Return distinct values for a field."""
        if not isinstance(field_name, str):
            raise TypeError("field_name must be a string")
        return list(cls.mycol.distinct(field_name))

    @classmethod
    def find_one(cls, doc_id: Any) -> AttributeDict:
        """Find one document by _id."""
        values = cls.mycol.find_one({"_id": doc_id}, {})
        if values is None:
            raise ValueError(f"AttackModel not found for id={doc_id}")
        return AttributeDict(values)

    
    findOne = find_one

    @classmethod
    def findall(cls, query: Mapping[str, Any]) -> List[AttributeDict]:
        """Find all documents matching query."""
        results: List[AttributeDict] = []
        for v in cls.mycol.find(dict(query), {}):
            results.append(AttributeDict(v))
        return results

    @classmethod
    def create(cls, values: Mapping[str, Any]) -> Any:
        """Create a new AttackModel document."""
        data = AttributeDict(dict(values))
        timestamp = time.time()
        time.sleep(1/1000)  # preserve slight delay
        doc: Dict[str, Any] = {
            "_id": timestamp,
            "UserId": data.userId,
            "attackModelId": timestamp,
            "modelName": data.modelName,
            "maxToken": data.maxToken,
            "attackModelRedTeamingId": data.attackConfigurationId,
            "CreatedDateTime": datetime.datetime.now(timezone.utc),
            "LastUpdatedDateTime": datetime.datetime.now(timezone.utc),
        }
        result = cls.mycol.insert_one(doc)
        log.debug(f"Inserted AttackModel id={result.inserted_id}")
        return result.inserted_id

    @classmethod
    def update(cls, doc_id: Any, update_values: Mapping[str, Any]) -> bool:
        """Update a document by _id."""
        new_values = {"$set": dict(update_values)}
        result = cls.mycol.update_one({"_id": doc_id}, new_values)
        log.debug(f"Updated AttackModel id={doc_id} acknowledged={result.acknowledged}")
        return result.acknowledged

    @classmethod
    def delete(cls, query: Mapping[str, Any]) -> int:
        """Delete documents matching query; return count."""
        result = cls.mycol.delete_many(dict(query))
        log.debug(f"Deleted {result.deleted_count} AttackModel documents")
        return result.deleted_count