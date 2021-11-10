import socket
import os

def get_route(req):
    method, route = '', ''
    try:
        head_data = req.split('\n')[0]
        method, route, protocol = head_data.split(' ')
        return {
            'method': method,
            'route': route,
            'data': response_data(route) if route != '/close' else 'Server closed',
        }
    except Exception as e:
        return None


def response_data(route):
    with open(os.path.join('data', route[1:])+".html") as f:
        return ''.join(f.readlines())


sock = socket.socket()

try:
    sock.bind(('', 80))
    print("Using port 80")
except OSError:
    sock.bind(('', 8080))
    print("Using port 8080")

sock.listen(5)

conn, addr = sock.accept()
print("Connected", addr)
data = conn.recv(8192)

msg = data.decode()
routing = get_route(msg)
resp = f"""HTTP/1.1 200 OK
    Server: SelfMadeServer v0.0.1
    Content-type: text/html
    Connection: close

    {routing['data']}"""
conn.send(resp.encode())

while routing is None or routing['route'] != '/close':
    data = conn.recv(8192)
    msg = data.decode()
    routing = get_route(msg)

    resp = f"""HTTP/1.1 200 OK
    Server: SelfMadeServer v0.0.1
    Content-type: text/html
    Connection: close
    
    {routing['data']}"""
    conn.send(resp.encode())
conn.close()