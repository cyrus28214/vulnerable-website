# 本文件用于SSRF漏洞伪造内网请求的复现
# 假设这是一个内网服务，提供了一些秘密的图片，没有暴露到外网

import http.server
import socketserver

PORT = 8000

# 自定义请求处理类
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/secret-image':
            image_path = "./secret-image.png"
            try:
                with open(image_path, 'rb') as file:
                    self.send_response(200)
                    self.send_header("Content-type", "image/png")
                    self.end_headers()
                    self.wfile.write(file.read())
            except FileNotFoundError:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Image not found")
        else:
            self.send_response(404)
            self.end_headers()

Handler = MyHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running at port {PORT}")
    httpd.serve_forever()