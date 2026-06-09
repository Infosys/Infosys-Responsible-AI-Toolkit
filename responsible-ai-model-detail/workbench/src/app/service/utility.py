'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from app.service.service import InfosysRAI
from app.dao.DatabaseConnection import DB
from app.config.logger import CustomLogger
from app.dao.ModelAttributesDb import ModelAttributes
import json

from app.dao.DataAttributesDb import DataAttributes


log = CustomLogger()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class Utility:

    mydb=DB.connect()

    def loadtenets():
        try:
            collist = Utility.mydb.list_collection_names()

            f=open(r"app/config/tenet.json",'r')
            tenetList = json.loads(f.read())
            if 'Tenet' not in collist:
                print("TenetList---",tenetList)
                for tenet in tenetList:
                    tenet = AttributeDict(tenet)
                    X = InfosysRAI.addTenet(tenet)
            
            return "Success"
        except Exception as exc:
            return "Something Went Wrong" 
        
    def loadmodelattributes():
        try:
            collist = Utility.mydb.list_collection_names()

            f=open(r"app/config/modelattributes.json",'r')
            modelAttributesList = json.loads(f.read())
            if 'ModelAttributes' not in collist:
                print("ModelAttributesList---",modelAttributesList)
                for modelAttributes in modelAttributesList:
                    modelAttributes = AttributeDict(modelAttributes)
                    id = ModelAttributes.create({"modelAttributeName":modelAttributes["ModelAttributeName"],"tenetId":modelAttributes["TenetId"]})
                    if id:
                        print(f"ModelAttributeName {modelAttributes.ModelAttributeName} got initalised Successfully")
            
            return "Success"
        except Exception as exc:
            return "Something Went Wrong" 
        
    def loaddataattributes():
        try:
            collist = Utility.mydb.list_collection_names()

            f=open(r"app/config/datasetattributes.json",'r')
            dataAttributesList = json.loads(f.read())
            if 'DataAttributes' not in collist:
                print("datasetAttributesList---",dataAttributesList)
                for dataAttributes in dataAttributesList:
                    dataAttributes = AttributeDict(dataAttributes)
                    id = DataAttributes.create({"dataAttributeName":dataAttributes["DataAttributeName"],"tenetId":dataAttributes["TenetId"]})
                    print(id)
                    if id:
                        print(f"DataAttributeName {dataAttributes.DataAttributeName} got initalised Successfully")
            
            return "Success"
        except Exception as exc:
            return "Something Went Wrong" 