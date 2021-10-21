from obfuscated_retrieval.BACnet.utils.logStore.appconn.obfuscatedRetrieval_connection import obfuscatedRetrievalFunction as Function
from obfuscated_retrieval.BACnet.utils.logStore.appconn.obfuscatedRetrieval_connection import obfuscatedRetrievalFunction
from obfuscated_retrieval.BACnet.utils.EventCreationTool import EventFactory
from Crypto.Cipher import AES
from obfuscated_retrieval.double_ratchet.crypto_signing import *
import datetime
import os

"""
Parts of this code were taken and modified from /HS2020/Groups/03-DoubleRatchet/src/helper_functions/helpers.py
"""

key_length = 290

path_x3dh_outstanding = os.getcwd() + FOLDERNAME_KEYS + '/outstanding_x3dh_contacts.key'
path_x3dh_established = os.getcwd() + FOLDERNAME_KEYS + '/established_x3dh_contacts.key'
path_x3dh_confirmed = os.getcwd() + FOLDERNAME_KEYS + '/confirmed_x3dh_contacts.key'
path_identity_key = os.getcwd() + FOLDERNAME_KEYS + '/identity_key.key'
path_keys = os.getcwd() + FOLDERNAME_KEYS + '/x3dh_keys.key'
path_first_keys = os.getcwd() + FOLDERNAME_KEYS + '/first_x3dh_keys'
path_backup = os.getcwd() + FOLDERNAME_KEYS + '/backup.key'
path_prev_pubkey = os.getcwd() + FOLDERNAME_KEYS + '/prev_pubkey.key'

