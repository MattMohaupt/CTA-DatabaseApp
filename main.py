#-------------------------------------------------------------------------------------------
#Project 1: CTA Database App
#Date: 1/31/24
#Course: CS 341, Spring 2024, UIC
#System: Visual Studio Code
#Author: Matthew Mohaupt; mmohau3; 651525023
#Description: a console-based Python program that inputs 
#    commands from the user and outputs data from the CTA2 L daily ridership database
#-------------------------------------------------------------------------------------------

import sqlite3
import matplotlib.pyplot as plt

import math #for cosine function


##################################################################  
#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    
    print("General Statistics:")
    #get the total number of all station
    dbCursor.execute("Select count(*) From Stations;")
    row = dbCursor.fetchone()
    print("  # of stations:", f"{row[0]:,}")
    #count the number of distinct stop_Id's so we know how many stops there are
    dbCursor.execute("Select count(DISTINCT Stop_ID) From Stops;")
    row = dbCursor.fetchone()
    print("  # of stops:", f"{row[0]:,}")
    #get the total number rideership entries 
    dbCursor.execute("Select count(Num_Riders) From Ridership;")
    row = dbCursor.fetchone()
    print("  # of ride entries:", f"{row[0]:,}")
    #get the lowest date and max date in the database
    dbCursor.execute("Select min(date(Ride_Date)), max(date(Ride_Date)) From Ridership;")
    row = dbCursor.fetchall()
    print("  date range:", f"{row[0][0]:}", "-", f"{row[0][1]:}")
    #get the number all riders ever in the database
    dbCursor.execute("Select sum(Num_Riders) From Ridership;")
    row = dbCursor.fetchone()
    print("  Total ridership:", f"{row[0]:,}")
    print()


##command 1 function
##Find all the station names that match the user input
def command1(dbConn):
    rowindex = 0
    dbCursor = dbConn.cursor()
    partialname = input("\nEnter partial station name (wildcards _ and %): ")
    #get the station id, and official station name from all the stations that have the substring in it
    dbCursor.execute("Select Station_ID, Station_Name From Stations where Station_Name LIKE (?) ORDER BY Station_Name asc;", (partialname,))
    row = dbCursor.fetchall()
    finalrowindex = len(row)
    if(rowindex == finalrowindex):
        print("**No stations found...")
    else:
        while(rowindex < finalrowindex):
            print(f"{row[rowindex][0]:}", ":", f"{row[rowindex][1]:}")
            rowindex+=1


##command 2 function
##find the percentage of riders on weekdays, on Saturdays, and on Sundays/holidays for a given station name
def command2(dbConn):
    dbCursor = dbConn.cursor()
    stationname = input("\nEnter the name of the station you would like to analyze: ")
    dbCursor.execute("""Select Station_ID from Stations where Station_Name = ?""", (stationname,))
    stationid = dbCursor.fetchone()
#if no station name is found then return
    if(stationid == None):
        print("**No data found...")
        return
    #get the total weekday ridership, total saturday ridership, and total sunday/holiday ridership seperatly for the station
    dbCursor.execute("""Select sum(Num_Riders) from Ridership where Type_of_Day = 'W' and Station_ID = ?;""", (stationid))
    weekdayriders = dbCursor.fetchone()
    dbCursor.execute("""Select sum(Num_Riders) from Ridership where Type_of_Day = 'A' and Station_ID = ?;""", (stationid))
    saturdayriders = dbCursor.fetchone()
    dbCursor.execute("""Select sum(Num_Riders) from Ridership where Type_of_Day = 'U' and Station_ID = ?;""", (stationid))
    holidayriders = dbCursor.fetchone()
    dbCursor.execute("""Select sum(Num_Riders) from Ridership where Station_ID = ?;""", (stationid))
    totalriders = dbCursor.fetchone()
    #print everything out and use python to compute percentage
    print("Percentage of ridership for the "+stationname+" station:")
    print("  Weekday ridership: {:,} ({:.2f}%)" .format(weekdayriders[0], (weekdayriders[0]/totalriders[0])*100))
    print("  Saturday ridership: {:,} ({:.2f}%)" .format(saturdayriders[0], (saturdayriders[0]/totalriders[0])*100))
    print("  Sunday/holiday ridership: {:,} ({:.2f}%)" .format(holidayriders[0], (holidayriders[0]/totalriders[0])*100))
    print("  Total ridership: {:,}" .format(totalriders[0]))

