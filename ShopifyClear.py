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
    # Pull all values from Shopify
    shopvals = sheet.values_get(range="Shopify!A4:F")['values']

    # Clear out all Shopify orders
    shopval = []
    # Save any row that has plz in the F col
    for x in shopvals:
        try: 
            if x[5].lower() == "plz":
                shopval.append(x)
        except IndexError:
            pass
    # To clear out the rest of the orders, we need the same number of blank rows.
    while len(shopval) < len(shopvals):
        shopval.append(['','','','','',''])
    
    sheet.values_update('Shopify!A4:F', params={'valueInputOption':'USER_ENTERED'},body={'values':shopval})

    # Clear out the Roast Sheet
    rsz = [[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0]]      
    # Clears the Manual Add section, and then the Lbs Roasted section
    sheet.values_update('Roast Sheet!C5:C51',params={'valueInputOption':'USER_ENTERED'},body={'values':rsz})
    sheet.values_update('Roast Sheet!D5:D51',params={'valueInputOption':'USER_ENTERED'},body={'values':rsz})
    # Clears the Total Blended section
    sheet.values_update('Roast Sheet!C54:C55',params={'valueInputOption':'USER_ENTERED'},body={'values':[[0],[0]]})

    # Clear out the Roast Calculator
    rcz = [[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],['Manual Lbs'],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0]]
    rcr = [[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],['Roasted On Hand'],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0]]
    # Clears the values while also putting the header in there
    sheet.values_update('Roast Calculator!J2:J56',params={'valueInputOption':'USER_ENTERED'},body={'values':rcz})
    sheet.values_update('Roast Calculator!L2:L56',params={'valueInputOption':'USER_ENTERED'},body={'values':rcr})

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
