from collections import OrderedDict

def address(num):
	ip = [0]*4
	for i in range(4):
		ip[i] = str(num%256)
		num = int(num/256)
	ip = ip[::-1]
	return '.'.join(ip)

def split_by_byte(value, size):
	value_b = bytearray(b'')
	for i in range(size):
		value_b = value_b + bytearray(b'\x00')
	for i in reversed(range(len(value_b))):
		value_b[i] = value % 256
		value = int(value / 256)
	return value_b


def message_send(info):
	message = bytearray(b'')
	for key in info:
		if key == 'info_hash' or key == 'peer_id' or key == 'connection_id':
			message = message + info[key][0]
		else:
			message = message + split_by_byte(info[key][0], info[key][1])
	return bytes(message)

def setup_receive(answer):
	answer = answer[0]

	action_b = answer[0:4]
	transaction_id_b = answer[4:8]
	connection_id_b = answer[8:16]
	formated = {
		'action': int.from_bytes(action_b, "big"),
		'transaction_id': int.from_bytes(transaction_id_b, "big"),
		#'connection_id': int.from_bytes(connection_id_b, "big"),
		'connection_id': connection_id_b,
	}
	return formated

def announce_receive(answer):
	answer = answer[0]

	action_b = answer[0:4]
	transaction_id_b = answer[4:8]
	#in order to catch errors uncommit next line
	#return answer[8:].decode()
	interval_b = answer[8:12]
	leechers_b = answer[12:16]
	seeders_b = answer[16:20]

	formated = {
		'action': int.from_bytes(action_b, "big"),
		'transaction_id': int.from_bytes(transaction_id_b, "big"),
		'interval': int.from_bytes(interval_b, "big"),
		'leechers': int.from_bytes(leechers_b, "big"),
		'seeders': int.from_bytes(seeders_b, "big"),
		'peers': answer[20:],
	}
	return formated

def split_peers(peers_b):
	i = 0
	pairs = []
	while i < len(peers_b):
		pairs.append((address(int.from_bytes(peers_b[i:i+4], "big")), int.from_bytes(peers_b[i+4:i+6], "big")))
		i = i + 6
	return pairs
