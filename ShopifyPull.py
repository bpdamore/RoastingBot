def printer(allOrders, soup, ordr):
    """
    allOrders == shopOrds
    soup == soup
    """
    logo ='</br><div class="logo col-sm-12 col-lg-12"><img style="margin-top: 20; align-items: center;" src="https://drive.google.com/uc?export=view&id=1arXMvyh7OvGt5d83rf6NosCviTa4oRF3"></div></br>'
    sg = '<div class="twins col-sm-6 col-lg-6"><h4>Stay Golden Coffee Co</h4><h5>2934 Sidco Dr STE #130 </h5><h5>Nashville, TN, 37204</h5></div></br>'
    thead = '<div class="col-sm-12 col-lg-12"><table class="table table-striped"><thead><tr><th scope="col">#</th><th scope="col">Item</th><th scope="col">Quantity</th></tr></thead>'
    tbody = '<tbody>'
    pbreak = '<P style="page-break-before: always"></P>'

    ords = 0
    ordlens = len(allOrders["emails"])
    while ords < ordlens:
        # print("doing and order")
        ordheader = f'<div class="col-sm-12 col-lg-12"><h3>Order {allOrders["ordnums"][ords]}</h3><h6>{allOrders["times"][ords]}</h6></div>'
        tbody = '<tbody>'
        # Add name
        ordinf = f'<div class="twins col-sm-6 col-lg-6"><h5>{allOrders["shippings"][ords][0]}'
        # If company name, add it
        if allOrders["shippings"][ords][1] != "None":
            ordinf = f'{ordinf}<br>{allOrders["shippings"][ords][1]}'
        else:
            pass
        # Add address 1 
        ordinf = f'{ordinf}<br>{allOrders["shippings"][ords][2]}'
        # If address 2...
        if allOrders["shippings"][ords][3] != "None":
            ordinf = f'{ordinf}<br>{allOrders["shippings"][ords][3]}'
        else:
            pass
        # add in city state zip
        try:
            ordinf = f'{ordinf}<br>{allOrders["shippings"][ords][4]}, {allOrders["shippings"][ords][5]} {allOrders["shippings"][ords][6]}</h5></div>'
        except:
            ordinf='</h5></div>'

        # Add all line items to a table
        singleline = allOrders["lineinfo"][ords][0]
        count = 1
        for x in singleline:
            tbody=f'{tbody}<tr><td scope="row"><strong>{count}</strong></td><td>{x}</td><td>{singleline[x][1]}</td></tr>'
            count+=1
        tbody = f'{tbody}</tbody></table></div>'
        # print("puttin together")///
        # Bring it all together
        soup = soup + logo + ordheader + ordinf + sg + thead + tbody
        if allOrders["notes"][ords] != "" and allOrders["notes"][ords] != None and allOrders["notes"][ords] != "None":
            if "\n" in allOrders["notes"][ords]:
                allOrders["notes"][ords].replace("\n"," - ")
            note = f'<p class=notes>{allOrders["notes"][ords]}</p>'
            soup = soup + note

        if allOrders["emails"][ords] != ""and allOrders["notes"][ords] != None and allOrders["notes"][ords] != "None":
            email = f'<p class=notes>{allOrders["emails"][ords]}</p>'
            soup = soup + email
        
        tags = '<p class=notes>'

        # if allOrders["custags"][ords] !="" and allOrders["custags"][ords] != "None" and allOrders["custags"][ords] != None:
        #     tags += f'{allOrders["custags"][ords]}, '

        # if allOrders["ordtags"][ords] !="" and allOrders["ordtags"][ords] != "None" and allOrders["ordtags"][ords] != None:
        #     tags += allOrders["ordtags"][ords]

        tags +='</p>'
        soup = soup + tags + pbreak
        ords+=1
    # print("that was fun")
    breakremove = len(soup) - len(pbreak)
    soup = soup[0:breakremove]
    soup = soup + "</body>"
    print("writing file")
    with open("static/output/"+ordr+".html", "w", encoding="utf-8") as f:
        f.write(soup)
    # print("opening")
    # webbrowser.open_new_tab("static/output/current_orders.html")

def puller(cat,pend,order,shopOrds):
    """
    cat == category you're looking for in shopify request
    pend == the place you're appending to
    order == the order?
    shopOrds == the big dictionary of orders
    """
    try:
        item = order[cat]
        if item == None or item == '':
            item = "None"
    except KeyError:
        item = "None"
    shopOrds[pend].append(item)

def shipPuller(cat,order,shipping):
    """
    cat == category you're looking for in shopify request
    order == the order
    shipping == the shipping list
    """
    try:
        item = order["shipping_address"][cat]
        if item == None or item == '':
            item = "None"
    except KeyError:
        item = "None"
    shipping.append(item)

def linePuller(x,shopOrds,z,sheetData,line):
    """
    x == the line item
    shopOrds
    z
    sheetData
    line
    """
    brrr = []
    name = x["name"]
    sku = x["sku"]
    if sku == None:
        sku = "None"
    qty = x["quantity"]
    brrr.append(sku)
    brrr.append(shopOrds["shippings"][z][0])
    brrr.append(shopOrds["ordnums"][z])
    brrr.append(name)
    brrr.append(qty)
    brrr.append("y")
    sheetData.append(brrr)
    line[name] = [sku,qty]

