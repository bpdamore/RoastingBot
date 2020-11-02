#### CREATED BY BRANDON DAMORE 2020 ####
#### github.com/bpdamore ####

# Make it a constant loop
run = "yes"
while run == "yes":
    # Put in a try/except to catch and email error while still running the next day. 
    try:
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
        import re
        from selenium.webdriver.common.keys import Keys

        # from utils import the various creds
        from config import *

        # Import G-sheet stuff
        import gspread
        from  oauth2client.service_account import ServiceAccountCredentials
        
        # What time is it?
        now = datetime.now()
        hour = now.strftime("%H")
        
        # The hour needs to be in %H%H format
        if hour == "04":
            
            print(f"\nIT'S {hour}!!\nIT'S TIME TO GOOOOOOOOOOOOOOOOOOOOOOOOOO")
        
            # Is it running on my work computer or RoastingBot?
            if platform == "win32":
                executable_path = {'executable_path': 'chromedriver.exe'}
                browser = Browser('chrome', **executable_path, headless=False)
                
            elif platform =="linux":
                browser = Browser('firefox', profile=r'/home/pi/.mozilla/firefox/yswkhxkr.default')

            # Go directly to the search
            url = "https://685897.app.netsuite.com/app/common/search/searchresults.nl?searchid=954&whence="
            browser.visit(url) 

            # Need to log in, so do it
            user = "input[id='userName']"
            pw = "input[id='password']"
            sub = "button[id='login-submit']"
            clicky = "span[role='checkbox']"

            print("\nwaiting to load ... ")
            time.sleep(20)

            fuser = browser.find_by_tag(user)
            fuser.fill(netUser)
            fpw = browser.find_by_tag(pw)
            fpw.fill(netPass)
            fsub = browser.find_by_tag(sub).click()

            ques = "input[name='answer']"

            print("\nLogging in ... ")
            time.sleep(20)

            # Check to see if security questions are needed
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

            # Check for 2 factor authorization
            try:
                if "A message containing a verification code" in browser.html:
                    place = 'input[placeholder="6-digit code"]'
                    ezgmail.init()
                    time.sleep(2)
                    unread = ezgmail.unread()
                    for email in unread:
                        subj = email.messages[0].subject
                        if "New text message from 74005" in subj:
                            num = len(email.messages)
                            body = email.messages[num-1].body
                            digitz = re.compile(r'\d+')
                            code = digitz.search(body)
                            code = str(code.group())
                            print(f"\nCopied code {code}!")
                            email.markAsRead()
                    clickyclicky = browser.find_by_tag(clicky).click()
                    codeplace = browser.find_by_tag(place)
                    codeplace.fill(code)
                    active_web_element = browser.driver.switch_to.active_element
                    active_web_element.send_keys(Keys.ENTER) 

                    time.sleep(10)

            except:
                pass

            print("\nLoading the search ... ")
            time.sleep(20)

            button = "div[title='Export - CSV']"
            fbutton = browser.find_by_tag(button).click()

            print("\nClicked the button ...")

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
            
            print("\nAdding to sheet ...")

            if platform == "win32":
                os.chdir("/Users/brand/Downloads/")

            elif platform == "linux":
                os.chdir("/home/pi/Downloads/")
                
            for f in os.listdir():
                df = pd.read_csv(f)
                sortdf = df.sort_values(['Bin Number'])
                sortdf.to_csv("../Documents/RBCCo/binData/data.csv")

                time.sleep(2)

                os.remove(f)
                
            os.chdir("../Documents/RBCCo/binData/")
            with open("data.csv", "r", encoding="UTF-8") as bins:
                content = bins.read()
                client.import_csv(sheet.id, data=content.encode("UTF-8"))
                
            os.remove('data.csv')

            print("\nFinished!")

            os.chdir("../")
            ezgmail.init()
            ezgmail.send('brandon@dw-collective.com','BinData Updated', 'The bin data was updated! \n\nI did it! Yay! \n\nLove,\n- RBCCo <3')

            time.sleep(3600)
            
        else:
            print(f"\nIt's not the right time\n The hour is {hour}")
            
            time.sleep(3600)

    except Exception as exp:
        # If there's an error, send an email with the error, then sleep for an hour. 
        import ezgmail
        import time
        print(f"\nThere was an error! \n\n{type(exp).__name__}\n{exp}")
        ezgmail.send('brandon@dw-collective.com', 'binUpdate Error!', f'Whoopsy! Looks like there was an error. \n\n Here it is! \n\n{type(exp).__name__}\n{str(exp)}\n\nLove,\n- RBCCo <3')
        time.sleep(3600)