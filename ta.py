from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import numpy as np
import talib as tb
import time
import pywhatkit
#import mplfinance as mpf

#username = 'YourTradingViewUsername'
#password = 'YourTradingViewPassword'

#tv = TvDatafeed(username, password)
#To use it without logging in

tv = TvDatafeed()
#n50 = pd.read_csv(io.BytesIO(uploaded["Symbols_nifty50.csv"]))
#n50_symbols=[]
#for i in range(51):
#    n50_symbols.append(n50.loc[:,"Symbol"][i])

n50_symbols=['NIFTY', 'HINDALCO', 'MARUTI', 'NESTLEIND', 'ONGC', 'TATAMOTORS', 'ITC', 'SUNPHARMA', 'BHARTIARTL', 'CIPLA', 'DIVISLAB', 'JSWSTEEL', 'HINDUNILVR', 'TITAN', 'NTPC', 'TATASTEEL', 'HEROMOTOCO', 'HDFCLIFE', 'ULTRACEMCO', 'SBILIFE', 'TCS', 'BAJFINANCE', 'BRITANNIA', 'AXISBANK', 'TECHM', 'COALINDIA', 'LT', 'DRREDDY', 'M_M', 'APOLLOHOSP', 'ADANIPORTS', 'BAJAJFINSV', 'GRASIM', 'TATACONSUM', 'ICICIBANK', 'HDFC', 'EICHERMOT', 'BPCL', 'ADANIENT', 'UPL', 'POWERGRID', 'HDFCBANK', 'INFY', 'WIPRO', 'RELIANCE', 'INDUSINDBK', 'ASIANPAINT', 'HCLTECH', 'KOTAKBANK', 'BAJAJ_AUTO', 'SBIN']

#print(n50_symbols)


#technical_indicator functions array to  be displayed in dataframe
ta_funcs=['ema_last5','ema_last5_mag','ma5','ema200','ema200_trend',"aroon","engulfing",'macd','macd_sig','macd_hist','macd_hist_mag','macd_hist_last','sar_now','sar_prev','sar_stoploss','atr','atr_stoploss','rsi','ppo','adx',"adx_trending_mark",'bbands_up','bbands_mid','bbands_down','obv_last','obv_avg5']
stpl=['sar_stoploss','atr_stoploss','final_stoploss']

ind_t_df = pd.read_excel('ind_t_data.xlsx')
ind_r_df = pd.read_excel('ind_r_data.xlsx')

col_ta_pos=['close','close5','diff5','ema200','aroon','engulfing','macd','sar','obv','ppo','bbands','rsi','final_pos','final_pos_trending','final_pos_ranging','net_final_pos','net_final_pos_trending','net_final_pos_ranging','net_final_pos_mag','stoploss','trend']

pf_cols=['symbol','quantity','order price']


balance=1000
brokerage=0

pf=pd.DataFrame(columns=pf_cols)

exit_df_colmns=['symbol','old quantity','exit order']


n_th=0 #nth time frame