class DoubleRatchetInterface():
	def __init__(self, identifier_partner, new_action, x3dh_role):
		print(f"<<<DoubleRatchetInterface().__init__(self, identifier_partner, new_action, {x3dh_role})")
		self.x3dh_status = get_x3dh_status(identifier_partner, new_action)
		self.path_backup = path_backup
		self.shared_key = None
		self.identifier_partner = identifier_partner
		self.path_prev_pubkey = path_prev_pubkey
		self.new_action = new_action #TODO: Phase out new_action, by using x3dh_role exclusively
		self.x3dh_role = x3dh_role
		print(f"   x3dh_status is {self.x3dh_status}")
		print(f"   x3dh_role is {self.x3dh_role}")
		self.path_first_keys = path_first_keys + identifier_partner.replace('/', '') + '.key'
		#for a definition of what each x3dh_status means, go to get_x3dh_status() at l.205
		if self.x3dh_status == 0:
			#This means we are trying to first establish contact with another person and they haven't initialized anything yet
			self.Ns = 0
			self.Nr = 1
			self.PNs = 0
			self.PNr = 1
			if new_action == "obfuscatedRetrieval/prekey_bundle":
				self.IK, self.EK = self.load_first_keys()
			else:
				(self.IK, self.SPK, self.OPK) = self.load_first_keys()
				self.DH_ratchet = X25519PrivateKey.generate() #initialize our DH ratchet as Bob
				self.save_keys()
				with open(path_x3dh_outstanding, 'a') as file:
					file.write(identifier_partner + os.linesep)
		elif self.x3dh_status == 1:
			self.load_keys()
			pass
		elif self.x3dh_status == 3:
			self.load_keys()
			pass
		elif self.x3dh_status == 4 and self.x3dh_role == 'slave':
				print("   We are Alice/slave")
				self.path_backup = path_backup
				(self.IK, _) = self.load_first_keys()
				load_status(self)
				pass
		elif self.x3dh_status == 4 and self.x3dh_role == 'master':
				print("   We are Bob/master")
				self.path_backup = path_backup
				load_status(self)
				pass
		else:
			print("   Something went wrong. Either the x3dh_status is invalid or the x3dh_role is")


	def save_prev_pubkey(self, serialized_key: bytes):
		with open(self.path_prev_pubkey, 'wb') as f:
			f.write(serialized_key)

	def save_keys(self):
		print(f"DoubleRatchetInterface().save_keys()\n   len(bytes(self.identifier_partner, encoding='utf-8')): {len(bytes(self.identifier_partner, encoding='utf-8'))}\n   len(bytes(self.identifier_partner, encoding='utf-8')).to_bytes(4, 'big'): {len(bytes(self.identifier_partner, encoding='utf-8')).to_bytes(4,'big')}\n   bytes(self.identifier_partner, encoding='utf-8'):{bytes(self.identifier_partner, encoding='utf-8')}")
		text_to_save = b''.join(
			[len(bytes(self.identifier_partner, encoding='utf-8')).to_bytes(4,"big"),
			bytes(self.identifier_partner, encoding='utf-8'),
			self.Ns.to_bytes(4, "big"),
			self.Nr.to_bytes(4, "big"),
			self.PNs.to_bytes(4, "big"),
			self.PNr.to_bytes(4, "big"),
			serialize_private_key(self.DH_ratchet),
			serialize_private_key(self.IK),
			serialize_private_key(self.SPK),
			serialize_private_key(self.OPK)]
		)
		with open(path_keys, "wb") as file:
			print("   text_to_save, path_keys: ", text_to_save[:60], path_keys)
			file.write(text_to_save)
		pass

	def load_first_keys(self):
		"""               -> (X25519PrivateKey, X25519PrivateKey, X25519PrivateKey) in the case of us being "bob"
						  -> (X25519PrivateKey, X25519PrivateKey) in the case of us being "alice"
		If there are already keys present, it will load them.
		If they do not already exist, it generates new keys and saves them.
		Generate OPKb once and does not save it.
		"""
		print("DoubleRatchetInterface().load_first_keys()")
		if  self.x3dh_status == 4 or self.new_action == 'obfuscatedRetrieval/prekey_bundle':
			"""
			Returns 2 keys:
			IK: X25519PrivateKey, EK: X25519PrivateKey
			"""
			EK = X25519PrivateKey.generate()
			try:
				with open(self.path_first_keys, 'rb') as path_keys_file:
					IK_bytes = path_keys_file.read()
					IK = deserialize_private_key(IK_bytes)
					print("   Loaded saved keys.")
			except FileNotFoundError:
				print("   No keys found. Creating new keys")
				IK = X25519PrivateKey.generate()
				with open(self.path_first_keys, 'wb') as path_keys_file:
					for key in [IK]:
						path_keys_file.write(serialize_private_key(key))
					print("   Keys")
				pass
			return (IK, EK)
		elif self.x3dh_status == 0:
			""""
			Returns 3 keys:   IK: X25519PrivateKey, SPK: X25519PrivateKey, OPK: X25519PrivateKey
			"""
			OPK = X25519PrivateKey.generate()
			try:
				with open(self.path_first_keys, "rb") as file:
					lines = file.read()
					assert(len(lines) == 2*key_length)
					IK_bytes = lines[:key_length]
					IK = deserialize_private_key(IK_bytes)
					SPK_bytes = lines[key_length:]
					SPK = deserialize_private_key(SPK_bytes)
			except FileNotFoundError:
				print("   No keys found. Creating new keys...")
				IK = X25519PrivateKey.generate()
				SPK = X25519PrivateKey.generate()
				with open(self.path_first_keys, "wb") as file:
					for key in [IK, SPK]:
						file.write(serialize_private_key(key))
					print("   Keys saved")
				pass
			return (IK, SPK, OPK)


	def load_keys(self):
		print("DoubleRatchetInterface().load_keys()")
		all = None
		with open(path_keys, 'rb') as file:
			all = file.read()
			print(f'   keys: {all[:75]}...')
		pass
		k = 0
		while True:
			identifier_length = int.from_bytes(all[k:k+4], 'big')
			if all[k+4:k+4+identifier_length] == bytes(self.identifier_partner, 'utf-8'):
				keys = all[k+4+identifier_length:k+4+identifier_length+1176]
				all_updated = all[:k] + all[k+4+identifier_length+1176:]
				print("   ALL UPDATED INSIDE IF", all_updated)
				break
			elif all[k+4:k+4+identifier_length] == b'':
				print("   Something went wrong. Cannot find saved keys for this person. Shutting down...")
				exit()
			k += 4 + identifier_length + 1176
		self.Ns = int.from_bytes(keys[0:4], 'big')
		self.Nr = int.from_bytes(keys[4:8], 'big')
		self.PNs = int.from_bytes(keys[8:12], 'big')
		self.PNr = int.from_bytes(keys[12:16], 'big')
		self.DH_ratchet = deserialize_private_key(keys[16:16+290])
		self.IK = deserialize_private_key(keys[16+290:16+2*290])
		self.SPK = deserialize_private_key(keys[16+2*290:16+3*290])
		self.OPK = deserialize_private_key(keys[16+3*290:16+4*290])

		with open(path_keys, 'wb') as file:
			print("load_keys(), file:", all_updated)
			file.write(all_updated)

	def complete_transaction_with_partner_keys(self, msg: bytes):
		print(f"DoubleRatchetInterface().complete_transaction_with_partner_keys(self, {msg})")
		"""
		In this case, we have sent the partner a "obfuscatedRetrieval/contactInfo" before,
		and they have now sent use an "obfuscatedRetrieval/connect" event.
		"""
		assert(len(msg) == 64)
		IK = deserialize_public_key(msg[:32])
		EK = deserialize_public_key(msg[32:])
		self.x3dh_with_keys("", "", IK, EK)
		self.initialize_ratchets()
		print(f"   Shared Key: {b64(self.shared_key)}")
		save_status(self)

		with open(path_x3dh_outstanding, 'r') as x3dh_outstanding_file:
			lines = x3dh_outstanding_file.read()
		lines = lines.replace(self.identifier_partner + os.linesep,"")
		with open(path_x3dh_outstanding, 'w') as x3dh_outstanding_file:
			x3dh_outstanding_file.write(lines)

		with open(path_x3dh_established, 'a') as x3dh_established_file:
			x3dh_established_file.write(self.identifier_partner + os.linesep)
		pass

	def x3dh_with_keys(self, SPK, OPK, IK, EK):
		print("DoubleRatchetInterface().x3dh_with_keys()")
		"""
		If we are "bob":  (IK: X25510PublicKey, EK: X25510PublicKey) -> None
		If we are "alice": (SPK: X25510PublicKey, IK: X25510PublicKey, OPK: X25510PublicKey) -> None
		In both cases, the shared key is calculated as: KDF(DH1|DH2|DH3|DH4)
		"""
		if EK == "":
			dh1 = self.IK.exchange(SPK)
			dh2 = self.EK.exchange(IK)
			dh3 = self.EK.exchange(SPK)
			dh4 = self.EK.exchange(OPK)
			self.shared_key = hkdf(dh1+dh2+dh3+dh4, 32)
		elif SPK == "" and OPK == "":
			dh1 = self.SPK.exchange(IK)
			dh2 = self.IK.exchange(EK)
			dh3 = self.SPK.exchange(EK)
			dh4 = self.OPK.exchange(EK)
			self.shared_key = hkdf(dh1+dh2+dh3+dh4, 32)

	def create_prekey_bundle(self) -> bytes:
		print("DoubleRatchetInterface().create_prekey_bundle()")
		# Initial key packet contains:
		# - [32] DH_ratchet_public_key: DH_ratchet_initial_bytes
		# - [32] Our/the initiator's identity key: IK
		# - [32] Our/the initiator's signed prekey: SPKb
		# - [32] Our/the initiator's one-time prekey: OPKb
		# - [32] Public key of the signature: signature_pubkey
		# - [64] Bob's prekey signature Sig(Encode(IK), Encode(SPKb)): signature
		#
		# DH_ratchet_public_key || IK || SPKb || OPKb || signature_pubkey || signature
		#        32             || 32  ||  32  ||  32  ||        32        ||    64
		# Total length: 224 bytes
		#
		# signature_pubkey and signature are generated by calling xed_sign(keys).
		#   signature_pubkey, signature = signing.xed_sign(keys),
		# where keys is the composition of the 3 keys: DH_ratchet_pubkey, IK, OPKb.
		# After that we send 224 bytes: keys || signature_pubkey || signature
		IK_bytes = serialize_public_key(self.IK.public_key())
		SPK_bytes = serialize_public_key(self.SPK.public_key())
		OPK_bytes = serialize_public_key(self.OPK.public_key())
		DH_ratchet_initial_bytes = serialize_public_key(self.DH_ratchet.public_key())
		keys = b''.join([DH_ratchet_initial_bytes, IK_bytes, SPK_bytes, OPK_bytes])
		signature_pubkey, signature = xeddsa_sign(keys)
		keys_to_send = b''.join([keys, signature_pubkey, signature])
		return(keys_to_send)

	def create_prekey_bundle_from_received_bundle(self, received_prekey_bundle: bytes) -> bytes:
		print("DoubleRatchetInterface().create_prekey_bundle_from_received_bundle()")
		assert(len(received_prekey_bundle) == 224)
		DH_ratchet_public_key_received = received_prekey_bundle[:32]
		IK_bytes_received = received_prekey_bundle[32:64]
		SPK_bytes_received = received_prekey_bundle[64:96]
		OPK_bytes_received = received_prekey_bundle[96:128]
		signature_pubkey = received_prekey_bundle[128:160]
		signature = received_prekey_bundle[160:224]
		keys = received_prekey_bundle[:128]

		if xeddsa_verify(pubkey=signature_pubkey, data=keys, signature=signature):
			print("   xeddsa verification succesful!")
			pass
		else:
			print("   Verification failed!")
			exit()
		IK = deserialize_public_key(IK_bytes_received)
		SPK = deserialize_public_key(SPK_bytes_received)
		OPK = deserialize_public_key(OPK_bytes_received)
		DH_ratchet_public_key_other = deserialize_public_key(DH_ratchet_public_key_received)
		self.x3dh_with_keys(SPK,OPK,IK,"")
		self.initialize_ratchets()
		dh_ratchet(self, DH_ratchet_public_key_other)
		IK_bytes = serialize_public_key(self.IK.public_key())
		EK_bytes = serialize_public_key(self.EK.public_key())
		msg_to_send = b''.join([IK_bytes, EK_bytes])
		print(f"   Shared key: {b64(self.shared_key)}")
		with open(path_x3dh_established, 'ab') as x3dh_established_file:
			x3dh_established_file.write(bytes(self.identifier_partner + os.linesep, 'utf-8'))
			pass
		save_status(self)
		return(msg_to_send)

	def load_prev_pubkey(self) -> bytes:
		print("DoubleRatchetInterface().load_prev_pubkey()")
		try:
			with open(self.path_prev_pubkey, 'rb') as file:
				key_bytes = file.read()
				return key_bytes
		except FileNotFoundError:
			return None

	def initialize_ratchets(self):
		print("DoubleRatchetInterface().initialize_ratchets")
		self.root_ratchet = SymmRatchet(self.shared_key)
		if self.x3dh_role == "master":
			print("   Initialized ratchets as master")
			#initialize the root chain with the shared key
			self.recv_ratchet = SymmRatchet(self.root_ratchet.next()[0])
			self.send_ratchet = SymmRatchet(self.root_ratchet.next()[0])
		elif self.x3dh_role == "slave":
			print("   Initialized ratchets as slave")
			self.send_ratchet = SymmRatchet(self.root_ratchet.next()[0])
			self.recv_ratchet = SymmRatchet(self.root_ratchet.next()[0])
			self.DH_ratchet = None
		else:
			print("Can't tell if we're Alice/Bob!")


