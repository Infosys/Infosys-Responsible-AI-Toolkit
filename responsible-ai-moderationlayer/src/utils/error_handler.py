'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import traceback
import time
from datetime import datetime
from config.logger import CustomLogger, request_id_var

log = CustomLogger()
log_dict = {}  # Global log dictionary

class BaseServiceHandler:
    """Base class for all service handlers with consistent error handling."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.log = CustomLogger()
    
    async def handle_request(self, func, *args, **kwargs):
        """
        Handles service requests with consistent error logging and exception handling.
        
        Args:
            func: The function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            The result of the function call
            
        Raises:
            The original exception after logging
        """
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            self._log_error(e, func.__name__)
            raise  # Re-raise the original exception
    
    def handle_sync_request(self, func, *args, **kwargs):
        """
        Handles synchronous service requests with consistent error logging.
        
        Args:
            func: The function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            The result of the function call
            
        Raises:
            The original exception after logging
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self._log_error(e, func.__name__)
            raise  # Re-raise the original exception
    
    def _log_error(self, error: Exception, method_name: str):
        """
        Logs error information in a consistent format.
        
        Args:
            error: The exception that occurred
            method_name: The name of the method where the error occurred
        """
        request_id = request_id_var.get()
        
        # Initialize log_dict for this request if it doesn't exist
        if request_id not in log_dict:
            log_dict[request_id] = []
        
        error_info = {
            "service": self.service_name,
            "method": method_name,
            "line_number": str(traceback.extract_tb(error.__traceback__)[0].lineno),
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        log_dict[request_id].append(error_info)
        
        # Log the error
        self.log.error(f"Error in {self.service_name}.{method_name}: {error}")
        self.log.error(f"Exception details: Line {error_info['line_number']}, Type: {error_info['error_type']}")

class ServiceException(Exception):
    """Custom exception for service layer errors."""
    
    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message)
        self.original_exception = original_exception
        self.timestamp = datetime.utcnow()

# Decorator for automatic error handling
def handle_service_errors(service_name: str):
    """
    Decorator to automatically handle errors in service methods.
    
    Args:
        service_name: Name of the service for logging purposes
    
    Usage:
        @handle_service_errors("ToxicityService")
        async def analyze_toxicity(self, text: str):
            # Method implementation
            pass
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            handler = BaseServiceHandler(service_name)
            return await handler.handle_request(func, *args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            handler = BaseServiceHandler(service_name)
            return handler.handle_sync_request(func, *args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and 'async' in func.__code__.co_flags:
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
