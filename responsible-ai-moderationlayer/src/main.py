'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import json
from werkzeug.exceptions import HTTPException,BadRequest,UnprocessableEntity,InternalServerError
from flask import Flask
from router.router import app
# from waitress import serve
# import gunicorn
from hypercorn.asyncio import serve
from hypercorn.config import Config

import os
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from config.logger import CustomLogger, request_id_var 
# import os
from dotenv import load_dotenv
load_dotenv()
log = CustomLogger()
request_id_var.set("StartUp")
SWAGGER_URL = '/rai/v1/moderations/docs'  # URL for exposing Swagger UI (without trailing '/')
# API_URL = '/static/metadata.json'  # Our API url (can of course be a local resource)
# API_URL = 'src/config/swagger/metadata.json'  # Our API url (can of course be a local resource)
API_URL = '/static/metadata.json'  # Our API url (can of course be a local resource)


# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Infosys Responsible AI - Moderation"
    },
)
  
app1 = Flask(__name__)
# app1.register_blueprint(app)

# CORS(app1, origins="*", methods="*", headers="*")

CORS(app1)

app1.register_blueprint(app)


app1.register_blueprint(swaggerui_blueprint)
 
 
@app1.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "details": e.description,
    })
    response.content_type = "application/json"
    return response

@app1.errorhandler(UnprocessableEntity)
def validation_error_handler(exc):
        """Return JSON instead of HTML for HTTP errors."""
        # start with the correct headers and status code from the error
        response = exc.get_response()
        print(response)
        # replace the body with JSON
        exc_code_desc=exc.description.split("-")
        exc_code=int(exc_code_desc[0])
        exc_desc=exc_code_desc[1]
        response.data = json.dumps({
            "code": exc_code,
            "details":  exc_desc,
        })
        response.content_type = "application/json"
        return response

@app1.errorhandler(InternalServerError)
def validation_error_handler(exc):
        """Return JSON instead of HTML for HTTP errors."""
        # start with the correct headers and status code from the error
        response = exc.get_response()
        print(response)
        # replace the body with JSON
        response.data = json.dumps({
            "code": 500,
            "details": "Some Error Occurred ,Please try Later",
        })
        response.content_type = "application/json"
        return response


# def run_gunicorn_server():
#     gunicorn.run(app, bind='0.0.0.0:5000')

 
async def main():
    
    config = Config()
    config.bind = ['0.0.0.0:'+os.getenv("PORT","8000")]
    config.loglevel = 'INFO'
    config.access_log_format = "%(R)s %(s)s %(D)s"
    config.worker_class = 'asyncio'
    config.workers = int(os.getenv('THREADS',6))
    log.info("Server starting with %d workers", config.workers)
    await serve(app1, config=config)
if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    
    import asyncio
    asyncio.run(main())    
# if __name__ == "__main__":
#    request_id_var.set("StartUp")
#    print(os.getenv("THREADS"))
#    run_gunicorn_server()
#    serve(app1, host='0.0.0.0', port=int(os.getenv("PORT")), threads=int(os.getenv('THREADS',6)),connection_limit=int(os.getenv('CONNECTION_LIMIT',500)), channel_timeout=int(os.getenv('CHANNEL_TIMEOUT',120)))


