import sqlite3
from os import listdir, getcwd, fsync
from os.path import isfile, join
from sqlalchemy import exc
import sqlalchemy.orm
from sqlalchemy import create_engine
from sqlalchemy.inspection import inspect
import json

#queryFile = os.cwd()

class DatabasesService:
    def __init__(self):
        self.databases_files = []
        self.__get_database_files__()
        self.database_structures = {}
        for file in self.databases_files:
            if file[-2:] == 'db':
                if not isfile(file[:-2]+'json'):
                    data = self.__get_database_schema__(file)
                    self.database_structures[file[:-2]] = data
                    self.__save_to_json__(file, data)
                else:
                    self.database_structures[file[-2]] = self.__read_json_file__(file)

    def __read_json_file__(self, file):
        with open(file, 'r') as f:
            return json.load(f)


    def __get_database_files__(self):
        path = getcwd()
        onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
        for file in onlyfiles:
            if file[-2:] == 'db':
                self.databases_files.append(file)

    def __get_database_schema__(self, databasefilepath):
        print(databasefilepath)
        engine = create_engine('sqlite:///'+databasefilepath)
        data = {}
        data['tables'] = engine.table_names()
        for table in engine.table_names():
            data[table] = engine.execute('SELECT * from ' + table).keys()
            data[table+'_length'] = engine.execute('SELECT COUNT() FROM ' + table).fetchall()[0][0]
        self.database_structures[databasefilepath[:-2]] = data
        return data

    def __save_to_json__(self, filename, data):
        with open('databases_structures.json', 'w') as filepath:
            json.dump(self.database_structures, filepath)

    def get_db_schemata(self):
        print(f"TYPE: {type(self.database_structures)}")
        return self.database_structures

    def get_databases_to_execute_query_against(self):
        return self.databases_files

    def execute_query(self, query):
        print("query: ", query)
        if query == '{}' or query[0] == '{':
            return None, None
        try:
            engine = create_engine('sqlite:///'+self.databases_files[0])
            result = engine.execute(query)
            print("query: ", query)
            keys = result.keys()
            print("keys: ", keys)
            result_fetchall = result.fetchall()
            keys_string = "("
            for key in keys:
                keys_string += "('"
                keys_string += key
                keys_string += "',None),"
            #keys_string[-1] = ')'
            keys_string = keys_string[:-1] + ')'
            #keys_string = keys_string[:-1] + ');'
            keys_string += ';'
            print("keys_string: ", keys_string)
            #keys = '((' + keys[0] + '))' + ' ; '
            return keys_string, result_fetchall
            #return result_fetchall
        except exc.SQLAlchemyError:
            return None, None
        except IndexError:
            #In the case the user does not possess a db on which this query can be executed
            return None, None

    def write_to_query_response_db(self, response):
        try:
            engine = create_engine('sqlite:///'+"queryresponses.db")
            print("response: ", response)
            #CREATE TABLE



        except exc.SQLAlchemyError:
            return None, None
        except IndexError:
            #In the case the user does not possess a db on which this query can be executed
            return None, None

    def execute_original_query(self, query):
        try:
            #engine = create_engine('sqlite:///'+self.databases_files[0])
            engine = create_engine('sqlite:///'+ "openpayments.db")
            result = engine.execute(query)
            print("query: ", query)
            keys = result.keys()
            print("keys: ", keys)
            result_fetchall = result.fetchall()
            return result_fetchall
        except exc.SQLAlchemyError as aler:
            print("SQL Alchemy Error: ", aler)
            return None, None
        except IndexError:
            print("Index Error")
            #In the case the user does not possess a db on which this query can be executed
            return None, None
