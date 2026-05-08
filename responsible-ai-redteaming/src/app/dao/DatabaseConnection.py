'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''



import os
import pymongo

from dotenv import load_dotenv
from app.config.logger import CustomLogger
from app.config.config import get_secret
load_dotenv()

log = CustomLogger()


class DB:
    
    @classmethod
    def connect(cls):
        """Create and return a database handle based on DB_TYPE env variable."""
        try:
            db_type = (get_secret("DB_TYPE") or "mongo").lower()
            if db_type in ("cosmos", "mongo"):
                path_var = "COSMOS_PATH" if db_type == "cosmos" else "MONGO_PATH"
                client_uri = get_secret(path_var)
                db_name = get_secret("DB_NAME")
                if not client_uri:
                    raise ValueError(f"{path_var} not set")
                if not db_name:
                    raise ValueError("DB_NAME not set")
                myclient = pymongo.MongoClient(client_uri)
                mydb = myclient[db_name]
                return mydb
            raise ValueError(f"Unsupported database type: {db_type}")
        except Exception as e:
            log.info(str(e))
            return None