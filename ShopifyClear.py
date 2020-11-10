def cleanShop():
    """
    README PLZ
    This should be pretty straighforward with all my comments, but still. 

    When you want to insert multiple cells, it needs to be in a list of lists form. 
    [[A1,B1,C1],[A2,B2,C2,D2],[A3,B3]]
    ^^ Each list inside of the big list is a row. The big list is the sheet range.
    That's why the rcz variable is a giant list of lists. It's only impacting one col, but a bunch of rows.  
    """
    import os, time, webbrowser, requests, gspread
    from datetime import datetime
    from bs4 import BeautifulSoup as Soup
    from  oauth2client.service_account import ServiceAccountCredentials
    from config import key, password, hostname, version, emPass
    from pprint import pprint

    mon = datetime.today().month
    day = datetime.today().day
    td = f"{mon}-{day}"
    # Build the query
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)

    # Choose the sheet/worksheet that you will be working on
    # sheet = client.open("test").worksheet(ws)
    sheet = client.open('Roast Sheet 2.4.7')
    # Pull col A in the grocery tab
    grocvals = sheet.worksheet('Grocery').col_values(1)
    # Clear out all Shopify orders
    sheet.values_clear('Shopify!A4:F')

    # Clear out the Roast Sheet
    rsz = [[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0]]
    # Clears the Manual Add section, and then the Lbs Roasted section
    sheet.values_update('Roast Sheet!C4:C50',params={'valueInputOption':'USER_ENTERED'},body={'values':rsz})
    sheet.values_update('Roast Sheet!D4:D50',params={'valueInputOption':'USER_ENTERED'},body={'values':rsz})
    # Clears the Total Blended section
    sheet.values_update('Roast Sheet!C53:C54',params={'valueInputOption':'USER_ENTERED'},body={'values':[[0],[0]]})

    # Clear out the Roast Calculator
    rcz = [[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],['Manual Lbs'],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0]]
    # Clears the values while also putting the header in there
    sheet.values_update('Roast Calculator!I2:I55',params={'valueInputOption':'USER_ENTERED'},body={'values':rcz})
    sheet.values_update('Roast Calculator!K2:K55',params={'valueInputOption':'USER_ENTERED'},body={'values':rcz})

    # Date the queued grocery rows. 
    x = 4
    # Iterate through col A, if there's a y, put today's date in
    while x < len(grocvals):
        if grocvals[x] == 'y':
            grocvals[x] = td
        x+=1
    # Now make a list of lists so we can throw it into the sheet. 
    grocval = []
    for x in grocvals:
        grocval.append([x])
    
    sheet.values_update('Grocery!A:A', params={'valueInputOption':'USER_ENTERED'},body={'values':grocval})

if __name__ == "__main__":
    cleanShop()
