"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import datetime
import json
from rai_backend.mappers.PageAuthorityMapper import PageAuthority
from fastapi import Response
from rai_backend.dao.DatabaseConnection import DB
from rai_backend.config.logger import CustomLogger
from dotenv import load_dotenv
from rai_backend.service.backend_service import UserInDB

load_dotenv()
log = CustomLogger()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


mydb=DB.connect()

class PageauthorityDb:
    
    def add_initial_data():
        page_authority_collection = mydb['PageAuthority']
        # Check if data already exists in the PageAuthority collection
        if page_authority_collection.count_documents({}) == 0:
            admin_role_data = {"role": "ROLE_ADMIN", "pages": ["Image", "Video", "Unstructured Text","FM Moderation","AI Fairness","Bulk Processing",
                                                               "RAI Explainability","Securiy","Code Upload","Excel Use Case","PPT Use Case","Bulk Processing Subpage"]}
            user_role_data = {"role": "ROLE_USER", "pages": ["Image", "Video", "Unstructured Text","FM Moderation","AI Fairness","Bulk Processing",
                                                               "RAI Explainability","Securiy","Code Upload","Excel Use Case","PPT Use Case", "Bulk Processing Subpage"]}
            page_authority_collection.insert_many([admin_role_data, user_role_data])
            print("recordsInserted")