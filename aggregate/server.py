
from threading import Thread

import zmq
from zmq.eventloop import ioloop


class Aggregator(object):
    def __init__(self):
        self.data = {}

    
    def insert(self, tags, values):
        key = frozenset(tags.items())
        try:
            rec = self.data[key]
        except KeyError:
            rec = self.data[key] = values.copy()
        else:
            for i, v in values.iteritems():
                rec[i] += v

        

    def select(self, group_by=[], where={}):
        if not group_by and not where:
            return [dict(list(k)+v.items()) for k,v in self.data.iteritems()]
        a = Aggregator()
        for k, v in self.data.iteritems():
            matched = 0
            for key_k, key_v in k:
                if where.get(key_k) == key_v:
                    matched += 1
                else:
                    break
            if matched < len(where):
                continue
            a.insert(dict((kk, vv) for kk,vv in k if kk in group_by),
                     v)
        return a.select()

    def clear(self):
        self.data = {}


def ctl(aggregator):
    context = zmq.Context.instance()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5557")
    while True:
        cmd, args, kwargs = socket.recv_pyobj()
        ret = getattr(aggregator, cmd)(*args, **kwargs)
        socket.send_pyobj(ret)

if __name__ == "__main__":
    context = zmq.Context.instance()
    socket = context.socket(zmq.SUB)
    socket.bind("tcp://*:5556")
    socket.setsockopt(zmq.SUBSCRIBE,'')
    a = Aggregator()
    statthread = Thread(target=ctl, args=(a,))
    statthread.start()
        
    while True:
        q = socket.recv_pyobj()
        a.insert(*q)