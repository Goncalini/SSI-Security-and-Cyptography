import datetime
import protocol, time

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

# Send message
def parse_message(msg):
    timestamp = int(time.time())
    cert, msg = unpair(msg)
    signature, msg = unpair(msg)
    sender_uid, msg = unpair(msg)
    deste_uid, msg = unpair(msg)
    subject, msg = unpair(msg) 
    prot = protocol.Protocol(sender_uid.decode(), deste_uid.decode(), subject.decode(), msg.decode(), timestamp, cert, signature)
    return prot

# Receive message
def get_message_client(msg):
    cert, msg = unpair(msg)
    signature, msg = unpair(msg)
    sender_uid, msg = unpair(msg)
    dest_uid, msg = unpair(msg)
    timestamp, msg = unpair(msg)
    subject, msg = unpair(msg)
    return sender_uid.decode(), int.from_bytes(timestamp,"little"), subject.decode(), msg.decode(), cert, signature, dest_uid.decode()


def ask_queue(queue):
    command = "askqueue"
    msg = ""
    i = 0
    if len(queue) == 0:
        msg = "You don't have any messages."
    else: 
        for (msg_, read) in queue:
            if not read:
                msg += "\n" if i > 0 else ""
                msg += f"Message: {i}, From: {msg_.sender_uid}, Subject: {msg_.subject}, Time: {datetime.datetime.fromtimestamp(msg_.timestamp).strftime('%Y-%m-%d %H:%M:%S')}" 
                i += 1
    if msg == "":
        msg = "You don't have any unread messages."
    msg_final = mkpair(command.encode(), msg.encode())
    return msg_final


def get_message(queue, num):
    msg = ""
    command = "getmsg"
    if num < 0 or num >= len(queue):
        msg = mkpair("error".encode(), "MSG RELAY SERVICE: Invalid message number.".encode())
    else:
        protocol, read = queue[num]
        queue[num] = (protocol, True)
        return mkpair(command.encode(), protocol.receive_message())
    return msg



#
# Help 
#

def print_help():
    print("\nBem-vindo ao CypherLink!")
    print("Instruções de uso: python3 msg_client.py [opções]")
    print("   -user <FNAME>:  Especificar um ficheiro keystore para o utilizador (opcional)")
    print("   send <UID> <SUBJECT>:  Enviar uma mensagem com assunto <SUBJECT> para o utilizador <UID>")
    print("   askqueue: Listar as mensagens não lidas.")
    print("   getmsg <NUM>: Pedir ao servidor o envio da mensagem com número <NUM> na queue.")
    print("   help: Exibe esta mensagem de ajuda.")
    print("   quit: Encerra a sessão do usuário.")

def validate_command(arguments):
    if len(arguments) < 1:
        return True
    command = arguments[0]
    if command != "-user" or len(arguments) != 2:
        return False
    else:
        return True
    
def validate_command2(arguments):
    if len(arguments) < 1 or len(arguments) > 5:
        return False
    command = arguments[0]
    if command not in ['send', 'askqueue', 'getmsg', 'help']:
        return False
    elif command == 'send' and len(arguments) != 3:
        return False
    elif command == 'askqueue' and len(arguments) != 1:
        return False
    elif command == 'getmsg' and len(arguments) != 2:
        return False
    elif command == 'help' and len(arguments) != 1:
        return False
    else:
        return True
