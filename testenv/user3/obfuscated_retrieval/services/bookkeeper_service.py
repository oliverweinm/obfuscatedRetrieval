from ..BACnet.utils.logStore.appconn.connection import Function
import hashlib
import json
import os

path_to_bookkeeping_file = os.getcwd() + '/bookkeeping.json'
path_to_feedregistry_file = os.getcwd() + '/feed_registry.json'
path_to_requests_file = os.getcwd() + '/requests_registry.json'

class BookkeeperService:
    def __init__(self, our_masterfeed_id):
        self.dictionary = None
        self.peer_feed_dictionary = None
        self.requests_dictionary = None
        self.our_masterfeed_id = our_masterfeed_id
        self.ourIdentifier = hashlib.md5(our_masterfeed_id).hexdigest()
        self.event_database_handler = Function()
        pass

    def __read_to_dict(self):
        #print("   __read_to_dict()")
        try:
            with open(path_to_bookkeeping_file,'x') as bookkeeping_file:
                # bookkeeping_file has just been created
                # dictionary is thus empty at this point
                print("   Created bookkeeping.json file")
                self.dictionary = {}
                return
        except OSError:
            #Bookeeping file already exists
            pass
        with open(path_to_bookkeeping_file,'r') as bookkeeping_file:
            self.dictionary = json.load(open(path_to_bookkeeping_file,'r'))

    def __read_to_peer_feed_dict(self):
        #print("   __read_to_peer_feed_dict()")
        try:
            with open(path_to_feedregistry_file,'x') as feedregistry_file:
                # feedregistry_file has just been created
                # dictionary is thus empty at this point
                print("   Created feed_registry.json file")
                self.peer_feed_dictionary = {}
                with open(path_to_feedregistry_file, 'r+') as feedregistry_file:
                    raw_data = feedregistry_file.read()
                    if raw_data != "":
                        feedregistry_file.seek(0)
                        feedregistry_file.truncate(0)
                return
        except OSError:
            #Bookeeping file already exists
            pass
        with open(path_to_feedregistry_file,'r') as feedregistry_file:
            self.peer_feed_dictionary = json.load(open(path_to_feedregistry_file,'r'))

    def __read_to_requests_dict(self):
        try:
            with open(path_to_requests_file,'x') as requests_file:
                # bookkeeping_file has just been created
                # list is thus empty at this point
                print("   Created requests_registry.json file")
                self.requests_dictionary = {}
                return
        except OSError:
            #Bookeeping file already exists
            pass
        with open(path_to_requests_file,'r') as requests_file:
            self.requests_dictionary = json.load(open(path_to_requests_file,'r'))

    def __write_to_file(self):
        print("   __write_to_file()")
        with open(path_to_bookkeeping_file,'r+') as bookkeeping_file:
            raw_data = bookkeeping_file.read()
            if raw_data != "":
                bookkeeping_file.seek(0)
                bookkeeping_file.truncate(0)
            json.dump(self.dictionary, bookkeeping_file)

    def write_to_requests_file(self, request, requests):
        print("__write_to_requests_file")
        self.__read_to_requests_dict()
        self.requests_dictionary["request"] = request
        self.requests_dictionary["requests_sent"] = requests
        self.requests_dictionary["num_requests_sent"] = len(requests)
        self.requests_dictionary["responses_received"] = 0
        with open(path_to_requests_file,'r+') as requests_file:
            raw_data = requests_file.read()
            if raw_data != "":
                requests_file.seek(0)
                requests_file.truncate(0)
            json.dump(self.requests_dictionary, requests_file)


    def check_feed_entry(self, seq_no, feed_id):
        feed_id = hashlib.md5(feed_id).hexdigest()
        print(f"check_feed_entry({seq_no},{feed_id})  feed_id hash: {feed_id}")
        self.__read_to_dict()
        try:
            if self.dictionary[feed_id] >= seq_no:
                return True
            else:
                self.dictionary[feed_id] = seq_no
                self.__write_to_file()
                return False
        except KeyError as keyerr:
            print("   Key did not exist before. We have added it to bookkeeping now.")
            self.dictionary[feed_id] = seq_no
            self.__write_to_file()
            return False

    def get_feed_for_user(self, user_hash):
        print("get_feed_for_user()")
        self.__read_to_peer_feed_dict()
        try:
            user_feed_hash = self.peer_feed_dictionary[user_hash]
            feed_ids = self.event_database_handler._handler.get_all_master_ids_feed_ids(self.our_masterfeed_id)
            for feed in feed_ids:
                print(f"   {hashlib.md5(feed).hexdigest()}, {user_feed_hash}")
                if hashlib.md5(feed).hexdigest() == user_feed_hash:
                    print(f"   returned feed: {feed}")
                    return(feed)
            print("   Key did not exist before. Are you sure, you are doing the right thing?")
            exit()
        except KeyError as keyerror:
            print("   Key did not exist before. Are you sure, you are doing the right thing?")
            exit()
        raise NotImplementedError

    def save_feed_for_user(self, user_hash, feed_id):
        print("save_feed_for_user()")
        print(f"   feed_id: {feed_id}")
        feed_id = hashlib.md5(feed_id).hexdigest()
        print(f"   feed_id hash: {feed_id}")
        self.__read_to_peer_feed_dict()
        self.peer_feed_dictionary[user_hash] = feed_id
        with open(path_to_feedregistry_file, 'r+') as feedregistry_file:
            raw_data = feedregistry_file.read()
            if raw_data != "":
                feedregistry_file.seek(0)
                feedregistry_file.truncate(0)
            json.dump(self.peer_feed_dictionary, feedregistry_file)

    def check_response(self):
        print("check_response()")
        try:
            self.__read_to_requests_dict()
            self.requests_dictionary["responses_received"] += 1
            with open(path_to_requests_file,'r+') as requests_file:
                raw_data = requests_file.read()
                if raw_data != "":
                    requests_file.seek(0)
                    requests_file.truncate(0)
                json.dump(self.requests_dictionary, requests_file)
            if self.requests_dictionary["responses_received"] == self.requests_dictionary["num_requests_sent"]:
                return True
            else:
                return False
        except KeyError:
            return False





