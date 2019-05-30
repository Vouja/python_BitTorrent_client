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


sizel = size
size = size + meta_info_decoded[b'info'][b'piece length']

info_hash = hashlib.sha1(Encoder(meta_info_decoded[b'info']).encode()).digest()


trackers = [meta_info_decoded[b'announce'].decode()]


for i in meta_info_decoded[b'announce-list']:
	trackers += [i[0].decode()]


pairs = []

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
		'info_hash': info_hash,
		'peer_id': peer_id,
		'downloaded': 0,
		'left': size,
		'uploaded': 0,
		'event': 1,
		'port': 6793,
	}

	answer = announce(adress, info)
	pairs += split_peers(answer['peers'])



handshake = bytearray(b'')
handshake += chr(19).encode()
handshake += b'BitTorrent protocol'
handshake += b'\x00\x00\x00\x00\x00\x00\x00\x00'
handshake += info_hash
handshake += peer_id


peers = list(set(pairs))
print(pairs)

loop = asyncio.get_event_loop()
asyncio.set_event_loop(loop)


try:
	loop.run_until_complete(setup_download(peers, bytes(handshake), peers))
finally:
	pass

pieces_num = int(pieces_num/20)

piece_start = 0
piece_end = 0
file_id=0


arrid = [[0, bytearray(b'')] for i in range(pieces_num)]

loop.run_until_complete(download(peers, piece_length, arrid, files))
