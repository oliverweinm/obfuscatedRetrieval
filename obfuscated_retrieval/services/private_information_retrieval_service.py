from obfuscated_retrieval.private_information_retrieval.obfuscated_query import *
import pickle

class PrivateInformationRetrievalService:
    def __init__(self):
        print("PrivateInformationRetrievalService.__init__()")
        self.query_builder = QueryBuilder()
        self.results_tableator = ResultsTableator()
        self.analyer = AnalyzeResults()

        try:
            f = open('query_builder', 'rb')
            print("open query_builder")
            self.query_builder = pickle.load(f)
            print("self.query_builder.clause.tableColumn:", self.query_builder.clause.tableColumn)
        except Exception as ex:
            print("encountered exception: ", ex)
            pass
        try:
            f = open('results_tabluator', 'rb')
            print("self.resTable.columns:", self.query_builder.clause.tableColumn)
            self.results_tableator = pickle.load(f)
        except Exception as ex:
            print("encountered exception: ", ex)
            pass

        try:
            f = open('analyzer', 'rb')
            self.analyer = pickle.load(f)
        except:
            pass

    def save(self):
        print("//////////////saved")
        with open('query_builder', 'wb') as qb:
            pickle.dump(self.query_builder, qb)
        with open('results_tabulator', 'wb') as rt:
            pickle.dump(self.results_tableator, rt)
        with open('analyzer', 'wb') as al:
            pickle.dump(self.analyer, al)

    def new_query(self):
        self.query_builder = QueryBuilder()
        self.save()

    def add_from_table(self, table):
        self.query_builder.from_(table)
        self.save()

    def add_select_column(self, col):
        self.query_builder.select([col])
        self.save()

    def add_where_clause(self, column, operator, value):
        self.query_builder.clause(Clause(column, operator, value))
        self.save()
        #return self.query_builder_clause

    def get_obfuscated_query(self):
        self.save()
        return self.query_builder.buildQueryForMultipleRecipients()

    def get_randomized_query(self, n, maxlength_of_table):
        self.save()
        return self.query_builder.randomized_queries(n, maxvalue=maxlength_of_table)

    def add_results_string(self, results):
         self.results_tableator.read_in_string(results)
         self.save()

    def get_queried_results(self):
        queried_results =self.analyer.applyClauses(self.query_builder.colsList, self.results_tableator, self.query_builder.clause)
        print("type(queried_results: ", type(queried_results))
        while True:
            try:
                print("Received on next(): ", next(queried_results))
            except StopIteration:
                break
        self.save()
        return queried_results
