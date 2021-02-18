def TradeScraper(sender):
    import os,time,time,re,ezgmail,json,gspread
    from datetime import datetime, date
    import pandas as pd
    from  oauth2client.service_account import ServiceAccountCredentials
    from fuzzywuzzy import fuzz

    # Find the file and load into a df
    os.chdir("trade")
    for f in os.listdir():
        trade_df = pd.read_csv(f)
        os.remove(f)

    os.chdir("../")

    # Get the necessary details out
    trade_df = trade_df[["product_name","grind", "grind_type" ,"quantity"]]

    # Get the skus from the sheet. 
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open('Roast Sheet 2.4.7')
    blends = sheet.values_get(range="SKUS!B3:B81")['values']
    sos = sheet.values_get(range="SKUS!J3:J121")['values']

    #######################################################################################
    # Add a value we'll delete later so when we add the SO data it won't be off by one. 
    blends.append('---')
    for x in sos:
        blends.append(x)
    x = 1
    name = [blends[0]]
    code = []
    while x < len(blends):
        # This is why we needed to add the '---' 
        if x%2 == 0:
            # Put all the coffee names and sizes in a list
            name.append(blends[x])
        else:
            # Put the sku codes and blanks in a list
            code.append(blends[x])
        x+=1
    
    # Slice the list so it keeps every other item. Read as [{from the start}{to the end}{by 2}]
    name = name[::2]
    code = code[::2]

    # Now make a dictionary pairing
    bad = ['Whiskey Note','Dark Palmera','RB Barrel Aged','1200 Broadway','Little Brother','---']
    x = 0 
    sku = {}
    while x < len(code):
        if name[x][0] in bad:
            pass
        else:
            sku[name[x][0]] = code[x][0]
        x+=1

    # Match the name of the order with the correct SKU
    # Also tally up based on grind size
    today = {}
    for i, row in trade_df.iterrows():
        # See if there is a match
        match = 'no'
        for y in sku:
            if match == 'yes':
                pass
            else:
                perc = fuzz.partial_ratio(row['product_name'].lower(),y.lower())
                if perc > 80:
                    match = 'yes'
                    coffee = f'{row["product_name"]}-{row["grind_type"]}'
                    cSKU = sku[y]+"12OZ"+row["grind"]
                    if coffee in today:
                        # If coffee already exists in Today, then add to the qty (position 0 in the list)
                        today[coffee][0] += int(row["quantity"])
                    else:
                        # If it's not, add the coffee, with a list of [qty, sku]
                        today[coffee] = [int(row["quantity"]), cSKU]
                else: pass
        
        if match == 'no':
            coffee = f'{row["product_name"]}-{row["grind_type"]}'
            cSKU = "NEEDS SKU"
            if coffee in today:
                today[coffee][0] += int(row["quantity"])
            else:
                today[coffee] = [int(row["quantity"]), cSKU]

    
    ############# IF THIS DOESN'T WORK, UNCOMMENT THESE, AND COMMENT ABOVE ##############
    # with open("CoffeeSku.json","r") as f:
    #     sku = json.load(f)
    # time.sleep(1)

    # today = {}
    # print("\n-----------------\nFormatting csv...")
    # for i,row in trade_df.iterrows():
    #     # Check looks to see if there was a match
    #     check = 0
    #     for x in sku:
    #         # If there was a match, skip. Otherwise, go on and look for a match.
    #         if check == 1:
    #             pass
    #         else:
    #             if x in row["product_name"]:
    #                 coffee = f'{row["product_name"]}-{row["grind_type"]}'
    #                 cSKU = sku[x]+"12OZ"+row["grind"]
    #                 if coffee in today:
    #                     today[coffee][0] += int(row["quantity"])
    #                 else:
    #                     today[coffee] = [int(row["quantity"]), cSKU]
    #                 check = 1
    #             else:
    #                 pass
    #     if check == 0:
    #         coffee = f'{row["product_name"]}-{row["grind_type"]}'
    #         cSKU = "NEEDS SKU"
    #         if coffee in today:
    #             today[coffee][0] += int(row["quantity"])
    #         else:
    #             today[coffee] = [int(row["quantity"]), cSKU]
   #####################################################################################

    time.sleep(5)

    rows = []
    tdate = date.today()
    for x in today:
        rows.append(["y",today[x][1], "TRADE - Automated", str(tdate), x, int(today[x][0])])

    # Grab the first open row on the subs page
    start = "A"+str(len(sheet.worksheet('Subs').col_values(1))+1)
    # Dump them all into the sheet at the same time.
    sheet.values_update('Subs!'+start,params={'valueInputOption':'USER_ENTERED'},body={'values':rows})

    # Email the person who called this function
    ezgmail.send(sender,"Subbys Are Posted!", "Hey!\nSorry I took a while...I'm done though!!\nI can't send you the print files, but the subs are good to go!\nsowwy :(\n\nLove, \n\n<3 RBCCo")

if __name__ == "__main__":
    TradeScraper("brandon@dw-collective.com")