class SymmRatchet(object):
	def __init__(self, key):
		print("SymmRatchet().__init__()")
		self.state = key

	def next(self, inp=b''):
		print("SymmRatchet().next()")
		# turn the ratchet, changing the state and yielding a new key and IV
		output = hkdf(self.state + inp, 80)
		self.state = output[:32]
		outkey, iv = output[32:64], output[64:]
		return(outkey, iv)

def get_x3dh_status(identifier_partner: str, new_action):
	print("get_x3dh_status()")
	#Returns:
	# 0 - Not initialized could be either Person1 or Person2
	# 1 - Initialized, waiting for the response x3dh prekey bundle from Person2
	# 3 - Person1, just received response_prekey bundle from Person2
	# 4 - x3dh exchange completed for Person1 or Person2
	# Check if files where identifier_partner exist, if not create them
	try:
		os.mkdir(os.getcwd() + FOLDERNAME_KEYS)
	except FileExistsError:
		pass
	try:
		with open(path_x3dh_established, 'x') as x3dh_established_file:
			print(f"    Created file: {path_x3dh_established}")
			pass
	except OSError:
		pass
	try:
		with open(path_x3dh_outstanding, 'x') as x3dh_outstanding_file:
			print(f"    Created file: {path_x3dh_outstanding}")
			pass
	except OSError:
		pass
	#Check files for identifier_partner
	with open(path_x3dh_established, 'rt') as x3dh_established_file:
		lines = [line.rsplit()[0] for line in x3dh_established_file.readlines()]
		print("   +++++++++")
		print(f"   identifier_partner: {identifier_partner}")
		print(f"   lines in x3dh_established_file: {lines}")
		print("   +++++++++")
		if identifier_partner in lines:
			return 4

	with open(path_x3dh_outstanding, 'rt') as x3dh_outstanding_file:
		lines = [line.rsplit()[0] for line in x3dh_outstanding_file.readlines()]
		print("   +++++++++")
		print(f"   identifier_partner: {identifier_partner}")
		print(f"   lines in x3dh_outstanding_file: {lines}")
		print("   +++++++++")
		if identifier_partner in lines:
			if new_action == "obfuscatedRetrieval/response_prekey_bundle":
				return 3
			else:
				return 1
		elif new_action == "obfuscatedRetrieval/prekey_bundle":
			return 0
	return 0


