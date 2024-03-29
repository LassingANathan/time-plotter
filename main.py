from sqlConnector import dataBase
import datetime
from matplotlib import pyplot as plt
import sys

myCursor = dataBase.cursor(buffered=True)

def main():
    personId, userName = userMenu()
    mainMenu(personId, userName)

def userMenu():
    loggedIn = False

    print("\n[LOGGED IN TO DATABASE] "+dataBase.database)
    print("[LOGGED IN TO DATABASE AS] "+dataBase.user)

    print("\nHello! Welcome to TimePlotter!")

    ## TODO: Delete users
    while not loggedIn:
        # Prompt for username
        print("Please enter your username: ")
        print("(Enter '-1' to exit, or 'new' to create a new user)")
        menuInput = input("")

        # Exit
        if (menuInput == '-1'):
            print("See you later!")
            sys.exit()

        # Enter new user
        elif (menuInput == 'new'):
            userNameInput = input("Please enter a new username: ")

            # Verify the user didn't enter 'new' or '-1' as a username (sentinals)
            if userNameInput == '-1' or userNameInput == 'new':
                print("\nError: Username can't be 'new' or '-1'\n")
                continue

            # Verify that no one already uses this username
            myCursor.execute("SELECT personName FROM People WHERE personName = %s", (userNameInput,))
            duplicateName = myCursor.fetchall()

            # If a duplicate name exists...
            if duplicateName:
                print("\nThis name already exists, maybe try another?\n")
            else:
                myCursor.execute("INSERT INTO People (personName) VALUES (%s)", (userNameInput,))
                dataBase.commit()
                personId = myCursor.lastrowid
                userName = userNameInput
                loggedIn = True
    
        # Entering an existing username
        else:   
            myCursor.execute("SELECT personId FROM People WHERE personName = %s", (menuInput,))
            personId = myCursor.fetchall()

            # If entered username was found...
            if personId:
                personId = personId[0][0] #TODO: Make fuction smh
                userName = menuInput
                loggedIn = True
            else: 
                print("\nNo user found with that name. Maybe create a new one?\n")

    return personId, userName     

def mainMenu(personId, userName):
    menuInput = ''

    while menuInput != '4':
        print("\nWhat would you like to do?\n"\
            "1: File Time\n"\
            "2: Activity Menu\n"\
            "3: Plot Time\n"\
            "4: Exit")
        menuInput = input()
        
        if menuInput == '4':
            print("See you next time!")
            myCursor.close()
            return 0
        elif menuInput == '1':
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            fileTime(personId)
        elif menuInput == '2':
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            activityTypesMenu(personId)
        elif menuInput == '3':
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            graphingMenu(personId)
        else:
            print("Error! Did not enter a valid option.")

def graphingMenu(personId):
    menuInput = ''

    while menuInput != '2':
        print("What would you like to do?\n"\
            "1: Graph time\n"\
            "2: Return to the main menu")
        menuInput = input()
    
        if menuInput == '2':
            return 0
        elif menuInput == '1':
            inputValid = False
            while inputValid == False:
                # Prompt for start date of graphing
                print("Please enter the start date of the range you would like to graph (yyyy-mm-dd)")
                print("(Enter -1 to return to the main menu)")
                startDate = input('Note: please enter "all" to graph time from every date ever entered: ')

                # Return to main menu if user entered -1
                if(startDate == '-1'):
                    return 0
                # If the user wants to graph all time ever entered...
                if (startDate.strip('" ') == "all"):
                    inputValid = True
                    plotRangeOfTime(personId)
                # If the user wants to graph from a specified range...
                else:
                    # Input validation
                    #try:
                    startDate = datetime.datetime.strptime(startDate,'%Y-%m-%d').date()

                    endDate = input("Please enter the end date of the range you would like to graph (yyyy-mm-dd): ")
                    endDate = datetime.datetime.strptime(endDate,'%Y-%m-%d').date()

                    inputValid = True

                    plotRangeOfTime(startDate,endDate, personId)
                #except ValueError:
                    print("\nError: Invalid date input. Please try again.")
                
        else:
            print("Error! Did not enter a valid option")

