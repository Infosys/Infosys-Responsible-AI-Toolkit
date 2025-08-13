'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from config.vader import SentimentIntensityAnalyzer
import time
import traceback
import uuid
from werkzeug.exceptions import InternalServerError
from config.logger import CustomLogger,request_id_var

log = CustomLogger()
log_dict={}


class Sentiment:
    def scan(self, prompt: str):
        log.info("inside sentiment_check")
        id=uuid.uuid4().hex
        request_id_var.set(id)
        log_dict[request_id_var.get()]=[]
        try:
            st = time.time()
            output={}
            sentiment_analyzer = SentimentIntensityAnalyzer()
            sentiment_score = sentiment_analyzer.polarity_scores(prompt)
            log.debug(f"sentiment_score : {sentiment_score}")
            output['score'] = sentiment_score
            output['time_taken'] = str(round(time.time()-st,3))+"s"
            er=log_dict[request_id_var.get()]
            logobj = {"_id":id,"error":er}
            if len(er)!=0:
                log.debug(str(logobj))
            del log_dict[id]
            return output
        except Exception as e:
            log.error("Error occured in sentiment_check")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at sentiment_check call"})
            raise InternalServerError()
