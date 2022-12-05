import functools
import time
from collections import defaultdict

import socketio


class AsyncClient:
    _methods = defaultdict(list)

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.io = socketio.Client()

        self.events_data = defaultdict(lambda: None)

        self.on_connect = self.io.on('connect')(self.on_connect)
        self.on_connect_error = self.io.on('connect_error')(self.on_connect_error)
        self.on_disconnect = self.io.on('disconnect')(self.on_disconnect)
        self.on_any_event = self.io.on('*')(
            self.on_any_event
        )

        for method, event in AsyncClient._methods[self.__class__.__name__]:
            setattr(self, method, self.io.on(event)(getattr(self, method)))

    async def connect(self):
        self.io.connect('http://' + self.host + ':' + str(self.port))

    async def disconnect(self):
        self.io.disconnect()

    async def on_connect(self):
        pass

    async def on_connect_error(self, hahaha):
        pass

    async def on_disconnect(self):
        pass

    async def on_any_event(self, event, data):
        self.events_data.__setitem__(event, data)

    async def emit(self, event, data):
        self.io.emit(event, data)

    def wait_for(self, event):
        self.events_data[event] = None
        while self.events_data[event] is None:
            time.sleep(0.1)
        return self.events_data[event]

    @staticmethod
    def io_event(class_name, event):
        def decor(method):
            AsyncClient._methods[class_name].append((method.__name__, event))

            @functools.wraps(method)
            def wrapper(*a, **kw):
                return method(*a, **kw)

            return wrapper

        return decor
