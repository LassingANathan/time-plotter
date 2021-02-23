### Holds a number of functions that makes it easier to interact with a mySQL database

## Retrives a number of columns
def getColumn(cursor,db,table,column): #cursor object, database to use, table to select (str), column to return (str)
    columnRows = [] # Holds the row values of the current column

    cursor.execute("SELECT "+column+" FROM "+table)

    for element in cursor: # For tuples retrieved from cursor
        columnRows.append(element[0]) # Append first element from tuple (Only element since retrieving from one column) to list

    return columnRows

## Adds a new column to a table
def addColumnToTable(cursor,db,table,columnName,columnType):  #cursor object, database to use, table to use, new column name, new column type
    cursor.execute("ALTER TABLE "+table+" ADD "+columnName+" "+columnType)

## Adds a value to a single cell when given a column and table name.
def addValueToCell(cursor,db,table,columnName,value):
    cursor.execute("INSERT INTO "+table+" ("+columnName+") VALUES (%s)", (value,))
