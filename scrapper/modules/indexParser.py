# -*- coding: utf-8 -*-
import requests
import sys
from bs4 import BeautifulSoup
import re
import logging
from .renderHtml import downloadHtml
from .detailsParser import scrapDetailsData
import json
from datetime import datetime
import time


LOG_FILENAME = 'webScrapper.log'
format = '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s[%(process)d]%(funcName)10s: %(message)s'
logging.basicConfig(filename=LOG_FILENAME, format=format, level=logging.DEBUG)
# logging.basicConfig(format=format, level=logging.DEBUG)
logger = logging.getLogger('indexParser')

recordMapping = ['property_type', 'region', 'address', 'price', 'rooms', 'floor', 'date']
recordOriginals = ['סוג הנכס', 'אזור בארץ', 'כתובת', 'מחיר', "חד'", 'קומה', 'תאריך']

propertyTypeMap = {"sales":"Residential", "business":"Commercial"}

nondigitMatcher = re.compile("[^\d]")
propertyIdMatcher = re.compile(r'(\?NadlanID=(?P<propertyID>[^\s&]+))')
pageNameFinder = re.compile(r'(sales|business)\.php\?')
currencyMap = "./db/currencyMap.json"

currencyMapData = None
currencySymbols = None

try:
    with open(currencyMap, 'r') as f:
        currencyJsonData = f.read()
        currencyMapData = json.loads(currencyJsonData)
        currencySymbols = currencyMapData.keys()
        
except Exception as e:
    logger.error("Currency mapping couldn't be parsed")
    sys.exit(1)


proxies = {
    'http' : "socks5://127.0.0.1:9050",
    'https' : "socks5://127.0.0.1:9050"
}

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0"
}
rootUrl = "http://www.yad2.co.il"


def getSoup(htmlDoc):
    '''
    Returns soup object for given htmlDoc
    '''
    soup = None
    try:
        soup = BeautifulSoup(htmlDoc, features="html5lib")
    except Exception as e:
        raise e

    return soup

def getTableRowsData(soup):
    dataRows = []
    dataTbls = soup.select("div[class='main_table_wrap'] table[class='main_table']")

    if dataTbls:
        for dataTbl in dataTbls:
            dataRows.extend([dataTbl.findAll("tr", attrs={'class':"showPopupUnder"})])
    else:
        logger.error("It seems none could be parsed from data tables")
        sys.exit(1)
    return dataRows
    
def getDetailsLink(rowSoup):
    lastTdData = rowSoup.select("td")[-1]

    detailsPageHref = lastTdData.find('a').attrs.get('href')
    detailsPageUrl = "{}{}".format(rootUrl, detailsPageHref)
    
    return detailsPageUrl

def getIndexRecords(url, useProxy, delayInterval):
    logger.info("Fetching records from index page")
    htmlDoc = downloadHtml(url, "main_table_wrap", delayInterval, useProxy)
    logger.info("Fetched records from index page")

    soup = getSoup(htmlDoc)
    dataRows = getTableRowsData(soup)

    return dataRows

def getCurrencyName(dataStr):
    for symbol in currencySymbols:
        if symbol in dataStr:
            return currencyMapData.get(symbol)

    return "N/A"

def getPropertyId(url):
    propertyID = None

    if url:
        propertyIDResult = propertyIdMatcher.search(url)
        if propertyIDResult:
            propertyID = propertyIDResult.group('propertyID')
    
    return propertyID


def getPropertyType(url):
    propertyCategory = None
    result = None

    if url:
        result = pageNameFinder.search(url)

        if result:
            propertyCategory = result.group(1)

    return propertyTypeMap.get(propertyCategory)

def getCurrentTime():
    currentTime = time.time()
    
    timeStamp = datetime.fromtimestamp(currentTime).strftime('%Y-%m-%d-%H:%M:%S')
    return timeStamp

def getRecordDetails(rowItem, tableNum, delayInterval, useProxy):
    detailsResult = {}
    scrapedData = None

    detailsResult['detailsLink'] = getDetailsLink(rowItem)
    scrapedData = scrapDetailsData(detailsResult['detailsLink'], delayInterval, useProxy)
    if not scrapedData:
        return None

    detailsResult['scrapped_on'] = getCurrentTime()
    detailsResult['propertyID'] = getPropertyId(detailsResult['detailsLink'])

    detailsResult.update(scrapedData)

    rawRowRecords = rowItem.findAll("td", attrs={"onclick":re.compile("^setFeed_place")})
    if rawRowRecords:
        rowRecords = [record.text.strip() for record in rawRowRecords]
        if (tableNum == 2) and (not rowRecords[-2]):
            del(rowRecords[-2])
    
    for (itemTitle, itemVal) in zip(recordOriginals, rowRecords):
        
        if itemTitle == 'מחיר':
            detailsResult["currency"] = getCurrencyName(itemVal)
            
            pricing = nondigitMatcher.sub("", itemVal)
            try:
                detailsResult[itemTitle] = float(pricing)
            except Exception as e:
                detailsResult[itemTitle] = pricing
        else:
            detailsResult[itemTitle] = itemVal
    
    
    priceVal = detailsResult.get('מחיר')
    sqmVal = detailsResult.get('גודל במ"ר')

    try:
        PPM = round(priceVal / sqmVal, 4)
    except Exception as e:
        logger.error("unable to calculate PPM for price:{} and SQM:{}".format(priceVal, sqmVal))
        PPM = "N/A"

    detailsResult['PPM'] = PPM
    return detailsResult

def getOneRowData(url, dataQueue, row, counter, tblCount, propertyType, delayInterval, useProxy):
    rowDetails = None

    if tblCount == 1:
        logger.info("[>]. Parsing 'Real Estate Business' data records for row: {}".format(counter))
    elif tblCount == 2:
        logger.info("[>]. Parsing 'Commercial Real Estate' data records for row: {}".format(counter))

    if propertyType == "Residential":
        rowDetails = getRecordDetails(row, 2, delayInterval, useProxy)

    elif propertyType == "Commercial":
        rowDetails = getRecordDetails(row, tblCount, delayInterval, useProxy)

    if rowDetails:
        rowDetails['targetUrl'] = url
        rowDetails['propertyType'] = propertyType
        
    return dataQueue.put({counter: rowDetails})

def scrapUrlData(url, useProxy, delayInterval):
    outputData = []
    dataTabls = getIndexRecords(url, useProxy, delayInterval)

    counter = 0
    tblCount = 0
    propertyType = getPropertyType(url)
    for dataRows in dataTabls:
        tblCount += 1
        if dataRows:

            #TODO apply multiprocessing here
            outputData = getOneRowData(url, dataRows[0], 1, tblCount, propertyType, delayInterval, useProxy)
        

        else:
            if tblCount == 1:
                logger.info("[!]. Parsing 'Real Estate Business' data table seems to be empty")
            elif tblCount == 2:
                logger.info("[!].'Commercial Real Estate' data table seems to be empty")


    return outputData

if __name__ == '__main__':

    targetUrl = "http://www.yad2.co.il/Nadlan/business.php?AreaID=&City=&Sale=&HomeTypeID=&fromSquareMeter=&untilSquareMeter=&fromPrice=1000&untilPrice=&PriceType=1&fromRooms=&untilRooms=&Info=&PriceOnly=1&Page={}"

    # htmlDoc = downloadHtml(targetUrl.format(1), "main_table_wrap")