def activityTypesMenu(personId):
    menuInput = ''

    while menuInput != '4':
        print("1: See list of activities\n"\
            "2: Add new activity\n"\
            "3: Delete activity\n"\
            "4: Back")
        menuInput = input()

        if menuInput == '4':
            return 0

        # Print list of activities
        elif menuInput == '1':
            # Get all user's activities ## TODO Print activities function
            myCursor.execute("SELECT activityName FROM Activities WHERE personId = %s", (personId,))
            activityList = myCursor.fetchall()

            # Print user's activities
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            for i in range(len(activityList)):
                print(str(i+1)+": "+activityList[i][0])
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        # Add a new activity
        elif menuInput == '2':
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("(Enter -1 to return to the main menu)")
            newActivity = input("Input the new activity name: ")

            # Return to main menu if user entered -1
            if (newActivity == '-1'):
                return 0
            
            addActivity = True
            myCursor.execute("SELECT activityName FROM Activities WHERE personId = %s", (personId,))

            # Check to ensure the user entered activity doesn't already exist
            for activity in myCursor:
                if activity == newActivity:
                    addActivity = False
                    break

            # If the activity isn't already entered, then enter it.
            if addActivity:
                myCursor.execute("INSERT INTO Activities (personId, activityName) VALUES (%s, %s);", (personId, newActivity))
                dataBase.commit()
                print ("Activity succesfully added!")
            else: # Otherwise, do not enter it.
                print("Sorry, we could not add the new activity. The activity likely already exists!")

        # Delete an activity
        elif menuInput == '3':
            # Get all user's activities
            myCursor.execute("SELECT activityName FROM Activities WHERE personId = %s", (personId,))
            activityList = myCursor.fetchall()

            # Print user's activities
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            for i in range(len(activityList)):
                print(str(i+1)+": "+activityList[i][0])
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

            # Prompt for activity to delete
            print("NOTE: When deleting an activity, ALL time filed for that activity will also be deleted!")
            print("(Enter -1 to return to the main menu)")
            activityChoice = input("Please enter the number of the activity you'd like to delete: ")

            # Return to main menu if user entered -1
            if (activityChoice == '-1'):
                return 0

            # Input validation, make sure entered activity number is within range
            while(int(activityChoice) > len(activityList) or (int(activityChoice) != -1 and int(activityChoice) <= 0)):
                print("Error: chosen activity number does not exist.")
                print("NOTE: When deleting an activity, ALL time filed for that activity will also be deleted!")
                print("(Enter -1 to return to the main menu)")
                activityChoice = input("Please enter the number of the activity you'd like to delete: ")

                # Return to main menu if user entered -1
                if (activityChoice == '-1'):
                    return 0
            
            # Get the activityId so we can delete from Days table
            myCursor.execute("SELECT activityId FROM Activities WHERE activityName = %s AND personId = %s", (activityList[int(activityChoice)-1][0], personId))
            activityId = myCursor.fetchone() #TODO: Make function so we don't have to do this everytime
            activityId = activityId[0]

            # Delete all filed time for this activity from the Days table
            myCursor.execute("DELETE FROM Days WHERE activityId = %s", (activityId,))

            # Delete activity from Activities table
            myCursor.execute("DELETE FROM Activities WHERE activityId = %s", (activityId,))

            dataBase.commit()
            print("Activity deleted!")
            
