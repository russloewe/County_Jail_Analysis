# Filename: jail_scraper.py
# Author: @russl_corey <russl_corey@proton.me>
# Date: Mar 10, 2023
# 
# This program is free software: you can redistribute it and/or modify it under 
# the terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later 
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY 
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
# PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with 
# this program. If not, see <https://www.gnu.org/licenses/>. 


# importing the libraries
from bs4 import BeautifulSoup
import csv
import requests
from urllib.parse import urlencode
import os.path
import re



fake_headers = {'Content-Type': 'application/x-www-form-urlencoded',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36',
'Referer': 'https://coeapps.eugene-or.gov/EPDDispatchLog/Search'
}

def format_inmate_req(inmate):
    # Format data object for the Jail's API
    values = {'BookingNumber': inmate}
    data = urlencode(values)
    return(data)

def parse_inmate_info(table):
    # Parse key/value pairs from html table
    booking_data = {}
    rows = tables[0].findAll('tr')
    for row in rows:
        cells = row.findAll('td')
        for cell in cells:
            try:
                attr = cell.find('span').text.strip()
                val = cell.find('strong').text.strip()
                booking_data[attr] = val
            except:
                pass
    return(booking_data)

def parse_charges(table):
    # Extract charges data from the table
    rows = table.findAll('tr')
        
    # create empty list to hold all inmate charges
    charges = []
    charge = None
    for row in rows:
        # Violation is the first entry for each charge. 
        # If charge is not None, then this is start of 
        # next charge on the list.
        if re.search(r"Violation:", row.text):
            # parse violation description
            val = row.find('strong').text.strip()
            
            # save current charge to charge list unless empty
            if charge is not None:
                charges.append(charge)
            
            # start new charge dict
            charge = {'Violation:': val, 'full name': name,
                        **booking_data}
        else:
            # Parse rest of key/value pairs
            cells = row.findAll('td')
            for cell in cells:
                try:
                    attr = cell.find('span').text.strip()
                    val = cell.find('strong').text.strip()
                    charge[attr] = val
                except Exception as e:
                    pass
    
    # Add the last charge to charge list
    charges.append(charge)
    
    return(charges)

# main function
if __name__ == "__main__":

    # URL of the web app
    url ="http://inmateinformation.lanecounty.org/Home/BookingSearchDetail"
    
    # run from current highest known booking number backwards.
    for inmate in range(23001767, 23001767-3, -1):
        # clear inmate's name at begining of loop
        name = None
        
        # format request data
        data = format_inmate_req(inmate)           
        
        # make request
        try:
            r = requests.post(url, data=data,  headers=fake_headers)
        except Exception:
            print(f'error requesting: {inmate}, skipping')
            continue
        
        # Parse html
        soup = BeautifulSoup(r.text,"lxml")
        mydivs = soup.find_all("div", {"class": "panel-heading"})
        tables = soup.find_all("table")
        
        # stop and skip to next booking number if there're less than two tablse
        if(len(tables) < 2):
            print(f'no table data for {inmate}')
            continue
        
        # parse inmate name from table header
        try:
            for div in mydivs:
                name_str = str(div.find('h4').text)
                name = re.search("[A-Z\s-]+(?=\sIN CUSTODY)", name_str).group().strip()
                name = " ".join(name.split())
                break
        except:
            print('Unable to parse inmate name')
            continue

        # Parse inmate and booking data
        booking_data = parse_inmate_info(tables[0])
        
        # Extract charges data from the table
        charges = parse_charges(tables[1])
        
        # Update user
        print(f'{inmate}: {name}, charges: {len(charges)}')
        
        # Write the data to a CSV file
        filename = f"/home/russell/Documents/scrape_jail/bookingid_{inmate}.csv"
        
        # Get fieldnames from all charges
        unique_keys = set().union(*(d.keys() for d in charges))
        
        # Open and write out to csv file
        with open(filename, 'w', newline='\n') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=unique_keys )
            writer.writeheader()
            for row in charges:
                writer.writerow(row)

     
