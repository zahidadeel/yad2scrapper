import pandas as pd
from glob import glob
import os
import shutil

def prepareReport(outFile, dirPath, filePattern=None):
    dfs = []

    #search files
    if filePattern:
        
        globPattern = os.path.join(dirPath, filePattern)

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


if __name__ == '__main__':
    prepareReport("finalReport-1-100-then-200-381.csv", "./tmp/", "*.csv*")
