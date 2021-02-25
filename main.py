from sqlConnector import dataBase
import datetime
from timeIntervals import Day
import sqlInteractions as sqlUtil

myCursor = dataBase.cursor(buffered=True) # prepared=True(?) 

def main():
    menuAns = ''
    print("\nHello! Welcome to TimePlotter!")

    while menuAns != '5':
        print("\nWhat would you like to do?\n"\
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
            fileDay()
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

        # Print list of activities
        elif menuAns == '1':
            print("~~~~~~~~~~~~~~~~~~~~~~~~")
            activityList = sqlUtil.getColumn(myCursor,dataBase,"Activities","activityName")
            for i in range(len(activityList)):
                print(str(i+1)+": "+activityList[i])

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
            # Print list of activities
            print("~~~~~~~~~~~~~~~~~~~~~~~~")
            activityList = sqlUtil.getColumn(myCursor,dataBase,"Activities","activityName")
            for i in range(len(activityList)):
                print(str(i+1)+": "+activityList[i])

            print("Note: When deleting an activity, all time filed for that activity will also be deleted!")
            activityChoice = input("Please enter the number of the activity you'd like to delete: ")
            
            # Get the activityId so we can delete from Days table
            myCursor.execute("SELECT activityId FROM Activities WHERE activityName = '"+activityList[int(activityChoice)-1]+"'")
            activityId = myCursor.fetchone() #TODO: Make function so we don't have to do this everytime
            activityId = activityId[0]

            # Delete activity from Activities table
            myCursor.execute("DELETE FROM Activities WHERE activityName = %s", (activityList[int(activityChoice)-1],)) #TODO Input Validation

            # Delete all filed time for this activity from the Days table
            myCursor.execute("DELETE FROM Days WHERE activityId = %s", (activityId,))

            dataBase.commit()
            print("Activity deleted!")
            
        

def fileTime(date=''):
    if date == '':  # If no date value is passed, then ask for the date name and get the dayID
        while date == '':
            date = input("Please enter what date you would like to file time for (YYYY/MM/DD): ")
            date = datetime.datetime.strptime(date,'%Y-%m-%d').date() # Converts from str to datetime.date
            #TODO Input validation

            # Get list of already entered dates and verify the user is entering a valid date
            datesList = sqlUtil.getColumn(myCursor,dataBase,"Days","date")
            dateFound = False
            for i in datesList:
                if i == date:
                    dateFound = True
                    break
            if dateFound == False:
                print("Error: could not find the entered date. Returning to main menu")
                return 0

    # Get a list of all activities then print them out. Output is numbered starting at 1
    activityList = sqlUtil.getColumn(myCursor,dataBase,"Activities","activityName")
    for i in range(len(activityList)):
        print(str(i+1)+": "+activityList[i])
    
    activityChoice = input("Please enter the number of the activity you'd like to file: ")
    myCursor.execute("SELECT activityId FROM Activities WHERE activityName = '"+activityList[int(activityChoice)-1]+"'")

    activityId = myCursor.fetchone() #TODO: Make this a function so we don't have to fetch then set equal to first index of tuple everytime
    activityId = activityId[0]

    activityTime = input("Please enter how much time you spent on this activity on "+str(date)+" in hours: ") #TODO, make it so they can enter in minutes or hours.
    #TODO, regardless, time will be stored in minutes. So eventually make it so if they enter in hours, then we convert to minutes first.

    # Enter activity data into database
    myCursor.execute("INSERT INTO Days (date, activityId, activityTime) VALUES (%s, %s, %s)", (date, activityId, activityTime)) ##TODO: Eventually make sure that the amount of time doesn't go over amount of time in day
    dataBase.commit()

def fileDay():
    print("Let's file a new day!")
    # Prompt for day info and enter into database
    newDate = input("Enter the date (YYYY-MM-DD):")
    newDate = datetime.datetime.strptime(newDate,'%Y-%m-%d').date() # Converts the user sting to a datetime.date for comparison

    # Get list of already entered dates and verify the user is not entering a repeat.
    datesList = sqlUtil.getColumn(myCursor,dataBase,"Days","date")
    for date in datesList:
        if date == newDate:
            print("Error: it seems that date has already been entered. We'll send you back to the main menu")
            return 0

    # Enter date into database
    myCursor.execute("INSERT INTO Days (date) VALUES (%s)", (newDate,))
    print("New date "+str(newDate)+" succesfully created!")
    dataBase.commit()

    menuAns = input(("Would you like to file time for this day now? (Y/N):"))
    if menuAns.lower() == 'y':
        fileTime(newDate)
    return 0

def test():
    print("Hello")
        


#test()
main()
