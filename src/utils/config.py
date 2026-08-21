import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"

def get_config_var(key: str, default: str = "") -> str:
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default

GEMINI_API_KEY = get_config_var("GEMINI_API_KEY", "")
OPENAI_API_KEY = get_config_var("OPENAI_API_KEY", "")
MODEL_NAME = get_config_var("MODEL_NAME", "gpt-4o-mini" if OPENAI_API_KEY else "gemini-3.6-flash")
