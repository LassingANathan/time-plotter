from sqlConnector import dataBase
import datetime
from matplotlib import pyplot as plt
import sys

myCursor = dataBase.cursor(buffered=True)

def main():
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
            myCursor.execute("SELECT personName FROM People WHERE personName = %s", (userNameInput,))
            duplicateName = myCursor.fetchall()

            # If a duplicate name exists...
            if (duplicateName):
                print("\nThis name already exists, maybe try another?\n")
            else:
                myCursor.execute("INSERT INTO People (personName) VALUES (%s)", (userNameInput,))
                dataBase.commit()
                personId = myCursor.lastrowid
                loggedIn = True
    
        # Entering an existing username
        else:   
            myCursor.execute("SELECT personId FROM People WHERE personName = %s", (menuInput,))
            personId = myCursor.fetchall()

            # If entered username was found...
            if (personId):
                personId = personId[0][0] #TODO: Make fuction smh
                userName = menuInput
                loggedIn = True
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
            #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            timeFilingMenu(personId)
        elif (menuInput == '2'):
            #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            activitiesMenu(personId)
        elif (menuInput == '3'):
            #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
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
                # Prompt for start date of graphing
                print("\nPlease enter the START DATE of the range you would like to graph (yyyy-mm-dd)")
                print("(Enter -1 to return to the main menu)")
                startDate = input('Note: please enter "all" to graph time from every date ever entered: ')

                # If the user wants to graph all time ever entered...
                if (startDate.strip('" ') == "all"):
                    inputValid = True
                    plotRangeOfTime(personId)
                # If the user wants to graph from a specified range...
                else:
                    # Input validation
                    try:
                        startDate = datetime.datetime.strptime(startDate,'%Y-%m-%d').date()

                        endDate = input("Please enter the END DATE of the range you would like to graph (yyyy-mm-dd): ")
                        endDate = datetime.datetime.strptime(endDate,'%Y-%m-%d').date()

                        inputValid = True

                        plotRangeOfTime(personId, startDate, endDate)
                    except ValueError:
                        if (startDate == '-1' or endDate == '-1'):
                            return 0
                        print("\nERROR: Invalid date input. Please try again.")
                
        else:
            print("\nERROR: Did not enter a valid option")

## Activities menu. Menu for all activity related options
#personId=the id of the current user
def activitiesMenu(personId):
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
            # Print all user activities
            printUserActivities(personId)

        # Add a new activity
        elif (menuInput == '2'):
            print("\n(Enter -1 to return to the main menu)")
            newActivity = input("Input the new activity name: ")

            # Return to main menu if user entered -1
            if (newActivity == '-1'):
                return 0
            
            addActivity = True
            myCursor.execute("SELECT activityName FROM Activities WHERE personId = %s", (personId,))

            # Check to ensure the user entered activity doesn't already exist
            for activity in myCursor:
                if (activity == newActivity):
                    addActivity = False
                    break

            # If the activity isn't already entered, then enter it.
            if (addActivity):
                myCursor.execute("INSERT INTO Activities (personId, activityName) VALUES (%s, %s);", (personId, newActivity))
                dataBase.commit()
                print ("Activity succesfully added!")
            else: # Otherwise, do not enter it.
                print("Sorry, we could not add the new activity. The activity likely already exists!")

        # Delete an activity
        elif (menuInput == '3'):
            # Get and print all user activities
            activityList = printUserActivities(personId)

            # Prompt for activity to delete
            print("\nNOTE: When deleting an activity, ALL time filed for that activity will also be deleted!")
            print("(Enter -1 to return to the main menu)")
            activityChoice = input("Please enter the number of the activity you'd like to delete: ")

            # Return to main menu if user entered -1
            if (activityChoice == '-1'):
                return 0

            # Input validation, make sure entered activity number is within range
            while(int(activityChoice) > len(activityList) or (int(activityChoice) != -1 and int(activityChoice) <= 0)):
                print("\nERROR: chosen activity number does not exist.\n")
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
                
        else:
            print("\nERROR: Did not enter a valid option.")
