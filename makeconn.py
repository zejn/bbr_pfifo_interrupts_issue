import socket
import sys
import time


def conn(addr):
    s = socket.socket()
    s.connect(addr)
    s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
    s.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, 10)
    s.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 1)
    s.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 4)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    try:
        for x in range(100):
            s.send(b'.')
            time.sleep(1)

        time.sleep(1000)
    except KeyboardInterrupt:
        s.close()

if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    conn((host, port))
