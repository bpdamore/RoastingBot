#Probably don't need all these but oh well
import os,PyPDF2,re,ezgmail,time,shutil,json
from datetime import datetime
from bs4 import BeautifulSoup as Soup
from sys import platform
import pandas as pd
from ShopifyPull import ShopPull,singlePrint
import trade
from LabelPrint import LabelPrinter
import draftBatch
from shopify import expediteMe,cleanShop
# Import G-sheet stuff
import gspread
from  oauth2client.service_account import ServiceAccountCredentials



if __name__ == "__main__":  
    # date = input("What date do you want on the labels?\n\ndd/dd/dd plz\n\n... ")
    
    date = '04/01/21'
    datasheet = 'fix'

    # ezgmail.init()
    # time.sleep(5)

    # datasheet = input("What is the name of the sheet with the data?\n\n... ")

    # Get data from the sheet specified
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open('Roast Sheet 2.4.7')
    shopvals = sheet.values_get(range=f"{datasheet}!A4:F")['values']

    LabelPrinter(date, shopvals)

