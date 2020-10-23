
def rbcco():
    #!/usr/bin/python3.7

    # Import dependencies
    import os
    import PyPDF2
    import re
    import ezgmail
    import time
    import shutil
    from datetime import datetime
    from bs4 import BeautifulSoup as Soup

    # Import G-sheet stuff
    import gspread
    from  oauth2client.service_account import ServiceAccountCredentials

    # Create function to check if the po has already been processed
    def poMatch(skip, cols):
        for po in cols:
            if po != "" and po in att:
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
                ordSearch = re.compile(r'(STAYGOLDEN )(\D+\d+)')
                text = ordSearch.findall(ord1)
                nameSearch = re.compile(r'(\D+)(\d+)?')
                # I'm putting the location and po together, but split by | so I can easily break them up later
                orders[po+"|"+loc]={}
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

        sheet=client.open('Stay Golden Wholesale Order Form (Responses)').worksheet('Grocery')
        data = sheet.get_all_records()
        g = int(len(data))

        ordRows = []
        for order in orders:
            p,l = order.split("|")
            ordRow = ["","","",today,p,l]
            count = 0
            for col in data[g-1]:
                if count<6:
                    pass
                else:
                    match = 0
                    if "6oz" in col:
                        pass
                    else:
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
            print(x)
            sheet.insert_row(x, g+2)
            g+=1

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
            "TBB12OZWB":"1200 Broadway Retail"
        }

        for f in os.listdir(path):
            if ".pdf" in f:
                pass
            elif ".html" in f:
                with open (f, "r") as ord:
                    soup = Soup(ord, "html.parser")
                # Find the po number in the h1 tag
                head = soup.find("h1")
                head = head.text
                # Actually get the number out
                poSearch = re.compile(r'\d+')
                po = poSearch.search(head)
                po = po.group()
                # print(po)
                # Use the po to match a store - this is easier than digging through the html
                for sub in wf:
                    if po in sub:
                        storeSearch = re.compile(r'(Store:)([a-z A-Z]+)')
                        store = storeSearch.search(sub)
                        store = store.group(2)
                        # print(store)
                        # print(sub)

                orders[po+"|"+store]={}
                tables = soup.findAll("table")
                ordTable = tables[6]
                trs = ordTable.findAll("tr")
                trs = trs[1:-2]
                # print(len(trs))
                for tr in trs:
                    tds = tr.findAll("td")
                    sku = tds[1].text
                    if "SSNL" in sku:
                        pass
                    else: 
                        sku = skuMatch[sku]
                    qty = tds[2].text
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

        sheet=client.open('Stay Golden Wholesale Order Form (Responses)').worksheet('Grocery')
        data = sheet.get_all_records()
        g = int(len(data))

        ordRows = []
        for order in orders:
            p,l = order.split("|")
            ordRow = ["","","y",today,p,l]
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

    monitor = "yes"
    while monitor == "yes":
        
        try:

            # Define today's date 
            month = datetime.now().month
            day = datetime.now().day
            today = f'{month}/{day}'

            # Initialize connection to RoastingBot
            ezgmail.init()
            time.sleep(5)

            # Grab all the unread emails
            unread = ezgmail.unread()
            # Skip if there aren't any
            if len(unread) == 0:
                print("\n No orders found ... \n\n")
                time.sleep(60)
                pass
            else:
                wf = []
                # Get that G-Sheet query up and running
                scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
                creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
                client = gspread.authorize(creds)

                # Get list of POs already in the sheet
                sheet=client.open('Stay Golden Wholesale Order Form (Responses)').worksheet('Grocery')
                col = sheet.col_values(5)

                # We need a list to hold the subj of emails with no attachments
                errors = []
                summary = []
                currents = []

                for email in unread:
                    skip = "n"
                    subj = email.messages[0].subject
                    att = email.messages[0].attachments

                    if "Whole Foods Market Order" in subj:
                        if subj in currents:
                            email.markAsRead()
                        else: 
                            currents.append(subj)
                            skip = poMatch(skip,col)
                            if skip == "y":
                                email.markAsRead()
                            elif len(att) == 0:
                                errors.append(subj)
                                email.markAsRead()
                            else:
                                wf.append(subj)
                                print(subj)
                                summary.append(subj)
                                email.messages[0].downloadAllAttachments(downloadFolder='orders')
                                email.markAsRead()

                    elif "Turnip Truck" and "PO" in subj:
                        if subj in currents:
                            email.markAsRead()
                        else:
                            currents.append(subj)
                            skip = poMatch(skip,col)
                            if skip == "y":
                                email.markAsRead()
                            elif len(att) == 0:
                                errors.append(subj)
                                email.markAsRead()
                            else:
                                print(subj)
                                summary.append(subj)
                                email.messages[0].downloadAllAttachments(downloadFolder='orders')
                                email.markAsRead()
                    elif "Status Report" in subj:
                        # ezgmail.send("brandon@dw-collective.com","Currently Active","I am on the job!\n\nLove, \n\n<3 RBCCo")
                        #email.reply("I am on the job!\n\nLove, \n\n-RBCCo <3")
                        sender = email.messages[0].sender
                        ezgmail.send(sender,"Currently Active","I am on the job!\n\nLove, \n\n<3 RBCCo")
                        email.markAsRead()
                    elif "love you" in email.messages[0].body:
                        sender = email.messages[0].sender
                        ezgmail.send(sender,"ERROR","I am unable to process love\n\nThis feature may be available in a future software update\n\n<3 RBCCo")
                        print("\nSomeone loves me <3")
                        email.markAsRead()
                    elif "KILL SWITCH" or "AMSTERDAM" in subj:
                        monitor = "no"
                        email.markAsRead()
                    elif "New text message from 74005" in subj:
                        print("\nEhhh I'll let my other process deal with this one")
                    else:
                        print("\nFound an email, but it's not relevant")
                        email.markAsRead()
                
                if len(summary) > 0:
                    noposts = ""
                    if len(errors) == 0:
                        pass
                    else:
                        for err in errors:
                            noposts+=f"\n\n{err}"
                        # ezgmail.send("brandon@dw-collective.com","Grocery Error",f"These orders don't have attachments{noposts}")
                        ezgmail.send("roasteryorders@gmail.com","Grocery Error",f"These orders weren't processed. {noposts}")

                    posts = ""
                    for post in summary:
                        posts += f"\n\n{post}"

                    print("\n Processing Orders ...")
                    wfOrder()

                    turnipOrder()
                    print("\n Adding to google sheet ...")
                    # ezgmail.send("brandon@dw-collective.com","Grocery Report",f"UwU I put some orders in the GroceryTest tab. \n\nPweeeze look at them and tell me I did good :3 \n\nSUMMARY\n\nOrders Posted: {posts}\n\nLove, \n- RBCCo <3")
                    ezgmail.send("roasteryorders@stay-golden.com","Grocery Report",f"UwU I put some orders in the Grocery tab. \n\nPweeeze look at them and tell me I did good :3 \n\nSUMMARY\n\nOrders Posted: {posts}\n\nLove, \n- RBCCo <3")

                    print("\n Finished! \n\n")

                    time.sleep(60)
                
        except Exception as err:
            print("\nOh no! There was an error. \n"+str(err)+"\nI'll try again in 5 minutes")
            ezgmail.send("brandon@dw-collective.com","Grocery Error",f"There was an error. \n\n{str(err)}\n\nWill try again in the next five minutes.\n\nLove, \n- RBCCo <3")
            time.sleep(300)

rbcco()