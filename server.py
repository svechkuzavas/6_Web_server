import os
import socket
import datetime


class HTTPServer:
    def __init__(self, port):
        self._port = port

    def run(self):
        serv_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM)
        try:
            serv_sock.bind(('', self._port))
            serv_sock.listen(1)
            print(f"Server is started and listening on port {self._port}")
            while True:
                conn, addr = serv_sock.accept()
                print(f"New connection: {str(addr)}")
                try:
                    self.handle_client(conn)
                except Exception as e:
                    print('Client handling failed', e)
        finally:
            serv_sock.close()

    def handle_client(self, conn):
        try:
            req = self.parse_request(conn)
            self.send_response(conn, req['data'])
        except ConnectionResetError:
            conn = None
        except Exception as e:
            self.send_error(conn, e)
        if conn:
            conn.close()

    def parse_request(self, conn):
        rfile = conn.makefile('r')
        raw = rfile.readline(64*1024 + 1).split()
        filename = '/index' if raw[1] == '/' else raw[1]
        return {
            'method': raw[0],
            'route': raw[1],
            'data': self.read_file(filename) if raw[1] != '/close' else 'Server closed',
        }

    def read_file(self, route):
        with open(os.path.join('data', f'{route[1:]}.html')) as f:
            return ''.join(f.readlines())

    def send_response(self, conn, resp_body):
        response = f"""HTTP/1.1 200 OK
Server: KirillZaycevWebServer v0.0.1
Content-type: text/html
Connection: close
Date: {datetime.date.today()}
Content-length: {len(resp_body)}


{resp_body}"""
        conn.send(response.encode('utf-8'))

    def send_error(self, conn, err):
        print(err)


if __name__ == '__main__':
    server = HTTPServer(8080)
    server.run()