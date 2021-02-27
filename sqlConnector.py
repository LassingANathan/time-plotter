import mysql.connector
import matplotlib.pyplot as plt

dataBase = mysql.connector.connect(
    host="johnny.heliohost.org",
    user="lassinga_public-user",
    passwd="PublicPasswd071902",
    database="lassinga_timePlotter"
    )
