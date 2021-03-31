
def rbcco():
    #!/usr/bin/python3.7
    # Import dependencies
    import os,PyPDF2,re,ezgmail,time,shutil,json
    from datetime import datetime
    from bs4 import BeautifulSoup as Soup
    from sys import platform
    import pandas as pd
    from ShopifyPull import ShopPull,singlePrint
    import trade
    import LabelPrint
    import draftBatch
    from shopify import expediteMe,cleanShop
    # Import G-sheet stuff
    import gspread
    from  oauth2client.service_account import ServiceAccountCredentials

    counter = 1

    # Create function to check if the po has already been processed
    def poMatch(skip, cols, att):
        if len(att) == 0:
            skip="y"
        else:
            for po in cols:
                if str(po) != "" and str(po) in att[0]:
                    skip = "y"
                else: pass
        return skip

    # Process Turnip Orders
    def turnipOrder():
        pname = "orders"
        path = os.chdir(pname)
        orders={}

        for f in os.listdir(path):
            # Only work on pdfs
            if ".html" in f:
                pass
            elif ".pdf" in f:
                # Search for the PO number, and only grab that group
                poSearch = re.compile(r'(PO \d+) ((Turnip Truck ([a-zA-Z ]+)?)(\(\D+\))?)')
                po = poSearch.search(f)
                loc = po.group(2)
                po = po.group(1)
                # Tack "Charlotte" on the end if it's anywhere in the filename. 
                if "char" in f.lower():
                    loc += "Charlotte"
                # Open the pdf, look at page 0, extract text
                pdfFileObj = open(f, 'rb')
                pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
                pageObj = pdfReader.getPage(0)
                ord1 = pageObj.extractText()
                # Search for Orders
                ordSearch = re.compile(r'(STAY ?GOLDEN )(\D+\d+)')
                text = ordSearch.findall(ord1)
                nameSearch = re.compile(r'(\D+)(\d+)?')
                # I'm putting the location and po together, but split by | so I can easily break them up later
                orders[po+"|"+loc]={}
                # Search for mugs
                mugsearch = re.compile(r'((MUG)(\d+?))(\$)')
                mugs = mugsearch.search(ord1)
                if mugs == None:
                    pass
                else:
                    mugqty = mugs.group(3)
                    orders[po+'|'+loc]['Holiday Mug']=[mugqty]
                # Pull out the individual orders from the matched group.
                for match in text:
                    if "SSNL" not in match[1]:
                        thing = nameSearch.search(match[1])
                        sku = (thing.group(1))
                        qty = int(thing.group(2))
                    elif len(match[1]) == 9:
                        sku = (match[1][1:-3])
                        qty = int(match[1][-3:])
                    elif len(match[1]) == 8:
                        sku = (match[1][1:-2])
                        qty = int(match[1][-2:])
                    elif len(match[1]) == 7:
                        sku = (match[1][1:-1])
                        qty = int(match[1][-1:])
                    else:
                        print("error ... ")

                    # Turnip usually orders individual bags, but the sheet counts cases. So divide by six if it is divisible by 6.
                    if int(qty)%6==0:
                        qty = int(qty/6)

                    if sku not in orders[po+"|"+loc]:
                        orders[po+"|"+loc][sku]=qty
                    else:
                        orders[po+"|"+loc][sku]+=qty
                pdfFileObj.close()
                os.remove(f)

        os.chdir("../")
        # Get that G-Sheet query up and running
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
        client = gspread.authorize(creds)

        sheet=client.open('Roast Sheet 2.4.7').worksheet('Grocery')
        data = sheet.get_all_records()
        g = int(len(data))

        ordRows = []
        for order in orders:
            p,l = order.split("|")
            ordRow = ["y","","",today,p,l]
            count = 0
            for col in data[g-1]:
                if count<6:
                    pass
                else:
                    match = 0
                    if "6oz" in col:
                        ordRow.append("")
                    else:
                        for item in orders[order]:
                            print(item)
                            if item.lower() in col.lower():
                                print(f"\nMatching col found! {item.lower()} -- {col.lower()}")
                                ordRow.append(orders[order][item])
                                match = 1
                            else: pass
                        if match == 0:
                            ordRow.append("")
                count+=1
            ordRows.append(ordRow)

        for x in ordRows:
            print(x)
            sheet.insert_row(x, g+2)
            g+=1
    
    # Process WF Orders
    def wfOrder():
        pname = "orders"
        path = os.chdir(pname)
        orders={}
        
        skuMatch = {
            "BBS12OZWB":"Buddy Buddy Retail",
            "CUB12OZWB":"Chin Up Retail",
            "HTB12OZWB":"Hang Tough Retail",
            "HTB6OZFP":"Hang Tough 6oz",
            "TBB6OZFP":"1200 Broadway 6oz",
            "CDC12OZWB":"Decaf Retail",
            "TBB12OZWB":"1200 Broadway Retail",
            "DTH12OZWB":"Deck The Halls Retail"
        }

        for f in os.listdir(path):
            print("\nWF - Looking at orders")
            if ".pdf" in f:
                pass
            elif ".html" in f:
                with open (f, "r") as ord:
                    soup = Soup(ord, "html.parser")
                # Find the po number in the h1 tag
                print(f"\nOpening {f}")
                head = soup.find("h1")
                head = head.text
                print("\nExtracting PO")
                # Actually get the number out
                poSearch = re.compile(r'\d+')
                po = poSearch.search(head)
                po = po.group()
                # print(po)
                # Use the po to match a store - this is easier than digging through the html
                for sub in wf:
                    if po in sub:
                        print("\nSearching for store")
                        storeSearch = re.compile(r'(Store:)([a-z A-Z]+)')
                        store = storeSearch.search(sub)
                        store = store.group(2)
                        # print(store)
                        # print(sub)

                orders[po+"|WF - "+store]={}
                tables = soup.findAll("table")
                ordTable = tables[6]
                trs = ordTable.findAll("tr")
                trs = trs[1:-2]
                # print(len(trs))
                print("\nFinding table of orders")
                for tr in trs:
                    tds = tr.findAll("td")
                    sku = tds[1].text
                    if "SSNL" in sku:
                        pass
                    else: 
                        sku = skuMatch[sku]
                    qty = tds[2].text
                    print("\nFinding Qty")
                    numSearch = re.compile(r'\d+')
                    qty = numSearch.search(qty)
                    qty = qty.group()
                    orders[po+"|WF - "+store][sku]=int(qty)

                os.remove(f)
                
        os.chdir("../")
        # Get that G-Sheet query up and running
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
        client = gspread.authorize(creds)

        sheet=client.open('Roast Sheet 2.4.7').worksheet('Grocery')
        data = sheet.get_all_records()
        g = int(len(data))

        ordRows = []
        for order in orders:
            p,l = order.split("|")
            ordRow = ["y","","",today,p,l]
            count = 0
            for col in data[g-1]:
                if count<6:
                    pass
                else:
                    match = 0
                    for item in orders[order]:
                        if item.lower() in col.lower():
                            ordRow.append(orders[order][item])
                            match = 1
                        else: pass
                    if match == 0:
                        ordRow.append("")
                count+=1
            ordRows.append(ordRow)

        for x in ordRows:
            sheet.insert_row(x, g+2)
            g+=1
    
    # Process UNFI Orders
    def unfiOrders():
        pname = "unfi"
        os.chdir(pname)

        # Define regex search for UNFI
        CUBsearch = re.compile(r'(\d+)( +)(CUB12OZWB)')
        HTBsearch = re.compile(r'(\d+)( +)(HTB12OZWB)')
        EDIsearch = re.compile(r'(\d+)( +)(EDI12OZWB)')
        CDCsearch = re.compile(r'(\d+)( +)(CDC12OZWB)')
        poSearch = re.compile(r'(PO Number:)( +)(\d+)')

        ords = {}
        for f in os.listdir():
            print(f"\nReading {f}")
            pdfFileObj = open(f, 'rb')
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            pageObj = pdfReader.getPage(1)
            ord1 = pageObj.extractText()

            print("\nfinding line items")

            po = poSearch.search(ord1)
            try:
                ords["UNFI|"+po.group(3)] = {}
            except:
                pass
            
            CUB = CUBsearch.search(ord1)
            try:
                ords["UNFI|"+po.group(3)]["Chin Up Retail"] = int(CUB.group(1))
            except:
                pass
            
            HTB = HTBsearch.search(ord1)
            try:
                ords["UNFI|"+po.group(3)]["Hang Tough Retail"] = int(HTB.group(1))
            except:
                pass

            EDI = EDIsearch.search(ord1)
            try:
                ords["UNFI|"+po.group(3)]["Decaf Retail"] = int(EDI.group(1))
            except:
                pass

            CDC = CDCsearch.search(ord1)
            try:
                ords["UNFI|"+po.group(3)]["Decaf Retail"] = int(CDC.group(1))
            except:
                pass
            
            print(ords)
            pdfFileObj.close()
            os.remove(f)

        os.chdir("../")
        # Get that G-Sheet query up and running
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
        client = gspread.authorize(creds)

        sheet=client.open('Roast Sheet 2.4.7').worksheet('Grocery')
        data = sheet.get_all_records()
        g = int(len(data))

        ordRows = []
        for order in ords:
            p,l = order.split("|")
            ordRow = ["y","","",today,l,p]
            count = 0
            for col in data[g-1]:
                if count<6:
                    pass
                else:
                    match = 0
                    if "6oz" in col:
                        pass
                    else:
                        for item in ords[order]:
                            if item.lower() in col.lower():
                                ordRow.append(ords[order][item])
                                match = 1
                            else: pass
                        if match == 0:
                            ordRow.append("")
                count+=1
            ordRows.append(ordRow)

        for x in ordRows:
            print(x)
            sheet.insert_row(x, g+2)
            g+=1

    def binUpdate():
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
        client = gspread.authorize(creds)

        time.sleep(20)
            
        # Completely rewrite the sheet
        # The WMS sheet will always reference the data on this sheet, so it's fine to overwrite it
        sheet = client.open('BinData')
        os.chdir('binData')
        
        read = 'yes'
        for f in os.listdir():
            if read == 'yes':
                print(f)
                df = pd.read_csv(f)
                sortdf = df.sort_values(['Bin Number'])
                sortdf.to_csv("../binData/outData.csv")
                time.sleep(2)
                os.remove(f)
                read = 'no'
            else: pass
            
        print("\nAdding to sheet")
        with open("outData.csv", "r", encoding="UTF-8") as bins:
            content = bins.read()
            client.import_csv(sheet.id, data=content.encode("UTF-8"))
        os.remove('outData.csv')
        os.chdir('../')

    monitor = "yes"
    while monitor == "yes":
        try:
            # Define today's date 
            month = datetime.now().month
            day = datetime.now().day
            year = datetime.now().year
            today = f'{month}/{day}/{str(year)[-2:]}'

            # Initialize connection to RoastingBot
            # print("\n Starting up! ")
            ezgmail.init()
            time.sleep(5)

            # Look for expedited orders that may have come in.
            if counter % 15 == 0:
                try:
                    print('\nChecking for expedited orders real quick...')
                    expmsg = expediteMe()
                    if expmsg != 'nothing here':
                        print('\nHey! Looks like one was placed!')
                        ezgmail.send('roasteryorders@stay-golden.com','An Expedited Order was Placed!', expmsg)
                        ezgmail.send('brandon@dw-collective.com','An Expedited Order was Placed!', expmsg)
                    else: print('\nLooks like there\'s nothing here.')
                except Exception as err:
                    print('Expedited script failed for some reason')
                    ezgmail.send('brandon@dw-collective.com','Expedited script failed',f'Hey there! \n\nThe expedited script failed because of {err}\n\nSorry! \n\nLove, \n\n<3 RBCCo')

            print("\n Checking emails")
            # Grab all the unread emails
            unread = ezgmail.unread()
            # Skip if there aren't any
            if len(unread) == 0:
                print("\n No orders found ... \n\n")
                counter += 1
                time.sleep(60)
                pass
            else:
                print("\n Oh! An email!")
                wf = []
                # Get that G-Sheet query up and running
                scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
                creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
                client = gspread.authorize(creds)

                # Get list of POs already in the sheet
                sheet=client.open('Roast Sheet 2.4.7').worksheet('Grocery')
                col = sheet.col_values(3)
                
                # We need a list to hold the subj of emails with no attachments
                errors = []
                summary = []
                currents = []
                
                print("\n Searching through emails")
                for email in unread:
                    skip = "n"
                    subj = email.messages[0].subject
                    print(subj)
                    att = email.messages[0].attachments
                    print(att)
                    sender = email.messages[0].sender
                    print(sender)
                    body = email.messages[0].body
                    # print(body)

                    if "Whole Foods Market Order" in subj:
                        print("A Whole Foods Email!")
                        if subj in currents:
                            email.markAsRead()
                        else: 
                            currents.append(subj)
                            skip = poMatch(skip,col,att)
                            print(skip)
                            if skip == "y":
                                email.markAsRead()
                            elif len(att) == 0:
                                errors.append(subj)
                                email.markAsRead()
                            else:
                                wf.append(subj)
                                print("WF")
                                print(subj)
                                summary.append(subj)
                                email.messages[0].downloadAllAttachments(downloadFolder='orders')
                                email.markAsRead()

                    elif body and "unfi.com" in body:
                        print("Woah a unfi order!")
                        # email.markAsRead()
                        if subj in currents:
                            email.markAsRead()
                        else:
                            currents.append(subj)
                            skip = poMatch(skip, col, att)
                            if skip == "y":
                                email.markAsRead()
                            elif len(att) == 0:
                                errors.append(subj)
                                email.markAsRead()
                            else: 
                                print("UNFI")
                                print(subj)
                                summary.append(subj)
                                email.messages[0].downloadAllAttachments(downloadFolder='unfi')
                                email.markAsRead()

                    elif "Turnip Truck" and "PO" in subj:
                        print("Tuurrrnip")
                        if subj in currents:
                            print("already processing... ")
                            email.markAsRead()
                        else:
                            currents.append(subj)
                            skip = poMatch(skip,col,att)
                            if skip == "y":
                                print("already processed... ")
                                email.markAsRead()
                            elif len(att) == 0:
                                print("there's no attachment...")
                                errors.append(subj)
                                email.markAsRead()
                            else:
                                print("TURNIP LET'S GO")
                                print(subj)
                                summary.append(subj)
                                email.messages[0].downloadAllAttachments(downloadFolder='orders')
                                email.markAsRead()

                    elif "Status Report" in subj:
                        # ezgmail.send("brandon@dw-collective.com","Currently Active","I am on the job!\n\nLove, \n\n<3 RBCCo")
                        #email.reply("I am on the job!\n\nLove, \n\n-RBCCo <3")
                        ezgmail.send(sender,"Currently Active","I am on the job!\n\nLove, \n- RBCCo <3")
                        email.markAsRead()

                    elif subj.lower() == "clean your room":
                        print("Cleaning the sheet!")
                        email.markAsRead()
                        cleanShop()
                        ezgmail.send(sender,"Sheet Has Been Cleaned","I cleaned the sheet all nice and good like! I hope you like it! \n\nLove, \n- RBCCo <3")
                        ezgmail.send("brandon@dw-collective.com","Someone Cleaned the Sheets",f"Hey!\n {sender} told me to clean the sheet, so I did!\n\nLove, \n\n<3 RBCCo")

                    elif subj.lower() == "subbywubby":
                        print("Doing subs!")
                        email.markAsRead()
                        email.messages[0].downloadAllAttachments(downloadFolder='trade')
                        trade.TradeScraper(sender)
                        ezgmail.send("brandon@dw-collective.com","Subs have been activated",f"Hey! \n{sender} told me to get the subs\n\nLove, \n\n<3 RBCCo")

                    elif "SinglePull" in subj:
                        print("Okay let's try to pull one order")
                        # Need to figure out how to also print these specific labels. 
                        email.markAsRead()
                        digitz = re.compile(r'\d+')
                        code = digitz.search(subj)
                        ordr = str(code.group())
                        mom = str(code.group())
                        ## Can get labels created it wanted...just need rdate somehow.
                        sheetdata = ShopPull(mom,"tag")
                        # Just take the sheetdata and throw it into LabelPrint.LabelPrinter(rdate, sheetdata)
                        ezgmail.send(sender,f"Pulled order {mom}","I've pulled the order you wanted! \n\nLove, \n- RBCCo <3",attachments=f"static/output/{mom}.html")
                        ezgmail.send("brandon@dw-collective.com",f"{sender} Pulled order {ordr}!",f"Hey!\n\nI started the pull for order {mom}! \n Hopefully it works! \n\nLove, \n\n<3 RBCCo",attachments=f"static/output/{mom}.html")
                        
                    elif "SinglePrint" in subj:
                        print("Creating printout!")
                        email.markAsRead()
                        digitz = re.compile(r'\d+')
                        code = digitz.search(subj)
                        ordr = str(code.group())
                        singlePrint(ordr)
                        ezgmail.send(sender,"Printed an order!",f"Hey!\n\nI started the print for order {ordr}! \n Hopefully it works! \n\nLove, \n\n<3 RBCCo",attachments=f"static/output/{ordr}.html")
                        ezgmail.send("brandon@dw-collective.com",f"{sender} printed order {ordr}",f"Hey!\n\nI started the print for order {ordr}! \n Hopefully it works! \n\nLove, \n\n<3 RBCCo",attachments=f"static/output/{ordr}.html")

                    # Pull the shopify data by email! 
                    elif subj.lower() == "go to work":
                        rdateSearch = re.compile(r'(\d\d/\d\d/\d\d(\d\d)?)')

                        try:
                            rdate = rdateSearch.search(body)
                            rdate = rdate.group(0)

                            if len(rdate) == 10:
                                rdate = rdate[:-4]+rdate[-2:]
                                
                            print(rdate)
                            
                            print("Creating full orders from drafts")
                            draftBatch.draftOrds()
                            time.sleep(4)

                            from sys import platform
                            print(platform)
                            if platform == "linux":
                                from subprocess import call
                                call("python3 ~/Documents/RBCCo/ShopifyPull.py", shell=True) 

                            elif platform == "win32":
                                sheetdata = ShopPull("Current_Orders","ignore")
                            
                            time.sleep(20)
                            LabelPrint.LabelPrinter(rdate,sheetdata)
                            time.sleep(5)
                            print('looks like it wrote everything. \nTime to email.')
                            ezgmail.send(sender,"Pulled Today's Order","Hey!\n\nI started the shopify pull! \n Hopefully it works! \n\nHere's the printout of the orders, and the labels for the day! \n\nLove, \n\n<3 RBCCo",attachments=["static/output/Current_Orders.html","static/output/sgLabes.html"])
                            ezgmail.send("brandon@dw-collective.com",f"{sender} Pulled Today's Order","Hey!\n\nI started the shopify pull! \n Hopefully it works! \n\nHere's the printout of the orders, and the labels for the day! \n\nLove, \n\n<3 RBCCo",attachments=["static/output/Current_Orders.html","static/output/sgLabes.html"])
                            email.markAsRead()

                        except AttributeError:
                            print("There was no date.")
                            ezgmail.send(sender,"Please Provide Date", "Hi there!\n In order for me to get the labels all formatted I'm going to need a date from you. Please send the email again, but with the date (XX/XX/XX) in the body of your email.\nIf the formatting isn't correct, I won't do it!\n\nLove, \n\n<3 RBCCo" )
                            email.markAsRead()

                    elif subj.lower() == "help":
                        print("Someone needs help!")
                        ezgmail.send(sender,"Table of Contents","Hey there! \n\nHere's a little that I can do.\n\nIf your subject line is 'Clean Your Room', I will completely reset the roast sheet. If there are any orders that you would like me to ignore, replace the 'y' in the queued column with 'plz'. :)\nPlease be careful with this one.\n\nIf your subject line is 'Go to work', I will pull all orders for the day and create the packing list that will be sent to your email. I will also create the SG labels for the day. Be sure to put the date (formatted like XX/XX/XX) you want on the labels in the body of the email, or else I won't do it! \n\nIf you want me to pull a single order from Shopify, make your subject 'SinglePull XXXX' where the Xs are your order number. \nI will send the html document with the order to your email.\n\nIf you want to print an order from the Shopify sheet on the google sheet, put your subject line as 'SinglePrint XXXX' where the X's are the order number (in the C column)\nI will send the html document with the order to your email.\n\nTo pull the Trade data, send me an email with the subject line 'SubbyWubby'. \nUnfortunately I can't send you the print files, but the orders will be in the sheet! \nI WILL however send you the csv with the orders in case you wanted to double check my work.\n\nContact Brandon if you have any issues! \n\nLove, \n- RBCCo <3")
                        email.markAsRead()
                            
                    elif "New text message from 74005" in subj:
                        email.markAsRead()
                        # print("\nEhhh I'll let my other process deal with this one")

                    # Look for Bin data from netsuite and update it. 
                    elif subj == "RB BIN DATA":
                        print("Bin data! Woo!")
                        email.messages[0].downloadAllAttachments(downloadFolder='binData')
                        binUpdate()
                        print('Bin update finished.')
                        email.markAsRead()
                        ezgmail.send('brandon@dw-collective.com','Bin Data Updated','Yoyoyoyoyo\nThe bin data was updated! It should have worked!\n\nLove, \n- RBCCo <3')

                    # elif subj.lower() == "tag":

                    #     ## WORK IN PROGRESS ##
                    #     ## I want this to basically pull all orders that have a certain tag ## 
                    #     # Subject : tag
                    #     # Body : 01/01/20 [recurring_order]
                    #     # Go from here to Shopify pull -> label print -> email
                    #     rdateSearch = re.compile(r'(\d\d/\d\d/\d\d(\d\d)?)')
                    #     try:
                    #         rdate = rdateSearch.search(body)
                    #         rdate = rdate.group(0)

                    #         if len(rdate) == 10:
                    #             rdate = rdate[:-4]+rdate[-2:]
                    #         print(rdate)
                    #     except Exception as err:
                    #         print('There was an error!')
                    #         ezgmail.send('brandon@dw-collective.com','Error at Tag',f'Hey!\n\nThere was an error {err} at the Tag function. \n\nJust thought you should know!\n\nLove, \n\n<3 RBCCo')


                    else:
                        print("\nFound an email, but it's not relevant")
                        email.markAsRead()
                        ezgmail.send('brandon@dw-collective.com','Found a random email',f'Hey!\n\nI found a random email, and I just marked it as read. The subject was {subj}. \n\nJust thought you should know!\n\nLove, \n\n<3 RBCCo')
                
                if len(summary) > 0:
                    noposts = ""
                    if len(errors) == 0:
                        pass
                    else:
                        for err in errors:
                            noposts+=f"\n\n{err}"
                        ezgmail.send("brandon@dw-collective.com","Grocery Error",f"These orders don't have attachments{noposts}")
                        # ezgmail.send("roasteryorders@gmail.com","Grocery Error",f"These orders weren't processed. {noposts}")

                    posts = ""
                    for post in summary:
                        posts += f"\n\n{post}"

                    print("\n Processing Orders ...")

                    print("\nProcessing WF")
                    wfOrder()
                    print("\nProcessing Turnip")
                    turnipOrder()
                    print("\nProcessing unfi")
                    unfiOrders()

                    print("\n Adding to google sheet ...")
                    ezgmail.send("brandon@dw-collective.com","Grocery Report",f"UwU I put some orders in the Grocery tab on the NEW sheet. \n\nPweeeze look at them and tell me I did good :3 \n\nSUMMARY\n\nOrders Posted: {posts}\n\nLove, \n- RBCCo <3")
                    ezgmail.send("roasteryorders@stay-golden.com","Grocery Report",f"UwU I put some orders in the Grocery tab on the NEW sheet. \n\nPweeeze look at them and tell me I did good :3 \n\nSUMMARY\n\nOrders Posted: {posts}\n\nLove, \n- RBCCo <3")

                    print("\n Finished! \n\n")
                    counter += 3
                    time.sleep(180)
                
        except Exception as err:
            print("\nOh no! There was an error. \n"+str(err)+"\nI'll try again in 5 minutes")
            try:
                ezgmail.send("brandon@dw-collective.com","RoastingBot Error",f"There was an error. \n\n{str(err)}\n\nWill try again in the next five minutes.\n\nLove, \n- RBCCo <3")
            except:
                print("\n\nI won't tell Brandon about the error...it's fine...")
            counter += 5
            time.sleep(300)

rbcco()