#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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

        self.header_base = {
            'http': 'HTTP/1.1',
            'status': '200 OK'
        }

        self.data_list = self.data.decode('utf-8').split('\r\n')
        print ("Got a request of: %s\n" % self.data)
        print(self.data_list)

        req_details = self.data_list[0].split()
        req_method = req_details[0]
        req_path = req_details[1]

        if req_method == "GET":
            self.getPath(os.path.abspath("www") + req_path)

        self.request.sendall(bytearray(self.response(),'utf-8'))

    def error404(self):
        self.header_base['status'] = '404 Not Found'

    def handleHeaders(self):
        headers = f'''{self.header_base['http']} {self.header_base['status']}'''
        return headers

    def getPath(self, path):
        print(path)

    def response(self):
        resp = self.handleHeaders()
        return resp

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
