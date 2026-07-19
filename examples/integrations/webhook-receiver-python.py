import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from sustainable_catalyst_lab import verify_webhook
SECRET = "replace-with-one-time-subscription-secret"
class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body=self.rfile.read(int(self.headers.get("Content-Length","0")))
        ok=verify_webhook(SECRET,self.headers.get("X-SC-Lab-Timestamp",""),body,self.headers.get("X-SC-Lab-Signature",""))
        self.send_response(204 if ok else 401); self.end_headers()
HTTPServer(("127.0.0.1",8787),Handler).serve_forever()
