#  coding: utf-8 
import socketserver
import os

# Copyright 2023 Abdullah Khadeli
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# This project is built from CMPUT404-assignment-webserver thus
# some of the code is Copyright © 2013 Abram Hindle, Eddie Antonio Santos
#
# https://github.com/abramhindle/CMPUT404-assignment-webserver
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        # Upon empty data, closure of connection
        if len(self.data.decode('utf-8')) == 0:
            return

        # Setting up some base header values for later use
        self.header_base = {
            'http': 'HTTP/1.1',
            'status': '200 OK',
            'content-type': 'text/html; charset=UTF-8',
            'body': '',
            'location': ''
        }

        # Extracting necessary request details
        self.data_list = self.data.decode('utf-8').split('\r\n')
        req_details = self.data_list[0].split()
        req_method = req_details[0]
        req_path = req_details[1]

        if req_method == "GET":
            self.getPath(req_path)
        else:
            # Limiting to GET
            self.error405()

        self.request.sendall(bytearray(self.response(),'utf-8'))


    def error301(self, location):
        self.header_base['status'] = "301 Moved Permanently"
        self.header_base['content-type'] = "text/html; charset=UTF-8"

        # Location is set by function caller
        self.header_base['location'] = location

        # Simple body for 301 Moved Permanently
        self.header_base['body'] = '''  <!DOCTYPE html>
                                        <html>
                                        <head>
                                            <title>301 Moved Permanently</title>
                                                <meta http-equiv="Content-Type"
                                                content="text/html;charset=utf-8"/>
                                        </head>
                                        <body>
                                            <p>301 Moved Permanently<p>
                                        </body>
                                        </html> 
                                    '''


    def error404(self):
        self.header_base['status'] = "404 Not Found"
        self.header_base['content-type'] = "text/html; charset=UTF-8"

        # Simple body for 404 Not Found
        self.header_base['body'] = '''  <!DOCTYPE html>
                                        <html>
                                        <head>
                                            <title>404 Not Found</title>
                                                <meta http-equiv="Content-Type"
                                                content="text/html;charset=utf-8"/>
                                        </head>
                                        <body>
                                            <p>404 Not Found<p>
                                        </body>
                                        </html> 
                                    '''
    
    def error405(self):
        self.header_base['status'] = "405 Method not allowed"


    def response(self):
        # Final function call, prepping the response
        headers = self.header_base['http'] + " " + self.header_base['status'] + "\r\n"
        headers += "Content-Type: " + self.header_base['content-type'] + "\r\n"
        headers += "Content-Length: " + str(len(self.header_base['body'].encode('utf-8'))) + "\r\n"
        headers += "Connection: close\r\n"
        headers += "Location: " + self.header_base['location'] + "\r\n"
        headers += "\r\n" + self.header_base['body'] + "\r\n"
        return headers


    def getPath(self, path):
        # File access is built around the absolute path to www
        root_path = os.path.abspath("www")

        # For accessing relative path provided by URI
        root_length = len(root_path)

        # Clean up multiple consecutive slashes and break .. for security
        cleaned_path = ""
        for i in range(len(path)):
            if path[i] == "?":
                break
            if path[i] == "/":
                if i+1 < len(path):
                    if path[i+1] == "/":
                        continue
            if path[i] == ".":
                if i+1 < len(path):
                    if path[i+1] == ".":
                        continue
            cleaned_path += path[i]
        
        # Further slash cleanup
        if cleaned_path == "/":
            path_list = ['']
        else:
            path_list = cleaned_path.split('/')[1:]

        # Loop to check paths, will catch onto non existent paths
        # before the whole path is parsed
        for p in path_list:
            if p == "":
                root_path += "/"
            elif os.path.exists(root_path + "/" + p):
                root_path += "/" + p
            else:
                self.error404()
                return
        
        # Ensuring that slashes after a directory will send index.html
        # additional safety for when a slash is added after a file path
        root_path_split = root_path.split('/')
        if root_path.endswith('/'):
            if not ("html" in root_path_split[-2] or ".css" in root_path_split[-2]):
                root_path += "index.html"
            else:
                self.error301(root_path[root_length:-1])
                return

        # Retrieving body
        self.getFile(root_path, root_length)
        return


    def getFile(self, path, root_length):
        # Enforcing that paths leading to directories need a slash
        if os.path.isdir(path):
            self.error301(path[root_length:] + "/")
            return
        try:
            # Adding support for html and css MIME types
            if path.endswith('.html'):
                self.header_base['content-type'] = "text/html; charset=UTF-8"
            if path.endswith('.css'):
                self.header_base['content-type'] = "text/css; charset=UTF-8"
            with open(path) as file:
                self.header_base['body'] = file.read()
            return
        # Conditions to handle possible errors
        except FileNotFoundError:
            self.error404()
            return
        except NotADirectoryError:
            self.error404()
            return


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.ThreadingTCPServer.allow_reuse_address = True
    # # Create the server, binding to localhost on port 8080
    # ADDITION added multithreading support for more reliability
    server = socketserver.ThreadingTCPServer((HOST, PORT), MyWebServer)

    # # Activate the server; this will keep running until you
    # # interrupt the program with Ctrl-C
    server.serve_forever()
