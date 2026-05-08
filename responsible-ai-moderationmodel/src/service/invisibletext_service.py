import unicodedata
import time
import traceback
import uuid
from werkzeug.exceptions import InternalServerError
from config.logger import CustomLogger,request_id_var

log = CustomLogger()
log_dict={}

class InvisibleText:
    '''
    A class for scanning if the prompt includes invisible characters.
    This class uses the unicodedata library to detect invisible characters in the output of the language model.
    It detects and removes characters in categories :
        'Cf' (Format characters),
        'Cc' (Control characters), 
        'Co' (Private use characters), and 
        'Cn' (Unassigned characters), which are typically non-printable.
    '''
    def scan(self, prompt: str,banned_categories: list):
        log.info("inside invisible_text check")
        id=uuid.uuid4().hex
        request_id_var.set(id)
        log_dict[request_id_var.get()]=[]
        try:
            st = time.time()
            chars = []
            output={}
            contains_unicode = any(ord(char) > 127 for char in prompt)
            log.info(f"contains_unicode: {contains_unicode}")
            if not contains_unicode:
                output['result']=[]
                output['time_taken']=str(round(time.time()-st,3))+"s"
            else:
                for char in prompt:
                    if unicodedata.category(char) not in banned_categories:
                        continue
                    chars.append(char)
                output['result']=chars
                output['time_taken']=str(round(time.time()-st,3))+"s"
            
            log.info(f"output: {output}")
            return output
            
        except Exception as e:
            log.error("Error occured in invisibletext_check")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at invisibletext_check call"})
            er=log_dict[request_id_var.get()]
            logobj = {"_id":id,"error":er}
            if len(er)!=0:
                log.debug(str(logobj))
            del log_dict[id]
            raise InternalServerError()
        
