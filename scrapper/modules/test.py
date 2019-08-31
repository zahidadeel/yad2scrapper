from indexParser import *
from detailsParser import *

rawTargetUrl = "http://www.yad2.co.il/Nadlan/sales.php?multiSearch=1&AreaID=&City=&HomeTypeID=&fromRooms=&untilRooms=&fromPrice=50000&untilPrice=&PriceType=1&fromSquareMeter=&untilSquareMeter=&FromFloor=&ToFloor=&Info=&PriceOnly=1&Order=price&Page={}"

# url = "http://www.yad2.co.il/Nadlan/tivbusiness_info.php?NadlanID=212776"
url = rawTargetUrl.format(1)

delayInterval = None
useProxy = False

htmlDoc = downloadHtml(url, "details_block_296", False, False)
soup = getSoup(htmlDoc)
generalDetailsTbl, itemCheckDetailsTbl  = detailsDataTbl(soup)

checkedItemsData = scrapCheckedItemSection(itemCheckDetailsTbl)
genericItemsData = scrapGenericDetailSection(generalDetailsTbl)