## Time filing menu. Menu for all time filing related options
#personId=the id of the current user
def timeFilingMenu(personId: str) -> int:
    inputValid = False
    while inputValid == False:
        # Prompt for date to file time for
        print("\n(Enter -1 to return to the main menu)")
        date = input("Please enter what date you would like to file time for (YYYY-MM-DD): ")

        # Input validation
        try:
            date = datetime.datetime.strptime(date,'%Y-%m-%d').date() # Converts from str to datetime.date
            inputValid = True

        except ValueError:
            # Return to main menu if user entered -1
            if (date == '-1'):
                return 0
            print("\nERROR: Invalid date input. Please try again.")

    # Get and print all user activities
    activityList = printUserActivities(personId)
    # Prompt for activity to file
    print("\n(Enter -1 to return to the main menu)")
    activityChoice = input("Please enter the number of the activity you'd like to file: ")

    # Return to main menu if user entered -1
    if (activityChoice == '-1'):
        return 0

    # Input validation
    while(int(activityChoice) > len(activityList) or (int(activityChoice) <= 0)):
        print("\nERROR: chosen activity number does not exist.")
        print("\n(Enter -1 to return to the main menu)")
        activityChoice = input("Please enter the number of the activity you'd like to file: ")
        # Return to main menu if user entered -1
        if (activityChoice == '-1'):
            return 0

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
        if (datesWhenActivityWasPreviouslyDone[i][0] == date):
            activityAlreadyDoneOnThisDate = True
            break

    if (activityAlreadyDoneOnThisDate):
        print("\nYou've already filed time for this activity on "+str(date))
        print("Any time you input now will override what you entered earlier!")

    print("\n(Enter -1 to return to the main menu)")
    activityTime = input("Please enter how much time you spent on this activity on "+str(date)+" in minutes: ") #TODO, make it so they can enter in minutes or hours.
    #TODO, regardless, time will be stored in minutes. So eventually make it so if they enter in hours, then we convert to minutes first.

    # Return to main menu if user entered -1
    if (activityTime == '-1'):
        return 0

    # If the activity has already been filed, then update the activityTime field...
    if (activityAlreadyDoneOnThisDate):
        myCursor.execute("UPDATE Days SET activityTime = %s WHERE activityId = %s AND date = %s",(activityTime,activityId,str(date)))
        dataBase.commit()
    # Else, create a new row
    else:
        myCursor.execute("INSERT INTO Days (date, personId, activityId, activityTime) VALUES (%s, %s, %s, %s)", (date, personId, activityId, activityTime)) ##TODO: Eventually make sure that the amount of time doesn't go over amount of time in day
        dataBase.commit()

## Creates a pyPlot pie chart of tracked time in a range of dates. Graphs all tracked time if no date range is given
#personId=the id of the current user, startDate=optional datetime.date for the beginning of range to graph, endDate=optional datetime.date for the end of range to graph
def plotRangeOfTime(personId: str, startDate: datetime.date = None, endDate: datetime.date = None) -> None:
    # Parallel arrays that hold the time spent on an activity and the activity's name
    totalActivitiesTimeValues = []
    activityNames = []

    # Set startDate and endDate to min and max dates (graph all tracked time) if no values were passed
    if (startDate == None and endDate == None):
        myCursor.execute("SELECT MIN(date) FROM Days WHERE personId = %s", (personId,))
        startDate = myCursor.fetchone()
        startDate = startDate[0]

        myCursor.execute("SELECT MAX(date) FROM Days WHERE personId = %s", (personId,))
        endDate = myCursor.fetchone()
        endDate = endDate[0]

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
        if (currentActivityTimeValues):
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

## Prints out numbered list of all activities belonging to the given person. Returns a list of the activities (as tuples holding activity name string)
#personId=the id of the current user
def printUserActivities(personId : str) -> list:
    myCursor.execute("SELECT activityName FROM Activities WHERE personId = %s", (personId,))
    activityList = myCursor.fetchall()

    # Print user's activities
    print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("Activity List:")
    for i in range(len(activityList)):
        print(str(i+1)+": "+activityList[i][0])
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    return activityList

main()