while(True):

  ########################################
    
  ta=pd.DataFrame(columns=ta_funcs)
  ta_pos=pd.DataFrame(columns=col_ta_pos)
  ta_stpl=pd.DataFrame(columns=stpl)


  ta.insert(0, "symbol", n50_symbols)
  ta_pos.insert(0, "symbol", n50_symbols)
  ta_stpl.insert(0, "symbol", n50_symbols)

  orders_sym=['x','x','x','x','x']
  oq=[0,0,0,0,0]  ###this is just for taking the order quantity as a string. Ignore it. It's not so imp###
  orders_quantity=[0,0,0,0,0]
  orders_brokerage=[0,0,0,0,0]
  orders_pos=[0,0,0,0,0]
  order_pri_arr=[0,0,0,0,0]
  orders=pd.DataFrame()

  # Sorting by net_final_pos_mag
  s_ta_pos=pd.DataFrame()
  final_data=pd.DataFrame()

  df50_init=[] #All the initial dataframes of the stocks
  #########################################

  begin=time.time()

  # index
  for i in range(51):

    data_5_min = tv.get_hist(symbol=f'{n50_symbols[i]}',exchange='NSE',interval=Interval.in_5_minute,n_bars=1000)
    df_init=pd.DataFrame(data_5_min)
    df50_init.append(df_init)

  for i,df in  enumerate(df50_init):
    
    #Slopes
    slopes=[]
    slopes.append(np.nan)

    for j in range(1,len(df.index)):
      slopes.append(((df['close'][j]/df['close'][j-1])-1)*100)

    df['candle_change']=slopes

    #df.to_csv(f"{n50_symbols[i]}_5_min.csv")
    #print(df)

    #ta_each.index=df.index

    #ema of last 5 candle changes
    ta['ema_last5'][i]=tb.EMA(df['candle_change'],5)[-1]
    ta['ema_last5_mag'][i]=ta['ema_last5'][i] if ta['ema_last5'][i]>=0 else (-1)*ta['ema_last5'][i]

    #ma
    ta.at[i,'ma5']= tb.MA(df['close'], 5)[-1]

    #ta_pos['close]
    ta_pos.at[i,'close']=df['close'][-1]
    ta_pos.at[i,'close5']=df['close'][-6]
    ta_pos.at[i,'diff5']=df['close'][-1]-df['close'][-6]


    #ema
    ta.at[i,'ema200']=tb.EMA(df['close'], 200)[-1]
    if df['close'][-1]>ta.at[i,'ema200']:
      ta.at[i,'ema200_trend']=1
    elif df['close'][-1]<ta.at[i,'ema200']:
      ta.at[i,'ema200_trend']=-1
    else:
      ta.at[i,'ema200_trend']=0     
    #ta.at[i,"ema"]=ta_each['ema'][-1]
    ta_pos['ema200']=ta['ema200_trend']


    #aroon
    ta.at[i,"aroon"]=tb.AROONOSC(df['high'],df['low'],timeperiod=14)[-1]
    #ta.at[i,"aroon"]=ta_each['aroon'][-1]
    
    if ta.at[i,"aroon"]>=90 and ta.at[i,'ema200_trend']==1:
        ta_pos.at[i,"aroon"]=1
    elif ta.at[i,"aroon"]<=-90 and ta.at[i,'ema200_trend']==-1:
        ta_pos.at[i,"aroon"]=-1
    else:
        ta_pos.at[i,"aroon"]=0
    ##aroon

    #engulfing
    #ta_each["engulfing"]=tb.CDLENGULFING(df['open'],df['high'],df['low'],df['close'])
    #ta.at[i,"engulfing"]=ta_each['engulfing'][-1]
    #ta_pos.at[i,'engulfing']=int(ta_each['engulfing'][-1]/100)

    #engulfing without using talib to save time
    if df['open'][-1]<df['close'][-2] and df['close'][-1]>df['open'][-2] and df['close'][-2]<df['open'][-2]:
      ta.at[i,"engulfing"]=1
      ta_pos.at[i,"engulfing"]=1
    elif df['open'][-1]>df['close'][-2] and df['close'][-1]<df['open'][-2] and df['close'][-2]>df['open'][-2]: 
      ta.at[i,"engulfing"]=-1
      ta_pos.at[i,"engulfing"]=-1
    else:
      ta.at[i,"engulfing"]=0
      ta_pos.at[i,"engulfing"]=0 

    #macd
    ta.at[i,"macd"]=tb.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)[0][-1]
    ta.at[i,"macd_sig"]=tb.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)[1][-1]
    ta.at[i,"macd_hist"]=tb.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)[2][-1]
    ta.at[i,'macd_hist_mag']=ta.at[i,'macd_hist'] if ta.at[i,'macd_hist']>0 else (-1)*ta.at[i,'macd_hist']

    ta.at[i,'macd_hist_last']=tb.MACD(df['close'][:-1], fastperiod=12, slowperiod=26, signalperiod=9)[2][-1]


    if ta.at[i,'macd_hist']>0 and ta.at[i,'macd_hist_last']<0 and ta.at[i,'macd']<0 and ta.at[i,'macd_sig']<0:
      ta_pos_macd=1
    elif ta.at[i,'macd_hist']<0 and ta.at[i,'macd_hist_last']>0 and ta.at[i,'macd']>0 and ta.at[i,'macd_sig']>0: 
      ta_pos_macd=-1
    elif ta.at[i,'macd_hist']>0 and ta.at[i,'macd_hist_last']>0 and ta.at[i,'macd_hist']>ta.at[i,'macd_hist_last']:    #######Multiply with the strength of macd#######
      ta_pos_macd=1
    elif ta.at[i,'macd_hist']<0 and ta.at[i,'macd_hist_last']<0 and ta.at[i,'macd_hist']<ta.at[i,'macd_hist_last']:  
      ta_pos_macd=-1
    else:
      ta_pos.at[i,"macd"]=0  

    #OBV indicator
    ta.at[i,"obv_last"]=tb.OBV(df['close'],df['open'])[-1] 
    ta.at[i,"obv_avg5"]=(tb.OBV(df['close'],df['open'])[-1]+tb.OBV(df['close'],df['open'])[-2] +tb.OBV(df['close'],df['open'])[-3]+tb.OBV(df['close'],df['open'])[-4]+tb.OBV(df['close'],df['open'])[-5])/5   

    if ta.at[i,"obv_last"]>ta.at[i,"obv_avg5"]:
      ta_pos.at[i,'obv']=1
    elif ta.at[i,"obv_last"]<ta.at[i,"obv_avg5"]:
      ta_pos.at[i,'obv']=-1
    else:
      ta_pos.at[i,'obv']=0 

    #sar
    ta.at[i,"sar_now"]=tb.SAR(df['high'],df['low'],0.02,0.2)[-1]
    ta.at[i,"sar_prev"]=tb.SAR(df['high'],df['low'],0.02,0.2)[-2]

    if ta.at[i,"sar_now"]<df['close'][-1] and ta.at[i,'ema200_trend']==1:
      ta_pos.at[i,"sar"]=1
    elif ta.at[i,"sar_now"]>df['close'][-1] and ta.at[i,'ema200_trend']==-1:
      ta_pos.at[i,"sar"]=-1
    else:
      ta_pos.at[i,"sar"]=0 

    #sar based stoploss
    if ta.at[i,"sar_now"]<df['close'][-1]:
      ta_stpl.at[i,"sar_stoploss"]=ta.at[i,"sar_now"]-0.05*(df['close'][-1]-ta.at[i,"sar_now"])
    elif ta.at[i,"sar_now"]>df['close'][-1]:    
      ta_stpl.at[i,"sar_stoploss"]=ta.at[i,"sar_now"]+0.05*(ta.at[i,"sar_now"]-df['close'][-1])
    else: 
      #don't consider in avg of stoplosses
      ta_stpl.at[i,"sar_stoploss"]=0

    ta.at[i,"sar_stoploss"]=ta_stpl.at[i,"sar_stoploss"]

    #adx
    ta.at[i,"adx"]=tb.ADX(df['high'],df['low'],df['close'])[-1]
    if ta.at[i,"adx"]>25:
      ta.at[i,"adx_trending_mark"]=1
    else:  
      ta.at[i,"adx_trending_mark"]=0


    #bbands
    ta.at[i,'bbands_up']=tb.BBANDS(df['close'],5,2,2,0)[0][-1]
    ta.at[i,'bbands_mid']=tb.BBANDS(df['close'],5,2,2,0)[1][-1]
    ta.at[i,'bbands_down']=tb.BBANDS(df['close'],5,2,2,0)[2][-1]

    if df['high'][-1]>ta.at[i,'bbands_up']:
      ta_pos.at[i,'bbands']=-1
    elif df['low'][-1]<ta.at[i,'bbands_down']:
      ta_pos.at[i,'bbands']=1
    else:
      ta_pos.at[i,'bbands']=0  

    #rsi
    ta.at[i,"rsi"]=tb.RSI(df['close'])[-1]
    if ta.at[i,'rsi']>70:
      ta_pos.at[i,'rsi']=-1
    elif ta.at[i,'rsi']<30:
      ta_pos.at[i,'rsi']=1
    else:
      ta_pos.at[i,'rsi']=0  


    #PPO
    ta.at[i,"ppo"]=tb.PPO(df['close'], fastperiod=12, slowperiod=26, matype=0)[-1]
    if ta.at[i,"ppo"]>0 and ta.at[i,'ema200_trend']==1:
      ta_pos.at[i,"ppo"]=1
    elif ta.at[i,"ppo"]<0 and ta.at[i,'ema200_trend']==-1:
      ta_pos.at[i,"ppo"]=-1
    else:
      ta_pos.at[i,"ppo"]=0  

    ############# No indicators after this #############

    #### Multiply the final pos with the average of the last 5 percentage changes in the price to know how good it is (be careful with the start of the day as it might be very high)


    #final_pos
    ta_pos.at[i,'final_pos']=0
    if ta.at[i,"adx_trending_mark"]==1:
      for n in range(len(ind_t_df['Name'])):
        ta_pos.at[i,'final_pos']=ta_pos.at[i,'final_pos']+(ta_pos.at[i,ind_t_df['Name'][n]])*ind_t_df['win rate'][n]*ind_t_df['reliability'][n]*ind_t_df['consistency'][n]
        ta_pos.at[i,'final_pos_trending']=ta_pos.at[i,'final_pos']
    else:
      for n in range(len(ind_r_df['Name'])):  
        ta_pos.at[i,'final_pos']=ta_pos.at[i,'final_pos']+ta_pos.at[i,ind_r_df['Name'][n]]*ind_r_df['win rate'][n]*ind_t_df['reliability'][n]*ind_t_df['consistency'][n]
        ta_pos.at[i,'final_pos_ranging']=ta_pos.at[i,'final_pos']

    #final_pos*slope_last5
    ta_pos.at[i,'net_final_pos']= ta_pos.at[i,'final_pos']*ta.at[i,'ema_last5_mag']
    if ta_pos.at[i,'final_pos_trending']*ta.at[i,'ema_last5']>0:
      ta_pos.at[i,'net_final_pos_trending']=ta_pos.at[i,'final_pos_trending']*ta.at[i,'ema_last5_mag']*ta.at[i,'ema200']*(ta.at[i,'macd_hist_mag']/ta.at[i,'ema200'])
    else:
      ta_pos.at[i,'net_final_pos_trending']=np.nan
    ta_pos.at[i,'net_final_pos_ranging']=ta_pos.at[i,'final_pos_ranging']*ta.at[i,'ema_last5_mag']


    
    #final_pos_mag
    if ta_pos.at[i,'net_final_pos']<0:
      ta_pos.at[i,'net_final_pos_mag']=(-1)*ta_pos.at[i,'net_final_pos']
    else:
      ta_pos.at[i,'net_final_pos_mag']=ta_pos.at[i,'net_final_pos']
    
    #atr
    ta.at[i,"atr"]=tb.ATR(df['high'],df['low'],df['close'])[-1]
    if ta_pos.at[i,'final_pos']>0:
      ta.at[i,"atr_stoploss"]=df['close'][-1]-2*(ta.at[i,"atr"])
    elif ta_pos.at[i,'final_pos']<0:
      ta.at[i,"atr_stoploss"]=df['close'][-1]+2*(ta.at[i,"atr"])
    else:
      ta.at[i,"atr_stoploss"]=df['close'][-1]
    ta_stpl.at[i,"atr_stoploss"]=ta.at[i,"atr_stoploss"]

    #final_stoploss
    s_stpl=0
    den=0
    for n in range(len(stpl)):
      if ta_pos.at[i,'final_pos']>0 and ta_stpl.at[i,stpl[n]]<df['close'][-1]:
        s_stpl=s_stpl+ ta_stpl.at[i,stpl[n]]
        den=den+1
      elif ta_pos.at[i,'final_pos']<0 and ta_stpl.at[i,stpl[n]]>df['close'][-1] :   
        s_stpl=s_stpl+ ta_stpl.at[i,stpl[n]]
        den=den+1
      if den!=0:
        ta_stpl.at[i,"final_stoploss"]=s_stpl/den

  ta_pos['stoploss']=ta_stpl['final_stoploss']
  ta_pos['trend']=ta['adx_trending_mark']
  
  s_ta_pos=ta_pos.sort_values(['net_final_pos_mag','final_pos'], ascending=False).reset_index(drop=True)
  #sorted df
  
  
  #This is for the new timeframe 
  final_data['symbol']=s_ta_pos['symbol']
  final_data['normal_pos']=s_ta_pos['final_pos']
  final_data['net_pos']=s_ta_pos['net_final_pos']
  final_data['trend']=s_ta_pos['trend']
  final_data['price']=s_ta_pos['close']
  final_data['stoploss']=s_ta_pos['stoploss']
  final_data['brokerage']=final_data['price']*0.0005
  for i in range(51):
    if final_data['brokerage'][i]>20:
      final_data['brokerage'][i]=20


  # print(ta)
  # print(s_ta_pos)
  #print(final_data)
  #print(ta_stpl) 
  

  top5=[]
  aff_top5=pd.DataFrame(columns=final_data.columns)
  k=0
  i=0
  while k<5 and i<51:  
    if final_data['price'][i]<balance:
      new_row_top5=pd.Series(final_data.loc[i].values, index=aff_top5.columns)
      aff_top5.loc[len(aff_top5.index)]=new_row_top5
      top5_each=f'''
      {k+1})
      symbol:{final_data['symbol'][i]}
      normal pos:{final_data['normal_pos'][i]}
      net pos:{final_data['net_pos'][i]}
      trend:{final_data['trend'][i]}
      price:{final_data['price'][i]}
      stoploss:{final_data['stoploss'][i]}
      brokerage:{final_data['brokerage'][i]}'''
      #print(top5_each)
      top5.append(top5_each)
      k=k+1
    i=i+1

  wapp_output=f'''
  Top performing stocks
  {top5[0]}
  {top5[1]}
  {top5[2]}
  {top5[3]}
  {top5[4]}'''

  

  #pywhatkit.sendwhatmsg_instantly("+918639147440",wapp_output,15,True,2) 
  print(wapp_output)


  ##Gotta send exit symbols too#############
  ###Very Very important

  #Exit signals
  exit_df=pd.DataFrame(columns=exit_df_colmns)
  for i in range(len(pf.index)):
    r=final_data.index[final_data['symbol']==pf['symbol'][i]][0] 
    if pf.at[i,'quantity']*final_data['net_pos'][r]<=0:
        new_row=pd.Series([pf['symbol'][i],pf['quantity'][i],(-1)*pf['quantity'][i]], index=exit_df.columns)
        exit_df.loc[len(exit_df.index)]=new_row
  if exit_df.size!=0:
    print(exit_df)

    for i in range(len(exit_df.index)-1):
      print(f"{exit_df['symbol'][i]}, ",end="")

    print(f"{exit_df['symbol'][len(exit_df.index)]}: ",end="")  
    exited_arr=input("").split()
    exited_int_arr = [int(num_str) for num_str in exited_arr]
    
    for i in range(len(exit_df.index)):
      if (pf['symbol']==exit_df['symbol'][i]).any() and exited_int_arr[i]!=0:
        r=pf.index[pf['symbol']==exit_df['symbol'][i]][0]
        pf=pf.drop(r).reset_index(drop=True)      


  ######Taking input of the number of stocks ordered in the last timeframe
  oq[0],oq[1],oq[2],oq[3],oq[4]=input(f"{aff_top5['symbol'][0]}, {aff_top5['symbol'][1]}, {aff_top5['symbol'][2]}, {aff_top5['symbol'][3]}, {aff_top5['symbol'][4]}:  ").split()
  for i in range(5):
    orders_quantity[i]=float(oq[i])
    orders_sym[i]=aff_top5['symbol'][i] #the aff_top5 here is of the last timeframe
    orders_brokerage[i]=aff_top5['brokerage'][i]*orders_quantity[i]
    if aff_top5['net_pos'][i]>0:
      orders_pos[i]=1
    elif aff_top5['net_pos'][i]<0:
      orders_pos[i]=-1
    else:
      orders_pos[i]=0  
    order_pri_arr[i]=aff_top5['price'][i]
    brokerage=brokerage+aff_top5['brokerage'][i]*orders_quantity[i]
    if (pf['symbol']==aff_top5['symbol'][i]).any() and orders_quantity[i]!=0:
      r=pf.index[pf['symbol']==aff_top5['symbol'][i]][0]
      q_old=pf.at[r,'quantity']
      pf.at[r,'quantity']=pf.at[r,'quantity']+orders_quantity[i]
      if pf.at[r,'quantity']==0:
        pf=pf.drop(r).reset_index(drop=True)
      else:
        pf.at[r,'order price']=(pf.at[r,'order price']*q_old+aff_top5['price'][i]*orders_quantity[i])/pf.at[r,'quantity']
    else:
      if orders_quantity[i]!=0:
        new_row=pd.Series([aff_top5['symbol'][i],orders_quantity[i],aff_top5['price'][i]], index=pf.columns)
        pf.loc[len(pf.index)]=new_row

  orders['symbol']=orders_sym
  orders['position']=orders_pos
  orders['quantity']=orders_quantity
  orders['order price']=order_pri_arr
  orders['brokerage']=orders_brokerage

  print(orders)
  print(pf)


  n_th=n_th+1

  #time.sleep(260)
  end = time.time()
  print(end-begin)

  

#Things left to do
#1) We should reduce its weitage if its reaching support or resiastance or if its overbought or oversold
#2) Keep track of the portfolio
#3) Decisions including brokerage
#4) Backtest the complete strategy

