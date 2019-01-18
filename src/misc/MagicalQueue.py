import threading, time
from collections import deque

_SENTINEL = object()

_counter = 0
_inc_lock = threading.Lock()
def getIdentifier():
    res = 0
    global _counter
    with _inc_lock: 
        _counter+=1
        res = _counter
    return res


class MagicalQueue(object):
    def __init__(self, processing_function):
        self.tasks_to_process = deque()
        self.completed_tasks = {}
        self.identifiers_to_locks = {}
        self.processing_function = processing_function
        self.terminate = False 
    
    def add_for_processing(self, opname, *args, **kwargs):
        identifier = getIdentifier()
        lock = threading.Lock()
        self.identifiers_to_locks[identifier] = lock
        self.tasks_to_process.append((identifier, opname, (args, kwargs)))
        lock.acquire()
        return identifier
    
    def get_result(self, identifier, default_value=500):
        if identifier in self.completed_tasks:
            return self.completed_tasks[identifier]
        elif self.terminate:
            return default_value
        
        lock = self.identifiers_to_locks[identifier]
        lock.acquire()

        return self.get_result(identifier, default_value)

    def set_result(self, identifier, result):
        self.completed_tasks[identifier] = result
        self.identifiers_to_locks[identifier].release()
        
    def releaseAllLocks(self):
        for lock in self.identifiers_to_locks.values():
            try:
                lock.release()
            except threading.ThreadError:  # This happens if we release an already released lock
                 pass
    
    def execute_next_task(self):
        try:
            identifier, (className, methodName), (args, kwargs) = self.tasks_to_process.popleft()
            if identifier in self.completed_tasks:
                return  #Skip execution as we already have the result
            self.set_result(identifier, self.processing_function(className, methodName, *args, **kwargs))
        except IndexError:
            pass
