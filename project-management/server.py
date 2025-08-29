#!/usr/bin/env python3
import http.server
import socketserver
import json
import urllib.parse
from pathlib import Path

class BacklogHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/save-backlog':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                backlog_data = json.loads(post_data.decode('utf-8'))
                with open('backlog.json', 'w') as f:
                    json.dump(backlog_data, f, indent=2)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"status": "saved"}')
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
        else:
            super().do_POST()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

PORT = 8080
with socketserver.TCPServer(("", PORT), BacklogHandler) as httpd:
    print(f"Server running at http://localhost:{PORT}")
    httpd.serve_forever()