def fileTime(personId):
    inputValid = False
    while inputValid == False:
        # Prompt for date to file time for
        print("(Enter -1 to return to the main menu)")
        date = input("Please enter what date you would like to file time for (YYYY-MM-DD): ")

        # Input validation
        try:
            date = datetime.datetime.strptime(date,'%Y-%m-%d').date() # Converts from str to datetime.date
            inputValid = True

        except ValueError:
            # Return to main menu if user entered -1
            if (date == '-1'):
                return 0
            print("\nError: Invalid date input. Please try again.")

        # Get a list of all activities then print them out. Output is numbered starting at 1
        # Get all user's activities
        myCursor.execute("SELECT activityName FROM Activities WHERE personId = %s", (personId,))
        activityList = myCursor.fetchall()

        # Print user's activities
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        for i in range(len(activityList)):
            print(str(i+1)+": "+activityList[i][0])
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    
    # Prompt for activity to file
    print("(Enter -1 to return to the main menu)")
    activityChoice = input("Please enter the number of the activity you'd like to file: ")

    # Return to main menu if user entered -1
    if (activityChoice == '-1'):
        return 0

    # Input validation
    while(int(activityChoice) > len(activityList) or (int(activityChoice) <= 0)):
        print("Error: chosen activity number does not exist.")
        print("(Enter -1 to return to the main menu)")
        activityChoice = input("Please enter the number of the activity you'd like to delete: ")

    myCursor.execute("SELECT activityId FROM Activities WHERE activityName = %s AND personId = %s", (activityList[int(activityChoice)-1][0], personId))

    activityId = myCursor.fetchone() #TODO: Make this a function so we don't have to fetch then set equal to first index of tuple everytime
    activityId = activityId[0]

    activityAlreadyDoneOnThisDate = False

    # Select the date field where the activityId is the same as the one the user selected, to confirm that this activity has not already been filed today
    myCursor.execute("SELECT date FROM Days WHERE activityId = %s",(str(activityId),))
    datesWhenActivityWasPreviouslyDone = myCursor.fetchall()

    ###TODO: Just change the above sql statement to select date from days where activityId = ... AND date = date and make sure it's equal to none

    # Iterate through every date where the selected activity has been already been done to make sure the user hasn't
    # already entered data for this activity on the selected day
    for i in range(len(datesWhenActivityWasPreviouslyDone)):
        if datesWhenActivityWasPreviouslyDone[i][0] == date:
            activityAlreadyDoneOnThisDate = True
            break

    if activityAlreadyDoneOnThisDate:
        print("You've already filed time for this activity on "+str(date))
        print("Any time you input now will override what you entered earlier!")

    print("(Enter -1 to return to the main menu)")
    activityTime = input("Please enter how much time you spent on this activity on "+str(date)+" in minutes: ") #TODO, make it so they can enter in minutes or hours.
    #TODO, regardless, time will be stored in minutes. So eventually make it so if they enter in hours, then we convert to minutes first.

    # Return to main menu if user entered -1
    if (activityTime == '-1'):
        return 0

    # If the activity has already been filed, then update the activityTime field...
    if activityAlreadyDoneOnThisDate:
        myCursor.execute("UPDATE Days SET activityTime = %s WHERE activityId = %s AND date = %s",(activityTime,activityId,str(date)))
        dataBase.commit()
    # Else, create a new row
    else:
        myCursor.execute("INSERT INTO Days (date, personId, activityId, activityTime) VALUES (%s, %s, %s, %s)", (date, personId, activityId, activityTime)) ##TODO: Eventually make sure that the amount of time doesn't go over amount of time in day
        dataBase.commit()

def plotRangeOfTime(*args): ##TODO: Replace with kargs so we can name the parameters and such
    # Parallel arrays that hold the time spent on an activity and the activity's name
    totalActivitiesTimeValues = []
    activityNames = []

    # Graph all time
    if len(args) == 1:
        personId = args[0]

        myCursor.execute("SELECT MIN(date) FROM Days WHERE personId = %s", (personId,))
        startDate = myCursor.fetchone()
        startDate = startDate[0]

        myCursor.execute("SELECT MAX(date) FROM Days WHERE personId = %s", (personId,))
        endDate = myCursor.fetchone()
        endDate = endDate[0]

    # Graph user entered range of time
    elif len(args) == 3:
        startDate = args[0]
        endDate = args[1]
        personId = args[2]

    myCursor.execute("SELECT activityId, activityName FROM Activities WHERE personId = %s", (personId,))
    # List of tuples. Each tuple holds an activity's id and its name
    activityAttributes = myCursor.fetchall()

    totalTimeGraphed = 0

    for i in range(len(activityAttributes)):
        # Holds the time spent on the current activity being iterated through
        currentActivityTime = 0

        # Get all time values spent on the current activity being iterated through
        myCursor.execute("SELECT activityTime FROM Days WHERE activityId = %s AND date BETWEEN %s AND %s", (str(activityAttributes[i][0]),startDate,endDate))
        # Holds all the time spent on the current activity in list form 
        currentActivityTimeValues = myCursor.fetchall()
        
        # If this activity has been filed at any time... (empty lists return False, so if no time is stored for the current activity, then this will be false and we won't add it)
        if currentActivityTimeValues:
            # Then add all values together, and then append to the total activities time values list
            for j in range(len(currentActivityTimeValues)):
                currentActivityTime += currentActivityTimeValues[j][0]

            totalActivitiesTimeValues.append(currentActivityTime)
            totalTimeGraphed += currentActivityTime

            # Append the name of the current activity being iterated through to the activityNames list
            activityNames.append(activityAttributes[i][1])
        
    # Format, plot, and show the graph
    plt.title("Time filed ("+str(totalTimeGraphed)+" minutes) from "+str(startDate)+" to "+str(endDate))
    plt.pie(totalActivitiesTimeValues,labels=activityNames,startangle=90, autopct='%1.2f%%',shadow=True, counterclock=False, normalize=True)
    plt.axis('equal')

    plt.show()

main()
