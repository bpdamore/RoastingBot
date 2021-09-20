def TradeScraper(sender, priority):
    """
    returns bool if there were labels created
    """
    import os,time,time,re,ezgmail,json,gspread
    from datetime import datetime, date, timedelta
    import pandas as pd
    from  oauth2client.service_account import ServiceAccountCredentials
    from fuzzywuzzy import fuzz
    from LabelPrint import LabelPrinter

    # Create a variable that we will return at the end. If true, it will email the currentLabels file to sender. 
    labes = False

    # Create an acceptable grindies list
    grindies = ['whole', 'french-press', 'espresso']

    # Find the file and load into a df
    os.chdir("trade")
    for f in os.listdir():
        trade_df = pd.read_csv(f)
        os.remove(f)

    os.chdir("../")

    # Get the necessary details out
    trade_df = trade_df[["batch_date","batch_id","product_name","grind", "grind_type" ,"quantity","size"]]

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

    # Filter through the df, match grind/sku/size
    today = {}
    for i, row in trade_df.iterrows():
        if row['product_name'] == 'Cold Brew Bags':
            pass
        else:
            # create grindy variable
            if row['grind_type'] not in grindies:
                grindy = 'automatic-drip'
            else:
                grindy = row['grind_type']
            # See if there is a match
            match = False
            for y in sku:
                # Only run if there is not a match
                if not match:
                    # Run a fuzzy search on the product name and each sku
                    perc = fuzz.partial_ratio(row['product_name'].lower(),y.lower())
                    if perc > 80:
                        match = True
                        # Match size and save as siz
                        if row['size'] == "11.464037633613634 oz" or row['size'] == "10.934928204369928 oz":
                            siz = '12OZ'
                            coffee = f'{row["product_name"]}-{grindy}'
                        elif row['size'] == "12 oz":
                            siz = '12OZ'
                            coffee = f'{row["product_name"]}-{grindy}'
                        elif row['size'] == "32 oz": 
                            siz = '2LB'
                            coffee = f'{row["product_name"]}-{grindy}-{siz}'
                        else:
                            siz - 'idklol'
                        # Create sku with correct sku from dictionary, size, and grind
                        cSKU = sku[y]+siz+row["grind"]

                        if coffee in today:
                            # If coffee already exists in Today, then add to the qty (position 0 in the list)
                            today[coffee][0] += int(row["quantity"])
                        else:
                            # If it's not, add the coffee, with a list of [qty, sku]
                            today[coffee] = [int(row["quantity"]), cSKU]
                    else: pass
            
            if match == 'no':
                coffee = f'{row["product_name"]}-{grindy}'
                cSKU = "NEEDS SKU"
                if coffee in today:
                    today[coffee][0] += int(row["quantity"])
                else:
                    today[coffee] = [int(row["quantity"]), cSKU]

    time.sleep(5)
    # Get date and ID from the csv
    # First convert from string -> datetime, then add a day, and convert to string in the right format
    batchDate = datetime.strptime(trade_df['batch_date'][0][:10],'%Y-%m-%d')
    aDay = timedelta(days=1)
    y,m,d = str(batchDate+aDay)[0:10].split('-')
    batchDate = f"{m}/{d}/{y}"
    
    batchID = str(trade_df['batch_id'][0])
    
    rows = []
    twofers = []
    for x in today:
        if priority:
            batchName = f"PRIORTY BATCH - {batchID}"
        else:
            batchName = f"BATCH - {batchID}"
        rows.append(["y", today[x][1], batchName, batchDate, x, int(today[x][0])])
        if "2LB" in today[x][1]:
            twofers.append([today[x][1],'','','',int(today[x][0]), 'y'])

    # Grab the first open row on the subs page
    start = "A"+str(len(sheet.worksheet('Subs').col_values(1))+1)
    # Dump them all into the sheet at the same time.
    sheet.values_update('Subs!'+start,params={'valueInputOption':'USER_ENTERED'},body={'values':rows})

    # Email the person who called this function
    ezgmail.send(sender,"Subbys Are Posted!", "Hey!\n\nSubs are good to go on the sheet fam\n\nLove, \n\n<3 RBCCo")

    if twofers:
        LabelPrinter(batchDate, twofers)
        labes = True
        
    return labes


if __name__ == "__main__":
    TradeScraper("brandon@dw-collective.com", False)