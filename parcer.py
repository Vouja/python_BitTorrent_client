from collections import OrderedDict

def cut_obj(obj):
	stri = b''

	if type(obj) is int:
		stri  = stri + b'i' + str(obj).encode() + b'e'

	if type(obj) is bytes:
		stri  = stri + str(len(obj)).encode() + b':' + obj

	if type(obj) is list:
		stri  = stri + b'l'
		for piece in obj:
			stri = stri + cut_obj(piece)
		stri = stri + b'e'

	if isinstance(obj, OrderedDict) or type(obj) is dict:
		stri  = stri + b'd'
		for piece in obj:
			stri = stri + cut_obj(piece) + cut_obj(obj[piece])
		stri = stri + b'e'

	return stri

def add_piece(stri, obj, num, last_particle=None):
	i = 0
	#print(stri)
	if len(stri) <= 0 or chr(stri[i]) == 'e':
		num[0] = num[0] + 1
		return
	if len(stri) > 0:
	#while i < len(stri):
		if chr(stri[i]).isdigit():
			#print(stri)
			length = ''
			while chr(stri[i]).isdigit():
				length = length + chr(stri[i])
				i = i + 1
			i = i + 1
			particle = b''
			for j in range(int(length)):
				particle = particle + stri[i+j:i+j+1]
			"""
			j = int(length)
			"""
			i = i + j + 1
			num[0] = num[0] + i
			#print(stri[i:])
			if isinstance(obj, OrderedDict) or type(obj) is dict:
				if last_particle:
					obj[last_particle] = particle
					return add_piece(stri[i:], obj, num)
				else:
					return add_piece(stri[i:], obj, num, particle)
			else:
				obj.append(particle)
				return add_piece(stri[i:], obj, num)

		if chr(stri[i]) == 'i':
			i = i + 1
			particle = ''
			#print(stri)
			while chr(stri[i]) != 'e':
				particle = particle + chr(stri[i])
				i = i + 1
			i = i + 1
			num[0] = num[0] + i
			if isinstance(obj, OrderedDict) or type(obj) is dict:
				if last_particle:
					obj[last_particle] = int(particle)
					return add_piece(stri[i:], obj, num)
				else:
					return add_piece(stri[i:], obj, num, int(particle))
			else:
				obj.append(particle)
				return add_piece(stri[i:], obj, num)

		if chr(stri[i]) == 'l' or chr(stri[i]) == 'd':
			if chr(stri[i]) == 'l':
				particle = []
			if chr(stri[i]) == 'd':
				particle = OrderedDict()
			lnt = [0]
			add_piece(stri[i+1:], particle, lnt)
			i = i + lnt[0] + 1
			num[0] = num[0] + i
			if isinstance(obj, OrderedDict) or type(obj) is dict:
				if last_particle:
					obj[last_particle] = particle
					return add_piece(stri[i:], obj, num)
				else:
					return add_piece(stri[i:], obj, num, particle)
			else:
				obj.append(particle)
				return add_piece(stri[i:], obj, num)


def unite_obj(stri):
	if chr(stri[0]) == 'd':
		obj = OrderedDict()
	if chr(stri[0]) == 'l':
		obj = []
	add_piece(stri[1:-1], obj, [0])
	return obj


class Encoder:
	obj = None

	def __init__(self, obj):
		self.obj = obj

	def encode(self):
		stri = ''
		stri = cut_obj(self.obj)
		return stri


class Decoder:
	stri = ''

	def __init__(self, stri):
		self.stri = stri

	def decode(self):
		return unite_obj(self.stri)
