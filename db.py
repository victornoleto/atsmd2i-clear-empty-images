import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    database=os.getenv('DB_DATABASE'),
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USERNAME'),
    password=os.getenv('DB_PASSWORD'),
    port=os.getenv('DB_PORT')
)

def execute(sql):
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()

def get(query):
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    return [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in rows]

def find(query):
    result = get(query)
    return result[0] if result else None