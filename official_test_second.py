import sys
import threading
from Queue import Queue
from threading import active_count, current_thread

from Client import Client
from Server import Server
from Utils import hash_n_times

# jest wielomian:x^2+4x+6 mod 31
# i sa trzy punkty:
# (1,11)
# (3,27)
# (7,21)

keys = {'alice': '1234', 'bob': '4321', 'charlie': '5678', 'david': '8812', 'edvard': '1111'}

server_input_queue = Queue()
server_output_queue = Queue()


def com_po(number, polynomial):
    result = 0
    for index, coefficient in enumerate(reversed(polynomial)):
        result += coefficient * number ** index
    return result


poly = [1, 4, 6, 5, 2]
alice = Client(server_input_queue=server_input_queue,
               server_output_queue=server_output_queue,
               name='alice',
               h_0='9944',
               K=50,
               key='1234',
               secret=(1, com_po(1, poly) % 31))
bob = Client(server_input_queue=server_input_queue,
             server_output_queue=server_output_queue,
             name='bob',
             h_0='6850',
             K=50,
             key='4321',
             secret=(3, com_po(3, poly) % 31))
charlie = Client(server_input_queue=server_input_queue,
                 server_output_queue=server_output_queue,
                 name='charlie',
                 h_0='5478',
                 K=50,
                 key='5678',
                 secret=(7, com_po(7, poly) % 31))
david = Client(server_input_queue=server_input_queue,
               server_output_queue=server_output_queue,
               name='david',
               h_0='7788',
               K=50,
               key='8812',
               secret=(8, com_po(8, poly) % 31))
edvard = Client(server_input_queue=server_input_queue,
                server_output_queue=server_output_queue,
                name='edvard',
                h_0='9977',
                K=50,
                key='1111',
                secret=(1, com_po(1, poly) % 31))

passwords = {'alice': (hash_n_times(alice.h_0, 50), 50, 1),
             'bob': (hash_n_times(bob.h_0, 50), 50, 1),
             'charlie': (hash_n_times(charlie.h_0, 50), 50, 1),
             'david': (hash_n_times(david.h_0, 50), 50, 1),
             'edvard': (hash_n_times(edvard.h_0, 50), 50, 1)
             }

server = Server(input_queue=server_input_queue,
                output_queue=server_output_queue,
                p=31,
                passwords=passwords,
                polynomial=poly,
                keys=keys)

assert alice.successfully_finished is None
assert bob.successfully_finished is None
assert charlie.successfully_finished is None
assert edvard.successfully_finished is None
assert david.successfully_finished is None

server.start()

alice.start()
bob.start()
charlie.start()
david.start()
edvard.start()

killed = False
timeout = 300
alice.join(timeout=timeout)
bob.join(timeout=timeout)
charlie.join(timeout=timeout)
edvard.join(timeout=timeout)
david.join(timeout=timeout)
server.finish()
server.join(timeout=timeout)

if active_count() > 1:
    for t in threading.enumerate():
        if t != current_thread():
            print t
            t._Thread__stop()
    sys.exit(1)

assert alice.successfully_finished is True
assert bob.successfully_finished is True
assert charlie.successfully_finished is True
assert david.successfully_finished is True
assert edvard.successfully_finished is True
