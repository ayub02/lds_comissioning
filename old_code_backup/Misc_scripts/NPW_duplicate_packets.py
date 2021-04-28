import psycopg2
import datetime
import numpy as np
import pandas as pd
from psycopg2 import sql
from datetime import datetime
from matplotlib import pyplot as plt


# Connecting to database
while True:
    try:
        print('Connecting to database ... ')
        conn = psycopg2.connect(dbname='postgres', user='postgres', password='@intech#123', host='localhost',
                                port='5432')
    except psycopg2.OperationalError as e:
        print('Unable to connect!\n{0}'.format(e))
    else:
        print('Connected!')
        break

conn.autocommit = True
cursor = conn.cursor()

tags = ['MKT.NPW.ByteArray', 'MOV60.NPW.ByteArray', 'BV61.NPW.ByteArray', 'BV62.NPW.ByteArray', 'BV63.NPW.ByteArray',
       'BV64.NPW.ByteArray', 'BV65.NPW.ByteArray', 'BV66.NPW.ByteArray', 'KBS1.NPW.ByteArray']

for tag in tags:

    print('\n', '****************', tag, '****************')
    query = sql.SQL("SELECT * FROM mfmdata where itemid= %s ORDER BY itemtimestamp ASC")
    cursor.execute(query, (tag, ))

    rows = cursor.fetchall()

    if rows:
        for i in range(len(rows)):
            row1 = rows[i]
            buffer1 = [int(val) for val in row1[1].split(",")]
            for j in range(len(rows)):
                if j > i:
                    row2 = rows[j]
                    buffer2 = [int(val) for val in row2[1].split(",")]
                    equal = True

                    for k in range(len(buffer1)):
                        if buffer1[k] != buffer2[k]:
                            equal = False
                    if equal:
                        print(i, j)
                        print(row1)
                        print(row2)

