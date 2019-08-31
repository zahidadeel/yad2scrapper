import pandas as pd
from glob import glob
import os
import shutil

# outputDir = "./output"
backDir = "./tmp"

listItems = ['moreDetails', 'availableFeatures', 'notAvailableFeatures', 'details']


def initDirs():
    try:
        if not os.path.exists(backDir):
            os.makedirs(backDir, exist_ok=True)
            print("[!]. Backup directory {} created successfully\n".format(backDir))
    except Exception as e:
        raise e


def dumpDataFile(data, pageNum, outFile="scrapped.csv"):
    try:

        df = pd.DataFrame(data)
        if pageNum == -1:
            df.to_csv(outFile, index=False)
            print ("[>]. Data inserted successfully in '{}'\n".format(outFile))
        else:
            bakFile = os.path.join(backDir, "{}.part{}".format(outFile, pageNum))
            df.to_csv(bakFile, index=False)

            print ("[>]. Data inserted successfully in '{}'\n".format(bakFile))
        
        return True

    except Exception as e:
        raise e

def prepareReport(outFile, sPageNum, ePageNum):
    dfs = []

    #search files
    globPattern = os.path.join(backDir, "{}.part*".format(outFile))

    fileParts = glob(globPattern)

    for filePart in fileParts:
        df = pd.read_csv(filePart, index_col=False, header=0)
        dfs.append(df)

    print("[!]. Merging {} part files to create a consolidated report\n".format(len(dfs)))
    try:
        finalDf = pd.concat(dfs, sort=False)
        
        finalDf.to_csv(outFile, index=False)

        print ("[>]. Data report generated successfully at filepath: '{}'\n".format(outFile))

    except Exception as e:
        raise e



