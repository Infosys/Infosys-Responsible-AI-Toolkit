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

class PageauthorityDbNew:
    
    def add_initial_data():
        page_authority_collection = mydb['PageAuthorityNew']
        # Check if data already exists in the PageAuthority collection
        if page_authority_collection.count_documents({}) == 0:
            common_data = {
                "pages": 
                    {
                        "Workbench": {
                            "subtabs": {
                                "Unstructured-Text": {
                                    "active": ["Traditional-AI", "Generative-AI"],
                                    "selectType": {
                                        "Traditional-AI": ["Privacy", "Profanity", "FM-Moderation", "Explainability"],
                                        "Generative-AI": ["Privacy", "Profanity", "FM-Moderation", "Explainability", "Fairness"]
                                    }
                                },
                                "Structured-Text": {
                                    "active": []
                                },
                                "Image": {
                                    "active": ["Traditional-AI", "Generative-AI", "T-AI-Upload", "T-AI-DICOM"],
                                    "selectType": {
                                        "Generative-AI": ["Profanity", "Explainability"]
                                    }
                                },
                                "Video": {
                                    "active": []
                                },
                                "Code": {
                                    "active": []
                                }
                            }
                        },
                        "Models": {
                            "subtabs": {
                                "Model-Form": {
                                    "active": []
                                },
                                "Data-Form": {
                                    "active": []
                                },
                                "Preprocessor": {
                                    "active": []
                                }
                            }
                        },
                        "Usecase": {
                            "active": []
                        },
                        "LLM-Benchmarking": {
                            "subtabs": {
                                "Model-Validation": {
                                    "active": []
                                },
                                "Leaderboard": {
                                    "active": []
                                },
                                "Infosys-Leaderboard": {
                                    "active": []
                                }
                            }
                        },
                        "AI-Content-Detector": {
                            "active": []
                        }
                    }
                
            }
            
            ml_role_data = {
            "role": "ROLE_ML",
            "pages": 
                {
                    "Workbench": {
                        "subtabs": {
                            "Unstructured-Text": {
                                "active": ["Generative-AI"],
                                "selectType": {
                                    "Traditional-AI": [],
                                    "Generative-AI": ["FM-Moderation"]
                                }
                            },
                        }
                    }
                }           
        }
            empty_role_data ={
                "role": "ROLE_EMPTY",
                "pages": 
                    {
                        "NewUser":{
                            "active": []
                        }
                    }
            }
                
            

            admin_role_data = {"role": "ROLE_ADMIN", **common_data}
            user_role_data = {"role": "ROLE_USER", **common_data}

            page_authority_collection.insert_many([admin_role_data, user_role_data,ml_role_data,empty_role_data])
            print("recordsInserted")

            # page_authority_collection.insert_many([admin_role_data, user_role_data])
            # print("recordsInserted")
            
            # page_authority_collection.insert_many([ml_role_data, user_role_data])
            # print("recordsInserted")