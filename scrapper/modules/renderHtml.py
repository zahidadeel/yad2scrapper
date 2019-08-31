# -*- coding: utf-8 -*-
import os
import random
import logging
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

LOG_FILENAME = 'webScrapper.log'
format = '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s[%(process)d]%(funcName)10s: %(message)s'
logging.basicConfig(filename=LOG_FILENAME, format=format, level=logging.DEBUG)
# logging.basicConfig(format=format, level=logging.DEBUG)
logger = logging.getLogger('htmlRenderer')


proxiesFile = "./db/proxies.txt"

def loadProxies(fname):
    try:
        if not os.path.exists(fname):
            print("[ERROR]: Proxies file './db/proxies.txt' seems to be missing")
            exit(1)

        with open(fname, 'r') as f:
            proxies = f.readlines()

        proxies = [line.strip() for line in proxies]
        
        if not proxies:
            print("Warning: Proxies file './db/proxies.txt' seems to be empty")
        return proxies

    except Exception as e:
        raise e
        exit(1)    

def getProxy():
    proxies = loadProxies(proxiesFile)
    chosenProxy = random.choice(proxies)
    print ("Chosen Proxy: {}".format(chosenProxy))
    proxyHost, proxyPort = chosenProxy.split(":")

    return (proxyHost, int(proxyPort))

def prepProxyProfile(proxyHost, proxyPort):
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.http", proxyHost)
    profile.set_preference("network.proxy.http_port", proxyPort)
    profile.set_preference("network.proxy.ssl", proxyHost)
    profile.set_preference("network.proxy.ssl_port", proxyPort)
    profile.update_preferences()

    return profile

def downloadHtml(url, classTag, delayInterval, useProxy=False):
    htmlDoc = None
    options = Options()
    # options.add_argument("--headless")

    if useProxy:
        proxyHost, proxyPort = getProxy()
        if (proxyHost and proxyPort):
            logger.info("[>]. Firefox proxy profile enabled for proxy:{}:{}".format(proxyHost,proxyPort))
            driver = webdriver.Firefox(firefox_profile=prepProxyProfile(proxyHost, proxyPort), firefox_options=options)
        else:
            logger.info("Something is wrong with proxy Host or Port where Host:{} and Port:{}".format(proxyHost, proxyPort))
    else:
        driver = webdriver.Firefox(firefox_options=options)

    if delayInterval:
        logger.info("[!]. Program is sleeping for {} seconds".format(delayInterval))
        time.sleep(delayInterval)
    try:
        driver.get(url)
    except Exception as e:
        return None
        
    headText = None
    try:
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, classTag)))
        htmlDoc = driver.find_element_by_tag_name('html').get_attribute('innerHTML')

    except:
        
        try:
            headText = driver.find_element_by_class_name('msg-head')
        except:
            pass
        logger.error("Something went wrong here")
        if headText:
            print("Message: {}".format(headText.text))
        
    finally:

        driver.quit()
        # if headText:
            

    return htmlDoc

def writeFile(fname, data):
    try:
        with open(fname, 'wb') as f:
            f.write(data)
            logger.info("File generated successfully")
    except Exception as e:
        raise e

if __name__ == '__main__':
    pass