##command 3 function
##get the total ridership on weekdays for each station and the percentage compared to total ridership for all stations
def command3(dbConn):
    print("Ridership on Weekdays for Each Station")
    dbCursor = dbConn.cursor()
    #we need to the totalridership for weekdays of all stations
    dbCursor.execute("""Select sum(Num_Riders) from Ridership where Type_of_Day = 'W';""")
    totalriders = dbCursor.fetchone()
    #we have to return the station name and total weekday riders for each station so we'll need to join both riderhsip and stations and we have to get the sation id from stations and use it for riderhsip and sum all of the weekday riderships from all dates 
    dbCursor.execute("SELECT Stations.Station_Name, COALESCE(SUM(Ridership.Num_Riders), 0) AS totalWeekdayRiders FROM Stations JOIN Ridership ON Stations.Station_ID = Ridership.Station_ID WHERE Ridership.Type_of_Day = 'W' GROUP BY Stations.Station_Name ORDER BY totalWeekdayRiders DESC;")
    table = dbCursor.fetchall()
    rowindex = 0
    finalindex = len(table)
    if(rowindex == finalindex):
        print("**No stations found...") #this should be possible but if the database is empty we will leave it there
        return
    else:
        while(rowindex < finalindex):
            #using python to get the percentage
            print("{:} : {:,} ({:.2f}%)" .format(table[rowindex][0], table[rowindex][1], (table[rowindex][1]/totalriders[0])*100))
            rowindex+=1

##command 4 function
##output all the stops fora specified line color in a specified direction
def command4(dbConn):
    dbCursor = dbConn.cursor()
    color = input("\nEnter a line color (e.g. Red or Yellow): ")
    #we have to format the color to be an exact type, so we need to have a check for specifically purple line express since it is Purple-Express in the database
    dashfinder = color.find("-")
    #we have to ower case everything and if there is a dash in the line name, not only do we need to capatilize the first letter but the first letter after the dash as well
    if(dashfinder > -1):
        color = color.lower()
        color = color[0].upper() + color[1:dashfinder+1] + color[dashfinder+1].upper() + color[dashfinder+2:]
    else:
        color = color.lower()
        color = color[0].upper() + color[1:]
        #get the line id of the color
    dbCursor.execute("Select Line_ID from Lines where Color = ?;", (color,))
    lineid = dbCursor.fetchone()
    if(lineid == None):
        print("**No such line...")
        return
    #get the direction but also make sure it is uppercase since in the database all the directions chars are upper case
    cardinal = input("Enter a direction (N/S/W/E): ")
    cardinal = cardinal.upper()
    #need to get the stop name, and accessibiity info where the stops are in the direction and on the line
    #we dont need to get direction, we know what it should be from what the user put in but its easier to just get all of them on the fetchall
    dbCursor.execute("Select Stop_Name, Direction, ADA from Stops where Stop_ID IN (Select Stop_ID from StopDetails where Line_ID = ?) AND Direction = ? ORDER BY Stop_Name asc;", (lineid[0], cardinal))
    table = dbCursor.fetchall()
    rowindex = 0
    finalrow = len(table)
    #if the query got nothing, then the line does not run in the direction
    if(finalrow == rowindex):
        print("**That line does not run in the direction chosen...")
        return
    while(rowindex < finalrow):
        #need to check if handicap flag has been checked for the stop
        if((table[rowindex][2]) == 1):
            accessibilty = "handicap accessible"
        else:
            accessibilty = "not handicap accessible"

        print("{:} : direction = {:} ({:})" .format(table[rowindex][0], table[rowindex][1], accessibilty))
        
        rowindex+=1
    



