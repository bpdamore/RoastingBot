#### CREATED BY BRANDON DAMORE 2020 ####
#### github.com/bpdamore ####

run = "yes"
while run == "yes":
    # Import dependencies for printing / moving files
    import os
    import time
    from bs4 import BeautifulSoup as Soup
    import webbrowser
    import time
    from splinter import Browser
    from sys import platform
    from datetime import datetime
    import pandas as pd
    import ezgmail

    # from utils import RoastingBot
    from config import *

    # Import G-sheet stuff
    import gspread
    from  oauth2client.service_account import ServiceAccountCredentials
    
    now = datetime.now()
    
    hour = now.strftime("%H")
    
    if hour == "06":
        
        print(f"\nIT'S {hour}!!\nIT'S TIME TO GOOOOOOOOOOOOOOOOOOOOOOOOOO")
    
        if platform == "win32":
            executable_path = {'executable_path': 'chromedriver.exe'}
            browser = Browser('chrome', **executable_path, headless=False)
            
        elif platform =="linux":
            browser = Browser('firefox', profile=r'/home/pi/.mozilla/firefox/yswkhxkr.default')

        url = "https://685897.app.netsuite.com/app/common/search/searchresults.nl?searchid=954&whence="
        browser.visit(url) 

        user = "input[id='userName']"
        pw = "input[id='password']"
        sub = "button[id='login-submit']"

        print("\nwaiting to load ... ")
        time.sleep(20)

        fuser = browser.find_by_tag(user)
        fuser.fill(netUser)
        fpw = browser.find_by_tag(pw)
        fpw.fill(netPass)
        fsub = browser.find_by_tag(sub).click()

        ques = "input[name='answer']"

        print("\nwaiting to load ... ")
        time.sleep(20)

        try:
            if "In what city did you meet your spouse/significant other?" in browser.html:
                fques = browser.find_by_tag(ques)
                fques.fill(meetPass)    
            elif "What street did you live on when you were 10 years old?" in browser.html:
                fques = browser.find_by_tag(ques)
                fques.fill(streetPass) 
            elif "What is the name of the place your wedding reception was held?" in browser.html:
                fques = browser.find_by_tag(ques)
                fques.fill(marryPass)

            time.sleep(20)

            quesSub = "input[type='submit']"
            fquesSub = browser.find_by_tag(quesSub).click()

        except:
            pass

        print("\nwaiting to load ... ")
        time.sleep(20)

        button = "div[title='Export - CSV']"
        fbutton = browser.find_by_tag(button).click()

        print("\nWaiting for the download to complete...")
        time.sleep(20)

        browser.quit()

        # Get that G-Sheet query up and running
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
        client = gspread.authorize(creds)

        time.sleep(20)
            
        # Completely rewrite the sheet
        # The WMS sheet will always reference the data on this sheet, so it's fine to overwrite it
        sheet = client.open('BinData')
        
        print("\nAdding to sheet")

        if platform == "wind32":
            os.chdir("/Users/brand/Downloads/")

        elif platform == "linux":
            os.chdir("/home/pi/Downloads/")
            
        for f in os.listdir():
            df = pd.read_csv(f)
            sortdf = df.sort_values(['Bin Number'])
            sortdf.to_csv("../Documents/RBCCo/binData/data.csv")

            time.sleep(2)

            os.remove(f)
            
        os.chdir("/home/pi/Documents/RBCCo/binData/")
        with open("data.csv", "r", encoding="UTF-8") as bins:
            content = bins.read()
            client.import_csv(sheet.id, data=content.encode("UTF-8"))
            
        os.remove('data.csv')

        print("\nFinished!")
        time.sleep(3600)

        ezgmail.init()
        ezgmail.send('brandon@dw-collective.com','BinData Updated', 'The bin data was updated! ')
        
    else:
        print(f"\nIt's not the right time\n The hour is {hour}")
        
        time.sleep(3600)
