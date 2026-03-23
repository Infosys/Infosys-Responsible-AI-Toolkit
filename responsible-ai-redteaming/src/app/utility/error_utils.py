from __future__ import annotations
'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


"""Common error handling helpers to reduce repetitive try/except blocks.

Provides a decorator (handle_exceptions) that logs and returns exceptions
without duplicating boilerplate in every service method. Existing methods
that previously returned the raw exception continue to do so to avoid
changing external behavior. The logger is injected (or lazily imported)
to keep the decorator lightweight.
"""

from functools import wraps
from typing import Callable, TypeVar, Any, cast

T = TypeVar("T")

def handle_exceptions(logger_attr: str = "log") -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator factory for wrapping service layer functions.

    Parameters
    ----------
    logger_attr: str
        Attribute name looked up on the first argument (cls/self module) to obtain a logger
        that has an .error method. Defaults to 'log'. If not found, a no-op logger is used.

    Behavior
    --------
    - Catches all Exceptions.
    - Logs a structured error message with function name.
    - Returns the exception object (mirrors prior pattern in codebase).
    """
    def _decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def _wrapped(*args: Any, **kwargs: Any) -> T:  
            try:
                return func(*args, **kwargs)
            except Exception as exc: 
                logger = None
                if args:
                    candidate = args[0]
                    logger = getattr(candidate, logger_attr, None)
                if logger is None:
                    # Fallback import to avoid circulars
                    try:
                        from app.config.logger import CustomLogger  # local import
                        logger = CustomLogger()
                    except Exception:  
                        class _NoOp: 
                            def error(self, *a: Any, **k: Any) -> None: ...
                        logger = _NoOp()
                try:
                    logger.error(f"Error in {func.__name__}: {exc}", exc_info=True)  
                except Exception:
                    pass
                return cast(T, exc)
        return _wrapped
    return _decorator

__all__ = ["handle_exceptions"]