#TODO: Go through code and adapt it to our codebase
def encrypt_msg(double_ratchet_interface: DoubleRatchetInterface, msg: str) -> (bytes, bytes):
	print("encrypt_msg()")
	# Encrypts the message.
	# Returns the ciphertext and the next DH_ratchet public key.
	print(f"   MSG: {msg[:50]}....")
	msg = msg.encode('utf-8')
	print(f"   MSG encoded: {msg[:50]}...")
	key, iv = double_ratchet_interface.send_ratchet.next()
	double_ratchet_interface.Ns += 1
	cipher = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(msg))
	print(f"   cipher: {cipher[:50]}...")
	#print(f"   key: {key}, iv:{iv}")
	print(f"   cipher decrypted {unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(cipher))[:50]}...")
	save_status(double_ratchet_interface)
	return cipher, serialize_public_key(double_ratchet_interface.DH_ratchet.public_key())


#TODO: Go through code and adapt it to our codebase
def decrypt_msg(double_ratchet_interface: DoubleRatchetInterface, cipher: bytes, public_key) -> str:
	print("decrypt_msg()")
	prev_pubkey = double_ratchet_interface.load_prev_pubkey()
	load_status(double_ratchet_interface)
	# receive (Alice's new) public key and use it to perform a DH
	if prev_pubkey != serialize_public_key(public_key):
		dh_ratchet(double_ratchet_interface, public_key)
	key, iv = double_ratchet_interface.recv_ratchet.next()
	# decrypt the message using the new recv ratchet
	decrypted = AES.new(key, AES.MODE_CBC, iv).decrypt(cipher)
	#print(f"   key: {key}, iv: {iv}")
	print(f"   CIPHER: {cipher[:50]}")
	print(f"   DECRYPTED: {decrypted[:50]}")
	msg = unpad(decrypted)
	#print("   MESSAGE:", msg)
	msg = msg.decode('utf-8')
	print(f"   MESSAGE decoded: {msg[:50]}")
	double_ratchet_interface.save_prev_pubkey(serialize_public_key(public_key))
	save_status(double_ratchet_interface)
	return msg

