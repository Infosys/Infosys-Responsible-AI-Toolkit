
'''
© <2023> Infosys Limited, Bangalore, India. All Rights Reserved.
 Version: 
Except for any free or open source software components embedded in this Infosys proprietary software program (“Program”), this Program is protected by copyright laws, international treaties and other pending or existing intellectual property rights in India, the United States and other countries. Except as expressly permitted, any unauthorized reproduction, storage, transmission in any form or by any means (including without limitation electronic, mechanical, printing, photocopying, recording or otherwise), or any distribution of this Program, or any portion of it, may result in severe civil and criminal penalties, and will be prosecuted to the maximum extent possible under the law.
'''

from privacy.service.service import PrivacyService as ps
from privacy.config.logger import request_id_var
import uuid
class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
class Privacy:
    def textAnalyze(payload):
        id = uuid.uuid4().hex
        request_id_var.set(id)
        return ps.analyze(AttributeDict(payload))
        
    def textAnonymize(payload):
        id = uuid.uuid4().hex
        request_id_var.set(id)
        return ps.anonymize(AttributeDict(payload))
    
    def imageAnalyze(payload):
        id = uuid.uuid4().hex
        request_id_var.set(id)
        return ps.image_analyze(AttributeDict(payload))
    def imageAnonymize(payload):
        id = uuid.uuid4().hex
        request_id_var.set(id)
        return ps.image_anonymize(AttributeDict(payload))
    def imageVerify(payload):
        id = uuid.uuid4().hex
        request_id_var.set(id)
        return ps.image_verify(AttributeDict(payload))
    def imageEncrypt(payload):
        id = uuid.uuid4().hex
        request_id_var.set(id)
        return ps.imageEncryption(AttributeDict(payload))
    


# d=AttributeDict({
#   "inputText": "Karan is working in Infosys. He is from Mumbai. His appointment for renewing passport is booked on March 12 and his old Passport Number is P2096457. Also, he want to link his Aadhaar Number is 567845678987 with his Pan Number is BNZAA2318A.",
#   "portfolio": None,
#   "account": None,
#   "exclusionList": None
# })
# Privacy.textAnalyze(d)





