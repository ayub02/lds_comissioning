import os
from configparser import ConfigParser
import psycopg2

def config(filename, section):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db


def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config('../config/database.ini', 'postgresql')

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()
        postgreSQL_select_Query = "SELECT * FROM (SELECT * FROM historytable ORDER BY itemtimestamp DESC LIMIT 10)Var1 ORDER BY itemtimestamp ASC;"

        cur.execute(postgreSQL_select_Query)
        print("Selecting rows from mobile table using cursor.fetchall")
        mobile_records = cur.fetchall()

        print("Print each row and it's columns values")
        for row in mobile_records:
            print("Id = ", row[0], "Value = ", row[1], "Timestamp  = ", row[2])


        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    connect()

# print(config('../config/database.ini', 'postgresql'))

