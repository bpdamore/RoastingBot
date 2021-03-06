def LabelPrinter(rdate, shopvals):

    import os, time, webbrowser, requests, gspread
    from bs4 import BeautifulSoup as Soup
    from  oauth2client.service_account import ServiceAccountCredentials
    from config import key, password, hostname, version, emPass
    from pprint import pprint

    # Define some variables to make this work
    splitter = "XX/XX/XX"
    putback = "</div></div></div></div>"
    endcap = "</body></html>"

    # If there's another label, we need to put a page break in, but we don't want it if it's the end.
    pbreak = '<P style="page-break-before: always"></P>'

    ##### TRYING SOMETHING ###########
    #     # scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    # creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    # client = gspread.authorize(creds)

    # # Choose the sheet/worksheet that you will be working on
    # # sheet = client.open("test").worksheet(ws)
    # sheet = client.open('Roast Sheet 2.4.7')
    # # shopvals = sheet.values_get(range="labes!A4:F")['values']
    # shopvals = sheet.values_get(range="Shopify!A4:F")['values']
    #################################


    sgOrds = {}
    rbOrds = {}
    tbOrds= {}
    sg2lb = {}
    rb2lb = {}
    tb2lb = {}
    wLabel = {}
    sglabes = ""

    for row in shopvals:
        if row[5] == "y":

            # Start getting white labels identified for the digest. 
            sku = row[0]
            cname = row[3]
            qty = row[4]

            # Weed out the skus that don't need a label
            check = False

            # Only grab white labels 
            if '-' in sku:
                if cname not in wLabel:
                    wLabel[cname] = qty
                else:
                    wLabel[cname] += qty
            checkers = ['5 lb', '2 lb']
            for x in checkers:
                if x in cname:
                    check = True
                else: 
                    pass 
            if "5LB" in row[0]:
                if "RB-" in row[0]:
                    if row[0][0:6] not in rbOrds:
                        rbOrds[row[0][0:6]] = int(row[4])
                    else: rbOrds[row[0][0:6]] += int(row[4])
                elif "3B-" in row[0]:
                    if row[0][0:6] not in tbOrds:
                        tbOrds[row[0][0:6]] = int(row[4])
                    else: tbOrds[row[0][0:6]] += int(row[4])
                else:
                    if row[0][0:3] not in sgOrds:
                        sgOrds[row[0][0:3]] = int(row[4])
                    else: sgOrds[row[0][0:3]] += int(row[4])
            elif "2LB" in row[0]:
                if "RB-" in row[0]:
                    if row[0][0:6] not in rb2lb:
                        rb2lb[row[0][0:6]] = int(row[4])
                    else: rb2lb[row[0][0:6]] += int(row[4])
                elif "3B-" in row[0]:
                    if row[0][0:6] not in tb2lb:
                        tb2lb[row[0][0:6]] = int(row[4])
                    else: tb2lb[row[0][0:6]] += int(row[4])
                else:
                    # print(row[0]+" - "+row[4])
                    if row[0][0:3] not in sg2lb:
                        sg2lb[row[0][0:3]] = int(row[4])
                    else: sg2lb[row[0][0:3]] += int(row[4])

    print(sgOrds)
    print(sg2lb)

    if len(sgOrds) > 0:
        print('Working on SG 5lbs')
        os.chdir("labels/static/sg/5lb")
        for cof in sgOrds:
            num=1
            # print("\n")
            for f in os.listdir():
                # print(f)|
                if cof.lower() in f.lower():
                    print(f.lower())
                    with open(f,"r") as infile:
                        soup = Soup(infile,"html.parser")
                        soup = str(soup)
                    begin,end = soup.split(splitter)
                    soup = begin + rdate + putback
                    while num <= int(sgOrds[cof]):
                        sglabes+=soup
                        sglabes+=pbreak
                        # print(num)
                        num +=1
        os.chdir("../../../../")
    
    if len(sg2lb) > 0:
        print('Working on SG 2lbs')
        os.chdir('labels/static/sg/2lb')
        for cof in sg2lb:
            num=1
            # print("\n")
            for f in os.listdir():
                if cof.lower() in f.lower():
                    print(f.lower())
                    with open(f,"r") as infile:
                        soup = Soup(infile,"html.parser")
                        soup = str(soup)
                    begin,end = soup.split(splitter)
                    soup = begin + rdate + putback
                    while num <= int(sg2lb[cof]):
                        sglabes+=soup
                        sglabes+=pbreak
                        # print(num)
                        num +=1
        os.chdir("../../../../")


    sglabes += endcap
    # print(sglabes)
    with open("static/output/sgLabels.html","w", encoding='cp437', errors='ignore') as f:
        print('\n\nWriting the label file')
        f.write(sglabes)
        print("written! ")

    if len(wLabel) != 0:
        digest = "Hey there! \nHere is your White Label Digest\n"

        for x in sorted(wLabel):
            digest+=(f"\n{wLabel[x]} -- {x}")
        print(digest)
    else:
        digest = False

    return digest

if __name__ == "__main__":
    LabelPrinter("02/18/21")