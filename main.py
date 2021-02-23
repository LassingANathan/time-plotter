from sqlConnector import dataBase
from timeIntervals import Day
from datetime import datetime
import sqlInteractions as sqlUtil

myCursor = dataBase.cursor(buffered=True) # prepared=True(?) 

def main():
    menuAns = ''

    while menuAns != '5':
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
            newDate = input("Enter the date (YYYY-MM-DD):")
            myCursor.execute("INSERT INTO Days (date) VALUES (%s)", (newDate,))
            print("New date "+newDate+" succesfully created!")
            dataBase.commit()
            # TODO, make sure the entered date hasn't already been entered into table

            #menuAns = input(("Would you like to file time for this day now? (Y/N):"))
            #if menuAns.lower() == 'y':
            #    myCursor.execute("SELECT dayId FROM Days WHERE date='"+str(newDate)+"'")
            #    dayIdToEdit = myCursor.fetchall()
            #    fileTime(dayIdToEdit)


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

        # See list of activities
        elif menuAns == '1':
            print("~~~~~~~~~~~~~~~~~~~~~~~~")
            column = sqlUtil.getColumn(myCursor, dataBase, "Activities","activityName") 

            for row in range(len(column)): # For every row in the columns...
                print(column[row]) # Print the value held there.
        # Add a new activity
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
                dataBase.commit()
                print ("Activity succesfully added!")
            else: # Otherwise, do not enter it.
                print("Sorry, we could not add the new activity. The activity likely already exists!")

        # Delete an activity
        elif menuAns == '3':
            print()

def fileTime(dayID=''):
    while dayID == '':  # If no dayID is passed, then ask for the date name and get the dayID
        date = input("Please enter what date you would like to file time for (YYYY/MM/DD): ")
        myCursor.execute("SELECT dayId FROM Days WHERE date='"+date+"'")
        dayID = myCursor.fetchone()
        # If there was no dayId (i.e., there is no day in the database with the given date)
        if (dayID) == None:
            print("Oops! We couldn't find the inputted date. Are you sure you've added that day already?")
            dayID = '' # Reset flag so program asks for input again
        else:
            dayID = dayID[0]

    #TODO: Make this function work if a dayID is passed in directly.
    #else: #If a dayID is passed, then get the date
    #    myCursor.execute("SELECT date FROM Days where dayId='"+dayID+"'")
    #    date = myCursor.fetchall()
    
    # Get a list of all activities then print them out. Output is numbered starting at 1
    activityList = sqlUtil.getColumn(myCursor,dataBase,"Activities","activityName")
    for i in range(len(activityList)):
        print(str(i+1)+": "+activityList[i])
    
    activityChoice = input("Please enter the number of the activity you'd like to file: ")
    myCursor.execute("SELECT activityId FROM Activities WHERE activityName = '"+activityList[int(activityChoice)-1]+"'")

    activityId = myCursor.fetchone() #TODO: Make this a function so we don't have to fetch then set equal to first index of tuple everytime
    activityId = activityId[0]

    activityTime = input("Please enter how much time you spent on this activity on "+date+" in hours: ") #TODO, make it so they can enter in minutes or hours.
    #TODO, regardless, time will be stored in minutes. So eventually make it so if they enter in hours, then we convert to minutes first.

    myCursor.execute("INSERT INTO Days (date, activityId, activityTime) VALUES (%s, %s, %s)", (date, activityId, activityTime)) ##TODO: Eventually make sure that the amount of time doesn't go over amount of time in day
    dataBase.commit()

def test():
    print("Hello")
        


#test()
main()
