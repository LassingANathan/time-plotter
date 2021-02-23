from sqlConnector import dataBase
from timeIntervals import Day
from datetime import datetime
import sqlInteractions as sqlUtil

myCursor = dataBase.cursor(buffered=True)

def main():
    menuAns = ''

    while menuAns != '4':
        print("\nHello! Welcome to TimePlotter!\n"\
            "1: Add New Day\n"\
            "2: File Time\n"\
            "3: Activity Types\n"\
            "4: Plot Time\n"\
            "5: Exit")
        menuAns = input()

        if menuAns == '5':
            print("See you next time!")
            return 0
        elif menuAns == '1':
            print("Let's file a new day!")

            # Prompt for day info and enter into database
            newDate = input("Enter the date (YYYY/MM/DD):")
            newDayName = input("Enter the day name (M,Tu,W,Th,F,Sat,Sun):")
            myCursor.execute("INSERT INTO Days (date, dayName) VALUES (%s,%s,%s)", (newDate, newDayName))
            print("New day "+newDayName+" on "+newDate+" succesfully created!")
            # TODO, make sure the entered date hasn't already been entered into table

            menuAns = ("Would you like to file time for this day now? (Y/N):")
            if menuAns.lower() == 'y':
                dayIdToEdit = myCursor.execute("SELECT dayid FROM Days WHERE date='"+str(newDate)+"'")
                fileTime(dayIdToEdit)


            ##activity=input("Enter activity")
            ##time=float(input("Input how many hours spent"))
            ##newDay.addTime(activity,time)
            #myCursor.execute("DROP TABLE Days")
            #myCursor.execute("CREATE TABLE Days (date VARCHAR(10) NOT NULL, dayName VARCHAR(3), "+activity+"Time VARCHAR(50))")
            #myCursor.execute("INSERT INTO Days (date, dayName, "+activity+"Time) VALUES (%s,%s,%s)", (newDate, newDayName,str(time)))
            #dataBase.commit()
        elif menuAns == '2':
            fileTime()
        elif menuAns == '3':
            activityTypesMenu()
        elif menuAns == '4':
            print("TODO: Select and graph and stuff idk thats a whole thing")
        else:
            print("Error! Did not enter a valid option.")

def activityTypesMenu():
    menuAns = ''

    while menuAns != '4':
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("1: See list of activities\n"\
            "2: Add new activity\n"\
            "3: Delete activity\n"\
            "4: Back")
        menuAns = input()

        if menuAns == '4':
            return 0
        elif menuAns == '1': # Add new activity to database
            print("~~~~~~~~~~~~~~~~~~~~~~~~")

            column = sqlUtil.getColumn(myCursor, dataBase, "Activities","activityName") # Get a list that holds every column, which holds every row in terms of single variable tuples

            for row in range(len(column)): # For every column in the columns...
                print(column[row]) # Print the value held there.
        elif menuAns == '2':
            newActivity = input("Input the new activity name: ")
            addActivity = True
            currentActivityList = sqlUtil.getColumn(myCursor,dataBase,"Activities","activityName")

            # Check to ensure the user entered activity doesn't already exist
            for row in range(len(currentActivityList)):
                if currentActivityList[row] == newActivity:
                    addActivity = False
                    break

            # If the activity isn't already entered, then enter it.
            if addActivity:
                sqlUtil.addValueToCell(myCursor,dataBase,"Activities","activityName",newActivity) # Add to Activities table
                sqlUtil.addColumnToTable(myCursor,dataBase,"Days",newActivity.replace(" ","_")+"_time","VARCHAR(50)")

                print ("Activity succesfully added!")
                #dataBase.commit()
            else: # Otherwise, do not enter it.
                print("Sorry, we could not add the new activity. The activity likely already exists!")
        elif menuAns == '3':
            print()

def fileTime(dayID=''):
    if dayID == '':  # If no dayID is passed, then ask for the date name and get the dayID
        date = input("Please enter what date you would like to file time for (YYYY/MM/DD): ")
        myCursor.execute("SELECT dayId FROM Days WHERE date='"+date+"'") # TODO, input validation
        for i in myCursor:
            dayID = str(i).strip("'(,)") #TODO learn how to just get it as a string originally without the for loop and all that
    else: #If a dayID is passed, then get the date
        myCursor.execute("SELECT date FROM Days where dayId='"+dayID+"'")
        for i in myCursor:
            date = i

    # Get a list of all activities then print them out. Output is numbered starting at 1
    activityList = sqlUtil.getColumn(myCursor,dataBase,"Activities","activityName")
    for i in range(len(activityList)):
        print(str(i+1)+": "+activityList[i])

    activityNum = int(input("Please enter the number of the activity you'd like to file: "))
    activityTime = input("Please enter how much time you spent on this activity on "+date+": ")

    activityName = activityList[activityNum-1] #The outputted list that the user sees starts at 1, so subtract one since lists start at 0
    activityName = activityName+"_time" # Add _time, because each time column in Days ends in _time

    query = "UPDATE Days SET '%s' = %s WHERE dayId = %s"
    #query = "UPDATE Days SET "+activityName+"_time = "+activityTime+" WHERE dayId = "+dayID
    values = (activityName,activityTime,dayID)

    myCursor.execute(query, values) ##TODO: Eventually make sure that the amount of time doesn't go over amount of time in day
    dataBase.commit()

def test():

    print("Hello %s" % ("world",))



#test()
main() 
