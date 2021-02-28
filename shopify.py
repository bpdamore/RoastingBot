# This will eventually contain all the shopify functions... 
# It might take a second.

def expediteMe():
    """
    Checks for expedited orders. If there are any, create the body of an email. 

    returns the body of the email.
    """
    import os, time, requests, json, gspread
    from  oauth2client.service_account import ServiceAccountCredentials
    from config import key, password, hostname, version, emPass
    from pprint import pprint
    from datetime import datetime, timedelta

    draftDate = datetime.today() - timedelta(days=14)

    # Load the ids of the orders that have already been checked
    # with open("shipcheck.json","r") as f:
    #     processed = json.load(f)
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open('Roast Sheet 2.4.7')
    processed = sheet.values_get(range="secret!A1:A")['values']

    query_url = f'https://{key}:{password}@{hostname}.myshopify.com/admin/api/{version}/'
    order_print = 'fields=name,shipping_lines,id'
    # Save all open orders into response
    response = requests.get(f'{query_url}orders.json?status=open&{order_print}').json()
    response = response['orders']

    # Now do it with drafts
    dresponse = requests.get(f"{query_url}draft_orders.json?updated_at_min={draftDate}&status=open").json()
    dresponse = dresponse["draft_orders"]
    # Create an empty list of expedited orders
    expedited = []
    for x in response:
        # If the order has been process, skip
        if x['id'] in processed:
            print(f"Order {x['name']} has already been processed")
            pass
        # Otherwise, process it and add the id to the processed list
        else: 
            print("Not yet processed! ")
            processed.append([str(x['id'])])
            # pprint(x['id'])
            try:
                for y in x['shipping_lines']:
                    if "Expedited" in y['title']:
                        if x['id'] not in expedited:
                            expedited.append(x['name'])
                            print(y['title'])
            except KeyError:
                for y in x['shipping_line']:
                    if "Expedited" in y['title']:
                        if x['id'] not in expedited:
                            expedited.append(x['name'])
                            print(y['title'])

    for x in dresponse:
        # If the order has been process, skip
        if x['id'] in processed:
            print(f"Order {x['name']} has already been processed")
            pass
        # Otherwise, process it and add the id to the processed list
        else: 
            print("Not yet processed! ")
            processed.append([str(x['id'])])
            # pprint(x['id'])
            try:
                if "Expedited" in x['shipping_line']['title']:
                    if x['id'] not in expedited:
                        expedited.append(x['name'])
                        print(x['shipping_line']['title'])
            except:pass


    if len(expedited) != 0:                    
        msg = f"Howdy! \n\nThe following Expedited orders were just placed! \n\n{expedited}\n\nIf there's a D in there, it should be a draft order.\n\nLove,\n<3 RBCCO"
    else:
        msg = "nothing here"

    # # Load the new list of processed orders back into the file for later. 
    # with open("shipcheck.json", "w") as f:
    #     json.dump(processed,f)
    sheet.values_update('secret!'+'A1',params={'valueInputOption':'USER_ENTERED'},body={'values':processed})
    
    return msg

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
    sheet.values_update('Roast Sheet!C54:C55',params={'valueInputOption':'USER_ENTERED'},body={'values':[[0],['']]})
    sheet.values_update('Roast Sheet!D54:D55',params={'valueInputOption':'USER_ENTERED'},body={'values':[[0],['']]})

    # Clear out the Roast Calculator
    rcz = [[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],['Manual Lbs'],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0]]
    rcr = [[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],['Roasted On Hand'],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0]]
    # Clears the values while also putting the header in there
    sheet.values_update('Roast Calculator!K2:K56',params={'valueInputOption':'USER_ENTERED'},body={'values':rcz})
    sheet.values_update('Roast Calculator!B2:B56',params={'valueInputOption':'USER_ENTERED'},body={'values':rcr})

    # Clear out Bagging Sheet
    # dang this is a lot of rows 
    bagval1 = [[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],\
    [''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],\
    [''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],\
    [''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],\
    [''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],\
    [''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],\
    [''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],\
    [''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],\
    [''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],\
    [''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],\
    [''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],\
    [''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],\
    [''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],\
    [''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],\
    [''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],\
    [''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],\
    [''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],\
    [''],[''],[''],[''],[''],[''],[''],[''],[''],['']]

    bagval2 = [[''],[''],[''],[''],[''],[''],[''],[''],[''],['']]
    bagval3 = [[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],[''],['']]

    sheet.values_update('Bag Report!D4:D248',params={'valueInputOption':'USER_ENTERED'},body={'values':bagval1})
    sheet.values_update('Bag Report!F4:F248',params={'valueInputOption':'USER_ENTERED'},body={'values':bagval1})
    sheet.values_update('Bag Report!H4:H248',params={'valueInputOption':'USER_ENTERED'},body={'values':bagval1})
    sheet.values_update('Bag Report!J4:J248',params={'valueInputOption':'USER_ENTERED'},body={'values':bagval1})
    sheet.values_update('Bag Report!L4:L248',params={'valueInputOption':'USER_ENTERED'},body={'values':bagval1})
    sheet.values_update('Bag Report!D253:D262',params={'valueInputOption':'USER_ENTERED'},body={'values':bagval2})
    sheet.values_update('Bag Report!F253:F262',params={'valueInputOption':'USER_ENTERED'},body={'values':bagval2})
    sheet.values_update('Bag Report!F266:F277',params={'valueInputOption':'USER_ENTERED'},body={'values':bagval3})



    # # GROCERY --- UNCOMMENT IF YOU WANT TO INCLUDE GROCERY
    # # Date the queued grocery rows. 
    # x = 4
    # # Iterate through col A, if there's a y, put today's date in
    # while x < len(grocvals):
    #     if grocvals[x] == 'y':
    #         grocvals[x] = td
    #     x+=1
    # # Now make a list of lists so we can throw it into the sheet. 
    # grocval = []
    # for x in grocvals:
    #     grocval.append([x])
    
    # sheet.values_update('Grocery!A:A', params={'valueInputOption':'USER_ENTERED'},body={'values':grocval})

if __name__ == "__main__":

    choices = input('which script would you like to run? \n\na. expediteMe()\n\nb. cleanShop()\n\nplease enter a or b \n\n... ')

    if choices.lower() == 'a':
        from datetime import datetime
        import ezgmail
        import time

        run = "yes"
        minutes = ["15","30","45","00", "08"]

        while run == "yes":
            now = datetime.now()
            hour = int(now.strftime("%H"))
            minute = now.strftime("%M")

            if hour < 8:
                print("It's too early.")
                pass
            elif minute not in minutes:
                print("...")
                pass
            else:
                print("Let's go!")
                msg = expediteMe()
                if msg != "nothing here":
                    ezgmail.send("brandon@dw-collective.com","Expedited Order Placed",msg)
                else:
                    print(msg)

            time.sleep(60)
    elif choices.lower() == 'b':
        cleanShop()


    
