from Server import AbstractEntity
from Utils import Cipher, hash_n_times


class Client(AbstractEntity):
    def __init__(self, server_input_queue, server_output_queue, name, h_0, K, key, secret):
        super(Client, self).__init__()
        self.server_input_queue = server_input_queue
        self.server_output_queue = server_output_queue
        self.name = name
        self.h_0 = h_0
        self.K = K
        self.key = key
        self.secret = secret
        self.successfully_finished = None
        self.index = 1

    def run(self):
        try:
            self.server_input_queue.put(self.name + ': Hi!')
            self.worker_input_queue, self.worker_output_queue = self.server_output_queue.get(timeout=self.timeout)
            self.worker_input_queue.put((self.name, self.prepare_encrypted_message()))
            server_response = self.worker_output_queue.get(timeout=self.timeout)
            if self.cipher.decrypt(server_response) == self.ok_signal:
                self.index += 1
                self.worker_input_queue.put(self.prepare_encrypted_polynomial_coordinates())
                server_confirmation = self.worker_output_queue.get(timeout=self.timeout)

                if self.is_message_valid(server_confirmation):
                    if self.cipher.decrypt(server_confirmation) == self.ok_signal:
                        self.successfully_finished = True
                        return
        except:
            pass
        self.successfully_finished = False

    def prepare_encrypted_message(self):
        message = '{0}:{1}:{2}'.format(self.name,
                                       self.index,
                                       hash_n_times(self.h_0, self.K - self.index))
        self.cipher = Cipher(self.key)
        return self.cipher.encrypt(message)

    def prepare_encrypted_polynomial_coordinates(self):
        message = '{0}:{1}'.format(self.secret[0], self.secret[1])
        return self.cipher.encrypt(message)
