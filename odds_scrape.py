# -*- coding: utf-8 -*-
"""
Created on Mon Dec 03 21:36:50 2018

@author: Chris
"""
import sqlite3
import os
import pandas as pd
import numpy as np
from datetime import datetime, date, time, timedelta
#time delta is the time difference...
import matplotlib.pyplot as plt
import scipy.stats as st
from scipy.stats import norm
import math
from selenium import webdriver
from time import sleep
import datetime

#NEED TO ADD BELOW TIME CODE INTO THE SQL - RECORD DATE AND TIME OF EACH ODDS CHECK
timeo = str.split(str(datetime.datetime.now()), ' ')
time2 = str.split(timeo[1], '.')
time = time2[0]
date = timeo[0]
print time
#print date


#database
os.chdir("C:\Users\Chris\.spyder\OP_sportsbetting")
conn = sqlite3.connect('scalping_data.db', timeout=10)
c = conn.cursor()
tennis= 1 #set to 0 for nba, 1 for any tennis

if tennis == 1:
    webpage = 'https://www.betfair.com.au/exchange/plus/tennis/today'
    c.execute('CREATE TABLE IF NOT EXISTS TennisTable(teamA TEXT, A_odds numeric(8,4), teamB TEXT, B_odds DECIMAL(8,4), time TEXT, date TEXT, exit_event TEXT, initial_Bodds DECIMAL(8,4), gain_loss DECIMAL(8,4), live TEXT, dollar_gain DECIMAL(8,4))')
    def new_odds_entry(teamA, A_odds, teamB, B_odds, time, date, exit_event, initial_odds, gain_loss, live, dollar_gain):
        #print "INSERT INTO stuffToPlot VALUES(%d, %s, %s)" %(year, home_team, away_team)
        c.execute("INSERT INTO TennisTable VALUES('%s', %f, '%s', %f, '%s', '%s', '%s', %f, %f, '%s', %f)" %(teamA, A_odds, teamB, B_odds, time, date, exit_event, initial_odds, gain_loss, live, dollar_gain))
        conn.commit()   #saving changes  
    table = 0
    
elif tennis == 0:           
    webpage = 'https://www.betfair.com.au/exchange/plus/basketball/competition/10547864'
    c.execute('CREATE TABLE IF NOT EXISTS oddsTable(teamA TEXT, A_odds numeric(8,4), teamB TEXT, B_odds DECIMAL(8,4), time TEXT, date TEXT, exit_event TEXT, initial_Bodds DECIMAL(8,4), gain_loss DECIMAL(8,4), live TEXT, dollar_gain DECIMAL(8,4))')
    def new_odds_entry(teamA, A_odds, teamB, B_odds, time, date, exit_event, initial_odds, gain_loss, live, dollar_gain):
        #print "INSERT INTO stuffToPlot VALUES(%d, %s, %s)" %(year, home_team, away_team)
        c.execute("INSERT INTO oddsTable VALUES('%s', %f, '%s', %f, '%s', '%s', '%s', %f, %f, '%s', %f)" %(teamA, A_odds, teamB, B_odds, time, date, exit_event, initial_odds, gain_loss, live, dollar_gain))
        conn.commit()   #saving changes    
    table = 0                      

#odds scrapy tracker

               
bet_stake = 10           #1 dollar stakes
live = 1

while 2 > 1:
    
    i = 0
    j = 10000
    #therefore i is 24 hours if pause is one minute
    
    while i < j:
        
        driver = webdriver.Chrome()
        driver.get(webpage)
        sleep(7)
    
        
        pages = driver.find_elements_by_css_selector("div.coupon-table-mod")
        #CHANGE Below to pages[0] to be live, pages[1] to 'coming up'
        if live == 1:
            page = pages[table] #this adjusts it for the sport (bball just the top, tennis is second from top)
            game_select = 0 # -2 makes it the last live game
            state = 'live'
        elif live ==0:
            page = pages[1]
            game_select = 0 #makes it the first upcoming game
            state = 'upcoming'
            
        body = page.find_elements_by_css_selector("tbody")
        body = body[0]
        games = body.find_elements_by_css_selector("tr")
        #game selection below - if you make it -2 then it will be last game in table      
        game = games[game_select]
        names = game.find_element_by_css_selector("ul.runners")
        
        team1 = names.text.splitlines()[0]
        team2 = names.text.splitlines()[1]
        prices = game.find_elements_by_css_selector("span.bet-button-price")
        #print prices[0].text
        #print prices[2].text
        teamA_odds = float(prices[0].text)
        teamB_odds = float(prices[2].text)

        
        #Making team B the underdog

        
        
        print team1, ' ', teamA_odds
        print team2, ' ', teamB_odds
        
        #NEED TO ADD BELOW TIME CODE INTO THE SQL - RECORD DATE AND TIME OF EACH ODDS CHECK
        timeo = str.split(str(datetime.datetime.now()), ' ')
        time2 = str.split(timeo[1], '.')
        time = time2[0]
        date = timeo[0]
        print time
        print date
        
        driver.close()
        driver.quit()
        
        if i == 0:
            initial_odds = teamB_odds
            initial_teamB = team2
            if initial_odds > 15:
                print 'no bet, odds too high'
                event = 'no bet'
                gain_loss = 0
                break
        if team2 != initial_teamB:
            print 'new match'
            break
        print 'initial odds: ', initial_odds, 'team B odds: ', teamB_odds
        print 'market efficiency: ', 1/teamB_odds + 1/teamA_odds
        if teamB_odds > initial_odds*3 :
            event = 'loss'
            gain_loss = float(initial_odds - teamB_odds)/float(initial_odds)
            if gain_loss < -1:
                gain_loss = -1
            dollar_gain = gain_loss
            print event
            new_odds_entry(team1, teamA_odds, team2, teamB_odds, time, date, event, initial_odds, gain_loss, state, dollar_gain)
            break 
        elif teamB_odds < initial_odds:
            event = 'gain'
            gain_loss = float(initial_odds - teamB_odds)/float(initial_odds)
            dollar_gain = gain_loss
            print event
            new_odds_entry(team1, teamA_odds, team2, teamB_odds, time, date, event, initial_odds, gain_loss, state, dollar_gain)
            break
        else:
            event = 'no exit'
            gain_loss = float(initial_odds - teamB_odds)/float(initial_odds)
            dollar_gain = 0
            #print gain_loss
            print event
            new_odds_entry(team1, teamA_odds, team2, teamB_odds, time, date, event, initial_odds, gain_loss, state, dollar_gain)
                    

        #sleep(42)
        #Running profit listed below
        conn = sqlite3.connect('scalping_data.db')
        c = conn.cursor()
        
        if tennis == 1:
            c.execute("SELECT * FROM TennisTable")
        elif tennis == 0:
            c.execute("SELECT * FROM oddsTable")
        all_data = c.fetchall()
        
        j = 0
        all_profits = []
        for row in all_data:
            instance_profit = all_data[j][-1]
            all_profits.append(instance_profit)  
            j += 1
        
        total_profit = 0 
        for row in all_profits:
            total_profit += row
        
        print 'Total profit: $', total_profit*bet_stake

        print ' ' 
        i += 1
        

#MAIN NEXT STEP IS TO MAKE IT SO TENNIS ALWAYS SELECTS THE 'IN-PLAY' OPTIONS AUTOMATICALLY (and BBall I guess)


# Could then work out how to text it to myself


# range trading - lock in gain then place new bet on when it goes back up to initial level