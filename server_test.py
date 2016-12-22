import socket
import threading
import time
import os
import requests

# Create the Port and initiate the socket connection

my_port = 8080
my_localhost_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Binding and Listening using Socket

my_localhost_server.bind(('127.0.0.1', my_port))
my_localhost_server.listen(300)
threads = []
start_clock = 0
counter = 0


class ProxyThread(threading.Thread):
    # Used to assign a particular thread variable to its object

    def __init__(self, header_split, client):
        threading.Thread.__init__(self)
        self.header_split = header_split
        self.client = client

    def run(self):
        # Caching a Request
        # Getting the request_type and header_split from the http_header received from User
        request_type = self.header_split[0]  # GET
        request_url = self.header_split[1][1:]  # www.google.com
        print "Request is to %s: %s" % (request_type, request_url)

        # Searching if the Request is available in the Cache
        cache_file = os.getcwd() + "/Cache/" + request_url

        try:
            # Opening the file if it is present
            file = open(cache_file, "r")
            cache_file_contents = file.read()
            print "The file already exists in the cache \n\n"

            # If the file is present then Proxy will send the Data
            # for f in range(0, len(cache_file_contents)):
            #     print (cache_file_contents[f])
            self.client.send(cache_file_contents)
            print "Started reading file from cache\n"
            # Calculating the time end time of processing the User Request
            end_clock = int(round(time.time() * 1000))
            # Opening the Log file
            log_file = open(os.getcwd() + "/Cache/log.txt", "a")
            # Calculating the Round Trip Time log_filer the whole Request and writing it to the log file
            log_file.write("Round Trip Time: " + str(end_clock - start_clock) + "\n" + "\n" + "\n" + "\n")
            log_file.close()

        # When the file is not there in the cache and exception is generated
        except IOError:
            print "File not in the cache"
            # Connecting the Proxy Server to HTTP port 80 to get the Client Object from the Original Server
            proxyServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # Connecting the proxy to port 80 with the requested client_address
                # hostn = request_url.replace("www.", "", 1)
                # print hostn
                proxyServer.connect((request_url, 80))
                print request_url
                print 'Socket successfully connected to the port 80 of the host'
                proxyNewFile = proxyServer.makefile('r', 0)
                # Putting the GET Request to the Server
                print "----------------"
                print request_url
                proxyNewFile.write("GET / HTTP/1.0\r\nHost: " + request_url + "\r\n\r\n")

                # Take a temporary variable and record data in it
                buffer = proxyNewFile.read()
                print "----------------"
                print buffer
                # Raising an Exception if the errors are 400 and 405"
                if "400" in buffer[0]:
                    raise ValueError('400 Bad Request')
                elif "405" in buffer[0]:
                    raise ValueError('405 Method Not Allowed')

                # Create a file log_filer the new request in the cache, Send the response to the client socket
                bufferFile = open(os.getcwd() + "/Cache/" + request_url, "wb")
                bufferFile.write(buffer)
                self.client.send(buffer)

                # Calculating the end time when the object is brought from the original Server
                end_clock = int(round(time.time() * 1000))
                log_file = open(os.getcwd() + "/Cache/log.txt", "a")
                # Calculating the Round Trip Time and logging it in the Log File
                log_file.write("Round Trip Time: " + str(end_clock - start_clock) + "\n" + "\n" + "\n" + "\n")
                log_file.close()
            except socket.gaierror:
                print 'Illegal Request'
                self.client.close()
            # Handling 404 Page not log_fileund error
            except Exception as error:
                print error
                # Handling any other Exception


while True:
    # Start receiving data from the client
    print "Server Initialized"
    print 'Server Started'
    print 'Enter the URL in Browser'
    if counter == 0:
        # Calculating the beginning time of Request
        start_clock = int(round(time.time() * 1000))
    try:
        # Accept a connection from client
        client, client_address = my_localhost_server.accept()

    except Exception:
        print "Cannot connect"

    print 'Request from client at: ', client_address
    # Recieves data from Socket
    # This is request header
    http_header = client.recv(1024)
    # Split the header
    header_split = http_header.split()

    if len(header_split) <= 1:
        continue
    url = header_split[1]  # this is /www.google.com
    try:
        # Getting Content-Length(Response-Length) from the Data Received
        response_status_code = requests.head("http://" + url[1:])
        response_headers = response_status_code.headers
        http_headerLength = str(len(http_header))
        response_content_length = response_headers['Content-Length']
        # Creating Log file
        log_file = open(os.getcwd() + "/Cache/log.txt", "a")
        log_file.write("Host Client Address: " + socket.gethostbyname(str(url[1:])))
        log_file.write("\nHost Name: " + str(url[1:]) + "\n")
        log_file.write("Local Port: 8080\n")
        log_file.write("Request Length: " + http_headerLength + "\n")
        log_file.write("Response Length: " + response_content_length + "\n")
        log_file.write("\n\n\n" + http_header)
        log_file.close()
    # Handling Exception
    except Exception as error:
        print "Error getting the response headers"

    # Creating thread log_filer each request (Multithreading)
    thread = ProxyThread(header_split, client)
    thread.start()
    threads.append(thread)

    for singleThread in threads:
        singleThread.join()
