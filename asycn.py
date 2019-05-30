import asyncio
import socket
from byte_splitter import split_by_byte

CHUNK_SIZE = 1024
PIECES_IN_MEMORY = 10

"""
status list:
	0: waiting
	1: working
	2: got b''
	3: error occured, still working
	4: choked
	5: other error
"""

class Peer:
	reader = None
	writer = None
	bitfield = None
	status = 0
	def __init__(self, address):
		self.ip = address[0]
		self.port = address[1]

	async def connect(self, handshake):
		try:
			con = asyncio.open_connection(self.ip, self.port)
			self.reader, self.writer = await asyncio.wait_for(con, 10)
			self.writer.write(handshake)
			await self.writer.drain()

			cor = self.reader.read(68)
			data = await asyncio.wait_for(cor, 10)
			self.handshake = data

			"""TO DO: check handshake"""

		except Exception as e:
			self.status = 5

	async def choke(self, i):
		if self.status in [0, 1, 2, 3, 4, 5]:
			try:
				self.writer.write(b'\x00\x00\x00\x01\x02')
				await self.writer.drain()
				cor = self.reader.read(4)
				length = await asyncio.wait_for(cor, 10)

				if length == b'':
					self.status = 2
					return

				cor = self.reader.read(int.from_bytes(length, "big"))
				data = await asyncio.wait_for(cor, 10)

				if data[0]!=1:
					self.status = 4
			except:
				self.status = 5

	async def have(self, id=0):
		if self.status in [0, 1, 2, 3, 4, 5]:
			try:
				self.writer.write(bytes(bytearray(b'\x00\x00\x00\x05\x04')+split_by_byte(id, 4)))
				await self.writer.drain()
				cor = self.reader.read(4)
				length = await asyncio.wait_for(cor, 10)

				if length == b'':
					self.status = 2
					return

				cor = self.reader.read(int.from_bytes(length, "big"))
				data = await asyncio.wait_for(cor, 10)

				if data[0] == 5:
					self.bitfield = data[1:]
				if self.bitfield == b'':
					self.status = 2
			except Exception as e:
				self.status = 5

	async def request(self, piece_id, size, pieces, status_start, num=3):
		err = None
		start = status_start[1]
		if num == 0:
			self.status = 3
			status_start[0] = 3
			status_start[1] = start
			return
		try:
			self.status = 1
			if self.status == 1 and len(pieces)<=start:

				message = bytes(bytearray(b'\x00\x00\x00\x0d\x06')+split_by_byte(piece_id, 4)+split_by_byte(start, 4)+split_by_byte(size, 4))

				self.writer.write(message)
				await self.writer.drain()
				cor = self.reader.read(4)

				length = await asyncio.wait_for(cor, 10)

				if length == b'':
					self.status = 2
					status_start[0] = 2
					status_start[1] = start
					return

				cor = self.reader.read(int.from_bytes(length, "big"))
				data = await asyncio.wait_for(cor, 15)

				"""TO DO: Develop check"""
				if len(data)>0:
					if data[0] != 7:
						await asyncio.wait([self.request(piece_id, size, pieces, status_start, num-1)])
						return

					elif len(data)>10:
						#this should be checked too
						#and and self.bitfield[int(piece_id/8)] & 2**(7-piece_id%8) > 0
						if int.from_bytes(data[5:9], "big") == start:
							if len(pieces)<=start and (len(data[9:]) == size or isEnd):

								pieces += data[9:]
								print('added {}'.format(len(pieces)))
								status_start[0] = 1
								status_start[1] = start + size
								return

							else:
								if len(data[9:]) != size:
									await asyncio.wait([self.request(piece_id, size, pieces, status_start, num-1)])
									return
						elif int.from_bytes(data[5:9], "big") != start :
							await asyncio.wait([self.request(piece_id, size, pieces, status_start, num-1)])
						else:
							self.status = 3
							status_start[0] = 3
							status_start[1] = start
							return
					else:
						if num > 0:
							await asyncio.wait([self.request(piece_id, size, pieces, status_start, num-1)])
							return
						else:
							self.status = 3
							status_start[0] = 3
							status_start[1] = start
							return
				else:
					await asyncio.wait([self.request(piece_id, size, pieces, status_start, num-1)])
					return
					self.status = 3
					status_start[0] = 3
					status_start[1] = start
					return
			else:
				await asyncio.wait([self.request(piece_id, size, pieces, status_start, num-1)])
				return
				self.status = 3
				status_start[0] = 3
				status_start[1] = start
				return
		except Exception as e:
			self.status = 5
			status_start[0] = 5
			status_start[1] = start
			return


	async def setup(self, handshake, id, start, size):
		await asyncio.wait([self.connect(handshake)])
		await asyncio.wait([self.have(id)])
		await asyncio.wait([self.choke(0)])




