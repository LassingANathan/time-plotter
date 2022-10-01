from sqlConnector import dataBase
import datetime
from matplotlib import pyplot as plt
import sys

myCursor = dataBase.cursor(buffered=True)

def main() -> None:
    personId = userMenu()
    mainMenu(personId)

## Login menu. Returns the personId as a string
def userMenu() -> str:
    loggedIn = False

    print("\n[LOGGED IN TO DATABASE] "+dataBase.database)
    print("[LOGGED IN TO DATABASE AS] "+dataBase.user)

    print("\nHello! Welcome to TimePlotter!")

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
            if (userNameInput == '-1' or userNameInput == 'new'):
                print("\nERROR: Username can't be 'new' or '-1'\n")
                continue

            # Verify that no one already uses this username
            myCursor.execute("SELECT personName FROM People WHERE personName = %s;", (userNameInput,))
            duplicateName = myCursor.fetchall()

            # Check that username isn't already taken
            if (duplicateName):
                print("\nThis name already exists, maybe try another?\n")
            # Enter user into database
            else:
                myCursor.execute("INSERT INTO People (personName) VALUES (%s);", (userNameInput,))
                dataBase.commit()
                personId = myCursor.lastrowid
                loggedIn = True
    
        # Entering an existing username
        else:   
            myCursor.execute("SELECT personId FROM People WHERE personName = %s;", (menuInput,))
            personId = myCursor.fetchall()

            # If the entered username was found then log in
            if (personId):
                personId = personId[0][0]
                userName = menuInput
                loggedIn = True
            # Username not found
            else: 
                print("\nNo user found with that name. Maybe create a new one?\n")

    return personId  

## Main menu. Leads to other menus for more specific actions
#personId=the id of the current user
def mainMenu(personId: str) -> int:
    menuInput = ''

    while menuInput != '4':
        print("\nMain Menu:")
        print("What would you like to do?\n"\
            "1: File Time\n"\
            "2: Activity Menu\n"\
            "3: Plot Time\n"\
            "4: Exit")
        menuInput = input()
        
        if (menuInput == '4'):
            print("See you next time!")
            myCursor.close()
            return 0
        elif (menuInput == '1'):
            timeFilingMenu(personId)
        elif (menuInput == '2'):
            activitiesMenu(personId)
        elif (menuInput == '3'):
            graphingMenu(personId)
        else:
            print("\nERROR: Did not enter a valid option.")

## Graphing menu. Menu for all time graphing options
#personId=the id of the current user
def graphingMenu(personId: str) -> int:
    menuInput = ''

    while menuInput != '2':
        print("\nGraphing Menu:")
        print("What would you like to do?\n"\
            "1: Graph time\n"\
            "2: Return to the main menu")
        menuInput = input()
    
        if (menuInput == '2'):
            return 0
        elif (menuInput == '1'):
            inputValid = False
            while inputValid == False:
                # Input validation
                try:
                    # Prompt for start date of graphing
                    print("\nPlease enter the START DATE of the range you would like to graph (yyyy-mm-dd)")
                    print("(Enter -1 to return to the main menu)")
                    startDate = input('Note: please enter "all" to graph time from every date ever entered: ')
                    # Main Menu
                    if (startDate == '-1'):
                        return 0

                    # Graph all tracked time if "all" was entered
                    if (startDate.strip('" ') == "all"):
                        inputValid = True
                        plotRangeOfTime(personId)
                    # Graph from a specific range of time
                    else:
                        # Try to convert startDate to a datetime.date
                        startDate = datetime.datetime.strptime(startDate,'%Y-%m-%d').date()

                        # Prompt for the end date of graphing
                        endDate = input("Please enter the END DATE of the range you would like to graph (yyyy-mm-dd): ")
                        # Main Menu
                        if (endDate == '-1'):
                            return 0

                        # Try to convert endDate to a datetime.date
                        endDate = datetime.datetime.strptime(endDate,'%Y-%m-%d').date()

                        inputValid = True
                        plotRangeOfTime(personId, startDate, endDate)

                except ValueError:
                    print("\nERROR: Invalid date input. Please try again.")
                
        else:
            print("\nERROR: Did not enter a valid option")

