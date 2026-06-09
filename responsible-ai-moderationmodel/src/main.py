'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
from flask import Flask,request,jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from routing.router import router
from config.logger import CustomLogger,request_id_var
from waitress import serve
from werkzeug.exceptions import HTTPException,UnsupportedMediaType,BadRequest
from dotenv import load_dotenv
load_dotenv()

# Add security headers to all HTTP responses
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; img-src 'self' data:"
    return response

SWAGGER_URL = '/rai/v1/raimoderationmodels/docs'  
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, 
    API_URL
)

log=CustomLogger()
app = Flask(__name__)
app.register_blueprint(swaggerui_blueprint)
app.register_blueprint(router,url_prefix='/rai/v1/raimoderationmodels')

# Apply security headers to all responses
@app.after_request
def after_request(response):
    return add_security_headers(response)


def handle_http_exception(exc):
    """Handles HTTP exceptions, returning a JSON response."""
    response = jsonify({"error": exc.description})
    response.status_code = exc.code
    return response

@app.errorhandler(HTTPException)
def handle_all_http_exceptions(exc):
    """Global exception handler for HTTP errors."""
    return handle_http_exception(exc)

def handle_unsupported_mediatype(exc):
    """Handles unsupported media type exceptions."""
    return jsonify({"error": "Unsupported media type"}), 415  # 415 Unsupported Media Type

@app.errorhandler(UnsupportedMediaType)
def handle_all_unsupported_mediatype_exceptions(exc):
    """Global exception handler for unsupported media types."""
    return handle_unsupported_mediatype(exc)


if __name__ == "__main__":
   serve(app, host='0.0.0.0', port=int(os.getenv('DB_PORT') or 8000), threads=int(os.getenv('THREADS') or 1),connection_limit=int(os.getenv('CONNECTION_LIMIT') or 500), channel_timeout=int(os.getenv('CHANNEL_TIMEOUT') or 120))

