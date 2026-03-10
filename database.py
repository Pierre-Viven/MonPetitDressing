import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()

DB_HOST=os.getenv("DB_HOST")
DB_PORT=os.getenv("DB_PORT")
DB_NAME=os.getenv("DB_NAME")
DB_USER=os.getenv("DB_USER")
DB_PASSWORD=os.getenv("DB_PASSWORD")


def connexion_database():
    """ Connect to the PostgreSQL database server """
    try:
        with psycopg2.connect(database = DB_NAME, user = DB_USER, host= DB_HOST,password = DB_PASSWORD,port = DB_PORT) as bdd:
            print('Connexion au serveur PostgreSQL réussie.')
            return bdd
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


