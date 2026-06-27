import json
import os
import secrets
from http.server import HTTPServer, SimpleHTTPRequestHandler
from workflow import coderouter
from cost_tracker import (
    get_session_stats, 
    register_user, 
    authenticate_user, 
    get_query_history
)

# In-memory session store: maps token -> user_id
SESSIONS = {}

class ServerHandler(SimpleHTTPRequestHandler):
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()

    def get_user_id_from_auth(self):
        auth_header = self.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            return SESSIONS.get(token)
        return None

    def do_GET(self):
        # ─── API Endpoints ───────────────────────────────────────────────────
        if self.path == '/api/stats':
            user_id = self.get_user_id_from_auth()
            if user_id is None:
                self.send_json({"error": "Unauthorized"}, 401)
                return
            self.send_json(get_session_stats(user_id))
            return

        if self.path == '/api/history':
            user_id = self.get_user_id_from_auth()
            if user_id is None:
                self.send_json({"error": "Unauthorized"}, 401)
                return
            self.send_json({"history": get_query_history(user_id)})
            return

        if self.path == '/':
            self.path = '/code.html'
        return super().do_GET()

    def do_POST(self):
        # ─── API Endpoints ───────────────────────────────────────────────────
        if self.path == '/api/register':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            username = body.get("username", "")
            password = body.get("password", "")
            
            if not username or not password:
                self.send_json({"error": "Username and password are required"}, 400)
                return

            if register_user(username, password):
                self.send_json({"success": True, "message": "User registered successfully"})
            else:
                self.send_json({"error": "Username already exists"}, 409)
            return

        elif self.path == '/api/login':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            username = body.get("username", "")
            password = body.get("password", "")

            user_id = authenticate_user(username, password)
            if user_id is not None:
                token = secrets.token_hex(32)
                SESSIONS[token] = user_id
                self.send_json({"token": token, "username": username})
            else:
                self.send_json({"error": "Invalid username or password"}, 401)
            return

        elif self.path == '/api/logout':
            auth_header = self.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                if token in SESSIONS:
                    del SESSIONS[token]
            self.send_json({"success": True})
            return

        elif self.path == '/api/chat':
            user_id = self.get_user_id_from_auth()
            if user_id is None:
                self.send_json({"error": "Unauthorized"}, 401)
                return

            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            query = body.get("query", "")
            
            if not query:
                self.send_json({"error": "Query is required"}, 400)
                return

            result = coderouter.invoke({"query": query, "user_id": user_id})
            self.send_json(result)
            return

        else:
            self.send_error(404)

if __name__ == '__main__':
    port = 8000
    server = HTTPServer(('0.0.0.0', port), ServerHandler)
    print(f'CodeRouter AI server running at http://localhost:{port}')
    server.serve_forever()
