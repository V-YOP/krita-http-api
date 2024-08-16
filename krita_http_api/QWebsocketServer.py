from websockets import WebSocketServerProtocol
import asyncio
import websockets
import json
import traceback
from krita import *
from .utils import *
from PyQt5.QtCore import *



# 创建一个 Semaphore 对象，限制最大并发任务数
MAX_CONCURRENT_TASKS = 10
semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

class SignalHandler(QObject):
    new_request = pyqtSignal(str)
    result_ready = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    @pyqtSlot(str)
    def result_ready_emit(self, body):
        print('result_ready: me dynamicly emit')
        self.result_ready.emit(body)
    @pyqtSlot(object)
    def result_ready_connect(self, go):
        print('result_ready: me dynamicly connect')
        def mygo(r):
            go(r)
            self.result_ready.disconnect(mygo)
        self.result_ready.connect(mygo)

    @pyqtSlot(str)
    def new_request_emit(self, body):
        print('new_request_emit: me dynamicly emit')
        self.new_request.emit(body)

    @pyqtSlot(object)
    def new_request_connect(self, go):
        print('new_request: me dynamicly connect')
        def mygo(r):
            go(r)
            self.new_request.disconnect(mygo)
        self.new_request.connect(mygo)
        

class QWebsocketServer(QThread):
    def __init__(self, port=8765):
        super().__init__()
        self.__signal_handler = SignalHandler()
        self.__port = port
        self.clients: dict[str, WebSocketServerProtocol] = {}
        def default_request_handler(request_body):
            # at Qt Event Loop here
            print('new_request emitted, (i.e. emit result_ready) with request:', request_body)
            self.__signal_handler.result_ready.emit(request_body) 
        self.__request_handler = default_request_handler
        

    async def __per_message(self, websocket: WebSocketServerProtocol, message: str):
        # 2. wait for result ready (use Future)
        loop = asyncio.get_event_loop()
        future: asyncio.Future[str] = loop.create_future()
        def go(response_body):
            loop.call_soon_threadsafe(lambda: future.set_result(response_body))
        
        QMetaObject.invokeMethod(self.__signal_handler, "result_ready_connect", Q_ARG(object, go))
        
        # 1. emit new_request
        self.__signal_handler.new_request.emit(message)

        # TODO 3. wait and send result
        try:
            print('before resolve')
            result = await future
            print('after resolve')
        except asyncio.TimeoutError:
            result = json.dumps(dict(
                ok=False,
                data='TIMEOUT'
            ))

        await websocket.send(result)

    async def __echo(self, websocket: WebSocketServerProtocol, path: str) -> None:
        # 为每个连接生成唯一标识符
        connection_id = str(uuid.uuid4())
        
        # 将客户端添加到字典中
        self.clients[connection_id] = websocket
        print(f"Client connected: {connection_id}")

        try:
            async for message in websocket:
                async with semaphore:
                    asyncio.create_task(self.__per_message(websocket, message))
        
        except websockets.ConnectionClosed:
            print(f"Client disconnected: {connection_id}")
        finally:
            if connection_id in self.clients:
                del self.clients[connection_id]
                print(f"Client removed from list: {connection_id}")

    async def __main(self):
        async with websockets.serve(self.__echo, "localhost", self.__port):
            print("Server started...")
            await asyncio.Future()  # run forever

    def on_request(self, cb: Callable[[dict, Callable[[dict], None], Callable[[dict], None]], None]):
        # self.__request_handler = None
        assert cb is not None
        def resolve(msg: dict):
            self.__signal_handler.result_ready.emit(json.dumps(msg)) 
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

        def __on_request(request_body):
            # at Qt Event Loop here
            print('new_request emitted, (i.e. emit result_ready) with request:', request_body)
            try:
                request_json = json.loads(request_body)
            except:
                return fail("expect a json object, got ...(check 'data' field)", request_body)
            return cb(request_json, ok, fail) 
            
        self.__request_handler = __on_request
        self.__signal_handler.new_request.connect(self.__request_handler)

    def run(self):  
        asyncio.run(self.__main())
