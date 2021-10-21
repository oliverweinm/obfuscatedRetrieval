#from obfuscated_retrieval.double_ratchet_functions_debug import *
from obfuscated_retrieval.double_ratchet.double_ratchet_functions import *
from .double_ratchet_files_service import DoubleRatchetFilesService

class DoubleRatchetService:
    def __init__(self):
        print("DoubleRatchetService.__init__()")
        self.double_ratchet_files_service = DoubleRatchetFilesService()
        pass

    def create_prekey_bundle(self, recipient_key, x3dh_role):
        print("DoubleRatchetService.create_prekey_bundle()")
        dri = DoubleRatchetInterface(recipient_key, "", x3dh_role)
        return dri.create_prekey_bundle()

    def create_response_prekey_bundle(self, recipient_key, prekey_bundle, x3dh_role):
        print("DoubleRatchetService.create_response_prekey_bundle()")
        dri = DoubleRatchetInterface(recipient_key, "obfuscatedRetrieval/prekey_bundle", x3dh_role)
        return dri.create_prekey_bundle_from_received_bundle(prekey_bundle)

    def complete_key_exchange(self, recipient_key, response_prekey_bundle, x3dh_role):
        print("DoubleRatchetService.complete_key_exchange()")
        dri = DoubleRatchetInterface(recipient_key, "obfuscatedRetrieval/response_prekey_bundle", x3dh_role)
        dri.complete_transaction_with_partner_keys(response_prekey_bundle[0])

    def encrypt(self, targetkey, msg, x3dh_role: str):
        print("DoubleRatchetService.encrypt()")
        dri = DoubleRatchetInterface(targetkey, "", x3dh_role)
        return encrypt_msg(dri, msg)

    def decrypt(self, targetkey, public_key, cipher, x3dh_role: str):
        print("DoubleRatchetService.decrypt()")
        dri = DoubleRatchetInterface(targetkey, "", x3dh_role)
        return decrypt_msg(dri, cipher, deserialize_public_key(public_key))

    def is_x3dh_outstanding(self, recipient_key):
        print(f"is_x3dh_outstanding({recipient_key})")
        return self.double_ratchet_files_service.is_x3dh_outstanding(recipient_key)

    def is_x3dh_established(self, recipient_key):
        print(f"DoubleRatchetService.is_x3dh_established({recipient_key})")
        return self.double_ratchet_files_service.is_x3dh_established(recipient_key)

    def is_x3dh_confirmed(self, recipient_key):
        print(f"DoubleRatchetService.is_x3dh_confirmed({recipient_key})")
        return self.double_ratchet_files_service.is_x3dh_confirmed(recipient_key)

    def is_x3dh_started(self, recipient_key):
        print(f"DoubleRatchetService.is_x3dh_started({recipient_key})")
        return self.double_ratchet_files_service.is_x3dh_started(recipient_key)

    def get_x3dh_confirmed_list(self):
        n_confirmed_peers, confirmed_list = self.double_ratchet_files_service.get_x3dh_confirmed_list()
        return n_confirmed_peers, confirmed_list