#TODO: Go through code and adapt it to our codebase
def dh_ratchet(double_ratchet_interface: DoubleRatchetInterface, public_key):
	print("dh_ratchet()")
	#perform a DH ratchet rotation using received public key
	if double_ratchet_interface.DH_ratchet is not None:
		# the first time we don't have a DH ratchet yet
		dh_recv = double_ratchet_interface.DH_ratchet.exchange(public_key)
		shared_recv = double_ratchet_interface.root_ratchet.next(dh_recv)[0]
		# use Bob's public and our old private key
		# to get a new recv ratchet
		double_ratchet_interface.recv_ratchet = SymmRatchet(shared_recv)
	# generate a new key pair and send ratchet
	# our new public key will be sent with the next message to Bob
	double_ratchet_interface.DH_ratchet = X25519PrivateKey.generate()
	dh_send = double_ratchet_interface.DH_ratchet.exchange(public_key)
	shared_send = double_ratchet_interface.root_ratchet.next(dh_send)[0]
	double_ratchet_interface.send_ratchet = SymmRatchet(shared_send)
	double_ratchet_interface.PNs = double_ratchet_interface.Ns
	double_ratchet_interface.Ns = 0


def save_status(double_ratchet_interface):
	print("save_status()")
	# 1. Find occurence and delete it
	try:
		with open(double_ratchet_interface.path_backup, 'rb') as backup_file:
			all = backup_file.read()
		k = 0
		all_updated = None
		while True:
			identifier_length = int.from_bytes(all[k:k + 4], 'big')
			if all[k + 4:k + 4 + identifier_length] == bytes(double_ratchet_interface.identifier_partner, 'utf-8'):
				all_updated = all[:k] + all[k + 4 + identifier_length + 692:]
				break
			elif all[k + 4:k + 4 + identifier_length] == b'':
				break
			k += 4 + identifier_length + 692

		if all_updated != None:

			with open(double_ratchet_interface.path_backup, 'wb') as backup_file:
				backup_file.write(all_updated)
	except FileNotFoundError:
		pass
	# 2. Save state
	bytes_to_save = b''.join(
		[len(bytes(double_ratchet_interface.identifier_partner, encoding='utf-8')).to_bytes(4, 'big'),  # 4
		 bytes(double_ratchet_interface.identifier_partner, encoding='utf-8'),  # ?
		 double_ratchet_interface.Ns.to_bytes(4, 'big'),  # 4
		 double_ratchet_interface.Nr.to_bytes(4, 'big'),  # 4
		 double_ratchet_interface.PNs.to_bytes(4, 'big'),  # 4
		 double_ratchet_interface.PNr.to_bytes(4, 'big'),  # 4
		 serialize_private_key(double_ratchet_interface.DH_ratchet),  # 290
		 serialize_private_key(double_ratchet_interface.IK),  # 290
		 double_ratchet_interface.send_ratchet.state,  # 32
		 double_ratchet_interface.recv_ratchet.state,  # 32
		 double_ratchet_interface.root_ratchet.state]  # 32
	)
	with open(double_ratchet_interface.path_backup, 'ab') as backup_file:
		backup_file.write(bytes_to_save)
	pass


