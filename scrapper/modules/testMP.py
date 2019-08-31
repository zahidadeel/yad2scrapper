# -*- coding: utf-8 -*-
import multiprocessing
from time import sleep
from multiprocessing import Queue, Process
import time

dataQueue = Queue()

from indexParser import *
from detailsParser import *

rawTargetUrl = "http://www.yad2.co.il/Nadlan/sales.php?multiSearch=1&AreaID=&City=&HomeTypeID=&fromRooms=&untilRooms=&fromPrice=50000&untilPrice=&PriceType=1&fromSquareMeter=&untilSquareMeter=&FromFloor=&ToFloor=&Info=&PriceOnly=1&Order=price&Page={}"

url = rawTargetUrl.format(1)

delayInterval = None
useProxy = False

dataTabls = getIndexRecords(url, useProxy, delayInterval)
tableOne = dataTabls[0]
propertyType = getPropertyType(url)

# tableOne = tableOne[:4]
dataQueue = Queue()
processes = []
tableOneClone = tableOne.copy()

beforeTime = time.time()
while tableOne:
    if (len(multiprocessing.active_children()) < 5) and (tableOne):
        rowData = tableOne.pop()
        rowIndex = tableOneClone.index(rowData)
        p = Process(target=getOneRowData, args=(url, dataQueue, rowData, rowIndex, 1, propertyType, delayInterval, useProxy))
        p.start()
        processes.append(p)

for p in processes:
    p.join()

elapsedTime = time.time() - beforeTime
print(elapsedTime)
while dataQueue dataQueue.get())