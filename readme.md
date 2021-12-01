# Welcome to RoastingBot!

RoastingBot (RB) is a project I started in late 2019 that aimed to simplify and automate Coffee Production. It has been developed and tailored for Good Citizen Coffee Company, but the goal is to eventually be tailored to any roasting facility. 

In a given week, RoastingBot takes care of processing orders for 10,000+ lbs of coffee. RoastingBot automates pulling open orders, generating labels for each bag, creating packing slips, and updates the needed lbs for roasting in real time. 

This is RoastingBot's second iteration that uses a Google Sheet as the user interface. RoastingBot currently runs on an AWS Lightsail iteration, and awaits an email to trigger a function. 

<br>

The email must have one of the following subject lines to function:
- <b>"Clean Your Room"</b> - RB clears out all data from the Google Sheet.

- <b>"Go To Work"</b> - RB connects to Shopify using their REST API, pulls all open orders, creates packing slips for each order, generates the needed labels for 2lb or 5lb bags, and pushes the newly formatted data into the Google Sheet. 

- <b>"SinglePull 4298"</b> - RB pulls order 4298, creates the packing slip and labels, and pushes it to the Google Sheet. This is perfect for rush orders or orders that came in after the deadline. 

- <b>"Subby Wubby"</b> - RB downloads the attached CSV, totals up the quantity needed for each SKU, grind type, and size. RB then pushes the transformed data into the Google Sheet. 

- Subject contains <b>"Turnip Truck"</b> or <b>"Whole Foods"</b> - RB will download the order form (typically a pdf or html file), scrape the text and use REGEX to pull the order information. That information is then pushed to the Google Sheet. 

<br>
RoastingBot has a companion repository, <a href='https://github.com/bpdamore/RoastingComputer'>RoastingComputer</a>, that allows each coffee roaster to update the Google Sheet in real time when roasts are finished. The Google Sheet contains a tab dedicated to the total needed lbs for each coffee, and RB's extension, RoastingComputer, analyzes each roast sheet for the coffee, batch size, and roast operator. 

The coffee name extracted from the roast sheet is matched to the coffee name on the Google Sheet by calculating the Levenshtein distance. If the ratio between the two is 75 or greater, then it assumes a match. If not, it asks the operator to clarify the coffee they just roasted. 

<br>
RoastingBot is constantly growing as new needs make themselves known. When starting this project I had no idea the scope of functions that would be developed and automated. Check back for updates as time goes on! There might be new functions or improvements to the code.
