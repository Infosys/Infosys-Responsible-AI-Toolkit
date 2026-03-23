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
    raise RuntimeError("Database connection failed for AttackConfiguration")
mydb: MongoDatabase = mydb_conn


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class AttackConfiguration:

    mycol: MongoCollection = mydb["AttackConfiguration"]  # typed
    fs: GridFS = GridFS(mydb)

    # type alias (snake_case per naming convention)
    attack_config_doc: TypeAlias = Dict[str, Any]
    # (Removed PascalCase field to satisfy Sonar S116)


    @classmethod
    def get_all(cls, field_name: str) -> List[Any]:
        """Return distinct values for a field."""
        if not isinstance(field_name, str):
            raise TypeError("field_name must be a string")
        return list(cls.mycol.distinct(field_name))


    @classmethod
    def find_one(cls, doc_id: Any) -> AttributeDict:
        """Find a single document by _id."""
        values = cls.mycol.find_one({"_id": doc_id}, {})
        if values is None:
            raise ValueError(f"AttackConfiguration not found for id={doc_id}")
        return AttributeDict(values)

    # Backward compatibility alias (not a method definition to satisfy naming rule)
    findOne = find_one
    

    @classmethod
    def findall(cls, query: Mapping[str, Any]) -> List[AttributeDict]:
        """Find all documents matching a query."""
        value_list: List[AttributeDict] = []
        for v in cls.mycol.find(dict(query), {}):
            value_list.append(AttributeDict(v))
        return value_list
    

    @classmethod
    def create(cls, values: Mapping[str, Any]) -> Any:
        """Create a new attack configuration document."""
        data = AttributeDict(dict(values))
        timestamp = time.time()
        time.sleep(1/1000) 
        common: Dict[str, Any] = {
             "_id": timestamp,
             "UserId": data.userId,
             "attackConfigurationId": timestamp,
             "redTeamingType": data.redTeamingType,
             "objectiveFileId": data.objectiveFileId,
            "CreatedDateTime": datetime.datetime.now(timezone.utc),
            "LastUpdatedDateTime": datetime.datetime.now(timezone.utc),
         }
        if data.redTeamingType == 'PAIR':
            mydoc = {
                **common,
                "retryLimit": data.retryLimit,
            }
        elif data.redTeamingType == 'TAP':
            mydoc = {
                **common,
                "depth": data.depth,
                "width": data.width,
                "branchingFactor": data.branchingFactor,
            }
        else:
            raise ValueError(f"Unsupported redTeamingType: {data.redTeamingType}")
        result = cls.mycol.insert_one(mydoc)
        log.debug(f"Inserted AttackConfiguration id={result.inserted_id}")
        return result.inserted_id
    

    @classmethod
    def update(cls, doc_id: Any, update_values: Mapping[str, Any]) -> bool:
        """Update a document by _id."""
        new_values = {"$set": dict(update_values)}
        result = cls.mycol.update_one({"_id": doc_id}, new_values)
        log.debug(f"Updated AttackConfiguration id={doc_id} acknowledged={result.acknowledged}")
        return result.acknowledged
    

    @classmethod
    def delete(cls, query: Mapping[str, Any]) -> int:
        """Delete documents matching query. Returns count deleted."""
        result = cls.mycol.delete_many(dict(query))
        log.debug(f"Deleted {result.deleted_count} AttackConfiguration documents")
        return result.deleted_count