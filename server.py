import os
import sys

# Automatically load virtual environment site-packages if not already activated
venv_site_packages = os.path.abspath(os.path.join(os.path.dirname(__file__), "venv", "Lib", "site-packages"))
if os.path.exists(venv_site_packages):
    sys.path.insert(0, venv_site_packages)

import secrets
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn

from workflow import coderouter
from cost_tracker import (
    get_session_stats, 
    register_user, 
    authenticate_user, 
    get_query_history
)

# In-memory session store: maps token -> user_id
SESSIONS = {}

app = FastAPI(title="CodeRouter AI Backend API")
@app.get("/health")
async def health():
    return {"status": "ok"}

# Enable CORS for cross-origin frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define schemas for POST requests
class UserAuth(BaseModel):
    username: str
    password: str

class ChatQuery(BaseModel):
    query: str

# Dependency to check Authorization token
def get_current_user_id(authorization: str = Header(None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1]
    user_id = SESSIONS.get(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user_id

# Serve Frontend files
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return FileResponse("code.html")

@app.get("/code.html", response_class=HTMLResponse)
async def serve_code_html():
    return FileResponse("code.html")

# API Endpoints
@app.post("/api/register")
async def register(auth: UserAuth):
    if not auth.username or not auth.password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    
    if register_user(auth.username, auth.password):
        return {"success": True, "message": "User registered successfully"}
    else:
        raise HTTPException(status_code=409, detail="Username already exists")

@app.post("/api/login")
async def login(auth: UserAuth):
    user_id = authenticate_user(auth.username, auth.password)
    if user_id is not None:
        token = secrets.token_hex(32)
        SESSIONS[token] = user_id
        return {"token": token, "username": auth.username}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/api/logout")
async def logout(authorization: str = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        if token in SESSIONS:
            del SESSIONS[token]
    return {"success": True}

@app.get("/api/stats")
async def get_stats(user_id: int = Depends(get_current_user_id)):
    return get_session_stats(user_id)

@app.get("/api/history")
async def get_history(user_id: int = Depends(get_current_user_id)):
    return {"history": get_query_history(user_id)}

@app.post("/api/chat")
async def chat(body: ChatQuery, user_id: int = Depends(get_current_user_id)):
    if not body.query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    result = coderouter.invoke({"query": body.query, "user_id": user_id})
    return result

if __name__ == '__main__':
    port = 8000
    print(f'CodeRouter AI server starting at http://localhost:{port}')
    uvicorn.run(app, host='0.0.0.0', port=port)
