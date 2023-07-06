import psycopg2 as pg
import os
import pandas as pd

query = open("cards_db_schema.sql", "r").read()

PG_USER = os.environ.get('PG_USER')
PG_PASSWORD = os.environ.get('PG_PASSWORD')
PG_HOST = os.environ.get('PG_HOST')
PG_PORT = os.environ.get('PG_PORT')

# Connect to the database
conn = pg.connect(
    database="cards",
    user=PG_USER,
    host=PG_HOST,
    password=PG_PASSWORD,
    port=PG_PORT
)
conn.autocommit = True

# with conn.cursor() as cursor:    
#     cursor.execute(query)

cards_df = pd.read_csv('data/cards.csv')
print(cards_df.head())