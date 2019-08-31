# Yad2scrapper
Real Estate Scrapper for scrapping data from YAD2 site (yad2.co.il).

# How to use it:
Run install.sh script like this:

    bash install.sh

It will setup all required depdendencies for the project. Once its done, try to use script for a single residential or commercial page.

# How to run it:
Main scrapper script is run.py which can be executed to scrap data from YAD2 for residential and commercial real-estates.

![alt text][scrapper-help]

[scrapper-help]: ./scrapper-help.png "Scrapper Help"

### Script supports two modes:
* Specific YAD2 commercial or residential url scrapping
* Scrap with a start and ending page number

### Examples:
1. Following example will launch firefox browser and scrape provided url. Here, `-p` flag will utilize proxies and `-t 3` flag will put delay of 3 seconds between making requests to fetched links.

    `python3 run.py -t 3 -p -u "http://www.yad2.co.il/Nadlan/business.php?AreaID=&City=&Sale=&HomeTypeID=&fromSquareMeter=&untilSquareMeter=&fromPrice=1000&untilPrice=&PriceType=1&fromRooms=&untilRooms=&Info=&PriceOnly=1&Page=1" sample.csv`

2. Following example will scrap a residential page

    `python3 run.py -e 2 -c sample.csv`

## Scrapper Features:
* Proxies support: Scrapper can use http proxies from `./db/proxies.txt` file which can be used
* Email support: Scrapped reports will be sent to configured email IDs. Email relevant configuration is available under `./db/email.yml`
* HTTP requests delay: `run.py -t` can be used for putting some delay between requests

## Sample Output:
I have included a sample csv output which contains a scrapped report.

[Download Sample Report here](./sample-output/sampleOutput-1-100-then-200-381.csv)