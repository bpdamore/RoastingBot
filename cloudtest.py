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

    # print("\nOpening html template...")
    # with open("static/template/order_template.html", "r") as f:
    #     soup= Soup(f, "html.parser")
    #     soup = str(soup)
    #     soup = soup[:-13]

    query_url = f'https://{key}:{password}@{hostname}.myshopify.com/admin/api/{version}/'
    order_print = 'fields=name,billing_address,shipping_address,contact_email,created_at,line_items,note,customer,tags'
    # Save all open orders into response

    if __name__ == "__main__":
        print("\nname is main")
        response = requests.get(f'{query_url}orders.json?status=open&fulfillment_status=unfulfilled&{order_print}&limit=250').json()
        response = response['orders']

    print(f'Number of orders : {len(response)}\n')
    print(response[0])

    # else:
    #     print("\nPulling all orders from Shopify")
    #     response = requests.get(f'{query_url}orders.json?status=open&fulfillment_status=unfulfilled&{order_print}&limit=250').json()
    #     response = response['orders']

    # shopOrds = {
    #     "emails":[],
    #     "ordnums":[],
    #     "times":[],
    #     "notes":[],
    #     "custags":[],
    #     "ordtags":[],
    #     "shippings":[],
    #     "lineinfo":[]
    # }
    # sheetData = []
    # z = 0
    # print(f"\nlength of the orders is {len(response)}")
    # for order in response:
    #     shipping = []
    #     lines = []
    #     line = {}
    #     shipinfo = ["name","company","address1","address2","city","province","zip"]
    #     # Fix format for created at and append
    #     created_at = (order["created_at"])
    #     created_date, created_time = created_at.split("T")
    #     created = (f"{created_date} at {created_time}")
    #     shopOrds["times"].append(created)
    #     # Get customer tags
    #     try:
    #         item = order["customer"]["tags"]
    #         if item == None or item == '':
    #             item = "None"
    #     except KeyError:
    #         item = "None"
    #     shopOrds["custags"].append(item)
    #     # Pull base info
    #     puller("contact_email","emails",order,shopOrds)
    #     # If this fails...
    #         # puller("order_number","ordnums")
    #     puller("name","ordnums", order, shopOrds)
    #     puller("note","notes", order, shopOrds)
    #     puller("tags","ordtags", order, shopOrds)
    #     # Pull shipping info
    #     for x in shipinfo:
    #         shipPuller(x, order, shipping)
    #     shopOrds["shippings"].append(shipping)
    #     # Pull line items 
    #     for lineitem in order["line_items"]:
    #         linePuller(lineitem, shopOrds, z, sheetData, line)
    #     lines.append(line)
    #     # print(lines)
    #     shopOrds["lineinfo"].append(lines)
    #     z+=1

    # # Build the query
    # print("\nConnecting to Google Sheets")
    # scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    # creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    # client = gspread.authorize(creds)

    # # Choose the sheet/worksheet that you will be working on
    # # sheet = client.open("test").worksheet(ws)
    # sheet = client.open('Roast Sheet 2.4.7')
    # rows = "A"+str(len(sheet.worksheet('Shopify').col_values(1))+1)
    # # print(sheetData)
    # print("\nAdding data to Shopify page")
    # sheet.values_update('Shopify!'+rows,params={'valueInputOption':'USER_ENTERED'},body={'values':sheetData})

    # printer(shopOrds, soup, mom)

if __name__ == "__main__":
    ShopPull('Current_Orders')