import ast
from random import randint


class Clause:
    """
    The class representing a logical WHERE clause in SQL. Supported Operating are =, > and <.
    """

    def __init__(self, tableColumn, operator, value):
        self.tableColumn = tableColumn
        self.operator = operator
        self.value = value


class QueryBuilder:
    """
    Querybuilder is a class which gets instantiated to build a SQL query.
    The query consists of a list of column names (the data we are interested in), the name of the table we are quering
    over and a single clause.

    First you call the from_, select and clause methods to build up a query.
    using the method buildQueryPir we get a SQL query asking for all columns ignoring the clause.

    The meds buildQueryForMultipleREcipients builds several queries, each asking for a single column so that they can
    be sent individually to different recipients.
    """

    def __init__(self):
        pass

    def from_(self, table):
        self.table = table

    def select(self, colsList):
        self.colsList = colsList

    def clause(self, clause):
        self.clause = clause

    def randomized_queries(self, n, maxvalue):
        for i in range(0, n):
            query = "SELECT * FROM " + self.table + " WHERE OID "
            x = randint(1, maxvalue)
            y = randint(1, maxvalue)
            mini = str(min(x, y))
            maxi = str(max(x, y))
            query = query + " > " + mini
            query = query + " AND OID < " + maxi
            yield query

    def buildQueryPir(self):
        querystring = ""
        querystring += "SELECT"
        for col in self.colsList:
            querystring += " " + col + ","
        querystring += " " + self.clause.tableColumn + ","
        querystring += 'FROM ' + self.table
        return querystring

    def buildQueryForMultipleRecipients(self):
        queries = []
        cols = self.colsList + [self.clause.tableColumn]
        for col in cols:
            qstring = ""
            qstring += "SELECT " + col + ' from ' + self.table
            queries.append(qstring)
        return queries

    def buildQuery(self):
        querystring = ""
        querystring += "SELECT"
        for col in self.colsList:
            querystring += " " + col + " "
        querystring += " FROM " + self.table
        querystring += " WHERE "
        querystring += self.clause.tableColumn + " " + self.clause.operator + " " + self.clause.value
        return querystring


class ResultsTableator:
    """
    The BACnet SqlRPC responses are string of the format ((columnName, None ...), (columnName2, None ...) ; [(data1, bata1) ... ]
    the first part is a tuple of tuples with the first element being the columnName corresponding to the element of eacht datatuple.
    The second part is the datatuples corresponding to a row of the table.

    This class is responsible for taking a resultsString and building a internal representation of the data, with a
    dictionary holding the data of each column as a list index by the columnName as key.
    """

    def __init__(self):
        self.columns = {}

    def read_in_string(self, resultsString):
        column_names = []
        table_names_tuples, data_results_tuples = resultsString.split(";")
        #table_names_tuples = queryBuilder.colsList
        #data_results_tuples = resultsString
        print("table_names_tuples: ", table_names_tuples)
        table_names_tuples = ast.literal_eval(table_names_tuples)
        data_results_tuples = ast.literal_eval(data_results_tuples)
        for table_name_tuple in table_names_tuples:
            print("table_name_tuple: ", table_name_tuple)
            if table_name_tuple != None:
                self.columns[table_name_tuple[0]] = []
                column_names.append(table_name_tuple[0])

        for datatuple in data_results_tuples:
            for data in datatuple:
                print("data_tuple: ", data)
                self.columns[column_names[datatuple.index(data)]].append(data)


class AnalyzeResults:
    """
    AnalyzeResults applies the original query on a resultsTabelator, basically applying the where clauses and
    returns the data we where looking for.
    """

    def applyClauses(self, select_from, resTab: ResultsTableator, clause):
        print("clause.tableColumn: ", clause.tableColumn)
        data = resTab.columns[clause.tableColumn]
        if clause.operator == "=":
            for d in data:
                if d == clause.value:
                    yield resTab.columns[select_from][data.index(d)]
        if clause.operator == "<":
            for d in data:
                if d < clause.value:
                    yield resTab.columns[select_from][data.index(d)]
        if clause.operator == ">":
            for d in data:
                if d > clause.value:
                    yield resTab.columns[select_from][data.index(d)]
