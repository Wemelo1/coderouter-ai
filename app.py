import os
import sys

# 1. Automatically load virtual environment site-packages if not already activated
venv_site_packages = os.path.abspath(os.path.join(os.path.dirname(__file__), "venv", "Lib", "site-packages"))
if os.path.exists(venv_site_packages):
    sys.path.insert(0, venv_site_packages)

import streamlit as st
import streamlit.components.v1 as components
import subprocess
import threading
import socket
import time

# Set Streamlit Page Config to widen layout and collapse sidebar
st.set_page_config(
    page_title="CodeRouter AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Check if port 8000 is in use
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

# Start backend server.py in background if it's not already running
if not is_port_in_use(8000):
    def run_backend():
        # Spawn backend using current Python interpreter
        # This will use server.py which also has auto-venv resolution enabled
        subprocess.Popen([sys.executable, "server.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    t = threading.Thread(target=run_backend, daemon=True)
    t.start()
    time.sleep(1.5)  # Wait for backend server to spin up and bind

# 3. Inject CSS to hide all default Streamlit chrome for a seamless custom UI
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        div.block-container {
            padding: 0rem !important;
            margin: 0rem !important;
            max-width: 100% !important;
        }
        iframe {
            width: 100vw !important;
            height: 100vh !important;
            border: none !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .stApp {
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# 4. Load code.html, update relative API endpoints to port 8000, and render
try:
    with open("code.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Replace relative API paths with backend localhost paths
    html_content = html_content.replace("'/api/", "'http://127.0.0.1:8000/api/")
    html_content = html_content.replace('"/api/', '"http://127.0.0.1:8000/api/')
    
    # Render the premium interface in full view
    components.html(html_content, height=1080, scrolling=True)
except Exception as e:
    st.error(f"Failed to load custom dashboard interface: {e}")
