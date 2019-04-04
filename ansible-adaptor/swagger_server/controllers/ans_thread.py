import threading

class ThreadLocal(threading.local):

    def __init__(self):
        self.data = {}

    def set(self, name, val):
        self.data[name] = val

    def get(self, name, default=''):
        # if hasattr(threadContext, name):
        return self.data.get(name, default)

threadLocal = ThreadLocal()