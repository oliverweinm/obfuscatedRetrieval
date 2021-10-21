import sqlite3

from obfuscated_retrieval.services.double_ratchet_service import DoubleRatchetService
from obfuscated_retrieval.services.eventfeed_service import EventfeedService
from obfuscated_retrieval.services.private_information_retrieval_service import PrivateInformationRetrievalService
from obfuscated_retrieval.services.databases_service import DatabasesService
from obfuscated_retrieval.services.double_ratchet_files_service import DoubleRatchetFilesService
from obfuscated_retrieval.services.bookkeeper_service import BookkeeperService
import hashlib
import ast


class ObfuscatedRetrievalCli:
    def __init__(self):
        self.double_ratchet_service = DoubleRatchetService()
        self.eventfeed_service = EventfeedService()
        self.pir_service = PrivateInformationRetrievalService()
        self.databases_service = DatabasesService()
        self.dr_file_service = DoubleRatchetFilesService()
        self.bookkeeper = BookkeeperService(self.eventfeed_service.event_database_handler._handler.get_host_master_id())
        self.our_masterfeed_id = self.bookkeeper.ourIdentifier

    def contact_bacnet_user(self):
        print("contact_bacnet_user(self):")
        selected_key = self.select_target_user()
        if self.double_ratchet_service.is_x3dh_started(selected_key):
            print("   X3DH HAS ALREADY BEEN STARTED WITH THIS USER/n PLEASE CONTACT ANOTHER USER.")
        else:
            x3dh_role = self.eventfeed_service.get_x3dh_role(selected_key)
            prekey_bundle = self.double_ratchet_service.create_prekey_bundle(selected_key, x3dh_role)
            self.eventfeed_service.contact_user(selected_key, prekey_bundle)

    def get_established_contacts(self):
        print("get_established_contacts(self):")
        return self.dr_file_service.get_x3dh_confirmed_list()

    def select_target_user(self):
        print("select_target_user()")
        keys, keys_hashes = self.eventfeed_service.get_foreign_master_keys()
        i = 1
        for k in keys:
            print(f"    {i}: {k}, {[keys_hashes[i-1]]}")
            i += 1
        selection = input(f"select [1-{i - 1}]: ")
        selected_key = keys_hashes[int(selection) - 1]
        return selected_key

    def check_for_prekey_bundle_events(self):
        print("check_for_prekey_bundle_event()")
        ids = self.eventfeed_service.get_all_feedids_with_obfuscated_retrieval_prekey_bundle_events()
        ids = [i for i in ids]
        for i in ids:
            recipient_key = hashlib.md5(self.eventfeed_service.event_database_handler._handler.get_master_id_from_feed(i)).hexdigest()
            if not self.double_ratchet_service.is_x3dh_started(recipient_key):
                x3dh_role = self.eventfeed_service.get_x3dh_role(recipient_key)
                responsekey_bundle=self.double_ratchet_service.create_response_prekey_bundle(
                    recipient_key,
                    self.eventfeed_service.read_event_data(i)[0],
                    x3dh_role)
                self.eventfeed_service.create_response_prekey_bundle_event(recipient_key, responsekey_bundle)

    def check_for_response_prekey_bundle_events(self):
        print("check_for_response_prekey_bundle_events(self)")
        ids = [i for i in self.eventfeed_service.get_all_feedids_response_prekey_bundle_events()]
        for id in ids:
            respkb = self.eventfeed_service.read_event_data(id)
            recipient_key = hashlib.md5(self.eventfeed_service.event_database_handler._handler.get_master_id_from_feed(id)).hexdigest()
            if not self.double_ratchet_service.is_x3dh_established(recipient_key):
                x3dh_role = self.eventfeed_service.get_x3dh_role(recipient_key)
                print("   check_for_response_prekey_bundle_events(), x3dh_role:", x3dh_role)
                self.double_ratchet_service.complete_key_exchange(recipient_key, respkb, x3dh_role)
                db_schema_as_string = str(self.databases_service.get_db_schemata())
                self.eventfeed_service.send_confirmation_message(recipient_key, db_schema_as_string)

    def relay_messages(self):
         message_feed_ids = self.eventfeed_service.get_all_message_feedids()
         contacts = self.get_established_contacts()
         for id in message_feed_ids:
             sender = self.eventfeed_service.event_database_handler._handler.get_master_id_from_feed(id)
             seq_no = self.eventfeed_service.event_database_handler._handler.get_current_seq_no(id)
             meta, content = self.eventfeed_service.event_database_handler._handler.get_obfuscatedRetrieval_event_as_cbor(id, seq_no)
             recipientKey = content['publicKey']
             for contact in contacts:
                 if sender is not contact:
                     if meta == 'obfuscatedRetrieval/response_prekey_bundle':
                         data = content['response_prekey_bundle']
                         self.eventfeed_service.create_response_prekey_bundle_event(recipientKey, data)
                     if meta == 'obfuscatedRetrieval/obfuscated_retrieval_request':
                         data = content['encrypted-pir-query']
                         self.eventfeed_service.create_obfuscated_retrieval_request_event(recipientKey, data[32:], data[:32])
                     if meta == 'obfuscatedRetrieval/obfuscated_retrieval_response':
                         data = content['encrypted-pir-response']
                         self.eventfeed_service.create_obfuscated_retrieval_response_event(recipientKey, data[32:], data[:32])
                     if meta == 'obfuscatedRetrieval/confirmation-message':
                         data = content['confirmation-message']
                         self.eventfeed_service.send_confirmation_message(recipientKey, data)

    def build_pir_query(self, method, n):
        print("build_pir_query(self, method, n")
        self.pir_service.new_query()
        table = input("table: ")
        self.pir_service.add_from_table(table)
        column = input("column: ")
        self.pir_service.add_select_column(column)
        clause_column = input("clause-column: ")
        operator = input("clause-operator: ")
        value = input("clause-value: ")
        self.pir_service.add_where_clause(clause_column, operator, value)
        maxlengthoftable = input("maxlengtht of table")
        if method == 1:
            return self.pir_service.get_randomized_query(n=n, maxlength_of_table=int(maxlengthoftable))
        if method == 2:
            return self.pir_service.get_obfuscated_query()

    def create_pir_request(self):
        print("create_pir_request(self)")
        method = int(input("Which PIR method: [1] random queries [2] entire columns"))
        contacts, number_of_contacts = self.get_established_contacts()
        print("   ENCRYPT MESSAGE CONTACTS:", contacts)
        queries = [q for q in self.build_pir_query(int(number_of_contacts), int(method))]
        print("   QUERIES:", queries)
        self.bookkeeper.write_to_requests_file(self.pir_service.query_builder.buildQuery(),queries)
        for contact in contacts:
            x3dh_role = self.eventfeed_service.get_x3dh_role(contact)
            print("   create_pir_request(), x3dh_role:", x3dh_role)
            print("   TARGET KEY/ IDENTIFIER PARTNER:", contact, len(contact))
            cipher, public_key = self.double_ratchet_service.encrypt(contact, queries[contacts.index(contact)], x3dh_role)
            self.eventfeed_service.create_obfuscated_retrieval_request_event(contact, cipher, public_key)

    def encrypt_message_for_user(self, targetkey, message):
        x3dh_role = self.eventfeed_service

    def decrypt_message_requests(self):
        print("decrypt_message_requests(self)")
        id = self.eventfeed_service.get_obfuscated_retrieval_request_cipher()
        l = [i for i in id]
        print(f"l: {l}")
        for i in l:
            recipient_key = hashlib.md5(self.eventfeed_service.event_database_handler._handler.get_master_id_from_feed(i)).hexdigest()
            self.dr_file_service.add_to_x3dh_confirmed_list(recipient_key)
            key_cipher = self.eventfeed_service.read_event_data(i)
            key_cipher = key_cipher[0]
            key = key_cipher[:32]
            cipher = key_cipher[32:]
            x3dh_role = self.eventfeed_service.get_x3dh_role(recipient_key)
            print("key,: ", key)
            print("cipher:", cipher[:100])
            yield (recipient_key, self.double_ratchet_service.decrypt(recipient_key, key, cipher, x3dh_role))

    def decrypt_message_response(self):
        id = self.eventfeed_service.get_obfuscated_retrieval_response_cipher()
        l = [i for i in id]
        print(f"l: {l}")
        for i in l:
            recipient_key = hashlib.md5(self.eventfeed_service.event_database_handler._handler.get_master_id_from_feed(i)).hexdigest()
            self.dr_file_service.add_to_x3dh_confirmed_list(recipient_key)
            key_cipher = self.eventfeed_service.read_event_data(i)
            key_cipher = key_cipher[0]
            key = key_cipher[:32]
            cipher = key_cipher[32:]
            x3dh_role = self.eventfeed_service.get_x3dh_role(recipient_key)
            print("key,: ", key)
            print("cipher:", cipher[:100])
            yield (recipient_key, self.double_ratchet_service.decrypt(recipient_key, key, cipher, x3dh_role))


    def read_all_obfuscated_retrieval_requests(self):
        print("read_all_obfuscated_retrieval_requests(self)")
        senderkey_sqlqueries_tuples = [q for q in self.decrypt_message_requests()]
        for q in senderkey_sqlqueries_tuples:
            print(f"q: {q}")
            query = q[1]
            keys, result = self.databases_service.execute_query(query)
            #result = "".join(keys,result)
            print(f"   result: {result}, type(result): {type(result)}")
            if result != None:
                targetkey = q[0]
                print(f"   targetkey: {targetkey}")
                x3dh_role = self.eventfeed_service.get_x3dh_role(targetkey)
                cipher, public_key = self.double_ratchet_service.encrypt(targetkey, keys+str(result), x3dh_role)
                self.eventfeed_service.create_obfuscated_retrieval_response_event(targetkey, cipher, public_key)
            else:
                #In this case, the and we're merely a point on the way fo the request to its target DB
                contacts, number_of_contacts = self.get_established_contacts()
                print(f"   contacts: {contacts}")
                for contact in contacts:
                    print(f"   contact: {contact}")
                    print(f"   q[0]: {q[0]}")
                    if contact != q[0] and query[0] != '{':
                        x3dh_role = self.eventfeed_service.get_x3dh_role(contact)
                        cipher, public_key = self.double_ratchet_service.encrypt(contact, query, x3dh_role)
                        print("$$$$$$$ created obfuscated_retrieval_response_event")
                        self.eventfeed_service.create_obfuscated_retrieval_request_event(contact, cipher, public_key)

    def read_all_obfuscated_retrieval_response(self):
        print("read_all_obfuscated_retrieval_response(self)")
        senderkey_sqlresponse_tuples = [q for q in self.decrypt_message_response()]
        for q in senderkey_sqlresponse_tuples:
            print("   RESPONSE", q[1][:75])
            print(q[0])
            self.pir_service.add_results_string(q[1])
            is_request_fulfilled = self.bookkeeper.check_response()
            print(f"   is_request_fulfilled: {is_request_fulfilled}")
            if is_request_fulfilled:
                #print(self.pir_service.get_queried_results())
                #results = self.pir_service.get_queried_results()
                original_query = self.bookkeeper.requests_dictionary["request"]
                #original_query = self.pir_service.query_builder.buildQuery
                print("original_query: ", original_query)
                results = self.databases_service.execute_original_query(original_query)
                print(results)
                print("FINISH")
            else:
                contacts, number_of_contacts = self.get_established_contacts()
                print(f"   contacts: {contacts}")
                for contact in contacts:
                    print(f"   contact: {contact}")
                    print(f"   q[0]: {q[0]}")
                    if contact != q[0]:
                        x3dh_role = self.eventfeed_service.get_x3dh_role(contact)
                        cipher, public_key = self.double_ratchet_service.encrypt(contact, q[1], x3dh_role)
                        print("$$$$$$$ created obfuscated_retrieval_response_event")
                        self.eventfeed_service.create_obfuscated_retrieval_response_event(contact, cipher, public_key)

    def get_confirmation_message_database_schemata(self):
        print("get_confirmation_message_database_schemata(self)")
        ids = [i for i  in self.eventfeed_service.get_confirmation_message_ids()]
        schematas = []
        for id in ids:
            print("   ID: ", id)
            #print("CONFIRMATION MESSAGE:", self.eventfeed_service.read_event_data(id))
            schematas.append(ast.literal_eval(self.eventfeed_service.read_event_data(id)[0]))
            print(f"   schematas: {schematas}")
            recipient_key = hashlib.md5(self.eventfeed_service.event_database_handler._handler.get_master_id_from_feed(id)).hexdigest()
            self.dr_file_service.add_to_x3dh_confirmed_list(recipient_key)
            db_schemata = str(self.databases_service.get_db_schemata())
            cipher, public_key = self.double_ratchet_service.encrypt(recipient_key, db_schemata, 'slave')
            self.eventfeed_service.create_obfuscated_retrieval_request_event(recipient_key, cipher, public_key)


if __name__ == "__main__":
    print("************************************************************************************************")
    print("************************************************************************************************")
    cli = ObfuscatedRetrievalCli()
    cmd = input(":>")
    print(f"Our own master feed ID: {cli.eventfeed_service.event_database_handler._handler.get_host_master_id()}")
    print(f"Our own master feed ID hash: {cli.bookkeeper.ourIdentifier}")
    if cmd == 'contact':
        cli.contact_bacnet_user()
    if cmd == 'read-pkb':
        cli.check_for_prekey_bundle_events()
    if cmd == 'read-res-pkb':
        cli.check_for_response_prekey_bundle_events()
    if cmd == 'pir':
        cli.create_pir_request()
    if cmd == 'decrypt-pir':
        cli.read_all_obfuscated_retrieval_requests()
    if cmd == 'db-schemata':
        cli.get_confirmation_message_database_schemata()
    if cmd == 'read-res-pir':
        cli.read_all_obfuscated_retrieval_response()
    if cmd == 'relay':
        cli.relay_messages()