async def router(piece_length, peers, peer_id, piece_id, start, status, arrid, files):
	isNew = False

	while arrid[piece_id][0] == 1:
		piece_id += 1
	if len(arrid) == piece_id+1:
		return
	arrid[piece_id][0] = 1

	status_start = [status, start]

	while True:
		while arrid[piece_id][0] == 1 and isNew:
			piece_id += 1
		if len(arrid) == piece_id+1:
			return
		arrid[piece_id][0] = 1
		isNew = False

		if status_start[0] == -1:
			peers[peer_id].status = 1
			await asyncio.wait([peers[peer_id].request(piece_id, CHUNK_SIZE, arrid[piece_id][1], status_start)])

		elif status_start[0] == 1:
			if status_start[1] + CHUNK_SIZE > piece_length:
				if len(arrid) == piece_id+1:
					await asyncio.wait([peers[peer_id].request(piece_id, piece_length-status_start[1], arrid[piece_id][1], status_start)])
					return
				else:
					peers[peer_id].status = 0

					while True:
						if piece_id==0 or arrid[piece_id-1][0]==0:
							break
						await asyncio.sleep(3)

					piece = 0
					"""
					 TO DO: hash sum check
					"""

					for file in files:
						with open('files/'+file['filename'], 'ab') as f:
							while file['downloaded'] < file['left'] and piece < len(arrid[piece_id][1]):
								f.write(bytes(arrid[piece_id][1][piece:piece+1]))
								file['downloaded'] += 1
								piece += 1


					arrid[piece_id][0] = 0
					arrid[piece_id][1] = b''
					piece_id += 1
					status_start = [1, 0]
					print("\n ended ", piece_id, '\n')
					isNew = True

			else:
				await asyncio.wait([peers[peer_id].request(piece_id, CHUNK_SIZE, arrid[piece_id][1], status_start)])
		else:
			if peer_id == -1:
				peer_id = 0
			else:
				peers[peer_id].status = status_start[0]

			peer_id += 1
			#working peers might send bad response so i track them as 3 or 5,
			#but finally i forgive them and allow them to try again
			while peer_id < len(peers) and (peers[peer_id].status == 1) :
				peer_id += 1

			if peer_id == len(peers):
				peer_id = -1
				await asyncio.sleep(10)
				pass
			else:
				peers[peer_id].status = 1
				await asyncio.wait([peers[peer_id].request(piece_id, CHUNK_SIZE, arrid[piece_id][1], status_start)])



async def setup_download(pairs, handshake, peersd):
	peers = [Peer(addr) for addr in pairs]
	tasks = [asyncio.create_task(obj.setup(handshake, 0, 0, 0)) for obj in peers]
	await asyncio.wait(tasks)
	for i in range(len(peers)):
		peersd[i] = peers[i]

async def download(peers, piece_length, arrid, files):
	tasks = [
		asyncio.create_task(router(piece_length, peers, i, i, 0, -1, arrid, files)) for i in range(PIECES_IN_MEMORY)
		]
	await asyncio.wait(tasks)