##command 5 function
##Output the number of stops for each line color, separated by direction
def command5(dbConn):
    dbCursor = dbConn.cursor()
    print("Number of Stops For Each Color By Direction")
    #first we need to get all the total amount of stops there are in the entire cta, so we need count distinct stops as to not have repeats
    dbCursor.execute("Select count(DISTINCT Stop_ID) From Stops;")
    totalcolorstop = dbCursor.fetchone()
    #now we have to return the color of the stop, the direction the train is going in at the stop, and count the total number of stops where the color and direction and direction are the in the same category as well
    dbCursor.execute("SELECT Lines.Color, Stops.Direction, COUNT(Stops.Stop_ID) FROM Lines JOIN StopDetails ON Lines.Line_ID = StopDetails.Line_ID JOIN Stops ON StopDetails.Stop_ID = Stops.Stop_ID GROUP BY Lines.Color, Stops.Direction ORDER BY Lines.Color ASC, Stops.Direction ASC;")
    colordirectionstop = dbCursor.fetchall()
    cdsindex = 0
    finalcdsindex = len(colordirectionstop)
    #printing out the info to the terminal
    while(cdsindex < finalcdsindex):
        print("{:} going {:} : {:} ({:.2f}%)" .format(colordirectionstop[cdsindex][0], colordirectionstop[cdsindex][1], colordirectionstop[cdsindex][2], (colordirectionstop[cdsindex][2]/totalcolorstop[0])*100))
        cdsindex+=1

##command 6 function
##output the total ridership for each year for a given station name and allow the user to plot the data
def command6(dbConn):
    dbCursor = dbConn.cursor()
     #get the name the user wants and do a check if the length is either more than 1(multiple stations found) or less than 1(no stations found)
    stationname = input("\nEnter a station name (wildcards _ and %): ")
    dbCursor.execute("""Select Station_ID from Stations where Station_Name LIKE ?""", (stationname,))
    stationid = dbCursor.fetchall()
    if(len(stationid) < 1):
        print("**No station found...")
        return
    elif(len(stationid) > 1):
        print("**Multiple stations found...")
        return 
    
    #get the official station name so we can use it later for print output
    dbCursor.execute("""Select Station_Name from Stations where Station_ID = ?""", (stationid[0][0],))
    stationname = dbCursor.fetchone()
#get the year and total riders for that year from the ridership table
    dbCursor.execute("""SELECT strftime('%Y', Ride_Date) AS Year, SUM(Num_Riders) AS Total_Ridership FROM Ridership WHERE Station_ID = ? GROUP BY Year ORDER BY Year ASC;""",(stationid[0][0],))
    ridership = dbCursor.fetchall()
    rindex = 0
    #print out the data to the terminal
    print("Yearly Ridership at {:}".format(stationname[0]))
    while(rindex < len(ridership)):
        print("{:} : {:,}" .format(ridership[rindex][0], ridership[rindex][1]))
        rindex+=1

#now time to plot the data
    decision = input("\nPlot? (y/n) ")
    decision = decision.lower()
    if(decision != 'y'):
        return

    years = [row[0] for row in ridership]
    totalrider = [row[1] for row in ridership]
    plt.plot(years, totalrider)
    plt.xlabel("Year")
    plt.ylabel("Number of Riders")
    plt.title("Yearly Ridership at {:} Station".format(stationname[0]))
    plt.tight_layout()
    plt.show()

##command 7 function
##output the total ridership for each month in a specified year for a specified station name and give the ability to plot the data
def command7(dbConn):
    dbCursor = dbConn.cursor()
    #get the name the user wants and do a check if the length is either more than 1(multiple stations found) or less than 1(no stations found)
    stationname = input("\nEnter a station name (wildcards _ and %): ")
    dbCursor.execute("""Select Station_ID from Stations where Station_Name LIKE ?""", (stationname,))
    stationid = dbCursor.fetchall()
    if(len(stationid) < 1):
        print("**No station found...")
        return
    elif(len(stationid) > 1):
        print("**Multiple stations found...")
        return
    #get the official station name so we can use it later for print output
    dbCursor.execute("""Select Station_Name from Stations where Station_ID = ?""", (stationid[0][0],))
    stationname = dbCursor.fetchone()
    #get the month and total riders for that month from the ridership table and only get those values if the year matches the one the user inputted
    year = input("Enter a year: ")
    dbCursor.execute("""SELECT strftime('%m/%Y', Ride_Date) as month, SUM(Num_Riders) FROM Ridership WHERE Station_ID = ? AND strftime('%Y', Ride_Date) = ? GROUP BY month ORDER BY month ASC;""", (stationid[0][0], year))
    ridership = dbCursor.fetchall()
    rindex = 0
    #printing out the information in the terminal
    print("Monthly Ridership at {:} for {:}" .format(stationname[0], year))
    while(rindex < len(ridership)):
        print("{:} : {:,}" .format(ridership[rindex][0], ridership[rindex][1]))
        rindex+=1

