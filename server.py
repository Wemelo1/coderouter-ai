import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from workflow import coderouter
from cost_tracker import get_session_stats

class ServerHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(get_session_stats()).encode())
            return
        if self.path == '/':
            self.path = '/code.html'
        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/chat':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            result = coderouter.invoke({"query": body["query"]})
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_error(404)

if __name__ == '__main__':
    port = 8000
    server = HTTPServer(('0.0.0.0', port), ServerHandler)
    print(f'CodeRouter AI server running at http://localhost:{port}')
    server.serve_forever()