## Activities menu. Menu for all activity related options
#personId=the id of the current user
def activitiesMenu(personId) -> int:
    menuInput = ''

    while menuInput != '4':
        print("\nActivities Menu:")
        print("1: See list of activities\n"\
            "2: Add new activity\n"\
            "3: Delete activity\n"\
            "4: Back")
        menuInput = input()

        if (menuInput == '4'):
            return 0

        # Print list of activities
        elif (menuInput == '1'):
            printUserActivities(personId)

        # Add a new activity
        elif (menuInput == '2'):
            print("\n(Enter -1 to return to the main menu)")
            newActivity = input("Input the new activity name: ")

            # Main Menu
            if (newActivity == '-1'):
                return 0
            
            # Get all activities for the current user
            myCursor.execute("SELECT activityName FROM Activities WHERE personId = %s;", (personId,))
            # Check to ensure the user entered activity doesn't already exist
            addActivity = True
            for activity in myCursor:
                if (activity[0] == newActivity):
                    addActivity = False
                    break

            # Enter activity into database
            if (addActivity):
                myCursor.execute("INSERT INTO Activities (personId, activityName) VALUES (%s, %s);", (personId, newActivity))
                dataBase.commit()
                print ("Activity succesfully added!")
            else:
                print("Sorry, we could not add the new activity. The activity likely already exists!")

        # Delete an activity
        elif (menuInput == '3'):
            inputValid = False
            while inputValid == False:
                # Input validation for entering an int
                try:
                    # Get and print all user activities
                    activityList = printUserActivities(personId)
                    # Prompt for activity to delete
                    print("\nNOTE: When deleting an activity, ALL time filed for that activity will also be deleted!")
                    print("(Enter -1 to return to the main menu)")
                    activityChoice = input("Please enter the number of the activity you'd like to delete: ")

                    # Main Menu
                    if (activityChoice == '-1'):
                        return 0
                    
                    # See if the input can be converted to an int
                    int(activityChoice)
                except ValueError:
                    print("\nERROR: given value was not a number.")
                    continue

                # Input validation for entering a valid int
                if ((int(activityChoice) > len(activityList)) or (int(activityChoice) <= 0)):
                    print("\nERROR: chosen activity number does not exist.")
                    continue
            
                inputValid = True
            
            # Get activityId of activity to delete
            myCursor.execute("SELECT activityId FROM Activities WHERE activityName = %s AND personId = %s;", (activityList[int(activityChoice)-1][0], personId))
            activityId = myCursor.fetchone()
            activityId = activityId[0]

            # Delete all filed time for this activity from the Days table
            myCursor.execute("DELETE FROM Days WHERE activityId = %s;", (activityId,))

            # Delete activity from Activities table
            myCursor.execute("DELETE FROM Activities WHERE activityId = %s;", (activityId,))

            dataBase.commit()
            print("Activity deleted!")

        else:
            print("\nERROR: Did not enter a valid option.")

