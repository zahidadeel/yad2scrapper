import requests
from bs4 import BeautifulSoup
import re
import logging

from .renderHtml import downloadHtml


LOG_FILENAME = 'webScrapper.log'
format = '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s[%(process)d]%(funcName)10s: %(message)s'
logging.basicConfig(filename=LOG_FILENAME, format=format, level=logging.DEBUG)
# logging.basicConfig(format=format, level=logging.DEBUG)
logger = logging.getLogger('detailsParser')

spaceMatcher = re.compile(r"\s+")
nondigitMatcher = re.compile("[^\d]")

proxies = {
    'http' : "http://176.123.164.26:8080",
    'https' : "https://176.123.164.26:8080"
}

targetUrl = "http://www.yad2.co.il/Nadlan/business.php?AreaID=&City=&Sale=&HomeTypeID=&fromSquareMeter=&untilSquareMeter=&fromPrice=1000&untilPrice=&PriceType=1&fromRooms=&untilRooms=&Info=&PriceOnly=1&Page={}"

headers = {

    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0"
}
rootUrl = "http://www.yad2.co.il"


def getHtmlDoc(url, proxies=None):
    session = requests.Session()
    if proxies:
        response = session.get(url, headers=headers, proxies=proxies)
    response = session.get(url, headers=headers, proxies=proxies)
    pageData = response.content

    return pageData


def getSoup(htmlDoc):
    '''
    Returns soup object for given htmlDoc
    '''
    try:
        soup = BeautifulSoup(htmlDoc, features="html5lib")
    except Exception as e:
        logger.error(e)
        return None

    return soup

def detailsDataTbl(htmlSoup):
    detailsDataTable = None
    detailsBlock = htmlSoup.select("div[class=details_block_296]")
    
    if detailsBlock and len(detailsBlock) == 2 :
        generalDetailsTbl = detailsBlock[0].select_one("table[class=innerDetailsDataGrid]")
        itemCheckDetailsTbl = detailsBlock[1].select_one("table[class=innerDetailsDataGrid]")
        
        detailsDataTable = (generalDetailsTbl, itemCheckDetailsTbl)

    return detailsDataTable

def checkedItemsPreprocessor(dataList):
    result = {}

    validFeatures = dataList.get('availableFeatures')
    invalidFeatures = dataList.get('notAvailableFeatures')

    for k in validFeatures:
        k = k.strip()
        result[k] = 1
    
    for k in invalidFeatures:
        k = k.strip()
        result[k] = 0

    return result

def getCheckedItems(dataTbl):
    result = {}
    if dataTbl:
        result['availableFeatures'] = [detailItem.parent.text for detailItem in dataTbl.findAll("div", attrs={"class":re.compile("v_checked")})]
        result['notAvailableFeatures'] = [detailItem.parent.text for detailItem in dataTbl.findAll("div", attrs={"class":re.compile("v_unchecked")})]

    return result

def moreDetailsPreprocessor(dataList):
    result = {}
    details = [item.split(":", 1) for item in dataList]

    for k, v in details:
        k = k.strip()
        v = v.strip()

        result[k] = v
    
    return result

def scrapCheckedItemSection(dataTbl):
    result = {}
    moreDetailsSection = dataTbl.parent.select("div div")

    detailsText = [item.text for item in moreDetailsSection]
    moreDetails = [spaceMatcher.sub(" ", txtItem).strip() for txtItem in detailsText]

    result.update(moreDetailsPreprocessor(moreDetails))
    checkedItemsData = checkedItemsPreprocessor( getCheckedItems(dataTbl))
    result.update(checkedItemsData)
    
    return result

def detailsPreprocessor(dataList):
    result = {}
    details = [item.split(":", 1) for item in dataList]

    for k, v in details:
        k = k.strip()
        v = v.strip()

        if (k == 'חדרים') or (k == 'גודל במ"ר'):
            normVal = nondigitMatcher.sub("", v)
            try:
                result[k] = float(normVal)
            except Exception as e:
                result[k] = normVal
        else:
            result[k] = v
    
    return result
    

def scrapGenericDetailSection(dataTbl):
    rawDataRecords = [record.text for record  in dataTbl.select("tr")]
    dataRecords = [spaceMatcher.sub(" ",record).strip() for record in rawDataRecords]

    return detailsPreprocessor(dataRecords)

def scrapDetailsData(url, delayInterval, useProxy):
    result = {}

    soup = None
    htmlDoc = downloadHtml(url, "details_block_296", delayInterval, useProxy)
    if htmlDoc:
        soup = getSoup(htmlDoc)
        generalDetailsTbl, itemCheckDetailsTbl  = detailsDataTbl(soup)

        checkedItemsData = scrapCheckedItemSection(itemCheckDetailsTbl)
        genericItemsData = scrapGenericDetailSection(generalDetailsTbl)

        result.update(checkedItemsData)
        result.update(genericItemsData)

        return result
    else:
        logger.info("[!]. Couldn't fetch HTML for given URL")
        return None
    

if __name__ == '__main__':
    url = "http://www.yad2.co.il/Nadlan/business_info.php?NadlanID=351369"
    print (scrapCheckedItemSection(url))