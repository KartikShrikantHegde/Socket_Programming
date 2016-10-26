import BaseHTTPServer
import hashlib
import os
import urllib2

class CacheHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
      m = hashlib.md5()
      m.update(self.path)
      cache_filename = m.hexdigest() + ".cached"
      if os.path.exists(cache_filename):
          print "Cache hit"
          data = open(cache_filename).readlines()
      else:
          print "Cache miss"
          data = urllib2.urlopen("http:/" + self.path).readlines()
          open(cache_filename, 'wb').writelines(data)
      self.send_response(200)
      self.end_headers()
      self.wfile.writelines(data)

def run():
    server_address = ('', 8000)
    httpd = BaseHTTPServer.HTTPServer(server_address, CacheHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    run()