def ShopPull(mom):
    """
    mom == order number.
    If importing this function, it will only pull the order you choose.
    """
    import os, time, webbrowser, requests, gspread
    from bs4 import BeautifulSoup as Soup
    from  oauth2client.service_account import ServiceAccountCredentials
    from config import key, password, hostname, version, emPass
    from pprint import pprint

    print("\nOpening html template...")
    with open("static/template/order_template.html", "r") as f:
        soup= Soup(f, "html.parser")
        soup = str(soup)
        soup = soup[:-13]

    query_url = f'https://{key}:{password}@{hostname}.myshopify.com/admin/api/{version}/'
    order_print = 'fields=name,billing_address,shipping_address,contact_email,created_at,line_items,note,customer,tags'
    # Save all open orders into response

    if mom != 'Current_Orders':
        print("\nPulling a single order!")
        response = requests.get(f'{query_url}orders.json?name={mom}&status=open&fulfillment_status=unfulfilled&{order_print}&limit=250').json()
        response = response['orders']

    else:
        print("\nPulling all orders from Shopify")
        response = requests.get(f'{query_url}orders.json?status=open&fulfillment_status=unfulfilled&{order_print}&limit=250').json()
        response = response['orders']

    shopOrds = {
        "emails":[],
        "ordnums":[],
        "times":[],
        "notes":[],
        "custags":[],
        "ordtags":[],
        "shippings":[],
        "lineinfo":[]
    }
    sheetData = []
    z = 0
    print(f"\nlength of the orders is {len(response)}")
    for order in response:
        shipping = []
        lines = []
        line = {}
        shipinfo = ["name","company","address1","address2","city","province","zip"]
        # Fix format for created at and append
        created_at = (order["created_at"])
        created_date, created_time = created_at.split("T")
        created = (f"{created_date} at {created_time}")
        shopOrds["times"].append(created)
        # Get customer tags
        try:
            item = order["customer"]["tags"]
            if item == None or item == '':
                item = "None"
        except KeyError:
            item = "None"
        shopOrds["custags"].append(item)
        # Pull base info
        puller("contact_email","emails",order,shopOrds)
        # If this fails...
            # puller("order_number","ordnums")
        puller("name","ordnums", order, shopOrds)
        puller("note","notes", order, shopOrds)
        puller("tags","ordtags", order, shopOrds)
        # Pull shipping info
        for x in shipinfo:
            shipPuller(x, order, shipping)
        shopOrds["shippings"].append(shipping)
        # Pull line items 
        for lineitem in order["line_items"]:
            linePuller(lineitem, shopOrds, z, sheetData, line)
        lines.append(line)
        # print(lines)
        shopOrds["lineinfo"].append(lines)
        z+=1

    # Build the query
    print("\nConnecting to Google Sheets")
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)

    # Choose the sheet/worksheet that you will be working on
    # sheet = client.open("test").worksheet(ws)
    sheet = client.open('Roast Sheet 2.4.7')
    rows = "A"+str(len(sheet.worksheet('Shopify').col_values(1))+1)
    # print(sheetData)
    print("\nAdding data to Shopify page")
    sheet.values_update('Shopify!'+rows,params={'valueInputOption':'USER_ENTERED'},body={'values':sheetData})

    printer(shopOrds, soup, mom)

def singlePrint(ordr):
    """
    This pull from the Google sheet alone, and will create a new html doc of the order. 
    """
    import os, time, webbrowser, requests, gspread
    from bs4 import BeautifulSoup as Soup
    from  oauth2client.service_account import ServiceAccountCredentials
    from config import key, password, hostname, version, emPass
    from pprint import pprint

    # Build the query
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)

    # Choose the sheet/worksheet that you will be working on
    # sheet = client.open("test").worksheet(ws)
    sheet = client.open('Roast Sheet 2.4.7')
    rows = "A"+str(len(sheet.worksheet("Shopify").get_all_records())+2)
    shopvals = sheet.values_get(range="Shopify!A4:F")['values']

    line = {}
    for x in shopvals:
        if ordr in x[2]:
            line[x[3]] = [x[0],x[4]]

    with open("static/template/order_template.html", "r") as f:
        soup= Soup(f, "html.parser")
        soup = str(soup)
        soup = soup[:-13]

    query_url = f'https://{key}:{password}@{hostname}.myshopify.com/admin/api/{version}/'
    order_print = 'fields=name,billing_address,shipping_address,contact_email,created_at,line_items,note,customer,tags'
    # Save all open orders into response

    response = requests.get(f'{query_url}orders.json?name={ordr}&status=open&fulfillment_status=unfulfilled&{order_print}').json()
    response = response['orders']

    shopOrds = {
    "emails":[],
    "ordnums":[],
    "times":[],
    "notes":[],
    "custags":[],
    "ordtags":[],
    "shippings":[],
    "lineinfo":[]
    }
    z=0
    for order in response:
        shipping = []
        lines = []
        shipinfo = ["name","company","address1","address2","city","province","zip"]
        # Fix format for created at and append
        created_at = (order["created_at"])
        created_date, created_time = created_at.split("T")
        created = (f"{created_date} at {created_time}")
        shopOrds["times"].append(created)
        # Get customer tags
        try:
            item = order["customer"]["tags"]
            if item == None or item == '':
                item = "None"
        except KeyError:
            item = "None"
        shopOrds["custags"].append(item)
        # Pull base info
        puller("contact_email","emails",order,shopOrds)
        # If this fails...
            # puller("order_number","ordnums")
        puller("name","ordnums",order,shopOrds)
        puller("note","notes",order,shopOrds)
        puller("tags","ordtags",order,shopOrds)
        # Pull shipping info
        for x in shipinfo:
            shipPuller(x,order,shipping)
        shopOrds["shippings"].append(shipping)
        # Format line items from gsheets

        lines.append(line)
        # print(lines)
        shopOrds["lineinfo"].append(lines)
        z+=1

    printer(shopOrds, soup, ordr)

if __name__ == "__main__":  
    ShopPull("Current_Orders")
    # singlePrint("4929")

