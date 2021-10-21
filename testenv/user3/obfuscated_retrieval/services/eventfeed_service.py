import time

import obfuscated_retrieval.double_ratchet.double_ratchet_functions
from ..BACnet.utils.logStore.appconn.connection import Function
from ..BACnet.utils.EventCreationTool import EventFactory
from obfuscated_retrieval.double_ratchet.crypto_signing import FOLDERNAME_KEYS, b64, serialize_public_key
from obfuscated_retrieval.services.double_ratchet_files_service import DoubleRatchetFilesService
from obfuscated_retrieval.services.bookkeeper_service import BookkeeperService
import inspect
import hashlib
import os

contactedFile = os.getcwd() + FOLDERNAME_KEYS + '/contacted.key'

class EventfeedService:
    def __init__(self):
        self.event_database_handler = Function()
        self.dr_files_handler = DoubleRatchetFilesService()
        self.BookkeeperService = BookkeeperService(self.event_database_handler._handler.get_host_master_id())

    def create_new_feed(self):
        print("create_new_feed()")
        event_factory = EventFactory(path_to_keys=os.getcwd() + "/public_key")
        first_event = event_factory.first_event('obfuscatedRetrieval', self.event_database_handler.get_host_master_id())
        self.event_database_handler.insert_event(first_event)
        return event_factory.get_feed_id()

    def create_prekey_bundle_event(self, recipient_key, feedid, prekeybundle):
        print("create_prekey_bundle_event()")
        last_event = self.event_database_handler.get_current_event(feedid)
        event_factory = EventFactory(last_event=last_event, path_to_keys=os.getcwd() + "/public_key")
        prekeybundle_event = event_factory.next_event('obfuscatedRetrieval/prekey_bundle', {
            'publicKey': recipient_key,
            'prekey_bundle': prekeybundle,
            'timestamp': time.time()
        })
        self.event_database_handler.insert_event(prekeybundle_event)

    def create_response_prekey_bundle_event(self, recipient_key, response_prekey_bundle):
        print("create_response_prekey_bundle_event()")
        feedid = self.create_new_feed()
        self.BookkeeperService.save_feed_for_user(recipient_key,feedid)
        last_event = self.event_database_handler.get_current_event(feedid)
        event_factory = EventFactory(last_event=last_event, path_to_keys=os.getcwd() + "/public_key")
        prekeybundle_event = event_factory.next_event('obfuscatedRetrieval/response_prekey_bundle', {
            'publicKey': recipient_key,
            'response_prekey_bundle': response_prekey_bundle,
            'timestamp': time.time()
        })
        self.event_database_handler.insert_event(prekeybundle_event)

    def send_confirmation_message(self, recipient_key, databases_schemata):
        print(f"send_confirmation_message(self, {recipient_key}), databases_schemata")
        #feedid = self.create_new_feed()
        feedid = self.BookkeeperService.get_feed_for_user(recipient_key)
        last_event = self.event_database_handler.get_current_event(feedid)
        event_factory = EventFactory(last_event=last_event, path_to_keys=os.getcwd() + "/public_key")

        obfuscated_retrieval_request_event = event_factory.next_event('obfuscatedRetrieval/confirmation-message', {
            'publicKey': recipient_key,
            'confirmation-message': databases_schemata,
            'timestamp': time.time()
        })
        self.event_database_handler.insert_event(obfuscated_retrieval_request_event)

    def contact_user(self, recipient_key, prekeybundle):
        print("contact_user()")
        feedid = self.create_new_feed()
        self.BookkeeperService.save_feed_for_user(recipient_key,feedid)
        self.create_prekey_bundle_event(recipient_key, feedid, prekeybundle)

    def add_user_to_contacted_file(self, recipient_key):
        print("add_user_to_contacted_file")
        try:
            with open(contactedFile, "a") as contacted_file:
                contacted_file.write(recipient_key + os.linesep)
        except Exception as ex:
            print("   Could not add {recipient_key} to contacted_file!")
            exit()
        print(f"   Added {recipient_key} to {contactedFile}")

    def get_x3dh_role(self, recipient_key):
        print(f"get_x3dh_role(self,{recipient_key})")
        try:
            with open(contactedFile, 'x') as contacted_file:
                if (inspect.stack()[1][3]) == "contact_bacnet_user":
                    self.add_user_to_contacted_file(recipient_key)
        except OSError:
            if (inspect.stack()[1][3]) == "contact_bacnet_user":
                self.add_user_to_contacted_file(recipient_key)
            pass

        try:
            with open(contactedFile, "rt") as contacted_file:
                lines = contacted_file.read().splitlines()
                print()
            print(f"   lines: {lines}")
            for line in lines:
                if type(recipient_key) == str:
                    print("   type(recipient_key) == str")
                    if line == recipient_key:
                        print("   master")
                        return "master"
                if type(recipient_key) == bytes:
                    if line == recipient_key:
                        print("   master")
                        return "master"
            print("   slave")
            return "slave"
        except FileNotFoundError as ex:
            print("    No contacted_file found.")
        except TypeError as typeex:
            print(f"    TypeError: {typeex}")
        except Exception as er:
            print(f"   Error: {er}")

    def read_event_data(self, targetfeedid):
        seqno = self.event_database_handler.get_current_seq_no(targetfeedid)
        data = self.event_database_handler._handler.get_obfuscatedRetrieval_event_data(targetfeedid, seqno)
        return data

    def get_foreign_master_keys(self):
        print("get_foreign_master_keys()")
        master_keys = self.event_database_handler._handler.get_all_master_ids()
        master_keys_hashes = [hashlib.md5(master_key).hexdigest() for master_key in master_keys]
        return (master_keys, master_keys_hashes)

    def get_all_message_feedids(self):
        return self.event_database_handler._handler.get_all_obfuscatedRetrieval_events_feed_ids()

    def get_all_feedids_with_obfuscated_retrieval_prekey_bundle_events(self):
        print("get_all_feedids_with_obfuscated_retrieval_prekey_bundle_events()")
        feedIDs = self.event_database_handler._handler.get_all_obfuscatedRetrieval_events_feed_ids()
        for id in feedIDs:
            seq_no = self.event_database_handler._handler.get_current_seq_no(id)
            meta, content = self.event_database_handler._handler.get_obfuscatedRetrieval_event_as_cbor(id, seq_no)
            if meta == 'obfuscatedRetrieval/prekey_bundle':
                if content['publicKey'] == hashlib.md5(self.event_database_handler._handler.get_host_master_id()).hexdigest():
                    yield id

    def get_all_feedids_response_prekey_bundle_events(self):
        print("get_all_feedids_response_prekey_bundle_events()")
        feedIDs = self.event_database_handler._handler.get_all_obfuscatedRetrieval_events_feed_ids()
        for id in feedIDs:
            seq_no = self.event_database_handler._handler.get_current_seq_no(id)
            event_already_processed = self.BookkeeperService.check_feed_entry(seq_no, id)
            meta, content = self.event_database_handler._handler.get_obfuscatedRetrieval_event_as_cbor(id, seq_no)
            if meta == 'obfuscatedRetrieval/response_prekey_bundle' and not event_already_processed:
                if content['publicKey'] == hashlib.md5(self.event_database_handler._handler.get_host_master_id()).hexdigest():
                    yield id

    def create_obfuscated_retrieval_request_event(self, recipient_key, cipher, public_key):
        #feedid = self.create_new_feed()
        feedid = self.BookkeeperService.get_feed_for_user(recipient_key)
        last_event = self.event_database_handler.get_current_event(feedid)
        event_factory = EventFactory(last_event=last_event, path_to_keys=os.getcwd() + "/public_key")

        obfuscated_retrieval_request_event = event_factory.next_event('obfuscatedRetrieval/obfuscated_retrieval_request', {
            'publicKey': recipient_key,
            'encrypted-pir-query': b''.join([public_key, cipher]),
            'timestamp': time.time()
        })
        self.event_database_handler.insert_event(obfuscated_retrieval_request_event)

    def create_obfuscated_retrieval_response_event(self, recipientkey, cipher, publickey):
        #feedid = self.create_new_feed()
        feedid = self.BookkeeperService.get_feed_for_user(recipientkey)
        last_event = self.event_database_handler.get_current_event(feedid)
        event_factory = EventFactory(last_event=last_event, path_to_keys=os.getcwd() + "/public_key")

        obfuscated_retrieval_request_event = event_factory.next_event(
            'obfuscatedRetrieval/obfuscated_retrieval_response', {
                'publicKey': recipientkey,
                'encrypted-pir-response': b''.join([publickey, cipher]),
                'timestamp': time.time()
            })
        self.event_database_handler.insert_event(obfuscated_retrieval_request_event)

    def get_confirmation_message_ids(self):
        print("get_confirmation_message_ids()")
        feedIDs = self.event_database_handler._handler.get_all_obfuscatedRetrieval_events_feed_ids()
        for id in feedIDs:
            seq_no = self.event_database_handler._handler.get_current_seq_no(id)
            event_already_processed = self.BookkeeperService.check_feed_entry(seq_no, id)
            meta, content = self.event_database_handler._handler.get_obfuscatedRetrieval_event_as_cbor(id, seq_no)
            if meta == 'obfuscatedRetrieval/confirmation-message' and not event_already_processed:
                if content['publicKey'] == hashlib.md5(self.event_database_handler._handler.get_host_master_id()).hexdigest():
                    yield id

    def get_obfuscated_retrieval_request_cipher(self):
        print("get_obfuscated_retrieval_request_ciper()")
        feedIDs = self.event_database_handler._handler.get_all_obfuscatedRetrieval_events_feed_ids()
        for id in feedIDs:
            seq_no = self.event_database_handler._handler.get_current_seq_no(id)
            meta, content = self.event_database_handler._handler.get_obfuscatedRetrieval_event_as_cbor(id, seq_no)
            hostmaster_id = hashlib.md5(self.event_database_handler._handler.get_host_master_id()).hexdigest()
            print(f"   meta: {meta}")
            publickey = content['publicKey']
            if meta == 'obfuscatedRetrieval/obfuscated_retrieval_request':
                event_already_processed = self.BookkeeperService.check_feed_entry(seq_no, id)
                if publickey == hostmaster_id and not event_already_processed:
                    print("publickey == hostmasterid")
                    print("   get_obfuscated_retrieval_request_cipher:", id)
                    self.dr_files_handler.add_x3dh_established(hashlib.md5(self.event_database_handler._handler.get_master_id_from_feed(id)).hexdigest())
                    yield id


    def get_obfuscated_retrieval_response_cipher(self):
        print("get_obfuscated_retrieval_response_cipher()")
        feedIDs = self.event_database_handler._handler.get_all_obfuscatedRetrieval_events_feed_ids()
        for id in feedIDs:
            seq_no = self.event_database_handler._handler.get_current_seq_no(id)
            meta, content = self.event_database_handler._handler.get_obfuscatedRetrieval_event_as_cbor(id, seq_no)
            hostmaster_id = hashlib.md5(self.event_database_handler._handler.get_host_master_id()).hexdigest()
            print(f"   meta: {meta}")
            publickey = content['publicKey']
            if meta == 'obfuscatedRetrieval/obfuscated_retrieval_response':
                if not self.BookkeeperService.check_feed_entry(seq_no, id) and publickey == hostmaster_id:
                    print("get_obfuscated_retrieval_request_cipher:", id)
                    self.dr_files_handler.add_x3dh_established(hashlib.md5(self.event_database_handler._handler.get_master_id_from_feed(id)).hexdigest())
                    yield id
