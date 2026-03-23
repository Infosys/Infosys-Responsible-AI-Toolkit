'''
Copyright 2024-2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
# """
# fileName: mappers.py
# description: A Pydantic model object for usecase entity model
#              which maps the data model to the usecase entity schema
# """

# from bson import ObjectId
# from pydantic import BaseModel, Field
# from datetime import datetime
# from typing import Optional,Union, List

# """
# description: piiEntity
# params:
# """

# class Docs(BaseModel):
#     docId:float=Field(example=2323.2323)
#     userId:str=Field(example="name")
#     fileName:str=Field(example="test.mp4")
#     status:status=Field(example="/")
#     type:str=Field(example="v/m")
#     CreatedDateTime:datetime=Field(example='2023-06-07T10:56:15.657+00:00')
#     LastUpdatedDateTime:datetime=Field(example='2023-06-07T10:56:15.657+00:00')
#     # resultFileId:ObjectId=ObjectId('6500066227bc3407660d03bb')

# # class Docs(BaseModel):

# #     docId:float=Field(example=2323.2323)
# #     userId:str=Field(example="name")
# #     fileName:str=Field(example="test.mp4")
# #     status:status=Field(example="/")
# #     type:str=Field(example="v/m")
# #     CreatedDateTime:datetime=Field(example='2023-06-07T10:56:15.657+00:00')
# #     LastUpdatedDateTime:datetime=Field(example='2023-06-07T10:56:15.657+00:00')
# #     resultFileId:ObjectId=ObjectId('6500066227bc3407660d03bb')
    
# class DocList(BaseModel):
#     r:List[Docs]
#     class Config:
#         orm_mode = True
    