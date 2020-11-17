def draftOrds():
    from pprint import pprint
    from config import key, password, hostname, version, emPass
    import time, webbrowser, requests

    query_url = f'https://{key}:{password}@{hostname}.myshopify.com/admin/api/{version}/'

    # Getting the open draft orders
    # response = requests.get(f"{query_url}draft_orders.json?status=open").json()
    response = requests.get(f"{query_url}draft_orders.json?updated_at_min=2020-11-01&status=open").json()

    time.sleep(2)

    query = response["draft_orders"]

    id_list = []
    for x in query:
            if "CML_order" in x["tags"]:
                id_list.append(x["id"])
            else:
                pass
                
    # print(id_list)

    go_list = []
    for id in id_list:
        print(id)
        for draft in query:
            if id == draft["id"]:
                # if draft["customer"]["first_name"] == "Brandino":
                print(f"{draft['customer']['first_name']} {draft['customer']['last_name']}")
                print(draft["created_at"])
                go_list.append(id)
    # print(go_list)

    for x in go_list:
        requests.put(f"{query_url}draft_orders/{x}/complete.json?payment_pending=true")
        print(f"Order {x} is now live!")

if __name__ == "__main__":
    draftOrds()
