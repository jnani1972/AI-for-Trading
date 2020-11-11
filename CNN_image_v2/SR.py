import pandas as pd
import numpy as np
import mplfinance as mpf
pd.options.mode.chained_assignment = None  # default='warn'

# Main SR Function
def sr(df_main, lookback):
    levels = []
    df_main["s"] = 0
    df_main["r"] = 0
    
    # reset index to make indexing easier, restore it at return
    df_main = df_main.copy().reset_index()
    df = df_main[-lookback:].copy()

    # average candle size - this isn't being used at the moment
    #s =  np.mean(df['high'] - df['low'])

    # Get S/R candles using fractals
    for i in df.index[2:-3]:
        
        if isSupport(df,i):
            df.loc[i,"s"] = 1
            l = df['low'][i]
            levels.append((i,l))
        
        elif isResistance(df,i):
            df.loc[i,"r"] = 1
            l = df['high'][i]
            levels.append((i,l))            
    
    # get the key levels
    df = KeyLevels(df, levels, df_main)
    
    # convert all zeros before a level was created to np.nan so the lines doesn't print on the graph
    df = df.replace(0,np.nan)
    
    return df.set_index("index", drop=True)

# get levels based on fractals
def isSupport(df,i):
  support = df['low'][i] < df['low'][i-1]  and df['low'][i] < df['low'][i+1] and df['low'][i+1] < df['low'][i+2] and df['low'][i-1] < df['low'][i-2]
  return support
def isResistance(df,i):
  resistance = df['high'][i] > df['high'][i-1]  and df['high'][i] > df['high'][i+1] and df['high'][i+1] > df['high'][i+2] and df['high'][i-1] > df['high'][i-2]
  return resistance
    
###### filter for key levels based on how many times the level was broken
def KeyLevels(df, levels, df_main):

    # First 
    # get a count of how many times each level was broken
    imp = []
    for level in levels:
        # levels contains the level and the candle which is was first formed. Only look for breaks after that candle, not before.
        candle = level[0]
        level = level[1]
        brokenCount = 0
        for i in range(candle,df.index[-1]-1):
            #down break - if first bar breaks and closes below level and second bar closes below level.
            if (df.open[i] > level and df.close[i] < level) and df.close[i+1] < level:
                brokenCount += 1

            #up break - if first bar breaks and closes above level and second bar closes above level.
            if (df.open[i] < level and df.close[i] > level) and df.close[i+1] > level:
                brokenCount +=1
                
        imp.append((candle, level, brokenCount))

    # Second
    # We will assume that a brokenCount == 1 means support changed to resistance, vice versa.
    # brokenCounts 0 and 1 are the strongest, then get weaker.
    broken_threshold = 1
    key_levels = [x for x in imp if x[2] <= broken_threshold]

    # Third
    # add levels to df starting at the appropraite candle, and return the df
    for level in key_levels:
        df_main[level[1]] = 0
        df_main.loc[level[0]:,level[1]] = level[1]
        
    return df_main