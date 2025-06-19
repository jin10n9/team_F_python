from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
from forecast import predict_sales

class PredictHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            prediction = predict_sales()  # forecast.py の関数を想定
            result = {
                "predicted_sales": prediction
            }
            self.send_response(200)
        except Exception as e:
            result = {"error": str(e)}
            self.send_response(500)

        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))


def run():
    server_address = ('0.0.0.0', 5000) #どのサーバからでも通信できる設定
    httpd = HTTPServer(server_address, PredictHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run()
