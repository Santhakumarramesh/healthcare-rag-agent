"""
Compatibility shim for Render.
Render Dashboard may be configured to run app.py instead of app_healthcare.py.
This file loads and runs the actual app.
"""
import importlib.util
import os

_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_healthcare.py")
_spec = importlib.util.spec_from_file_location("app_healthcare", _path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
