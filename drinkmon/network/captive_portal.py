"""
Captive portal server logic and HTML template loading.
Implements captive portal server and HTML template loader.
"""
import socket
import machine
import utime as time
import uasyncio as asyncio

def load_html_template(file_path: str = "./drinkmon/network/config.html") -> str:
    """
    Load the captive portal HTML template from an external file.
    """
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading HTML template: {e}")
        return "<html><body><h2>Setup Page Unavailable</h2></body></html>"

async def captive_portal_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    s.setblocking(False)
    print('Listening on', addr)
    html_template = load_html_template()
    while True:
        try:
            cl, addr = s.accept()
        except OSError:
            await asyncio.sleep_ms(10)
            continue
        req = b""
        while True:
            try:
                data = cl.recv(1024)
                if not data: break
                req += data
                if b"\r\n\r\n" in req: break
            except OSError:
                await asyncio.sleep_ms(1)
                continue
        req_str = req.decode()
        if req_str.startswith("GET / "):
            cl.send(b"HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
            cl.sendall(html_template.encode())
        elif req_str.startswith("POST /save"):
            body = req_str.split('\r\n\r\n', 1)[1]
            params = {}
            for pair in body.split('&'):
                k, v = pair.split('=', 1)
                params[k] = v  # URL decode to be handled in config_manager
            cl.send(b"HTTP/1.0 200 OK\r\n\r\nSaved! Restarting...")
            cl.close()
            time.sleep(2)
            machine.reset()
            return
        cl.close()
