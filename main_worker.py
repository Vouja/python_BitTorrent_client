from parcer import Encoder, Decoder
from collections import OrderedDict
from connecter import setup, announce
from byte_splitter import *
from asycn import *
import asyncio
import hashlib
import binascii
import urllib.parse
import random
import re
import os

with open('t.torrent', 'rb') as f:
	meta_info = f.read()
	meta_info_decoded = Decoder(meta_info).decode()

size = 0
# for obj in meta_info_decoded[b'info'][b'files']:
# 	size = size + obj[b'length']
if b'files' in meta_info_decoded[b'info']:
	for i in meta_info_decoded[b'info'][b'files']:
		size = size + i[b'length']

	files = []
	for i in meta_info_decoded[b'info'][b'files']:
		if not os.path.exists(os.getcwd()+'/files/'+os.path.dirname('/'.join([j.decode() for j in i[b'path']]))):
			os.makedirs(os.getcwd()+'/files/'+os.path.dirname(i))
		filename = ('/'.join([j.decode() for j in i[b'path']]))
		files = files + [{'downloaded':0, 'left':i[b'length'], 'filename':filename}]
# files = [{'downloaded':0, 'left':11499899, 'filename': 'brin.fb2'}]
else:
	size = meta_info_decoded[b'info'][b'length']

	files = [{
			'downloaded': 0,
			'left': meta_info_decoded[b'info'][b'length'],
			'filename': meta_info_decoded[b'info'][b'name'].decode(),
			}]
	if not os.path.exists(os.getcwd()+'/files/'):
		os.makedirs(os.getcwd()+'/files/')
piece_length = meta_info_decoded[b'info'][b'piece length']
pieces_num = len(meta_info_decoded[b'info'][b'pieces'])

# size = size + meta_info_decoded[b'info'][b'length']
sizel = size
size = size + meta_info_decoded[b'info'][b'piece length']

info_hash = hashlib.sha1(Encoder(meta_info_decoded[b'info']).encode()).digest()


trackers = [meta_info_decoded[b'announce'].decode()]
# tracker = meta_info_decoded[b'announce'].decode()
#print(meta_info_decoded[b'announce-list'])

for i in meta_info_decoded[b'announce-list']:
	#print(i[0].decode())
	trackers += [i[0].decode()]

# trackers = trackers[1:2]
pairs = []
# print(files)
# x = 0/0
peer_id = ('-PC0001-' + ''.join([str(random.randint(0,9)) for _ in range(12)])).encode()
for tracker in trackers:

	if re.findall(":\d+", tracker) == []:
		adress = (re.findall("//.+[/:]", tracker)[0][2:-1], 2710)
	else:
		adress = (re.findall("//.+[/:]", tracker)[0][2:-1], int(re.findall(":\d+", tracker)[0][1:]))

	transaction_id = random.randint(1, 999999)
	print(adress)
	answer = setup(adress, transaction_id)
	if answer == 'ERROR':
		continue

	transaction_id = random.randint(1, 999999)
	peer_id = ('-PC0001-' + ''.join([str(random.randint(0,9)) for _ in range(12)])).encode()

	info = {
		'connection_id': answer['connection_id'],
		'transaction_id': transaction_id,
		#'info_hash': int.from_bytes(hashlib.sha1(Encoder(meta_info_decoded[b'info']).encode()).digest(), "big"),
		'info_hash': info_hash,
		#int(0xffffffffffffffffffffffffffffffffffffffff)-int.from_bytes(hashlib.sha1(Encoder(meta_info_decoded[b'info']).encode()).digest(), "big"),
		'peer_id': peer_id,
		'downloaded': 0,
		'left': size,
		'uploaded': 0,
		'event': 1,
		'port': 6793,
	}
	#print('send to server:')
	#print(info)
	answer = announce(adress, info)
	pairs += split_peers(answer['peers'])

#print("received from server:")
#print(answer)
#print('\n')

handshake = bytearray(b'')
handshake += chr(19).encode()
handshake += b'BitTorrent protocol'
handshake += b'\x00\x00\x00\x00\x00\x00\x00\x00'
handshake += info_hash
handshake += peer_id
# pairs = split_peers(answer['peers'])

peers = list(set(pairs))
print(pairs)

loop = asyncio.get_event_loop()
asyncio.set_event_loop(loop)

#print(answer)

try:
	loop.run_until_complete(setup_download(peers, bytes(handshake), peers))
finally:
	pass
    #loop.close()

pieces_num = int(pieces_num/20)

piece_start = 0
piece_end = 0
file_id=0


arrid = [[0, bytearray(b'')] for i in range(pieces_num)]

loop.run_until_complete(download(peers, piece_length, arrid, files))
# while w < pieces_num:
# 	arr = [bytearray(b'') for i in range(3)]
#
# 	if w < (pieces_num - 10):
# 		arr = [bytearray(b'') for i in range(10)]
# 		loop.run_until_complete(download(peers, piece_length, arr, w, 10))
# 		w += 10
# 	elif w == (pieces_num -1):
# 		arr = [bytearray(b'') for i in range(1)]
# 		loop.run_until_complete(download(peers, piece_length-(pieces_num*piece_length - sizel), arr, w, 1, True))
# 		w += 10
# 	elif w >= (pieces_num -10):
# 		arr = [bytearray(b'') for i in range(pieces_num-w-1)]
# 		loop.run_until_complete(download(peers, piece_length, arr, w, pieces_num-w-1))
# 		w += pieces_num-w-1
#
# 	for piece in arr:
# 		print(hashlib.sha1(piece).digest())
# 		for bt in piece:
# 			if files[file_id]['downloaded'] != files[file_id]['left']:
# 				files[file_id]['downloaded'] += 1
# 				with open(files[file_id]['filename'], 'ab') as f:
# 					f.write(bytes([bt]))
# 			else:
# 				file_id += 1


# arr = [bytearray(b'') for i in range(10)]
# piece_length = 262144
# #piece_length = 220160
# piece_amount=10
# asyncio.run(download(piece_length, piece_amount, peers, bytes(handshake), arr, int(len((meta_info_decoded[b'info'][b'pieces']))/20)))
#
# for i in arr:
# 	print(hashlib.sha1(i).digest())
