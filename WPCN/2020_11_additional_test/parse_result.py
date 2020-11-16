import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as seab

import sys
sys.path.insert(0, '../../AI_BASE')
import readData as RD

def main(fn):
    if fn == None: fn = input() # file name

    # read file
    f = open(fn, 'r')
    fl = f.readlines()
    f.close()

    # result array
    result = []

    # split data
    for i in range(len(fl)):
        thisLine = fl[i].split('\n')[0]

        # extract each column
        mapNo = int(thisLine.split(' ')[4])
        Y = float(thisLine.split('Y=')[1].split(' ')[0])
        X = float(thisLine.split('X=')[1].split(' ')[0])
        HT = float(thisLine.split('HT=')[1].split(']')[0])
        thrput = float(thisLine.split(' ')[9])
        maxThrput = float(thisLine.split(' ')[11])
        rate = float(thisLine.split('(')[1].split(' ')[0])

        result.append([mapNo, Y, X, HT, thrput, maxThrput, rate])

    # convert to dataFrame
    cols = ['mapNo', 'Y', 'X', 'HT', 'thrput', 'maxThrput', 'rate']
    df = pd.DataFrame(np.array(result), columns=cols)

    # print dataFrame
    print(df)

    # save data as file
    RD.saveArray(fn[:len(fn)-4] + '_data.txt', result)

    # display correlation
    # https://seaborn.pydata.org/generated/seaborn.clustermap.html
    dfCorr = df.corr() # get correlation
    seab.clustermap(dfCorr,
                    annot=True,
                    cmap='RdYlBu_r',
                    vmin=-1, vmax=1)
    plt.show()

if __name__ == '__main__':
    for size in [8, 12, 16]:
        for WDs in [6, 10]:
            main('DL_WPCN_forpaper_1_' + str(size) + '_' + str(WDs) + '_detail.txt')
