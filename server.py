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
my_localhost_server.listen(10)
threads = []


class ProxyThread(threading.Thread):
    # Calling the constructor and passing the URL and client_address

    def __init__(self, header_split, client):
        threading.Thread.__init__(self)
        self.header_split = header_split
        self.client = client

    # Calling the thread run method
    def run(self):

        # Getting the request_type and header_split from the http_header received from User
        request_type = self.header_split[0]  # GET
        request_url = self.header_split[1][1:]  # www.google.com
        print "* Request type is %s: %s" % (request_type, request_url)
        log_file = open(os.getcwd() + "/log.txt", "a")
        log_file.write("\n******** Request-Response Cycle ***********" + "\n\n")
        log_file.write("* Request type is %s: %s\n\n" % (request_type, request_url))
        log_file.close()

        try:
            # Check if the Requested cache file is available in the Cache
            start_clock = int(round(time.time() * 1000))
            cache_file = os.getcwd() + request_url
            # Opening the file if it is present and writing to log
            cache_file_read = open(cache_file, "r")
            cache_file_contents = cache_file_read.read()
            print "* The file already exists in the cache"
            log_file = open(os.getcwd() + "/log.txt", "a")
            log_file.write("* The file already exists in the cache\n")
            log_file.write("HTTP/1.0 200 OK\n")
            log_file.write("Content-Type:text/html\n")
            log_file.close()

            print "* Sending file from cache to the Browser"
            print "* Success! Sent the response to client browser from Cache. Check the browser.\n"
            print ("NOTE: Any Further request are related to images which cannot be fetched due to relative path. "
                   "Eg: Like fevicon.io file are logos which can not be fetched" + "\n")

            # Sending the cache response to client from cache

            for content in range(0, len(cache_file_contents)):
                self.client.send(cache_file_contents[content])

            # Calculating the RTT time for processing the User Request
            end_clock = int(round(time.time() * 1000))
            print ("* Round Trip Time using Cache in mili-seconds : " + str(end_clock - start_clock) + "\n")
            print ("******** End of Request ***********" + "\n")
            # Opening the Log file
            log_file = open(os.getcwd() + "/log.txt", "a")
            # Calculating the Round Trip Time log_filer the whole Request and writing it to the log file
            log_file.write("* Successfully sent the response from Cache to the Web Browser" + "\n\n")
            log_file.write("* Round Trip Time using Cache in mili-seconds : " + str(end_clock - start_clock) + "\n\n")
            log_file.write(
                "NOTE: Any Further request are related to images which cannot be fetched due to relative path. "
                "Eg: Like favicon.ico file are logos which can not be fetched" + "\n\n")
            log_file.write("******** End of File ***********" + "\n\n")
            log_file.close()

        # If Cache is not present then, then reroute the request to original server.
        except IOError:

            # Connecting the Proxy Server to HTTP port 80 to get the Client Object from the Original Server
            proxy_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                proxy_server.connect((request_url, 80))
                print "* First time Request - Thus file was not found in the cache."
                print '* Fetching from Original Server. Proxy server successfully connected to the port 80 of Original Server.'
                # Start the timer
                start_clock = int(round(time.time() * 1000))
                # Send the request
                proxy_server.send("GET / HTTP/1.0\r\nHost: " + request_url + "\r\n\r\n")
                # Read data into temp file
                temp = recv_timeout(proxy_server)

                # Create a temp file and save the new request in the cache
                tempfile = open(os.getcwd() + request_url, "wb")
                tempfile.write(temp)
                tempfile.close()

                # Send the response to the client socket
                self.client.send(temp)

                proxy_server.close()
                self.client.close()
                print "* Success! Sent the response to client browser from Original server. Check the Browser.\n"

                # Calculating the end time to fetch from original Server
                end_clock = int(round(time.time() * 1000))
                print ("* Round Trip Time using Cache in mili-seconds : " + str(end_clock - start_clock) + "\n")
                print ("NOTE: Any Further request are related to images which cannot be fetched due to relative path. "
                   "Eg: Like fevicon.io file are logos which can not be fetched" + "\n")
                print ("******** End of Request ***********" + "\n")
                log_file = open(os.getcwd() + "/log.txt", "a")
                # Calculating the Round Trip Time and logging it in the Log File
                log_file.write("* First time Request - Thus file was not found in the cache. " + "\n\n")
                log_file.write("* Proxy server successfully connected to the port 80 of Original Server. " + "\n\n")
                log_file.write("* Fetching and sending the response from the Original Server. " + "\n\n")
                log_file.write("* Success! Sent response to browser from Original server And saved file in Cache. " + "\n\n")
                log_file.write("* Round Trip Time for first request in mili-seconds : " + str(end_clock - start_clock) + "\n\n")
                log_file.write("NOTE: Any Further request are related to images which cannot be fetched due to relative path. "
                                "Eg: Like favicon.ico file are logos which can not be fetched" + "\n\n")
                log_file.write("******** End of File ***********" + "\n\n")
                log_file.close()

                self.client.close()
            except socket.gaierror:
                print '* Illegal URL. Please enter correct address.'
                log_file = open(os.getcwd() + "/log.txt", "a")
                log_file.write("* Illegal URL. Please enter correct address. No Cache created for this. " + "\n\n")
                log_file.close()
                self.client.close()
            # Handling 404 Page not found error
            except Exception as error:
                print error
                self.client.close()

        self.client.close()

