from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from xeddsa.implementations import XEdDSA25519
import base64
import os

#Code taken directly from /HS2020/Groups/03-DoubleRatchet/src/helper_functions

# This is not cryptographically safe. To be that the program should be a fixed set of operations that run every time.

''' HOW TO USE
from signing import xeddsa_sign, xeddsa_verify

##### SENDING PART #####
msg = 'This is a secret message.'
pubkey, signed_msg = xeddsa_sign(msg)

#### RECEIVING PART ####
if xeddsa_verify(pubkey=pubkey, data=msg, signature=signed_msg):
    #print('Verification successful!')
else:
    #print('Verification failed!')
'''

FOLDERNAME_KEYS = '/encryption_key_files'
path_keys = os.getcwd() + FOLDERNAME_KEYS + '/xed_keys.key'


def load_key():
    try:
        with open(path_keys, 'rb') as f:
            privkey = f.read()
            assert (len(privkey) == 32)
            #print("Loaded saved xed private key.")
    except FileNotFoundError:
        #print("No XEd private key found. Creating new key...")
        xed = XEdDSA25519(mont_priv=None, mont_pub=None)
        privkey = xed.generate_mont_priv()
        with open(path_keys, 'wb') as f:
            f.write(privkey)
            #print("Xed private key saved.")
        pass
    return privkey


def xeddsa_sign(msg) -> (bytes, bytes):
    # Returns: public key, signed message
    xed_private_key = load_key()
    xed_send = XEdDSA25519(mont_priv=xed_private_key)
    xed_public_key = xed_send.mont_pub_from_mont_priv(xed_private_key)
    signed_msg = xed_send.sign(msg)
    return xed_public_key, signed_msg


def xeddsa_verify(pubkey, data, signature) -> bool:
    # Returns: True or False
    xed_recv = XEdDSA25519(mont_priv=None, mont_pub=pubkey)
    return xed_recv.verify(data=data, signature=signature)

def b64(msg):
    # base64 encoding helper function
    return base64.encodebytes(msg).decode('utf-8').strip()

def hkdf(inp, length):
    # HKDF = HMAC Key-derivation funktion
    # use HKDF on an input to derive a key
    hkdf = HKDF(algorithm=hashes.SHA256(), length=length, salt=b'',
                info=b'', backend=default_backend())
    return hkdf.derive(inp)

def pad(msg):
    # pkcs7 padding
    #print(f"pad({msg})")
    num = 16 - (len(msg) % 16)
    #print(f"   num: {num}")
    #print(f"   bytes([num]*num): {bytes([num]*num)}")
    #print(f"   msg + bytes([num] * num): {msg+bytes([num]*num)}")
    return msg + bytes([num] * num)

def unpad(msg):
    # remove pkcs7 padding
    #print(f"unpad({msg})")
    #print(f"   msg[-1]: {msg[-1]}")
    #print(f"   -msg[-1]: {-msg[-1]}")
    #print(f"   msg[:-msg[-1]]: {msg[:-msg[-1]]}")
    return msg[:-msg[-1]]

def serialize_public_key(public_key: X25519PublicKey) -> bytes:
    return public_key.public_bytes(encoding=serialization.Encoding.Raw,
                                   format=serialization.PublicFormat.Raw)
def deserialize_public_key(public_bytes) -> X25519PublicKey:
    return X25519PublicKey.from_public_bytes(public_bytes)


def serialize_private_key_raw(private_key: X25519PrivateKey) -> bytes:
    return private_key.private_bytes(encoding=serialization.Encoding.Raw,
                                     format=serialization.PrivateFormat.Raw,
                                     encryption_algorithm=serialization.NoEncryption())

def serialize_private_key(private_key: X25519PrivateKey) -> bytes:
    # Takes a X25519PrivateKey object and returns a bytestring representing this key.
    return private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                     format=serialization.PrivateFormat.PKCS8,
                                     encryption_algorithm=serialization.BestAvailableEncryption(b'pw'))

def deserialize_private_key(private_bytes) -> X25519PrivateKey:
    # Takes a bytestring and returns the corresponding X25519PrivateKey object.
    loaded_key = serialization.load_pem_private_key(data=private_bytes,
                                                    password=b'pw',
                                                    backend=default_backend())
    return loaded_key
