import psycopg2
import psycopg2.extras
import os
import csv
import threading

path = os.path.dirname(os.path.realpath(__file__))
parsed = None
progress_timer_thread = None
cutoff_date = 1990

# executes commands to set up schema in database
def setup_schema(connection_string):
    print("Loading data")
    conn = psycopg2.connect(connection_string)
    print ("Connection established")
    cursor = conn.cursor()
    print("Cursor created")
    with open(os.path.join(path, 'schema.sql'), 'r') as schema:
        setup_queries = schema.read()
        cursor.execute(setup_queries)
        conn.commit()

# all of the _query functions below are functions which are used
# in a factory manner by the load_file function which calls
# the appropriate _query function for the type of data to
# be inserted
def company_information_query(line):
    if line:
        data = {
                'ticker': line[0],\
                'exchange': line[1],\
                'name': line[2],\
                'sector': line[3],\
                'industry': line[4]
            }
    else:
        data = None
    return ("INSERT INTO company_information VALUES("\
                "%(ticker)s, "\
                "%(exchange)s, "\
                "%(name)s, "\
                "%(sector)s, "\
                "%(industry)s);",
            data)

def historical_stock_prices_query(line):
    global cutoff_date
    if line:
        dateTotal = line[7]
        separatedDates = dateTotal.split('-')
        year = separatedDates[0]
        data = {
                    'ticker': line[0],\
                    'open': line[1],\
                    'close': line[2],\
                    'adj_close': line[3],\
                    'low': line[4],\
                    'high': line[5],\
                    'volume': line[6],\
                    'trade_date': line[7]
                }
        if int(year) > cutoff_date:
            data = None
    else:
        data = None
    return ("INSERT INTO historical_stock_prices VALUES("\
                "%(ticker)s, "\
                "%(open)s, "\
                "%(close)s, "\
                "%(adj_close)s, "\
                "%(low)s, "\
                "%(high)s, "\
                "%(volume)s, "\
                "%(trade_date)s);",
            data)

def attacks_query(line):
    global cutoff_date
    if line:
        year = line[1].zfill(4)
        month = line[2].zfill(2)
        day = line[3].zfill(2)
        date = '-'.join([year, month, day])
        if year == '0000' or month == '00' or day == '00':
            date = None
        summary = line[18]
        if len(summary) > 511:
            summary = None
        data = {
                    'id': line[0],\
                    'date':  date,\
                    'summary': summary
                }
        if int(year) > cutoff_date:
            data = None
    else:
        data = None
    return ("INSERT INTO attacks VALUES("\
                "%(id)s, "\
                "%(date)s, "\
                "%(summary)s);",
            data)

def attack_location_query(line):
    global cutoff_date
    if line:
        year = line[1].zfill(4)
        data = {
                    'id': line[0],\
                    'country': line[8],\
                    'region': line[10],\
                    'provstate': line[11],\
                    'city': line[12]
                }
        if int(year) > cutoff_date:
            data = None
    else:
        data = None
    # print(data)
    return ("INSERT INTO attack_location VALUES("\
                "%(id)s, "\
                "%(country)s, "\
                "%(region)s, "\
                "%(provstate)s, "\
                "%(city)s);",
            data)

def attack_data_query(line):
    global cutoff_date
    if line:
        year = line[1].zfill(4)
        number_killed = line[98]
        if number_killed == '':
            number_killed = None
        data = {
                    'id': line[0],\
                    'extended': line[5],\
                    'multiple': line[25],\
                    'success': line[26],\
                    'suicide': line[27],\
                    'attack_type': line[29],\
                    'target_type': line[35],\
                    'target_nationality': line[41],\
                    'number_killed': number_killed
                }
        if int(year) > cutoff_date:
            data = None
    else: 
        data = None
    # print(data)
    return ("INSERT INTO attack_data VALUES("\
                "%(id)s, "\
                "%(extended)s, "\
                "%(multiple)s, "\
                "%(success)s, "\
                "%(suicide)s, "\
                "%(attack_type)s, "\
                "%(target_type)s, "\
                "%(target_nationality)s, "\
                "%(number_killed)s);",
            data)

# this function is called continuously when loading data to output progress of loading
def print_progress():
    global parsed
    global progress_timer_thread
    if parsed is not None:
        print("{} rows parsed".format(parsed))
    progress_timer_thread = threading.Timer(5.0, print_progress)
    progress_timer_thread.start()

def load_file(connection_string, query_factories, filename, encoding='utf_8'):
    global parsed
    global loaded
    global progress_timer_thread
    parsed = None
    loaded = None
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    with open(os.path.join(path, 'datasets', filename), 'r', encoding=encoding) as file:
        reader = csv.reader(file)
        skip_first_line = True
        queries = {}
        # this collects the factory functions for each query into a list that can be
        # used with execute_batch in the interest of efficiency
        for f_idx, factory in enumerate(query_factories):
            queries[f_idx] = []
        print_progress()
        for idx, line in enumerate(reader):
            parsed = idx
            if skip_first_line:
                skip_first_line = False
                continue
            # iterates over factory functions
            for f_idx, factory in enumerate(query_factories):
                query = factory(line)
                if query[1] == None:
                    break
                queries[f_idx].append(query[1])
                if len(queries[f_idx]) > 50000:
                    psycopg2.extras.execute_batch(cursor, query[0], queries[f_idx])
                    queries[f_idx] = []
        for f_idx, factory in enumerate(query_factories):
            psycopg2.extras.execute_batch(cursor, factory('')[0], queries[f_idx])
        conn.commit()
        if progress_timer_thread is not None:
            progress_timer_thread.cancel()