# Getting the response from the original server.

def recv_timeout(the_socket,timeout=2):
    #make socket non blocking
    the_socket.setblocking(0)

    #total data partwise in an array
    total_data=[]
    data=''

    #beginning time
    begin=time.time()
    while 1:
        #if you got some data, then break after timeout
        if total_data and time.time()-begin > timeout:
            break

        #if you got no data at all, wait a little longer, twice the timeout
        elif time.time()-begin > timeout*2:
            break

        #recv something
        try:
            data = the_socket.recv(8192)
            if data:
                total_data.append(data)
                #change the beginning time for measurement
                begin = time.time()
            else:
                #sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass

    #join all parts to make final string
    return ''.join(total_data)



while True:
    # Start receiving data from the client
    print "\n***** About to Start the server********\n"
    print '* Server Initialized'
    print '* Server Started'
    print '* Enter the URL in Browser\n'
    # Calculating the beginning time of Request

    try:
        # Accept a connection from client
        client, client_address = my_localhost_server.accept()
    except Exception:
        print '* Received Request from Web Browser from address: ', client_address
        print "* Unable to establish the connection to server"

    print '* Success! Received Request from Web Browser at address: ', client_address
    # Receives data from Socket
    # This is request header received from browser
    http_header = client.recv(1024)
    # Split the header
    header_split = http_header.split()
    if len(header_split) <= 1:
        continue
    url = header_split[1]  # this is /www.msn.com

    try:
        # Getting Content-Length(Response-Length) from the Data Received
        response_status_code = requests.head("http://" + url[1:])
        response_headers = response_status_code.headers
        header_len = str(len(http_header))
        response_content_length = response_headers['Content-Length']
        # Creating Log file
        log_file = open(os.getcwd() + "/log.txt", "a")
        log_file.write("\n******** Writing Details about Client or Web Browser ***********" + "\n\n")
        log_file.write("Client url is: " + header_split[4] + "\n")
        log_file.write("Host Client IP Address: " + socket.gethostbyname(str(url[1:])) + "\n")
        log_file.write("Host Name: " + str(url[1:]) + "\n")
        log_file.write("Local Port: 8080" + "\n")
        log_file.write("\n******** Writing Details about HTTP Messeges ***********" + "\n\n")
        log_file.write("Request Length: " + header_len + "\n")
        log_file.write("Response Length: " + response_content_length + "\n\n")
        log_file.write("******** Http Request Header Information ***********")
        log_file.write("\n\n" + http_header)
        log_file.write("******** End of Request Header Information ***********\n")
        log_file.close()
    # Handling Exception
    except Exception as error:
        print "* Error getting the request headers"

    # Creating thread log_filer each request
    thread = ProxyThread(header_split, client)
    thread.start()
    threads.append(thread)

    for singleThread in threads:
        singleThread.join()

my_localhost_server.close()