#now time to plot the data
    decision = input("\nPlot? (y/n) ")
    decision = decision.lower()
    if(decision != 'y'):
        return
    
    months = [row[0][0:2] for row in ridership]
    totalrider = [row[1] for row in ridership]
    plt.plot(months, totalrider)
    plt.xlabel("Month")
    plt.ylabel("Number of Riders")
    plt.title("Yearly Ridership at {:} Station ({:})".format(stationname[0], year))
    plt.tight_layout()
    plt.show()


##command 8 function
##Given two station names and year, output the total ridership for each day in that year and then plot the data
def command8(dbConn):
    dbCursor = dbConn.cursor()
    year = input("\nYear to compare against? ")

    #station1 name and id gathering
    station1name = input("\nEnter station 1 (wildcards _ and %): ")
    dbCursor.execute("""Select Station_ID from Stations where Station_Name LIKE ?""", (station1name,))
    station1id = dbCursor.fetchall()
    if(len(station1id) < 1):
        print("**No station found...")
        return
    elif(len(station1id) > 1):
        print("**Multiple stations found...")
        return  
    dbCursor.execute("""Select Station_Name from Stations where Station_ID = ?""", (station1id[0][0],))
    station1name = dbCursor.fetchone()

    #station2 name and id gathering
    station2name = input("\nEnter station 2 (wildcards _ and %): ")
    dbCursor.execute("""Select Station_ID from Stations where Station_Name LIKE ?""", (station2name,))
    station2id = dbCursor.fetchall()
    if(len(station2id) < 1):
        print("**No station found...")
        return
    elif(len(station2id) > 1):
        print("**Multiple stations found...")
        return  
    dbCursor.execute("""Select Station_Name from Stations where Station_ID = ?""", (station2id[0][0],))
    station2name = dbCursor.fetchone()
    station1index = 0

    #now get the ridershipdata for each day of the year for station1 and station2
    dbCursor.execute("""SELECT date(Ride_Date) AS Date, SUM(Num_Riders) FROM Ridership WHERE Station_ID = ? AND strftime('%Y', Ride_Date) = ? GROUP BY Date ORDER BY Date ASC;""", (station1id[0][0], year))
    station1ridership = dbCursor.fetchall()
    dbCursor.execute("""SELECT date(Ride_Date) AS Date, SUM(Num_Riders) FROM Ridership WHERE Station_ID = ? AND strftime('%Y', Ride_Date) = ? GROUP BY Date ORDER BY Date ASC;""", (station2id[0][0], year))
    station2ridership = dbCursor.fetchall()
    station2index = 0

    #now printing the first 5 and last data points on station 1
    print("Station 1: {:} {:}" .format(station1id[0][0], station1name[0]))
    while(station1index < len(station1ridership)):
        #check so that we only display first 5 and then last 5
        if(station1index == 5):
            station1index = len(station1ridership) - 5
        #printing the info
        print("{:} {:}" .format(station1ridership[station1index][0], station1ridership[station1index][1]))
        station1index+=1

    #now printing the first 5 and last data points on station 1
    print("Station 2: {:} {:}" .format(station2id[0][0], station2name[0]))
    while(station2index < len(station2ridership)):
        #check so that we only display first 5 and then last 5
        if(station2index == 5):
            station2index = len(station2ridership) - 5
        #printing the info
        print("{:} {:}" .format(station2ridership[station2index][0], station2ridership[station2index][1]))
        station2index+=1

    #now time to plot the data
    decision = input("\nPlot? (y/n) ")
    decision = decision.lower()
    if(decision != 'y'):
        return
