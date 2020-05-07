import pandas as pd
from datetime import datetime
import database

def main():
    # connecting to database
    conn = database.database_connect()

    # Interface starts:
    print("Welcome to Database Course Project !!!")
    print("This project explores data on terrorist attack information and stock price from YEAR 1970 to YEAR 1990.")

    # Q1. Input a country name to see attack details:
    print("Step 1: Please input a country name to check attack details:")
    print("e.g. United States, United Kindom, Japan, Mexico, Italy.")    
    while(True):
        input_country = input('Enter the country name => ')
        country = database.valid_country_list(conn)
        if (input_country in country):
            data1 = database.count_country_attack(conn, input_country)
            df = pd.DataFrame(data1, columns=['Country', 'Year (Starts from Jan 01)', 'Total Attacks', 'Total Killed'])
            print(df)
            print()
            break 
        else:
            print("Enter a valid country or check your spelling, please")
            print()
    
    input('Hit keyboard to continue => ')
    
    # Q2. Show top 10 countries in terrorist attacks:
    print("Step 2. Show the top 10 countries in terrorist attack numbers from 1970 to 1990: ")
    rows = database.country_attack_summary(conn)
    ten_countries = []
    for r in rows:
        ten_countries.append(r[0])
    year = []
    total_attack = []
    for r in ten_countries:
        temp = database.count_country_attack(conn, r)
        temp_year = [r[1] for r in temp]
        temp_attack_number = [r[2] for r in temp]
        year.append(temp_year)
        total_attack.append(temp_attack_number)
    database.plot_country_attack(total_attack, year, ten_countries)
    print("Close graph to continue")
    input('Hit keyboard to continue => ')
    
# Q3. Relation between number of attacks in US and NASDAQ price:
    print("Step 3: Check the relationship between number of attacks in US and NASDAQ price in ONE year:")
    while(True):
        input_year = input('Enter YEAR => ')
        if (int(input_year) > 1990 or int(input_year) < 1970):
            print("Enter a valid year or check your spelling, please")
            print()
        else:
            year_start = datetime.strptime(input_year, '%Y')
            year_end = datetime.strptime(str(int(input_year)+1), '%Y')
            nasdaq = [r[1] for r in database.nasdaq_year(conn,year_start, year_end)]
            month = [r[0] for r in database.nasdaq_year(conn, year_start, year_end)]
            us_attack = [r[2] for r in database.count_US_attack(conn, year_start, year_end)]
            month_attack = [r[1] for r in database.count_US_attack(conn, year_start, year_end)]
        
            # Case 1: There were attacks every month in that year:
            if len(month_attack) == 12:
                database.plot_nasdaq_US_attack(conn, month, us_attack, nasdaq)
        
            # Case 2: There were months where no attacks happened:
            else:
                us_attack_special = []
                # Use a month_tmp container to add 0's into the list of attack numbers:
                month_tmp = [r.month for r in month_attack]
        
                index = 0
                m = 1
                while(len(us_attack_special) < 11):
                    if(month_tmp[index] != m):
                        us_attack_special.append(0)
                        m = m + 1
                    else:
                        us_attack_special.append(us_attack[index])
                        m = m + 1
                        index = index + 1
                if (len(us_attack_special) < 12):
                    us_attack_special.append(0)
                database.plot_nasdaq_US_attack(conn, month, us_attack_special, nasdaq)
            break
        
    print("Close graph to continue")
    input('Hit keyboard to continue => ')

    # Q4. Check the TOP 5 most frequent terrorist attacks worldwide from 1970 to 1990:
    print("Step 4: Now we will tell you the 5 most frequent types of terrorist attack that happened between 1970 to 1990: ")
    data2 = database.attack_type_summary(conn)
    df = pd.DataFrame(data2, columns=['Attack Type', 'Total Attacks'])
    print(df)
    print()
    input('Hit keyboard to continue => ')

    # Q5. Check the TOP 5 targets most frequently attacked by terrorists worldwide from 1970 to 1990:
    print("Step 5: Now we will tell you the TOP 5 target types most frequently attacked between 1970 to 1990:")
    data3 = database.attack_target_summary(conn)
    df = pd.DataFrame(data3, columns=['Attack Target', 'Total Attacks'])
    print(df)
    print()
    input('Hit keyboard to continue => ')

    # Q6. Create cross-tabling to explore relationship between target type and attack type:
    print("Step 6: Now we will use cross-tabbing to help you understand how target types and attack types are related !")
    data4 = database.cross_tabbing(conn)
    df = pd.DataFrame(data4, columns=["Attack Type", "Business", "Private Citizens & Property", "Military", "Government (General)", "Police"])
    print(df)
    print()
    input('Thank you!!! Hit keyboard to end => ')

if __name__ == "__main__":
    main()
