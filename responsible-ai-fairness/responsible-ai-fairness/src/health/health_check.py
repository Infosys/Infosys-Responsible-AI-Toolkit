"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import os
from fairness.config.logger import CustomLogger
from fairness.dao.LlmConnection import Azureopenai, GeminiFlash, GeminiPro
from fairness.dao.WorkBench.databaseconnection import DataBase_WB

class HealthCheck:
    def __init__(self):
        self.system_prompt = "You are a helpful assistant."
        self.user_text = "Test"

    def check_azure_openai(self):
        """
        Health check for Azure OpenAI connectivity.
        """
        try:
            self.azure_openai = Azureopenai()
            response = self.azure_openai.get_chat_completion(prompt_template=self.system_prompt,
                                                             text=self.user_text)
            if response:
                return {"healthy": bool(response), 
                        "status": "Azure OpenAI OK",
                        "message": "Azure OpenAI OK" if response else "No response."}
            else:
                return {"healthy": False, 
                        "status": "Azure OpenAI Unhealthy",
                        "message": "No response from Azure OpenAI"}
        except Exception as e:
            return {"healthy": False, 
                    "status": "Azure OpenAI Unhealthy",
                    "message": str(e)} 
        
    def check_gemini_flash(self):
        """
        Health check for Gemini Flash connectivity.
        """
        try: 
            self.gemini_flash = GeminiFlash()
            response_flash = self.gemini_flash.get_chat_completion(prompt_template=self.system_prompt,
                                                                   text=self.user_text)
            if response_flash:
                return {"healthy": bool(response_flash), 
                        "status": "Gemini Flash OK",
                        "message": "Gemini Flash OK" if response_flash else "No response."}
            else:
                return {"healthy": False, 
                        "status": "Gemini Flash Unhealthy",
                        "message": "No response from Gemini Flash"}
        except Exception as e:
            return {"healthy": False, 
                    "status": "Gemini Flash Unhealthy",
                    "message": str(e)}
        
    def check_gemini_pro(self):
        """
        Health check for Gemini Pro connectivity.
        """
        try: 
            self.gemini_pro = GeminiPro()
            response_pro = self.gemini_pro.get_chat_completion(prompt_template=self.system_prompt,
                                                               text=self.user_text)
            if response_pro:
                return {"healthy": bool(response_pro), 
                        "status": "Gemini Pro OK",
                        "message": "Gemini Pro OK" if response_pro else "No response"}
            else:
                return {"healthy": False, 
                        "status": "Gemini Pro Unhealthy",
                        "message": "No response from Gemini Pro"}
        except Exception as e:
            return {"healthy": False, 
                    "status": "Gemini Pro Unhealthy",
                    "message": str(e)}
        
    def check_database(self):
        """
        Health check for MongoDB/Cosmos connectivity.
        """
        try:
            self.db_obj = DataBase_WB()
            response = (self.db_obj.client and self.db_obj.db)
            if response:
                return {"healthy": True, 
                        "status": "Database OK",
                        "message": "Database OK" if response else "No response"}
            else:
                return {"healthy": False, 
                        "status": "Database Unhealthy",
                        "message": "Database connection failed"}
        except Exception as e:
            return {"healthy": False, 
                    "status": "Database Unhealthy",
                    "message": str(e)}
        
    def check_logger(self):
        """
        Health check for Logging system.
        Verifies that the logger is properly initialized and functional.
        """
        try:
            logger=CustomLogger()
            checks = []
            issues = []
            
            # Check 1: Verify logger instance exists and is of correct type
            if isinstance(logger, CustomLogger):
                checks.append("Logger instance created")
            else:
                issues.append("Logger is not a CustomLogger instance")
            
            # Check 2: Verify console handler is present and enabled
            if hasattr(logger, 'has_console_handler') and logger.has_console_handler():
                checks.append("Console handler active")
            elif hasattr(logger, 'handlers'):
                # Fallback check for console handlers
                console_handlers = [h for h in logger.handlers if hasattr(h, 'stream')]
                if console_handlers:
                    checks.append("Console handler active")
                else:
                    issues.append("Console handler missing")
            else:
                issues.append("Console handler missing")
            
            # Check 3: Verify file handler is present (if configured)
            if hasattr(logger, 'has_file_handler') and logger.has_file_handler():
                checks.append("File handler active")
                
                # Check 4: Verify log file exists and is writable
                if hasattr(logger, 'file_handler') and logger.file_handler:
                    log_file_path = logger.file_handler.baseFilename
                    if os.path.exists(log_file_path):
                        checks.append(f"Log file exists: {os.path.basename(log_file_path)}")
                        
                        # Test write permissions
                        if os.access(log_file_path, os.W_OK):
                            checks.append("Log file is writable")
                        else:
                            issues.append("Log file is not writable")
                    else:
                        issues.append("Log file does not exist")
            elif hasattr(logger, 'handlers'):
                # Fallback check for file handlers
                file_handlers = [h for h in logger.handlers if hasattr(h, 'baseFilename')]
                if file_handlers:
                    checks.append("File handler active")
                else:
                    checks.append("File handler not configured (console only)")
            else:
                checks.append("File handler not configured (console only)")
            
            # Check 5: Test actual logging functionality
            test_message = "Health check test message"
            logger.info(test_message)
            checks.append("Test log message sent successfully")
            
            # Determine overall health
            is_healthy = len(issues) == 0
            
            # Prepare response message
            checked_message_parts = []
            issue_message_parts = []
            if checks:
                checked_message_parts.append(f"{'; '.join(checks)}")
            if issues:
                issue_message_parts.append(f"{'; '.join(issues)}")
            
            if is_healthy:
                return {
                    "healthy": is_healthy,
                    "status": "Logger OK",
                    "message": " | ".join(checked_message_parts)
                }
            else:
                return {
                    "healthy": is_healthy,
                    "status": "Logger Unhealthy",
                    "message": " | ".join(issue_message_parts)
                }
            
        except Exception as e:
            return {
                "healthy": False, 
                "message": f"Logging health check failed: {str(e)}"
            }