import psycopg2
import psycopg2.extras
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import matplotlib.dates as dates
from decimal import Decimal
from datetime import datetime

pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)

def database_connect():
    connection_string = "host='localhost' dbname='dbms_final_project' user='dbms_project_user' password='dbms_password'"
    conn = psycopg2.connect(connection_string) 
    return conn

def valid_country_list(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT distinct country from attack_location")
    ret = cursor.fetchall();
    country = [r[0] for r in ret]
    return country

# Query to count the numbers of attacks happened in a country defined by user:
def count_country_attack(conn, country):
    cursor = conn.cursor()
    query1 = ''' 
    DROP TABLE IF EXISTS ret CASCADE; 
    SELECT country, date_trunc('year', date) as year, count(*) AS total_attacks, sum(number_killed) AS total_killed
    INTO TEMP TABLE ret
    FROM attack_data, attack_location, attacks
    WHERE attack_data.attackid = attack_location.attackid 
    AND attack_data.attackid = attacks.attackid 
    AND date > date '1970-01-01'
    AND date < date '1991-01-01'    
    GROUP BY country, date_trunc('year', date)
    ORDER BY country, date_trunc('year', date)
    '''
    cursor.execute(query1)
    query2 = '''
    SELECT country, year, total_attacks, total_killed
    FROM ret
    WHERE country = %s
    '''
    cursor.execute(query2, (country,))
    rows = cursor.fetchall();

    return rows

# Function to plot TOP-10 countries in number
def plot_country_attack(total_attack, year, country):
    fig, ax1 = plt.subplots(figsize=(20, 6))
    years = mdates.YearLocator()
    months = mdates.MonthLocator()
    yearsFmt = mdates.DateFormatter('%Y')
    ax1.xaxis.set_major_locator(years)
    ax1.xaxis.set_major_formatter(yearsFmt)
    ax1.xaxis.set_minor_locator(months)

    for i in range(len(total_attack)):
        plt.plot(year[i], total_attack[i], label=country[i])
        plt.legend()
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Total Attacks')
        ax1.set(ylim=(0, 800))
    plt.title('10 Countries with the Most Terrorist Attacks')
    plt.show()

def country_attack_summary(conn):
    cursor = conn.cursor()
    query3 = '''
    DROP TABLE IF EXISTS ret CASCADE;
    SELECT country, date_trunc('year', date) as year, count(*) AS total_attacks, sum(number_killed) AS total_killed
    INTO TEMP TABLE ret
    FROM attack_data, attack_location, attacks
    WHERE attack_data.attackid = attack_location.attackid 
    AND attack_data.attackid = attacks.attackid 
    AND date > date '1970-01-01'
    AND date < date '1991-01-01'    
    GROUP BY country, date_trunc('year', date)
    ORDER BY country, date_trunc('year', date)    
    '''
    cursor.execute(query3)

    query4 = '''
    SELECT country, sum(total_attacks) AS SUMofATTACK
    FROM ret
    GROUP BY country
    ORDER BY SUMofATTACK DESC
    LIMIT 10
    '''
    cursor.execute(query4)
    rows = cursor.fetchall();
    return rows

def count_US_attack(conn, year_start, year_end):
    cursor = conn.cursor()
    query5 = ''' 
    DROP TABLE IF EXISTS ret CASCADE;
    SELECT country, date_trunc('month', date) as year, count(*) AS total_attacks, sum(number_killed) AS total_killed
    INTO TEMP TABLE ret
    FROM attack_data, attack_location, attacks
    WHERE attack_data.attackid = attack_location.attackid
    AND country = 'United States'
    AND attack_data.attackid = attacks.attackid 
    AND date > %s
    AND date < %s   
    GROUP BY country, date_trunc('month', date)
    ORDER BY country, date_trunc('month', date)
    '''
    cursor.execute(query5, (year_start, year_end,))

    query6 = '''
    SELECT country, year, total_attacks, total_killed
    FROM ret
    '''
    cursor.execute(query6)
    rows = cursor.fetchall();
    return rows

def nasdaq_year(conn, year_start, year_end):
    cursor = conn.cursor()
    query7 = '''
    SELECT date_trunc('month',trade_date) as month, sum(adj_close * volume)/ sum(volume) AS weight_avg
    FROM company_information, historical_stock_prices
    WHERE exchange = 'NASDAQ' AND company_information.ticker = historical_stock_prices.ticker
    AND trade_date > %s AND trade_date < %s
    GROUP BY date_trunc('month',trade_date)
    ORDER BY date_trunc('month',trade_date);
    '''
    cursor.execute(query7, (year_start, year_end,))
    rows = cursor.fetchall();
    return rows

def plot_nasdaq_US_attack(conn, month, us_attack, nasdaq):
    fig, ax1 = plt.subplots(figsize=(16, 4))
    months = mdates.MonthLocator()
    monthsFmt = mdates.DateFormatter('%m')
    ax1.xaxis.set_major_locator(months)
    ax1.xaxis.set_major_formatter(monthsFmt)
    plt.plot(month, us_attack, label ='Numer of Attack in US', color='aquamarine')
    plt.legend(loc="upper right")
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Total Attacks')
    ax1.set(ylim=(0, 70))

    months = mdates.MonthLocator()
    monthsFmt = mdates.DateFormatter('%m')
    ax2 = ax1.twinx()
    ax2.xaxis.set_major_locator(months)
    ax2.xaxis.set_major_formatter(monthsFmt)

    plt.plot(month, nasdaq, label ='NASDAQ Volume Weighted Average Price (VWAP)', color='paleturquoise')
    plt.legend(loc="lower left")
    ax2.set_xlabel('Month')
    ax2.set_ylabel('NASDAQ VWAP')
    ax2.set(ylim=(0, 5))
    plt.title('Relation of Terrorist Attacks in US with NASDAQ Price \n(Color from Animal Crossing)')
    plt.show()

def attack_target_summary(conn):
    cursor = conn.cursor()
    query8 = '''
    DROP TABLE IF EXISTS ret CASCADE;
    SELECT target_type, count(*) AS total_attacks, sum(number_killed) AS total_killed
    INTO TEMP TABLE ret
    FROM attack_data, attack_location, attacks
    WHERE attack_data.attackid = attack_location.attackid 
    AND attack_data.attackid = attacks.attackid  
    GROUP BY target_type
    ORDER BY total_attacks 
    '''
    cursor.execute(query8)

    query9 = '''
    SELECT target_type, sum(total_attacks) AS SUMofATTACK
    FROM ret
    GROUP BY target_type
    ORDER BY SUMofATTACK DESC
    LIMIT 5
    '''
    cursor.execute(query9)
    rows = cursor.fetchall();
    return rows

def attack_type_summary(conn):
    cursor = conn.cursor()
    query10 = '''
    DROP TABLE IF EXISTS ret CASCADE;
    SELECT attack_type, count(*) AS total_attacks, sum(number_killed) AS total_killed
    INTO TEMP TABLE ret
    FROM attack_data, attacks
    WHERE attack_data.attackid = attacks.attackid  
    GROUP BY attack_type
    ORDER BY total_attacks    
    '''
    cursor.execute(query10)

    query11 = '''
    SELECT attack_type, sum(total_attacks) AS SUMofATTACK
    FROM ret
    GROUP BY attack_type
    ORDER BY SUMofATTACK DESC
    LIMIT 5
    '''
    cursor.execute(query11)
    rows = cursor.fetchall();
    return rows

def cross_tabbing(conn):
    cursor = conn.cursor()
    query11 = '''
    CREATE EXTENSION IF NOT EXISTS tablefunc;
    SELECT * 
    FROM crosstab(
    'select attack_type,target_type, count(*) as total_attack
    from attack_data, attack_location
    where attack_data.attackid = attack_location.attackid
    and (attack_type = ''Bombing/Explosion'' or attack_type = ''Armed Assault''
    or attack_type = ''Assassination'' or attack_type = ''Facility/Infrastructure Attack''
    or attack_type = ''Hostage Taking (Kidnapping)'')
    and (target_type = ''Business'' or target_type = ''Private Citizens & Property''
    or target_type = ''Military'' or target_type = ''Government (General)''
    or target_type = ''Police'')
    group by target_type, attack_type
    order by 1,2') 

    AS ct(attack_type varchar(255), "Business" bigint, "Private Citizens & Property" bigint,
    "Military" bigint, "Government (General)" bigint, "Police" bigint);
    '''
    cursor.execute(query11)
    rows = cursor.fetchall();
    return rows
