# This should go through each labe, check for the old css and change it to the new one
import os

def run():
    # Put new link here
    new = '<link href="https://cdn.shopify.com/s/files/1/0040/9272/3318/files/labestyle.css?v=1617857070" rel="stylesheet"/>'

    # 2lbs first
    os.chdir('sg/2lb/')
    labechanger(new)

    # 5lbs next
    os.chdir('../2lb/')
    labechanger(new)

def labechanger(new):
    '''
    new = the new css path including link html tags
    '''
    for f in os.listdir():
        if "html" in f.lower():
            with open(f,'r') as labe:
                htm = labe.read()
                print(labe.name)
            try:
                one,two=htm.split('<link href="https://cdn.shopify.com/s/files/1/0040/9272/3318/files/labestyle.css" rel="stylesheet"/>')
            except ValueError:
                try:
                    one,two=htm.split('<link href="labestyle.css" rel="stylesheet"/>')
                except ValueError:
                    try:
                        one,two=htm.split('<link href="https://cdn.shopify.com/s/files/1/0040/9272/3318/files/labestyle.css?v=1617857070" rel="stylesheet"/>')
                    except Exception as err:
                        print(f"ERROR\n{err}")
            htm = one+new+two
            with open(f,'w') as labe:
                labe.write(htm)

if __name__ == "__main__":
    print("Changing Labes to reference a new css!\n\n")
    run()

