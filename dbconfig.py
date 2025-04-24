# dbconfig.py

import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ikr5615d",
        database="body_shape_db"
    )
