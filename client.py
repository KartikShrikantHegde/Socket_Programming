import socket
import sys

# Create a TCP/IP socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


# Connect the socket to the port where the server is listening

server_address = ('localhost', 8080)
print sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

try:
    # Send data

    message = 'This is the message.  It will be repeated.'
    print sys.stderr, 'sending "%s"' % message
    sock.sendall(message)

    # Look for the response

    amount_received = 0
    amount_expected = len(message)

    while amount_received < amount_expected:
        data = sock.recv(9000)
        amount_received += len(data)
        print sys.stderr, 'received "%s"' % data

finally:
    print sys.stderr, 'closing socket'
    sock.close()