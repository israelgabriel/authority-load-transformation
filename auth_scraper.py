import sys
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Takes an unedited authority file (auth_file) from Marcive and isolates
# authority IDs from the file using regEx. It then takes the authority IDs
# and transforms each ID into a clickable link to the LOC website.

# To run from command line: python auth_scraper.py ncsaall###.txt

# VARIABLES USED:
# - authIDs_list: a list of all authority IDs beginning with "N" from auth_file
# - auth_lower_list: takes authIDs_list and lowercases it so that it is
#   compatible with the URL
# - authURL: URL string that prepends the scraped authority IDs
# - urlList: final list of URLs

def URL_list(auth_file):
    authIDs_list = re.findall("ID (N.*)", auth_file)
    authIDs_lower_list = [sub.lower() for sub in authIDs_list]
    authURL = 'https://id.loc.gov/authorities/names/'
    urlList = [authURL + i + '.html' for i in authIDs_lower_list]
    return urlList

# Takes the list of URLs from URL_list function and grabs the h1 heading
# text from each link in order to isolate the actual first and last names
# associated with each authority ID.

# VARIABLES USED:
# - url_list: a list of all authority IDs beginning with "N" from auth_file
# - new: empty list to be filled in with scraped list of name data and returned
#   from the function
# - url: each individual URL in url_list that is looped over
# - reqs: requests driver
# - soup: BeautifulSoup driver
# - heading: h1 headings from each link in url_list
# - name: each individual name stripped from heading

def name_list(url_list):
    new = []
    # Iterate through list of URLs
    for i in url_list:
        url = i
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, 'lxml')
        # Strip HTML from name header data
        for heading in soup.find_all(["h1"]):
            name = heading.text.strip()
            new.append(name)
    return new

# Takes the list of names from name_list and appends the {100} tag to each
# name in the list.

# VARIABLES USED:
# - name_list: List of names created from name_list function
# - new_list: New list of names with {100} appended
def add_100_tag(name_list):
    new_list = [name + " {100}" for name in name_list]
    return new_list

# Takes the list of names from name_list and appends the {700} tag to each
# name in the list.

# VARIABLES USED:
# - name_list: List of names created from name_list function
# - new_list: New list of names with {700} appended
def add_700_tag(name_list):
    new_list = [name + " {700}" for name in name_list]
    return new_list

# Transform links from URL list into clickable links
def fun(path):
    return '<a href="{}">{}</a>'.format(path, url)

################################## MAIN ########################################

# Open the file, save to text string
authFile = open(sys.argv[1], "rt")
contents = authFile.read()
authFile.close()

# Call functions and assign to variables
urlList = URL_list(contents)
nameList = name_list(urlList)
nameList_100 = add_100_tag(nameList)
nameList_700 = add_700_tag(nameList)

# Create a dataframe with assigned columns
df = pd.DataFrame()
df['URLs'] = urlList
df['Names'] = nameList
df['100 Tag'] = nameList_100
df['700 Tag'] = nameList_700
df['Done?'] = ''

# Applying URL cleanup function to authIDs column
df = df.style.format({'URLs' : fun})

# Convert to spreadsheet without indexing
df.to_excel('authority-ID-list.xlsx', index=False)
