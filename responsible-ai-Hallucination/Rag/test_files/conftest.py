# C:\Users\kirubhakaran.v\Desktop\hallucination_new\2.2.1\responsible-ai-Hallucination\Rag\test_files\conftest.py

import os
from pathlib import Path
from dotenv import load_dotenv

def pytest_sessionstart(session):
    # Adjust path: test_files -> src -> .env
    root = Path(__file__).resolve().parent.parent  # Rag/
    env_path = root / "src" / ".env"

    if env_path.exists():
        load_dotenv(env_path)
    else:
        raise RuntimeError(f".env file not found at {env_path}")