#need to make ranges for the days since we have to display them out 365 instead of date and afterwards take that range and make into a list
    station1dayrange = range(1, len(station1ridership)+1)
    days1 = list(station1dayrange)
    totalrider1 = [row[1] for row in station1ridership]
    station2dayrange = list(range(1, len(station2ridership) + 1))
    days2 = list(station2dayrange)
    totalrider2 = [row[1] for row in station2ridership]
    plt.plot(days1, totalrider1, label = station1name[0])
    plt.plot(days2, totalrider2, label = station2name[0])
    plt.xlabel("Day")
    plt.ylabel("Number of Riders")
    plt.title("Ridership at each day {:}".format(year))
    plt.tight_layout()
    plt.show()
        


##command 9 function
##Given a set of latitude and longitude from the user, find all stations within a mile square radius of that location and plot those stations on a map
def command9(dbConn):
    dbCursor = dbConn.cursor()
    latitude = input("\nEnter a latitude: ")
    latitude = float(latitude)
    if(latitude > 43.0 or latitude < 40.0):
        print("**Latitude entered is out of bounds...")
        return
    longitude = input("\nEnter a longitude: ")
    longitude = float(longitude)
    if(longitude > -87.0 or longitude < -88.0):
        print("**Longitude entered is out of bounds...")
        return
    #convert the string to an float number
    
    

    #now that we know the latitude and longitude are correct we must find the square mile radius around in and convert the four corners to lat and lon
    #this is a ist so corners[0] is up, corners[1] is down, corners[2] is left, corners[3] is right
    corners = boundaries(latitude, longitude)
    dbCursor.execute("SELECT Distinct(Stations.Station_Name), Stops.Latitude, Stops.Longitude FROM Stations JOIN Stops ON Stations.Station_ID = Stops.Station_ID WHERE Stops.Latitude BETWEEN ? AND ? AND Stops.Longitude BETWEEN ? AND ? ORDER BY Stations.Station_Name asc;", (corners[1], corners[0], corners[2], corners[3]))
    stations = dbCursor.fetchall()
    index = 0
    print("List of Stations Within a Mile")
    while(index < len(stations)):
        print("{:} : ({:}, {:})" .format(stations[index][0], stations[index][1], stations[index][2]))
        index+=1
    #now time to plot the data
    decision = input("\nPlot? (y/n) ")
    decision = decision.lower()
    if(decision != 'y'):
        return #not doing the plot
    #initialize x and y lists
    x = []
    y = []

    image = plt.imread("chicago.png")
    xydims = [-87.9277, -87.5569, 41.7012, 42.0868]
    plt.imshow(image, extent=xydims)
    plt.title("Stations near you")
    x.append(longitude);
    y.append(latitude);
    plt.plot(x, y, marker='o', linestyle=None)
#
# annotate each (x, y) coordinate with its station name:
#
    for row in stations:
        stationname = row[0];
        xposition = row[2];
        yposition = row[1];
        plt.annotate(stationname, (xposition, yposition, ))
    plt.xlim([-87.9277, -87.5569])
    plt.ylim([41.7012, 42.0868])
    plt.show()





#
##finds the boundaries of the square mile radius of a given latitude and longitude
def boundaries(lat, lon):
    deltalat = 1/69 #Each degree of latitude is approximately 69 miles so we need 1/69th for the mile radius
    deltalon = (1/69) / math.cos(math.radians(lat)) #Each degree of longitude is each degree of latitude divided by the cosine of the latitude

    # Calculate the four corners
    up = lat + deltalat
    down = lat - deltalat
    left = lon - deltalon
    right = lon + deltalon

    return up, down, left, right






##################################################################  
#
# main
#
print('** Welcome to CTA L analysis app **')
print()

dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')

print_stats(dbConn)

##reapeating loop for user input
userinput = input("Please enter a command (1-9, x to exit): ")
while(userinput != "x"):
    match userinput:
        case "1":
            command1(dbConn)
        case "2":
            command2(dbConn)
        case "3":
            command3(dbConn)
        case "4":
            command4(dbConn)
        case "5":
            command5(dbConn)
        case "6":
            command6(dbConn)
        case "7":
            command7(dbConn)
        case "8":
            command8(dbConn)
        case "9":
            command9(dbConn)
        case _:
            print("**Error, unknown command, try again...")

    userinput = input("\nPlease enter a command (1-9, x to exit): ")
# end of user input loop

    


#
# done
#
