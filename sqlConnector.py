import mysql.connector
import matplotlib.pyplot as plt

dataBase = mysql.connector.connect(
    host="localhost",
    user="<MUST_ADD>",
    passwd="<MUST_ADD>",
    database="timeplotter"
    ) 
