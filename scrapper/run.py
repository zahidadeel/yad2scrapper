#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from modules.indexParser import *
from modules.reportMaker import *
from argparse import ArgumentParser
from datetime import datetime
from modules.sendEmail import sendEmail
import os
import time
import re

LOG_FILENAME = 'webScrapper.log'
format = '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s[%(process)d]%(funcName)10s: %(message)s'
logging.basicConfig(filename=LOG_FILENAME, format=format, level=logging.DEBUG)
# logging.basicConfig(format=format, level=logging.DEBUG)
logger = logging.getLogger('webScrapper')

urlMatcher = re.compile(r'https?://[^/]+')
ts = time.time()
timeStamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H:%M:%S')

def validateUrl(url):
    if urlMatcher.search(url):
        return True
    return False


parser = ArgumentParser(description='Scrap data from YAD')
parser.add_argument('filename', help='output filename')
parser.add_argument('-u', '--url', dest='inputUrl', help='Provide a custom input URL for scraping')
parser.add_argument('-s', '--start-page', type=int, dest='sPageNum', default=1, help='Provide the start page number from where you want to start scrapping')
parser.add_argument('-e', '--end-page', type=int, dest='ePageNum', help='Provide the last page number upto which you want to do scrapping')
parser.add_argument('-p', '--use-proxy', dest='useProxy', action='store_true', help='Enable proxy support for scrapping. Proxies are picked up from proxies configuration file "./db/proxies.txt"')
parser.add_argument('-t', '--use-delay', dest='delayInterval', type=int, help='Provide a sleep delay for which program will sleep before launching every HTTP request')
parser.add_argument('-C', '--cleanup', dest='cleanup', action='store_true', help='Perform a cleanup operation to remove temporary files')

group = parser.add_mutually_exclusive_group()
group.add_argument('-r', '--residential', dest='isResidential', action='store_true', help="Start scrapping using default residential URL")
group.add_argument('-c', '--commercial', dest='isCommercial', action='store_true', help="Start scrapping using default commercial URL")


args = parser.parse_args()
filename = args.filename
sPageNum = args.sPageNum
ePageNum = args.ePageNum
useProxy = args.useProxy
delayInterval = args.delayInterval
inputUrl = args.inputUrl
doCleanup = args.cleanup

isResidential = args.isResidential
isCommercial = args.isCommercial

if (not inputUrl) and (not (isCommercial or isResidential)):
    print("[!]. Please provide scrapping type either -r or -c\n")
    exit(1)


if inputUrl:
    inputUrl = inputUrl.strip()
    if not validateUrl(inputUrl):
        print ("[ERROR]. URL pattern doesn't seem right")
        exit(1)

print ("\n")



if not inputUrl:

    if sPageNum and (not ePageNum):
        print("[!]. End page number is not mentioned so only starting page number will be scrapped\n")
        ePageNum = sPageNum

    if sPageNum > ePageNum:
        print("[ERROR]. Start page number should be lesser than ending page number\n")
        exit(1)

    if ePageNum and (not sPageNum):
        print ("[!]. Please provide start page number as well\n")
        exit(1)
elif inputUrl:
    print("[!]. Start and End page ranges are ignored in case of custom URL\n")
if useProxy:
    print("[>]. Firefox proxy profile enabled\n")

if delayInterval:
    print("[>]. Configured a {} seconds delay for each HTTP request\n".format(delayInterval))

outFile = "{}-{}.csv".format(filename, timeStamp)

print("[!]. Task launched at '{}'".format(timeStamp))

targetUrl = None
isFirstPage = True
exceptionCount = 0

#initialize output directories
initDirs()

rawTargetUrl = "http://www.yad2.co.il/Nadlan/sales.php?multiSearch=1&AreaID=&City=&HomeTypeID=&fromRooms=&untilRooms=&fromPrice=50000&untilPrice=&PriceType=1&fromSquareMeter=&untilSquareMeter=&FromFloor=&ToFloor=&Info=&PriceOnly=1&Order=price&Page={}"

if isCommercial:
    rawTargetUrl = "http://www.yad2.co.il/Nadlan/business.php?AreaID=&City=&Sale=&HomeTypeID=&fromSquareMeter=&untilSquareMeter=&fromPrice=1000&untilPrice=&PriceType=1&fromRooms=&untilRooms=&Info=&PriceOnly=1&Page={}"
    
elif isResidential:
    rawTargetUrl = "http://www.yad2.co.il/Nadlan/sales.php?multiSearch=1&AreaID=&City=&HomeTypeID=&fromRooms=&untilRooms=&fromPrice=50000&untilPrice=&PriceType=1&fromSquareMeter=&untilSquareMeter=&FromFloor=&ToFloor=&Info=&PriceOnly=1&Order=price&Page={}"


exceptionIDs = []
if not inputUrl:

    for pageNum in range(sPageNum, ePageNum +1):
        
        targetUrl = rawTargetUrl.format(pageNum)
        print("[>]. Scrapping Page {}: {}\n".format(pageNum, targetUrl))

        try:
            outputData = scrapUrlData(targetUrl, useProxy, delayInterval)

        except Exception as e:
            exceptionCount += 1
            exceptionIDs.append(pageNum)
            print(e)
            print ("[!]. Exception happened at page {}".format(pageNum))
        
        print("[!]. Dumping data into output file")
        fileGenerated = dumpDataFile(outputData, pageNum, outFile=outFile)

    #prepare report by joining all part files
    prepareReport(outFile, sPageNum, ePageNum)

    #cleanup data
    if doCleanup:
        print("[!]. Performing a cleanup operations at path: {}".format(backDir))

elif inputUrl:
    targetUrl = inputUrl
    print("[>]. Scrapping Url: {}\n".format(targetUrl))

    try:
        outputData = scrapUrlData(targetUrl, useProxy, delayInterval)

    except Exception as e:
        print(e)
    
    
    print("[!]. Dumping data into output file")
    fileGenerated = dumpDataFile(outputData, -1, outFile=outFile)


endTime = time.time()
endTimeStamp = datetime.fromtimestamp(endTime).strftime('%Y-%m-%d-%H:%M:%S')

if os.path.exists(outFile):
    if inputUrl:
        sendEmail(outFile,1 ,1, timeStamp, endTimeStamp)
    else:
        sendEmail(outFile, sPageNum, ePageNum, timeStamp, endTimeStamp)


# endTimeStamp = datetime.fromtimestamp(endTime).strftime('%Y-%m-%d-%H:%M:%S')
print("[!]. Task launched at '{}'\n".format(endTimeStamp))
print ("[!]. Total encountered Exceptions: {}".format(exceptionCount))
print ("[!]. Encountered Exception IDs: {}".format(', '.join(exceptionIDs)))
