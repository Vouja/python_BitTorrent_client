from parcer import Decoder
import hashlib
# with open('t.torrent', 'rb') as f:
# 	meta_info = f.read()
# 	meta_info_decoded = Decoder(meta_info).decode()
#
# print(meta_info_decoded[b'info'][b'pieces'][:20])

# with open('check.io', 'rb') as f:
# 	with open('t.torrent', 'rb') as g:
# 		meta_info = g.read()
# 		meta_info_decoded = Decoder(meta_info).decode()
# 	data = f.read()
# 	print(len(data))
# 	#print(data)
# 	print('expected {}'.format((meta_info_decoded[b'info'][b'pieces'][:20])))
# 	print('got {}'.format(hashlib.sha1(data).digest()))

# def collect_pieces():
# 	with open('t.torrent', 'rb') as f:
# 		meta_info = f.read()
# 		meta_info_decoded = Decoder(meta_info).decode()
# 	pieces = [str(meta_info_decoded[b'info'][b'pieces'][20*i:20*i+20]) for i in range(10)]
# 	for i in pieces:
# 		print(i)

# collect_pieces()
def get_piece_length():
	with open('t.torrent', 'rb') as f:
		meta_info = f.read()
		meta_info_decoded = Decoder(meta_info).decode()
	return str(meta_info_decoded[b'info'][b'piece length'])

def get_piece_hash(piece_id):
	with open('t.torrent', 'rb') as f:
		meta_info = f.read()
		meta_info_decoded = Decoder(meta_info).decode()
	return str(meta_info_decoded[b'info'][b'pieces'][20*piece_id:20*piece_id+20])
		#pieces = [str(meta_info_decoded[b'info'][b'pieces'][20*i:20*i+20]) ]

print(get_piece_hash(6))
