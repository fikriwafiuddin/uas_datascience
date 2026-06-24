"""
Flask Application untuk PythonAnywhere
File ini adalah entry point untuk WSGI di PythonAnywhere
"""

import sys
from app import app as application

# PythonAnywhere akan menggunakan variabel 'application' sebagai WSGI entry point
__all__ = ['application']
