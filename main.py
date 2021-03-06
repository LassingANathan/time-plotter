from matplotlib.colors import Normalize
from sqlConnector import dataBase
import datetime
import sqlInteractions as sqlUtil
from matplotlib import pyplot as plt

myCursor = dataBase.cursor(buffered=True)

def main():
    menuAns = ''
    print("\n[LOGGED IN TO] "+dataBase.database)
    print("[LOGGED IN AS] "+dataBase.user)
    print("\nHello! Welcome to TimePlotter!")

    while menuAns != '4':
        print("\nWhat would you like to do?\n"\
            "1: File Time\n"\
            "2: Activity Menu\n"\
            "3: Plot Time\n"\
            "4: Exit")
        menuAns = input()
        
        if menuAns == '4':
            print("See you next time!")
            myCursor.close()
            return 0
        elif menuAns == '1':
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            fileTime()
        elif menuAns == '2':
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            activityTypesMenu()
        elif menuAns == '3':
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            graphingMenu()
        else:
            print("Error! Did not enter a valid option.")

def graphingMenu():
    menuAns = ''

    while menuAns != '2':
        print("What would you like to do?\n"\
            "1: Graph time\n"\
            "2: Return to the main menu")
        menuAns = input()
    
        if menuAns == '2':
            return 0
        elif menuAns == '1':
            inputValid = False
            while inputValid == False:
                # Prompt and get input
                print("Please enter the start date of the range you would like to graph (yyyy-mm-dd)")
                print("(Enter -1 to return to the main menu)")
                startDate = input('Note: please enter "all" to graph time from every date ever entered: ')

                # Return to main menu if user entered -1
                if(startDate == '-1'):
                    return 0
                # If the user wants to graph all time ever entered...
                if (startDate.strip('" ') == "all"):
                    inputValid = True
                    plotRangeOfTime()

                else:
                    # Input validation
                    try:
                        startDate = datetime.datetime.strptime(startDate,'%Y-%m-%d').date()

                        endDate = input("Please enter the end date of the range you would like to graph (yyyy-mm-dd): ")
                        endDate = datetime.datetime.strptime(endDate,'%Y-%m-%d').date()

                        inputValid = True

                        plotRangeOfTime(startDate,endDate)
                    except ValueError:
                        print("\nError: Invalid date input. Please try again.")
                
        else:
            print("Error! Did not enter a valid option")

def activityTypesMenu():
    menuAns = ''

    while menuAns != '4':
        print("1: See list of activities\n"\
            "2: Add new activity\n"\
            "3: Delete activity\n"\
            "4: Back")
        menuAns = input()

        if menuAns == '4':
            return 0

        # Print list of activities
        elif menuAns == '1':
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            activityList = sqlUtil.getColumn(myCursor,dataBase,"Activities","activityName")
            for i in range(len(activityList)):
                print(str(i+1)+": "+activityList[i])
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # Add a new activity
        elif menuAns == '2':
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("(Enter -1 to return to the main menu)")
            newActivity = input("Input the new activity name: ")

            # Return to main menu if user entered -1
            if (newActivity == '-1'):
                return 0
            
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
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            activityList = sqlUtil.getColumn(myCursor,dataBase,"Activities","activityName")
            for i in range(len(activityList)):
                print(str(i+1)+": "+activityList[i])

            print("NOTE: When deleting an activity, ALL time filed for that activity will also be deleted!")
            print("(Enter -1 to return to the main menu)")
            activityChoice = input("Please enter the number of the activity you'd like to delete: ")

            # Return to main menu if user entered -1
            if (activityChoice == '-1'):
                return 0

            # Input validation
            while(int(activityChoice) > len(activityList) or (int(activityChoice) != -1 and int(activityChoice) <= 0)):
                print("Error: chosen activity number does not exist.")
                print("NOTE: When deleting an activity, ALL time filed for that activity will also be deleted!")
                print("(Enter -1 to return to the main menu)")
                activityChoice = input("Please enter the number of the activity you'd like to delete: ")

                # Return to main menu if user entered -1
                if (activityChoice == '-1'):
                    return 0
            
            # Get the activityId so we can delete from Days table
            myCursor.execute("SELECT activityId FROM Activities WHERE activityName = %s", (activityList[int(activityChoice)-1],))
            activityId = myCursor.fetchone() #TODO: Make function so we don't have to do this everytime
            activityId = activityId[0]

            # Delete all filed time for this activity from the Days table
            myCursor.execute("DELETE FROM Days WHERE activityId = %s", (activityId,))

            # Delete activity from Activities table
            myCursor.execute("DELETE FROM Activities WHERE activityName = %s", (activityList[int(activityChoice)-1],))

            dataBase.commit()
            print("Activity deleted!")
            
def fileTime():
    inputValid = False
    while inputValid == False:
        # Prompt and get input
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
    activityList = sqlUtil.getColumn(myCursor,dataBase,"Activities","activityName")
    for i in range(len(activityList)):
        print(str(i+1)+": "+activityList[i])
    
    activityChoice = input("Please enter the number of the activity you'd like to file: ")
    # Input validation
    while(int(activityChoice) > len(activityList) or (int(activityChoice) != -1 and int(activityChoice) <= 0)):
        print("Error: chosen activity number does not exist.")
        print("(Enter -1 to return to the main menu)")
        activityChoice = input("Please enter the number of the activity you'd like to delete: ")

        # Return to main menu if user entered -1
        if (activityChoice == '-1'):
            return 0

    myCursor.execute("SELECT activityId FROM Activities WHERE activityName = '"+activityList[int(activityChoice)-1]+"'")

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
        myCursor.execute("INSERT INTO Days (date, activityId, activityTime) VALUES (%s, %s, %s)", (date, activityId, activityTime)) ##TODO: Eventually make sure that the amount of time doesn't go over amount of time in day
        dataBase.commit()

def plotRangeOfTime(*args): ##TODO: Replace with kargs so we can name the parameters and such
    # Parallel arrays that hold the time spent on an activity and the activity's name
    totalActivitiesTimeValues = []
    activityNames = []

    if len(args) == 0:
        myCursor.execute("SELECT MIN(date) FROM Days")
        startDate = myCursor.fetchone()
        startDate = startDate[0]

        myCursor.execute("SELECT MAX(date) FROM Days")
        endDate = myCursor.fetchone()
        endDate = endDate[0]
    else:
        startDate = args[0]
        endDate = args[1]

    myCursor.execute("SELECT activityId, activityName FROM Activities")
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
    plt.title(str(totalTimeGraphed)+" minutes")
    plt.pie(totalActivitiesTimeValues,labels=activityNames,startangle=90, autopct='%1.2f%%',shadow=True, counterclock=False)
    plt.axis('equal')

    plt.show()

def test():
    endDate = input("Please enter the end date of the range you would like to graph (yyyy-mm-dd): ")
    endDate = datetime.datetime.strptime(endDate,'%Y-%m-%d').date()

    print(type(endDate))
    if type(6) == int:
        print(type(6))

#test()
main()
