import os
import socket
import datetime
import config
import threading
import logging
import base64


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
            logging.info(f"Server is started and listening on port {self._port}")
            while True:
                conn, addr = serv_sock.accept()
                logging.info(f"New connection: {str(addr[0])}:{str(addr[1])}")
                try:
                    t = threading.Thread(target=self.handle_client, args=(conn,))
                    t.start()
                except Exception as e:
                    logging.info(f'Client handling failed {addr}', e)
        finally:
            serv_sock.close()

    def handle_client(self, conn):
        try:
            req = self.parse_request(conn)
            self.send_response(req['status_code'], conn, req['data'], req['message'])
        except ConnectionResetError:
            conn = None
        except Exception as e:
            self.send_error(conn, e)
        if conn:
            conn.close()

    def parse_request(self, conn):
        rfile = conn.makefile('r')
        raw = rfile.readline(64*1024 + 1).split()
        status_code = 200
        filename = '/index.html' if raw[1] == '/' else raw[1]
        response_obj = {
            'status_code': 200,
            'method': raw[0],
            'route': raw[1],
            'data': '',
            'message': 'OK'
        }
        if filename.split('.')[1] in ['jpg', 'jpeg', 'png']:
            try:
                with open(os.path.join(config.PATH, filename[1:]), 'rb') as f:
                    response_obj['data'] = f"""<html><head></head><body><img src="data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"/></body></html>"""
            except Exception as e:
                response_obj['status_code'] = 404
                response_obj['data'] = self.read_file('/404.html')
                response_obj['message'] = 'NotFound'
                return response_obj
        else:
            try:
                data = self.read_file(filename) if raw[1] != '/close' else 'Server closed'
                response_obj['data'] = data
            except Exception as e:
                response_obj['status_code'] = 404
                response_obj['data'] = self.read_file('/404.html')
                response_obj['message'] = 'NotFound'
                logging.info(f"{' '.join(raw)} -> HTTP/1.1 {response_obj['status_code']} {response_obj['message']}")
                return response_obj
        if not filename.split('.')[1] in ['js', 'html', 'css', 'jpg', 'png', 'jpeg']:
            response_obj['status_code'] = 403
            response_obj['data'] = self.read_file('/403.html')
            response_obj['message'] = 'Forbidden'
            logging.info(f"{' '.join(raw)} -> HTTP/1.1 {response_obj['status_code']} {response_obj['message']}")
            return response_obj

        logging.info(f"{' '.join(raw)} -> HTTP/1.1 {response_obj['status_code']} {response_obj['message']}")
        return response_obj

    def read_file(self, route):
        with open(os.path.join(config.PATH, f'{route[1:]}')) as f:
            return ''.join(f.readlines())

    def send_response(self, status_code, conn, resp_body, message):
        response = f"""HTTP/1.1 {status_code} {message}
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
    logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG, filename='server.log', filemode='a')
    server = HTTPServer(config.PORT)
    server.run()