def load_status(double_ratchet_interface):
	print("load_status()")
	with open(double_ratchet_interface.path_backup, 'rb') as backup_file:
		all = backup_file.read()
	k = 0
	keys = None
	while True:
		identifier_length = int.from_bytes(all[k:k + 4], 'big')
		print(f"   backup_file: {all[:100]}")
		if all[k + 4:k + 4 + identifier_length] == bytes(double_ratchet_interface.identifier_partner, 'utf-8'):
			keys = all[k + 4 + identifier_length:k + 4 + identifier_length + 692]
			break
		elif all[k + 4:k + 4 + identifier_length] == b'':
			print("   Something went wrong. Cannot find saved keys for this person. Shutting down...")
			raise Exception('Trying to create a DR Interface as recipient, even though we are the initiator.')
		k += 4 + identifier_length + 692

	double_ratchet_interface.Ns = int.from_bytes(keys[0:4], 'big')
	double_ratchet_interface.Nr = int.from_bytes(keys[4:8], 'big')
	double_ratchet_interface.PNs = int.from_bytes(keys[8:12], 'big')
	double_ratchet_interface.PNr = int.from_bytes(keys[12:16], 'big')
	double_ratchet_interface.DH_ratchet = deserialize_private_key(keys[16:16 + 290])
	double_ratchet_interface.IK = deserialize_private_key(keys[16 + 290:16 + 2 * 290])
	double_ratchet_interface.send_ratchet = SymmRatchet(keys[596:596 + 32])
	double_ratchet_interface.recv_ratchet = SymmRatchet(keys[596 + 32:596 + 2 * 32])
	double_ratchet_interface.root_ratchet = SymmRatchet(keys[596 + 2 * 32:596 + 3 * 32])
