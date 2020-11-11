import pandas as pd
import numpy as np


def zigzag(df, minSegSize=1,sizeInDevs=10):
    
    dfSeries = df.copy().reset_index().close
    minRetrace = minSegSize
    direction = []

    curVal = dfSeries[dfSeries.index[0]]
    curPos = dfSeries.index[0]
    curDir = 1
    #dfRes = pd.DataFrame(np.zeros((len(dfSeries.index), 2)), index=dfSeries.index, columns=["Dir", "Value"])
    dfRes = pd.DataFrame(index=dfSeries.index, columns=["Dir", "Value"])
    #print(dfRes)
    #print(len(dfSeries.index))
    for ln in dfSeries.index:
        if((dfSeries[ln] - curVal)*curDir >= 0):
            curVal = dfSeries[ln]
            curPos = ln
            #print(str(ln) + ": moving curVal further, to " + str(curVal))
        else:      
            retracePrc = abs((dfSeries[ln]-curVal)/curVal*100)
            #print(str(ln) + ": estimating retracePrc, it's " + str(retracePrc))
            if(retracePrc >= minRetrace):
                #print(str(ln) + ": registering key point, its pos is " + str(curPos) + ", value = " + str(curVal) + ", dir=" +str(curDir))
                dfRes.at[curPos, 'Value'] = curVal
                dfRes.at[curPos, 'Dir'] = curDir
                direction.append((curPos, curDir*-1))
                curVal = dfSeries[ln]
                curPos = ln
                curDir = -1*curDir
                #print(str(ln) + ": setting new cur vals, pos is " + str(curPos) + ", curVal = " + str(curVal) + ", dir=" +str(curDir))
        #print(ln, curVal, curDir)
    dfRes[['Value']] = dfRes[['Value']].astype(float)
    dfRes.at[dfSeries.index[0], 'Value'] = dfSeries[dfSeries.index[0]]
    dfRes.at[dfSeries.index[-1], 'Value'] = dfSeries[dfSeries.index[-1]]
    dfRes.Value.interpolate(method='linear', inplace=True)
    
    df = join(df, direction)
    return df, dfRes


def join(df, signal):
    signal = pd.DataFrame(signal, index=[i[0] for i in signal]).drop(columns=0)
    df = df.reset_index().join(signal).set_index("index", drop=True)
    return df