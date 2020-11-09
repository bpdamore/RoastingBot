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

sheet.values_clear('Shopify!A4:F')

# Clear out the Roast Sheet
rsz = [[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0]]
# Clears the Manual Add section, and then the Lbs Roasted section
sheet.values_update('Roast Sheet!C4:C50',params={'valueInputOption':'USER_ENTERED'},body={'values':rsz})
sheet.values_update('Roast Sheet!D4:D50',params={'valueInputOption':'USER_ENTERED'},body={'values':rsz})
# Clears the Total Blended section
sheet.values_update('Roast Sheet!C53:C54',params={'valueInputOption':'USER_ENTERED'},body={'values':[[0],[0]]})

# Clear out the Roast Calculator
rcz = [[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],['Manual Lbs'],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0]]
# Clears the values while also putting the header in there
sheet.values_update('Roast Calculator!I2:I55',params={'valueInputOption':'USER_ENTERED'},body={'values':rcz})
sheet.values_update('Roast Calculator!K2:K55',params={'valueInputOption':'USER_ENTERED'},body={'values':rcz})


