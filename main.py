from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
from forecast import predict_sales

class PredictHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 予測を取得
            prediction = predict_sales()

            # 結果辞書を作成
            result = {
                "predicted_sales": prediction
            }

            # JSONファイルに保存
            with open("predicted_sales.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)

            # ここでファイルから読み込んでレスポンスに使う
            with open("predicted_sales.json", "r", encoding="utf-8") as f:
                response_data = f.read()

            # HTTP 200 OK を送る
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()

            # ファイルの内容をそのままレスポンスに書き込む
            self.wfile.write(response_data.encode("utf-8"))

        except Exception as e:
            error_result = {"error": str(e)}
            error_json = json.dumps(error_result, ensure_ascii=False)

            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(error_json.encode("utf-8"))


def run():
    server_address = ('0.0.0.0', 5000)
    httpd = HTTPServer(server_address, PredictHandler)
    print("Starting server on port 5000...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
