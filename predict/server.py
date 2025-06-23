from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from azure_insert import register_to_azure  # sales登録関数

class CollectHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            sales = data.get('sales')
            weather_entry = data.get('weather_entry')
            if sales is None:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Missing \"sales\" in request body.')
                return

            register_to_azure(weather_entry, sales)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'success', 'message': 'Sales data registered successfully'}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            error_msg = {'status': 'error', 'message': str(e)}
            self.wfile.write(json.dumps(error_msg).encode('utf-8'))


def start_collect_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, CollectHandler)
    print(f'Collect server running on port {port}...')
    httpd.serve_forever()
if __name__ == '__main__':
    start_collect_server()

