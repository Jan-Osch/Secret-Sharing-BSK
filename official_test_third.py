from Queue import Queue
from Client import Client
from Server import Server
import sys
from threading import active_count, enumerate, current_thread

# jest wielomian:x^2+4x+6 mod 31
# i sa trzy punkty:
# (1,11)
# (3,27)
# (7,21)

passwords = {'alice':   ('2a414846467aadb9872f029787224bdb', 50, 1),
             'bob':     ('b1cf97c60932ab006be914b668ae8f46', 50, 1),
             'charlie': ('11250c7c4e996c15c32fb9cb43695c5d', 50, 1)
            }
keys = {'alice': '1234', 'bob': '4321', 'charlie': '5678'}

server_input_queue = Queue()
server_output_queue = Queue()

server = Server(input_queue=server_input_queue,
                output_queue=server_output_queue,
                p=31,
                passwords=passwords,
                polynomial=[1,4,6],
                keys=keys)
alice = Client(server_input_queue=server_input_queue,
               server_output_queue=server_output_queue,
               name='alice',
               h_0='9944',
               K=50,
               key='1234',
               secret=(1, 11))
bob = Client(server_input_queue=server_input_queue,
             server_output_queue=server_output_queue,
             name='bob',
             h_0='6850',
             K=50,
             key='4321',
             secret=(3, 27))
charlie = Client(server_input_queue=server_input_queue,
                 server_output_queue=server_output_queue,
                 name='charlie',
                 h_0='5478',
                 K=50,
                 key='5678',
                 secret=(7, 21))

assert alice.successfully_finished is None
assert bob.successfully_finished is None
assert charlie.successfully_finished is None

server.start()

alice.start()
bob.start()
charlie.start()

killed = False
alice.join(timeout=30)
bob.join(timeout=30)
charlie.join(timeout=30)
server.finish()
server.join(timeout=30)

if active_count() > 1:
    for t in enumerate():
        if t != current_thread():
            print t
            t._Thread__stop()
    sys.exit(1)

assert alice.successfully_finished is True
assert bob.successfully_finished is True
assert charlie.successfully_finished is True
