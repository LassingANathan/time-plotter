import mysql.connector
import matplotlib.pyplot as plt

# Replace arguments below
dataBase = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="INSERT_PASSWD",
    database="timeplotter"
    )
