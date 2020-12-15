def TradeScraper(sender):
    import os,time,webbrowser,time,re,ezgmail,json,gspread
    from bs4 import BeautifulSoup as Soup
    from splinter import Browser
    from sys import platform
    from datetime import datetime, date
    import pandas as pd
    from selenium.webdriver.common.keys import Keys
    from  oauth2client.service_account import ServiceAccountCredentials
    from config import tuser,tpass
    import re

    #### UNCOMMENT WHEN YOU WANT TO AUTOMATE EVERYTHING ####
    # batchnum = re.compile(r'Batch #(\d+) -')

    # if platform == "win32":
    #     executable_path = {'executable_path': 'chromedriver.exe'}
    #     browser = Browser('chrome', **executable_path, headless=False)

    # elif platform == "linux":
    #     browser = Browser('firefox', profile=r'/home/pi/.mozilla/firefox/hmwq79bz.default-esr')

    # url = "https://beta.roasters.drinktrade.com/"
    # browser.visit(url)

    # time.sleep(3)

    # html = browser.html

    # if "Login | Trade" in html:
    #     user = "input[id='admin_user_email']"
    #     pw = "input[id='admin_user_password']"
    #     sub = "input[type='submit']"
    #     # Log in
    #     truser = browser.find_by_tag(user)
    #     truser.fill(tuser)
    #     trpw = browser.find_by_tag(pw)
    #     trpw.fill(tpass)
    #     trsub = browser.find_by_tag(sub).click()
    #     time.sleep(4)

    # accept = "button[id='accept-roasts']"
    # taccept = browser.find_by_tag(accept).click()
    # time.sleep(2)

    # browser.find_by_text("OK").click()
    # time.sleep(4)

    # # input("Press enter ")

    # # Download the batch details for the google sheet
    # browser.find_by_xpath("/html/body/div[1]/div[4]/div[1]/div/div[2]/div[1]/div/div/div[1]/h3").click()
    # time.sleep(5)

    # # Get the file name through regex
    # html = browser.html
    # fname = "batch_"
    # batch = str(batchnum.search(html).group(1))
    # fname +=batch

    ###################################

    # Find the file and load into a df
    os.chdir("trade")
    for f in os.listdir():
        trade_df = pd.read_csv(f)
        os.remove(f)

    os.chdir("../")

    # Get the necessary details out
    trade_df = trade_df[["product_name","grind", "grind_type" ,"quantity"]]

    with open("CoffeeSku.json","r") as f:
        sku = json.load(f)
    time.sleep(1)

    today = {}
    print("\n-----------------\nFormatting csv...")
    for i,row in trade_df.iterrows():
        # Check looks to see if there was a match
        check = 0
        for x in sku:
            # If there was a match, skip. Otherwise, go on and look for a match.
            if check == 1:
                pass
            else:
                if x in row["product_name"]:
                    coffee = f'{row["product_name"]}-{row["grind_type"]}'
                    cSKU = sku[x]+"12OZ"+row["grind"]
                    if coffee in today:
                        today[coffee][0] += int(row["quantity"])
                    else:
                        today[coffee] = [int(row["quantity"]), cSKU]
                    check = 1
                else:
                    pass
        if check == 0:
            coffee = f'{row["product_name"]}-{row["grind_type"]}'
            cSKU = "NEEDS SKU"
            if coffee in today:
                today[coffee][0] += int(row["quantity"])
            else:
                today[coffee] = [int(row["quantity"]), cSKU]

    time.sleep(2)

    # ezgmail.send(sender,"Subby CSV","Hiya! \n\nHere's the csv for today's trade batch! Enjoy!\n\nLove, \n\n<3 RBCCo",[trade_csv])

    time.sleep(5)
    os.remove(trade_csv)

    rows = []
    tdate = date.today()
    for x in today:
        rows.append(["y",today[x][1], "TRADE - Automated", str(tdate), x, int(today[x][0])])
        # rows.append([today[x][1], "TRADE - Automated", str(tdate), x, int(today[x][0])])

    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)

    ### NEW SHEET ###
    sheet = client.open('Roast Sheet 2.4.7')
    # start = "A"+str(len(sheet.worksheet('Subs').col_values(1))+1)
    start = "A"+str(len(sheet.worksheet('tester').col_values(1))+1)
    sheet.values_update('tester!'+start,params={'valueInputOption':'USER_ENTERED'},body={'values':rows})

    ezgmail.send(sender,"Subbys Are Posted!", "Hey!\nSorry I took a while...I'm done though!!\nI can't send you the print files, but the subs are good to go!\nsowwy :(\n\nLove, \n\n<3 RBCCo")
    #################

    # Old Sheeet #####################
    # sheet = client.open('Roast Sheet 2.4.7')
    # start = "A"+str(len(sheet.worksheet('Subscriptions').col_values(1))+1)
    # sheet.values_update('Subscriptions!'+start,params={'valueInputOption':'USER_ENTERED'},body={'values':rows})
    ##################################


    # # Wait for the various packing slips to load
    # dl = "no"

    # # time.sleep(120)
    # # browser.reload()

    # while dl == "no":
    #     try:
    #         time.sleep(2)
    #         browser.find_by_xpath("//*[@id='main_content']/div[2]/div[1]/div/div/div/div/div[2]/div/ul[1]/li/a").click()
    #         time.sleep(2)
    #         browser.find_by_xpath("//*[@id='main_content']/div[2]/div[1]/div/div/div/div/div[2]/div/ul[2]/li[1]/a").click()
    #         time.sleep(2)
    #         browser.find_by_xpath("//*[@id='main_content']/div[2]/div[1]/div/div/div/div/div[2]/div/ul[3]/li[1]/a").click()
    #         dl = "yes"
    #         time.sleep(120)
    #     except:
    #         time.sleep(120)
    #         browser.reload()

    # att = []
    # os.chdir("../../Downloads")
    # time.sleep(2)
    # for f in os.listdir():
    #     if ".pdf" in f:
    #         print(f)
    #         att.append(f"../../Downloads/{f}")
    # os.chdir("../Documents/RBCCo")
    # ezgmail.send(sender,"Subscription Printies","Hey here are all the things to print!\n\nI hope it works because it hasn't the last few times! \n\nLove, \n\n<3 RBCCo",att)
    # time.sleep(30)
    # for x in att:
    #     os.remove(x)

if __name__ == "__main__":
    TradeScraper("brandon@dw-collective.com")