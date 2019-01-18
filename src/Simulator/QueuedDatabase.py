import threading
from Simulator.MagicalQueue import MagicalQueue

_counter = 0
_inc_lock = threading.Lock()
def getIdentifier():
    res = 0
    global _counter
    with _inc_lock: 
        _counter+=1
        res = _counter
    return res

def taskExecutor(opname, *args, **kwargs):
    pass

q = MagicalQueue(taskExecutor)

class CatchAllClass(object):
    def __getattr__(self, name):
        def foo(*args, **kwargs):
            print("Added %d, %s, with params", getIdentifier(), name)
            for arg in args:
                print("Param %s",str(arg))
            q.add_for_processing(getIdentifier(), name, *args, **kwargs)
        return foo

