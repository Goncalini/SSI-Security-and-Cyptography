import time
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding



def mkpair(x, y):
    """produz uma byte-string contendo o tuplo '(x,y)' ('x' e 'y' são byte-strings)"""
    len_x = len(x)
    len_x_bytes = len_x.to_bytes(2, "little")
    return len_x_bytes + x + y


def unpair(xy):
    """extrai componentes de um par codificado com 'mkpair'"""
    len_x = int.from_bytes(xy[:2], "little")
    x = xy[2 : len_x + 2]
    y = xy[len_x + 2 :]
    return x, y

# Protocol class
class Protocol:
    def __init__(self, sender_uid, dest_uid, subject, msg, timestamp=None, cert=None, signature=None):
        self.sender_uid = sender_uid
        self.dest_uid = dest_uid
        self.subject = subject
        self.msg = msg
        if timestamp is None:
            self.timestamp = time.time()
        else:
            self.timestamp = timestamp
        self.cert = cert
        self.signature = signature

    def send_message(self, cert, private_key):
        command = 'send'
        msg = mkpair(self.sender_uid.encode(), mkpair(self.dest_uid.encode(), mkpair(self.subject.encode(), self.msg.encode())))
        signature = private_key.sign(
                msg,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        return mkpair(command.encode(), mkpair(cert.public_bytes(encoding=serialization.Encoding.PEM), mkpair(signature, msg)))
    
    def receive_message(self):
        command = 'getmsg'
        msg = mkpair(self.sender_uid.encode(), mkpair(self.dest_uid.encode(), mkpair(self.timestamp.to_bytes(4, "little"), mkpair(self.subject.encode(), self.msg.encode()))))
        return  mkpair(self.cert, mkpair(self.signature, msg))