## Time filing menu. Menu for all time filing related options
#personId=the id of the current user
def timeFilingMenu(personId: str) -> int:
    inputValid = False
    while inputValid == False:
        # Input validation
        try:
            # Prompt for date to file time for
            print("\n(Enter -1 to return to the main menu)")
            date = input("Please enter what date you would like to file time for (YYYY-MM-DD): ")

            # Convert date from string to datetime.date
            date = datetime.datetime.strptime(date,'%Y-%m-%d').date()
            inputValid = True
        except ValueError:
            # Main Menu
            if (date == '-1'):
                return 0
            print("\nERROR: Invalid date input. Please try again.")

    # Reset inputValid for next prompt
    inputValid = False
    
    # Ask for activity to file time for
    while (inputValid == False):
        # Input validation for entering an int
        try:
            # Get and print all user activities
            activityList = printUserActivities(personId)
            # Prompt for activity to file
            print("\n(Enter -1 to return to the main menu)")
            activityChoice = input("Please enter the number of the activity you'd like to file: ")

            # Return to main menu if user entered -1
            if (activityChoice == '-1'):
                return 0
            
            # See if the input can be converted to an int
            int(activityChoice)
        except ValueError:
            print("\nERROR: given value was not a number.")
            continue

        # Input validation for entering a valid int
        if ((int(activityChoice) > len(activityList)) or (int(activityChoice) <= 0)):
            print("\nERROR: chosen activity number does not exist.")
            continue
    
        inputValid = True

    # Get activityId of the activity to file
    myCursor.execute("SELECT activityId FROM Activities WHERE activityName = %s AND personId = %s;", (activityList[int(activityChoice)-1][0], personId))
    activityId = myCursor.fetchone()
    activityId = activityId[0]

    activityAlreadyDoneOnThisDate = False

    # Select the date field where the activityId is the same as the one the user selected, to confirm that this activity has not already been filed today
    myCursor.execute("SELECT date FROM Days WHERE activityId = %s AND date = %s;",(str(activityId), str(date)))
    dateWhereActivityWasDone = myCursor.fetchall()
    print(dateWhereActivityWasDone)

    # If the activity was already done on this date, warn about overriding
    if (dateWhereActivityWasDone):
        print("\nYou've already filed time for this activity on "+str(date))
        print("Any time you input now will override what you entered earlier!")

    print("\n(Enter -1 to return to the main menu)")
    activityTime = input("Please enter how much time you spent on this activity on "+str(date)+" in minutes: ") #TODO, make it so they can enter in minutes or hours.
    #TODO, regardless, time will be stored in minutes. So eventually make it so if they enter in hours, then we convert to minutes first.

    # Main Menu
    if (activityTime == '-1'):
        return 0

    # Update existing row if activity already filed
    if (activityAlreadyDoneOnThisDate):
        myCursor.execute("UPDATE Days SET activityTime = %s WHERE activityId = %s AND date = %s;",(activityTime,activityId,str(date)))
        dataBase.commit()
    # Create new row for this activity and date
    else:
        myCursor.execute("INSERT INTO Days (date, personId, activityId, activityTime) VALUES (%s, %s, %s, %s);", (date, personId, activityId, activityTime)) ##TODO: Eventually make sure that the amount of time doesn't go over amount of time in day
        dataBase.commit()

## Creates a pyPlot pie chart of tracked time in a range of dates. Graphs all tracked time if no date range is given
#personId=the id of the current user, startDate=optional datetime.date for the beginning of range to graph, endDate=optional datetime.date for the end of range to graph
def plotRangeOfTime(personId: str, startDate: datetime.date = None, endDate: datetime.date = None) -> None:
    # Parallel arrays that hold the time spent on an activity and the activity's name
    totalActivitiesTimeValues = []
    activityNames = []

    # Set startDate and endDate to min and max dates (graph all tracked time) if no values were passed
    if (startDate == None and endDate == None):
        myCursor.execute("SELECT MIN(date) FROM Days WHERE personId = %s;", (personId,))
        startDate = myCursor.fetchone()
        startDate = startDate[0]

        myCursor.execute("SELECT MAX(date) FROM Days WHERE personId = %s;", (personId,))
        endDate = myCursor.fetchone()
        endDate = endDate[0]

    myCursor.execute("SELECT activityId, activityName FROM Activities WHERE personId = %s;", (personId,))
    # List of tuples. Each tuple holds an activity's id and its name
    activityAttributes = myCursor.fetchall()

    totalTimeGraphed = 0

    for i in range(len(activityAttributes)):
        # Holds the time spent on the current activity being iterated through
        currentActivityTime = 0

        # Get all time values spent on the current activity being iterated through
        myCursor.execute("SELECT activityTime FROM Days WHERE activityId = %s AND date BETWEEN %s AND %s;", (str(activityAttributes[i][0]),startDate,endDate))
        # Holds all the time spent on the current activity in list form 
        currentActivityTimeValues = myCursor.fetchall()
        
        # Checl that the current activity has ever been filed in this range
        if (currentActivityTimeValues):
            # Sum all time for this activity in currentActivityTime
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

## Prints out numbered list of all activities belonging to the given person. Returns a list of the activities (as tuples holding activity name string)
#personId=the id of the current user
def printUserActivities(personId : str) -> list:
    myCursor.execute("SELECT activityName FROM Activities WHERE personId = %s;", (personId,))
    activityList = myCursor.fetchall()

    # Print user's activities
    print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("Activity List:")
    for i in range(len(activityList)):
        print(str(i+1)+": "+activityList[i][0])
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    return activityList

main()
