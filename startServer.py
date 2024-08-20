#!/usr/bin/env python
"""
Very simple HTTP server in python (Updated for Python 3.7)
Usage:
    ./startServer.py -h
    ./startServer.py -l localhost -p 8000
Send a POST request:
    curl -d "foo=bar&bin=baz" http://localhost:8000
"""

# show active ports and pids
# netstat -anvp tcp | awk 'NR<3 || /LISTEN/'

import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from multiprocessing import Process
import subprocess
import json
import ada
from ada.ui.uiManager import UIHandler

home_dir = Path.home()

DIRECTORY=home_dir

handler = UIHandler(print_calls=True)

class S(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        self._set_headers()
        content_length = int(self.headers['Content-Length'])
        content = self.rfile.read(content_length)
        contentDict = json.loads(content.decode('utf8'))

        portNumber = int(self.connection.getsockname()[1])

        queryText = contentDict['queryText']
        callMode = contentDict['callMode']
        handler.makeCall(queryText, callMode, portNumber)
        outputText = handler.generateBodyHTML()
        filetreeText = handler.generateFiletreeHTML()
        geometryText = handler.generateGeometryHTML()
        analysisText = handler.generateAnalysisHTML()
        dataText     = handler.generateDataHTML()
        graphicWindow = handler.generateGraphicWindow()

        message = {}
        message['mainBodyText'] = outputText
        message['filetreeText'] = filetreeText
        message['geometryText'] = geometryText
        message['analysisText'] = analysisText
        message['dataText']     = dataText
        message['graphicWindow'] = graphicWindow

        jsn = json.dumps(message)
        self.wfile.write(jsn.encode('utf-8'))


def run(server_class=HTTPServer, handler_class=S, addr="localhost", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting httpd server on {addr}:{port}")
    httpd.serve_forever()

def openBrowser(port=8000):
    sleepTime = 0.25
    subprocess.run(['sleep '+str(sleepTime)+' && open http:/:'+str(port)+'/.ada/index.html -a Safari'],shell=True)

if __name__ == "__main__":
    # try:
    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="localhost",
        help="Specify the IP address on which the server listens",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Specify the port on which the server listens",
    )
    args = parser.parse_args()
    # run(addr=args.listen, port=args.port)
    t1 = Process(target=run, kwargs={"addr":args.listen, "port":args.port})
    t1.start()
    t2 = Process(target=openBrowser,  kwargs={"port":args.port})
    t2.start()

    # except KeyboardInterrupt:
    #     print ('^C received, shutting down the web server')
    # #     server.socket.close()