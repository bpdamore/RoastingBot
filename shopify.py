# This contains all of the shopify funcitons

def expediteMe():
    """
    Checks for expedited orders. If there are any, create the body of an email. 

    returns the body of the email.
    """
    import os, time, requests, json
    from  oauth2client.service_account import ServiceAccountCredentials
    from config import key, password, hostname, version, emPass
    from pprint import pprint

    # Load the ids of the orders that have already been checked
    with open("shipcheck.json","r") as f:
        processed = json.load(f)

    query_url = f'https://{key}:{password}@{hostname}.myshopify.com/admin/api/{version}/'
    order_print = 'fields=name,shipping_lines,id'
    # Save all open orders into response
    response = requests.get(f'{query_url}orders.json?status=open&{order_print}').json()
    response = response['orders']

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
            processed.append(x['id'])
            # pprint(x['id'])
            for y in x['shipping_lines']:
                if "Expedited" in y['title']:
                    if x['id'] not in expedited:
                        expedited.append(x['name'])
                        print(y['title'])
    if len(expedited) != 0:                    
        msg = f"Hey there! \n\nThe following Expedited orders were just placed! \n\n{expedited}\n\nLove,\n<3 RBCCO"
    else:
        msg = "nothing here"

    # Load the new list of processed orders back into the file for later. 
    with open("shipcheck.json", "w") as f:
        json.dump(processed,f)
    
    return msg

if __name__ == "__main__":
    from datetime import datetime
    import ezgmail
    import time

    run = "yes"
    minutes = ["15","30","45","00"]

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


    
