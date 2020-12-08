# Name: David Lee
# Purpose: This program imports data from csv files into a pandas dataframe and cleans any
# corrupted data into randomly generated information based on given constraints. This cleaned
# data is then inserted into a sql database. Then relevant information is calculated and pulled
# from the database based on user input via sql commands.

import pandas as pd
import pymysql as pymysql

from creds import *
from files import *
from cleaning import *
from init_sql import extract_init_sql

print("Beginning import")
Housing = pd.read_csv(housingFile, ",")
Income = pd.read_csv(incomeFile, ",")
Zip = pd.read_csv(zipFile, ",")

# Dictionary holding the unique guis with the randomly generated new zip codes for previously corrupted zip codes
auto_zip = {}

try:
    myConnection = pymysql.connect(host=hostname,
                                   user=username,
                                   password=password,
                                   db=database,
                                   charset='utf8mb4',
                                   cursorclass=pymysql.cursors.DictCursor)

except Exception as e:
    print(f"An error has occurred.  Exiting: {e}")
    print()
    exit()

# Run init sql file
try:
    init_list = extract_init_sql()
    with myConnection.cursor() as cursor:
        for cmd in init_list:
            cursor.execute(cmd)
            myConnection.commit()


except Exception as e:
    print(f"An error has occurred.  Exiting: {e}")
    print()
    exit()

## Fix Housing File
print("Cleaning Housing File data")
Housing, auto_zip = clean_housing(Housing, Zip, auto_zip)

sql_insert_housing = """INSERT INTO housing (guid, zip_code, median_age, total_rooms, 
total_bedrooms, population, households, median_house_value, county, city, state, median_income) 
Values(%s, %s,%s,%s,%s,%s,%s,%s,%s, %s, %s, %s)"""
try:
    count = 0
    with myConnection.cursor() as cursor:
        for i in range(len(Housing)):
            data = (str(Housing.iloc[i,0]), int(Housing.iloc[i,1]), int(Housing.iloc[i,2]),
                           int(Housing.iloc[i,3]), int(Housing.iloc[i,4]), int(Housing.iloc[i,5]), int(Housing.iloc[i,6]),
                           int(Housing.iloc[i,7]), '', '', '', 0)
            cursor.execute(sql_insert_housing, data)
            myConnection.commit()
            count += 1
    print(f"{count} records imported into the database")
except Exception as e:
    print(f"An error has occurred.  Exiting: {e}")
    print()
    exit()

## Clean Income File
print("Cleaning Income File data")
Income = clean_income(Income, auto_zip)
sql_insert_income = """UPDATE housing SET zip_code = %s, median_income = %s WHERE guid = %s"""

try:
    count = 0
    with myConnection.cursor() as cursor:
        for i in range(len(Income)):
            data = (int(Income.iloc[i,1]), int(Income.iloc[i,2]), str(Income.iloc[i,0]))
            cursor.execute(sql_insert_income, data)
            myConnection.commit()
            count += 1
    print(f"{count} records imported into the database")
except Exception as e:
    print(f"An error has occurred.  Exiting!: {e}")
    print()
    exit()


## Clean Zip File
print("Cleaning ZIP File data")
Zip = clean_zip(Zip, auto_zip)

sql_insert_zip = """UPDATE housing SET zip_code = %s, city = %s, state = %s, county = %s WHERE guid = %s"""

try:
    count = 0
    with myConnection.cursor() as cursor:
        for i in range(len(Zip)):
            data = (int(Zip.iloc[i,1]), str(Zip.iloc[i,2]), str(Zip.iloc[i,3]), str(Zip.iloc[i,4]), str(Zip.iloc[i,0]))
            cursor.execute(sql_insert_zip, data)
            myConnection.commit()
            count += 1
    print(f"{count} records imported into the database")
except Exception as e:
    print(f"An error has occurred.  Exiting: {e}")
    print()
    exit()

print("\nBeginning validation\n")


# Below two sql commands sourced from Mr. Kenneth Holm
roomSql = """select

    sum(total_rooms)

    from

    housing

    where

    total_rooms > %s

"""
incomeSql = """select

    format(round(avg(median_income)),0)

    from

    housing

    where

    zip_code = %s

"""

try:
    # Asking user for how many rooms
    rslt = 0
    num_rooms = input("Total Rooms: ")
    if not num_rooms.isdigit():
        print("Invalid number of rooms. Input must be a non-negative integer.")
    else:
        with myConnection.cursor() as cursor:
            cursor.execute(roomSql, int(num_rooms))
            for row in cursor:
                rslt = row['sum(total_rooms)']
            myConnection.commit()
        if rslt == None:
            rslt = 0
        print(f"For locations with more than {num_rooms} rooms, there are a total of {rslt} bedrooms.\n")

    # Asking user for zip code
    input_zip = input("ZIP code: ")
    if not input_zip.isdigit():
        print("Invalid ZIP code. Zip code must be an integer value.")
    elif len(input_zip) != 5:
        print("Invalid ZIP code. ZIP code must be exactly 5 integers long.")
    else:
        with myConnection.cursor() as cursor:
            cursor.execute(incomeSql, int(input_zip))
            for row in cursor:
                rslt = row["format(round(avg(median_income)),0)"]
            myConnection.commit()
        if rslt == None:
            print(f"No ZIP code corresponding to {input_zip} in database.")
        else:
            print(f"The median household income for ZIP code {input_zip} is {rslt}.")

except Exception as e:
    print(f"An error has occurred.  Exiting: {e}")
    print()
finally:
    print()
    print("Program exiting.")
    myConnection.close()
