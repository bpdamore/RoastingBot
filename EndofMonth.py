def EndMonth(mon):
    import os, calendar
    import pandas as pd
    
    lastDay = str(mon)+"-"
    lastDay += str(calendar.monthrange(2020,int(mon))[1])

    data = pd.read_csv("report/sales.csv")
    df = data[['product_title','variant_sku','net_quantity']].copy()
    df['net_quantity'] = df['net_quantity'] * -1

    for i,r in df.iterrows():
        try:
            if "Bottomless Drip Plan" in r["product_title"]:
                print(r["product_title"])
                print(f"dropping row {i}\n")
                df.drop(i, inplace=True)
            elif "Shipping" in r["product_title"]:
                print(r["product_title"])
                print(f"dropping row {i}\n")
                df.drop(i, inplace=True)
            elif "Expedited Order Fee" in r["product_title"]:
                print(r["product_title"])
                print(f"dropping row {i}\n")
                df.drop(i, inplace=True)
            elif r['variant_sku'][-2:] == "CS":
                print(i)
                print(f"{r['product_title']} - {r['variant_sku']} - {r['net_quantity']}")
                df.at[i,"variant_sku"] = r["variant_sku"][:-2]+"WB"
                df.at[i,"net_quantity"] = r["net_quantity"]*6
            elif r['variant_sku'][-2:] == "GR":
                df.at[i,"variant_sku"] = r['variant_sku'][:-2]+"WB"
        except TypeError:
            pass

    sampDex = []
    df2 = df[df["product_title"].str.contains("Sample|sample")].copy()
    for i,r in df2.iterrows():
        sampDex.append(i)

    for i,r in df.iterrows():
        if i in sampDex:
            df.drop(i, inplace=True)

    df["External_ID"] = 800545
    df2["External_ID"] = 800546

    df.to_csv(f"report/eom_{lastDay}.csv", index=False)
    df2.to_csv(f"report/eom_{lastDay}_samp.csv", index=False)

EndMonth(10)