import socket
from collections import OrderedDict
from byte_splitter import *

def setup(adress, transaction_id):
	try:
		UDP_IP_ADRESS  = adress[0]
		UDP_PORT_NO = adress[1]

		clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		msgToServer = message_send(OrderedDict([
			('connection_id', (split_by_byte(int(0x41727101980),8), 8)),
			('action', (0, 4)),
			('transaction_id', (transaction_id, 4))
		]))
		#print((UDP_IP_ADRESS, UDP_PORT_NO))
		clientSock.settimeout(5.0)
		clientSock.sendto(msgToServer, (UDP_IP_ADRESS, UDP_PORT_NO))

		msgFromServer = clientSock.recvfrom(1024)

		return setup_receive(msgFromServer)
	except:
		return 'ERROR'

def announce(adress, info):
	UDP_IP_ADRESS  = adress[0]
	UDP_PORT_NO = adress[1]

	clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	msgToServer = message_send(OrderedDict([
		('connection_id', (info['connection_id'], 8)),
		('action', (1, 4)),
		('transaction_id', (info['transaction_id'], 4)),
		('info_hash', (info['info_hash'], 20)),
		('peer_id', (info['peer_id'], 20)),
		('downloaded', (info['downloaded'], 8)),
		('left', (info['left'], 8)),
		('uploaded', (info['uploaded'], 8)),
		('event', (info['event'], 4)),
		('IPv4', (0, 4)),
		('key', (0, 4)),
		('num_want', (int(0xffffffff), 4)),
		('port', (info['port'], 2)),
	]))
	clientSock.sendto(msgToServer, (UDP_IP_ADRESS, UDP_PORT_NO))

	msgFromServer = clientSock.recvfrom(1024)

	return announce_receive(msgFromServer)

# UDP_IP_ADDRESS = "127.0.0.1"
# UDP_PORT_NO = 6789
# serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))
# while True:
#     data, addr = serverSock.recvfrom(1024)
#     print ("Message: ", data)
