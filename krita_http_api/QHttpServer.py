import sys
import json
from threading import Thread
import time
import traceback
from typing import Callable, Tuple, Union
from PyQt5.QtCore import pyqtSignal, QObject, QThread, QCoreApplication, QEventLoop, QTimer
from PyQt5.QtWidgets import QApplication
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import uuid
from concurrent.futures import ThreadPoolExecutor

from .Logger import Logger




logger = Logger("QHttpServer")

# biz code timeout (ms)
BIZ_TIMEOUT = 5000

class RequestHandler(BaseHTTPRequestHandler):
    
    def send_json_error(self, msg: str):
        response_json = json.dumps({
            'ok': False,
            'msg': msg,
        })

        # Send response status code
        self.send_response_only(200)

        # Send headers
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Connection', 'keep-alive')
        response_bytes = response_json.encode('utf-8')
        self.send_header('Content-Length', str(len(response_bytes)))  # Add Content-Length header
    
        self.end_headers()

        self.wfile.write(response_bytes)

    def __go(self):
        # Get the length of the request body
        if 'Content-Length' not in self.headers:
            logger.warn("No Header 'Content-Length'")
            return self.send_json_error("Header 'Content-Length' is required!")

        content_length = int(self.headers['Content-Length'])
        #logger.info(f"{content_length=}")

        if content_length == 0:
            logger.warn("no request body")
            return self.send_json_error("No Request Body!")
            
        # Read the request body
        try:
            request_body_str = self.rfile.read(content_length).decode('utf-8')
            request_body = json.loads(request_body_str)
            if not isinstance(request_body, dict):
                raise BaseException()
        
        except:
            logger.warn(f"body parse error, got '{request_body_str}'")
            return self.send_json_error("Body must be a JSON Object!")
        
        #logger.info(f"read json body succeed, emit it...")

        start_time = time.time()
        curr_request_id = str(uuid.uuid4())
        # Emit signal with the requested path
        self.server.signal_handler.new_request.emit(curr_request_id, request_body)

        # Wait for the result to be set by the main thread
        loop = QEventLoop()

        response = None
        def on_result_ready(request_id):
            nonlocal response
            if request_id != curr_request_id:
                return
            response = self.server.signal_handler.response[request_id]
            del self.server.signal_handler.response[request_id]
            loop.quit()
        self.server.signal_handler.result_ready.connect(on_result_ready)
        
        timeout = False

        # Set up a QTimer for timeout
        timeout_timer = QTimer()
        timeout_timer.setSingleShot(True)
        def go():
            nonlocal timeout
            timeout = True
            loop.quit()
        timeout_timer.timeout.connect(go)
        timeout_timer.start(BIZ_TIMEOUT)  # Timeout set to 5000 milliseconds (5 seconds)
        loop.exec_()
        timeout_timer.stop()

        if timeout:
            return self.send_json_error(f"respond timeout for {BIZ_TIMEOUT} ms, check your biz code! request body: {request_body_str}")

        end_time = time.time()
        
        #logger.info(f"cost_time: {end_time - start_time} s, response received from krita, responding to client...")

        # Send response status code
        self.send_response_only(200)

        if not isinstance(response, str):
            try:
                response = json.dumps(response)
            except:
                stack_trace = traceback.format_exc()
                logger.warn(stack_trace)
                response = json.dumps({
                    'ok': False,
                    'msg': f"json dump response failed, check your biz code! request body: {request_body_str}",
                    'data': None,
                    'call_stack': stack_trace
                })
        
        # Send headers
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Connection', 'keep-alive')
        response_bytes = response.encode('utf-8')
        self.send_header('Content-Length', str(len(response_bytes)))  # Add Content-Length header
    
        self.end_headers()

        self.wfile.write(response_bytes)

    def do_POST(self):
        self.do_GET()

    def do_GET(self):
        #logger.info(f"start handling...")

        # Record start time
        start_time = time.time()
        
        self.__go()
        
        end_time = time.time()
        #logger.info(f"handling finished, cost time: {end_time - start_time} ms")

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class SignalHandler(QObject):
    new_request = pyqtSignal(str, dict)
    result_ready = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.response = {}

class ServerThread(QThread):
    def __init__(self, signal_handler, port=8080):
        super().__init__()
        self.signal_handler = signal_handler
        self.port = port

    def run(self):
        server_address = ('', self.port)
        httpd = ThreadingHTTPServer(server_address, RequestHandler)
        httpd.request_queue_size
        httpd.signal_handler = self.signal_handler
        logger.info(f'Starting httpd server on port {self.port}...')
        httpd.serve_forever()

class QHTTPServer(QObject):
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.signal_handler = SignalHandler()
        self.server_thread = ServerThread(self.signal_handler, port)
        # Connect signals
        self.signal_handler.new_request.connect(self.__handle_request)

        def go(req: dict, resolve: Callable[[dict], None]):
            resolve({
                'ok': False,
                'msg': 'No Request Handler given.',
                'data': req,
            })
        self.__on_request = go

    def start(self):
        #logger.info(f"HTTP_SERVER port={self.port} starting...")
        self.server_thread.start()

    # TODO make it async using qt event loop
    def on_request(self, cb: Callable[[dict, Callable[[dict], None], Callable[[dict], None]], None]):
        def go(req: dict, resolve: Callable[[dict], None]):
            def ok(res):
                resolve({
                    'ok': True,
                    'data': res
                })
            def fail(msg, res):
                stack_trace = traceback.format_exc()
                resolve({
                    'ok': False,
                    'msg': msg,
                    'data': res,
                    'call_stack': stack_trace,
                })
            return cb(req, ok, fail)
        self.__on_request = go

    def __handle_request(self, req_id, req):
        resolve_called = False
        def resolve(res):
            nonlocal resolve_called
            resolve_called = True
            self.__send_response(req_id, res)
        try:
            self.__on_request(req, resolve)
        except BaseException as e:
            stack_trace = traceback.format_exc()
            logger.warn(f"something bad happened for request {req}; expection: {e}")
            logger.warn(stack_trace)
            if not resolve_called:
                resolve({'ok': False, 'msg': 'something bad happened, check your biz code', 'e': str(e), 'call_stack': stack_trace})
                

    def __send_response(self, req_id, response):
        # Set the response and notify the handler
        self.signal_handler.response[req_id] = response
        self.signal_handler.result_ready.emit(req_id)

