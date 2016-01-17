import threading
from Queue import Queue

from Utils import hash_function, Cipher


class AbstractEntity(threading.Thread):
    def __init__(self):
        super(AbstractEntity, self).__init__()
        self.timeout = 1000
        self.error_signal = 'ERROR'
        self.ok_signal = 'OK'

    def is_message_valid(self, message, intended_length=1):
        try:
            if intended_length > 1:
                return len(message) == intended_length and message != self.error_signal
            return message != self.error_signal
        except:
            return False


class Server(AbstractEntity):
    def __init__(self, input_queue, output_queue, p, passwords, polynomial, keys):
        super(Server, self).__init__()
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.p = p
        self.passwords = passwords
        self.polynomial = polynomial
        self.keys = keys
        self.finish_signal = 'FINISH'

        self.logged = set()
        self.confirmed = {}
        self.workers_queue = Queue()

    def run(self):
        try:
            while True:
                message = self.input_queue.get(timeout=self.timeout)
                if self.is_finish_signal(message):
                    break
                if self.is_message_valid(message):
                    worker = ServerWorker(self.p, self.passwords, self.keys, parent=self)
                    worker.start()
                    self.output_queue.put((worker.input_queue, worker.output_queue))
        except:
            pass

    def finish(self):
        self.input_queue.put(self.finish_signal)

    def is_finish_signal(self, message):
        return message == self.finish_signal

    def confirm(self, client_id, client_secret):
        self.confirmed[client_id] = client_secret
        self.check_if_complete()

    def check_if_complete(self):
        try:
            if len(self.confirmed) == len(self.passwords):
                if all([self.validate_polynomial(pair[0], pair[1]) for pair in self.confirmed.values()]):
                    self.pass_signal_to_workers(self.ok_signal, number=len(self.confirmed))
                else:
                    self.pass_signal_to_workers(self.error_signal, number=len(self.confirmed))
                self.finish()
        except:
            self.pass_signal_to_workers(self.error_signal, number=len(self.confirmed))
            self.finish()

    def pass_signal_to_workers(self, signal, number):
        for _ in range(number):
            self.workers_queue.put(signal)

    def can_login(self, client_id):
        return client_id not in self.logged

    def login(self, client_id):
        self.logged.add(client_id)

    def validate_polynomial(self, x, y):
        return (self.polynomial[0] * x ** 2 +
                self.polynomial[1] * x +
                self.polynomial[2]) % self.p == y


class ServerWorker(AbstractEntity):
    def __init__(self, p, passwords, keys, parent):
        super(ServerWorker, self).__init__()
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.p = p
        self.passwords = passwords
        self.keys = keys
        self.parent = parent

    def run(self):
        try:
            client_message = self.input_queue.get(timeout=self.timeout)
            if self.is_message_valid(client_message, intended_length=2):
                client_id, client_encrypted = client_message
                if self.parent.can_login(client_id):
                    client_decrypted = self.decrypt_message(client_id, client_encrypted)
                    if self.is_decrypted_message_valid(client_id, client_decrypted):
                        self.output_queue.put(self.create_encrypted_ok_message())
                        self.parent.login(client_id)
                        encrypted_confirmation = self.input_queue.get(timeout=self.timeout)
                        self.parent.confirm(client_id, self.decrypt_confirmation(encrypted_confirmation))
                        response = self.parent.workers_queue.get(timeout=self.timeout)
                        if response == self.ok_signal:
                            self.output_queue.put(self.create_encrypted_ok_message())
                            return
        except:
            pass
        self.output_queue.put(self.error_signal)

    def is_hashed_secret_valid(self, client_id, client_hash):
        try:
            client_secret = self.passwords.get(client_id)[0]
            return hash_function(client_hash) == client_secret
        except KeyError:
            pass
        return False

    def create_encrypted_ok_message(self):
        return self.cipher.encrypt(self.ok_signal)

    def decrypt_message(self, client_id, client_encrypted):
        self.cipher = Cipher(self.keys.get(client_id))
        return self.cipher.decrypt(client_encrypted)

    def is_decrypted_message_valid(self, client_id, client_decrypted):
        try:
            inner_id, inner_index, client_hash = client_decrypted.split(':')
            return (inner_id == client_id and
                    self.passwords.get(client_id)[2] == int(inner_index) and
                    self.is_hashed_secret_valid(client_id, client_hash))
        except:
            pass
        return False

    def decrypt_confirmation(self, encrypted_confirmation):
        return [int(coordinate) for coordinate in self.cipher.decrypt(encrypted_confirmation).split(':')]
