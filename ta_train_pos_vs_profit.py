from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import numpy as np
import talib as tb
import time
import os
import pywhatkit
import matplotlib.pyplot as plt

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

#####Getting the .xlsx files of the nifty50 stocks#####
# Get the current working directory
current_directory = os.getcwd()

# Specify the folder name
folder_name = 'Nifty50_train'

# Construct the folder path
folder_path = os.path.join(current_directory, folder_name)

# List all files in the folder
files = os.listdir(folder_path)

# Iterate over the files and process .xlsx files
df50 = []
for file in files:
    if file.endswith('.xlsx'):
        file_path = os.path.join(folder_path, file)
        df = pd.read_excel(file_path)
        df50.append(df)



#technical_indicator functions array to  be displayed in dataframe
ta_funcs=['change_last5','change_last5_mag','ma5','ema200','ema200_trend',"aroon","engulfing",'macd','macd_sig','macd_hist','sar_now','sar_prev','sar_stoploss','atr','atr_stoploss','rsi','ppo','adx',"adx_trending_mark",'bbands_up','bbands_mid','bbands_down','obv_last','obv_avg5']
stpl=['sar_stoploss','atr_stoploss','final_stoploss']

ind_t_df = pd.read_excel('ind_t_data.xlsx')
ind_r_df = pd.read_excel('ind_r_data.xlsx')

col_ta_pos=['close','close5','diff5','ema200','aroon','engulfing','macd','sar','obv','ppo','bbands','final_pos','final_pos_trending','final_pos_ranging','net_final_pos','net_final_pos_trending','net_final_pos_ranging','net_final_pos_mag','stoploss','trend']

pf_colmns=['symbol','quantity','order price']

# ta=pd.DataFrame(columns=ta_funcs)
# ta_pos=pd.DataFrame(columns=col_ta_pos)
# ta_stpl=pd.DataFrame(columns=stpl)


# ta.insert(0, "symbol", n50_symbols)
# ta_pos.insert(0, "symbol", n50_symbols)
# ta_stpl.insert(0, "symbol", n50_symbols)

balance=1200
brokerage=0

orders_sym=['x','x','x','x','x']
oq=[0,0,0,0,0]  ###this is just for taking the order quantity as a string. Ignore it. It's not so imp###
orders_quantity=[0,0,0,0,0]
orders_brokerage=[0,0,0,0,0]
orders_pos=[0,0,0,0,0]
order_pri_arr=[0,0,0,0,0]
orders=pd.DataFrame()
pf=pd.DataFrame(columns=pf_colmns)

exit_df_colmns=['symbol','old quantity','exit order']


# Sorting by net_final_pos_mag
s_ta_pos=pd.DataFrame()
final_data=pd.DataFrame()

n_th=0 #nth time frame

begin=time.time()



# index
for i in range(33,34):

  #technical analysis of a single stock in each time frame
  #ta_each=pd.DataFrame()

  data_5_min = tv.get_hist(symbol=f'{n50_symbols[i]}',exchange='NSE',interval=Interval.in_5_minute,n_bars=5000)
  data=pd.DataFrame(data_5_min)
  #print(data)

  data['net pos']=np.nan
  data['exit change price']=np.nan
  data['exit_change%']=np.nan
  data['brokerage_price']=data['close']*0.0005
  data['net_profit']=np.nan
      
  #print(data)

  df=pd.DataFrame()
  df=data.copy()
  #print(df)

  #df.to_csv(f"{n50_symbols[i]}_5_min.csv")
  #print(df) 

  for j in range(len(df.index)-5):

    ###All variables
    ta_change_last5=np.nan
    ta_change_last5_mag=np.nan
    ta_slope_last5=np.nan
    ta_slope_last5_mag=np.nan
    ta_ema200_trend=np.nan
    ta_pos_aroon=np.nan
    ta_pos_sar=np.nan
    ta_pos_obv=np.nan
    ta_pos_macd=np.nan
    ta_engulfing=np.nan
    ta_adx_trending_mark=np.nan
    ta_pos_final_pos_trending=np.nan
    ta_pos_final_pos_ranging=np.nan
    ta_pos_net_final_pos_trending=np.nan
    ta_pos_net_final_pos_ranging=np.nan
    ta_pos_net_final_pos=np.nan
    
    #total change in last 5 candles
    ta_change_last5=((df['close'][-1]/df['close'][-6])-1)*100
    if ta_change_last5<0:
      ta_change_last5_mag=ta_change_last5*(-1)
    else:
      ta_change_last5_mag=ta_change_last5  


    # #slope last 5
    # arr_x=[1,2,3,4,5]
    # arr_y=df['close'].tail(5)
    # reg_num=0
    # reg_den=0
    # reg_x_mean=np.mean(arr_x)
    # reg_y_mean=np.mean(arr_y)
    # for k in range(5):
    #   reg_num+= (arr_x[k]-reg_x_mean)*(arr_y[k]-reg_y_mean)
    #   reg_den+= (arr_x[k]-reg_x_mean)**2
    # ta_slope_last5=reg_num/reg_den
    # if ta_slope_last5<0:
    #   ta_slope_last5_mag=ta_slope_last5*(-1)
    # else:
    #   ta_slope_last5_mag=ta_slope_last5      

    #ma
    ta_ma5= tb.MA(df['close'], 5)[-1]

    #ta_pos['close]
    ta_pos_close=df['close'][-1]
    ta_pos_close5=df['close'][-6]
    ta_pos_diff5=df['close'][-1]-df['close'][-6]


    #ema
    ta_ema200=tb.EMA(df['close'], 200)[-1]
    if df['close'][-1]>ta_ema200:
      ta_ema200_trend=1
    elif df['close'][-1]<ta_ema200:
      ta_ema200_trend=-1
    else:
      ta_ema200_trend=0     
    #ta_ema"]=ta_each['ema'][-1]
    ta_pos_ema200=ta_ema200_trend


    #aroon
    ta_aroon=tb.AROONOSC(df['high'],df['low'],timeperiod=14)[-1]
    #ta_aroon"]=ta_each['aroon'][-1]
    
    if ta_aroon>=90 and ta_ema200_trend==1:
        ta_pos_aroon=1
    elif ta_aroon<=-90 and ta_ema200_trend==-1:
        ta_pos_aroon=-1
    else:
        ta_pos_aroon=0
    ##aroon

    #engulfing
    #ta_each["engulfing"]=tb.CDLENGULFING(df['open'],df['high'],df['low'],df['close'])
    #ta_engulfing"]=ta_each['engulfing'][-1]
    #ta_pos_engulfing']=int(ta_each['engulfing'][-1]/100)

    #engulfing without using talib to save time
    if df['open'][-1]<df['close'][-2] and df['close'][-1]>df['open'][-2] and df['close'][-2]<df['open'][-2]:
      ta_engulfing=1
      ta_pos_engulfing=1
    elif df['open'][-1]>df['close'][-2] and df['close'][-1]<df['open'][-2] and df['close'][-2]>df['open'][-2]: 
      ta_engulfing=-1
      ta_pos_engulfing=-1
    else:
      ta_engulfing=0
      ta_pos_engulfing=0 

    #macd
    ta_macd=tb.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)[0][-1]
    ta_macd_sig=tb.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)[1][-1]
    ta_macd_hist=tb.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)[2][-1]
    ta_macd_hist_mag=ta_macd_hist if ta_macd_hist>0 else (-1)*ta_macd_hist

    ta_macd_hist_last=tb.MACD(df['close'][:-1], fastperiod=12, slowperiod=26, signalperiod=9)[2][-1]

    if ta_macd_hist>0 and ta_macd_hist_last<0 and ta_macd<0 and ta_macd_sig<0:
      ta_pos_macd=1
    elif ta_macd_hist<0 and ta_macd_hist_last>0 and ta_macd>0 and ta_macd_sig>0:  
      ta_pos_macd=-1
    elif ta_macd_hist>0 and ta_macd_hist_last>0 and ta_macd_hist>ta_macd_hist_last:    #######Multiply with the strength of macd#######
      ta_pos_macd=1
    elif ta_macd_hist<0 and ta_macd_hist_last<0 and ta_macd_hist<ta_macd_hist_last:  
      ta_pos_macd=-1
    else:
      ta_pos_macd=0  

    #OBV indicator
    ta_obv_last=tb.OBV(df['close'],df['open'])[-1] 
    ta_obv_avg5=(tb.OBV(df['close'],df['open'])[-1]+tb.OBV(df['close'],df['open'])[-2] +tb.OBV(df['close'],df['open'])[-3]+tb.OBV(df['close'],df['open'])[-4]+tb.OBV(df['close'],df['open'])[-5])/5   

    if ta_obv_last>ta_obv_avg5:
      ta_pos_obv=1
    elif ta_obv_last<ta_obv_avg5:
      ta_pos_obv=-1
    else:
      ta_pos_obv=0 

    #sar
    ta_sar_now=tb.SAR(df['high'],df['low'],0.02,0.2)[-1]
    ta_sar_prev=tb.SAR(df['high'],df['low'],0.02,0.2)[-2]

    if ta_sar_now<df['close'][-1] and ta_ema200_trend==1:
      ta_pos_sar=1
    elif ta_sar_now>df['close'][-1] and ta_ema200_trend==-1:
      ta_pos_sar=-1
    else:
      ta_pos_sar=0 

    # #sar based stoploss
    # if ta_sar_now<df['close'][-1]:
    #   ta_stpl.loc[i].at["sar_stoploss"]=ta_sar_now-0.05*(df['close'][-1]-ta_sar_now)
    # elif ta_sar_now>df['close'][-1]:    
    #   ta_stpl.loc[i].at["sar_stoploss"]=ta_sar_now+0.05*(ta_sar_now-df['close'][-1])
    # else: 
    #   #don't consider in avg of stoplosses
    #   ta_stpl.loc[i].at["sar_stoploss"]=0

    # ta_sar_stoploss=ta_stpl.loc[i].at["sar_stoploss"]

    #adx
    ta_adx=tb.ADX(df['high'],df['low'],df['close'])[-1]
    if ta_adx>30:
      ta_adx_trending_mark=1
    else:  
      ta_adx_trending_mark=0


    #bbands
    ta_bbands_up=tb.BBANDS(df['close'],5,2,2,0)[0][-1]
    ta_bbands_mid=tb.BBANDS(df['close'],5,2,2,0)[1][-1]
    ta_bbands_down=tb.BBANDS(df['close'],5,2,2,0)[2][-1]

    if df['high'][-1]>ta_bbands_up:
      ta_pos_bbands=-1
    elif df['low'][-1]<ta_bbands_down:
      ta_pos_bbands=1
    else:
      ta_pos_bbands=0  

    #rsi
    ta_rsi=tb.RSI(df['close'])[-1]
    if ta_rsi>70:
      ta_pos_rsi=-1
    elif ta_rsi<30:
      ta_pos_rsi=1
    else:
      ta_pos_rsi=0  


    #PPO
    ta_ppo=tb.PPO(df['close'], fastperiod=12, slowperiod=26, matype=0)[-1]
    if ta_ppo>0 and ta_ema200_trend==1:
      ta_pos_ppo=1
    elif ta_ppo<0 and ta_ema200_trend==-1:
      ta_pos_ppo=-1
    else:
      ta_pos_ppo=0  

    ############# No indicators after this #############

    #### Multiply the final pos with the average of the last 5 percentage changes in the price to know how good it is (be careful with the start of the day as it might be very high)


    #final_pos
    ta_pos_final_pos=0
    if ta_adx_trending_mark==1:
      ta_pos_final_pos=ta_pos_ema200*0.56*5.5*6.4+ta_pos_final_pos+ta_pos_aroon*0.4*4*1+ta_pos_engulfing*0.55*5*4+ta_pos_macd*0.78*8*7+ta_pos_sar*0.42*4.2*2+ta_pos_ppo*0.58*6*6
      ta_pos_final_pos_trending=ta_pos_final_pos
    else: 
      ta_pos_final_pos=np.nan
      #ta_pos_final_pos=ta_pos_final_pos+ta_pos_bbands*0.55
      #ta_pos_final_pos_ranging=ta_pos_final_pos

    #final_pos*slope_last5
    if ta_pos_final_pos*ta_change_last5>0:
      ta_pos_net_final_pos= ta_pos_final_pos*ta_change_last5_mag        #*(ta_macd_hist_mag/ta_ema200)
    else:
      ta_pos_net_final_pos=np.nan  
    # if ta_pos_final_pos_trending*ta_change_last5>0:
    #   ta_pos_net_final_pos_trending=ta_pos_final_pos_trending*ta_change_last5_mag
    # else:
    #   ta_pos_net_final_pos_trending=np.nan
    #   ta_pos_net_final_pos_ranging=ta_pos_final_pos_ranging*ta_change_last5_mag

    #storing the net pos at each timeframe
    data['net pos'][j]=ta_pos_net_final_pos
    #dropping last row
    df = df.drop(df.index[-1])
  


  data = data.dropna(subset=['net pos'])

  temp_data=data.reset_index()
  sign_change = temp_data.index[(temp_data['net pos'].shift(1) * temp_data['net pos']) <= 0].tolist()

  dpk=0
  scx=0
  while dpk<len(data.index) and scx<len(sign_change):
    if sign_change[scx]>dpk:
      data['exit change price'][dpk]=data['close'][sign_change[scx]]-data['close'][dpk]
      data['exit_change%'][dpk]=((data['close'][sign_change[scx]]/data['close'][dpk])-1)*100
      if data['net pos'][dpk]<0: ##short selling##
        data['net_profit'][dpk]=-data['exit_change%'][dpk]-0.05 ######brokerage %####
      else:
        data['net_profit'][dpk]=data['exit_change%'][dpk]-0.05 ######brokerage %####
         
      dpk=dpk+1  
    else:
      scx=scx+1

      
  data=data.dropna()

  print(data)
  print(len(data.index))
  print(len(data[data['net_profit']>0]))

  total_n=len(data.index)
  wins=len(data[data['net_profit']>0])
  win_rate=wins*100/total_n
  print(win_rate)


  plt.scatter(data['net pos'],data['net_profit'])
  plt.xlabel('net pos')
  plt.ylabel('profit')
  plt.show()
      
#     #final_pos_mag
#     if ta_pos_net_final_pos']<0:
#       ta_pos_net_final_pos_mag']=(-1)*ta_pos_net_final_pos']
#     else:
#       ta_pos_net_final_pos_mag']=ta_pos_net_final_pos']
    
#     #atr
#     ta_atr"]=tb.ATR(df['high'],df['low'],df['close'])[-1]
#     if ta_pos_final_pos']>0:
#       ta_atr_stoploss"]=df['close'][-1]-2*(ta_atr"])
#     elif ta_pos_final_pos']<0:
#       ta_atr_stoploss"]=df['close'][-1]+2*(ta_atr"])
#     else:
#       ta_atr_stoploss"]=df['close'][-1]
#     ta_stpl.loc[i].at["atr_stoploss"]=ta_atr_stoploss"]

#     #final_stoploss
#     s_stpl=0
#     den=0
#     for n in range(len(stpl)):
#       if ta_pos_final_pos']>0 and ta_stpl.loc[i].at[stpl[n]]<df['close'][-1]:
#         s_stpl=s_stpl+ ta_stpl.loc[i].at[stpl[n]]
#         den=den+1
#       elif ta_pos_final_pos']<0 and ta_stpl.loc[i].at[stpl[n]]>df['close'][-1] :   
#         s_stpl=s_stpl+ ta_stpl.loc[i].at[stpl[n]]
#         den=den+1
#       if den!=0:
#         ta_stpl.loc[i].at["final_stoploss"]=s_stpl/den

#   ta_pos['stoploss']=ta_stpl['final_stoploss']
#   ta_pos['trend']=ta['adx_trending_mark']
  
#   s_ta_pos=ta_pos.sort_values(['net_final_pos_mag','final_pos'], ascending=False).reset_index(drop=True)
#   #sorted df
  
  
#   #This is for the new timeframe 
#   final_data['symbol']=s_ta_pos['symbol']
#   final_data['normal_pos']=s_ta_pos['final_pos']
#   final_data['net_pos']=s_ta_pos['net_final_pos']
#   final_data['trend']=s_ta_pos['trend']
#   final_data['price']=s_ta_pos['close']
#   final_data['stoploss']=s_ta_pos['stoploss']
#   final_data['brokerage']=final_data['price']*0.0005
#   for i in range(51):
#     if final_data['brokerage'][i]>20:
#       final_data['brokerage']=20


#   #print(ta)
#   #print(s_ta_pos)
#   #print(final_data)
#   #print(ta_stpl) 
  

#   top5=[]
#   aff_top5=pd.DataFrame(columns=final_data.columns)
#   k=0
#   i=0
#   while k<5 and i<51:  
#     if final_data['price'][i]<balance:
#       new_row_top5=pd.Series(final_data.loc[i].values, index=aff_top5.columns)
#       aff_top5.loc[len(aff_top5.index)]=new_row_top5
#       top5_each=f'''
#       {k+1})
#       symbol:{final_data['symbol'][i]}
#       normal pos:{final_data['normal_pos'][i]}
#       net pos:{final_data['net_pos'][i]}
#       trend:{final_data['trend'][i]}
#       price:{final_data['price'][i]}
#       stoploss:{final_data['stoploss'][i]}
#       brokerage:{final_data['brokerage'][i]}'''
#       #print(top5_each)
#       top5.append(top5_each)
#       k=k+1
#     i=i+1

#   wapp_output=f'''
#   Top performing stocks
#   {top5[0]}
#   {top5[1]}
#   {top5[2]}
#   {top5[3]}
#   {top5[4]}'''

  

#   #pywhatkit.sendwhatmsg_instantly("+918639147440",wapp_output,15,True,2) 
#   print(wapp_output)


#   ##Gotta send exit symbols too#############
#   ###Very Very important

#   #Exit signals
#   exit_df=pd.DataFrame(columns=exit_df_colmns)
#   for i in range(len(pf.index)):
#     r=aff_top5.index[aff_top5['symbol']==pf['symbol'][i]][0] 
#     if pf.loc[i].at['quantity']*aff_top5['net_pos'][r]<=0:
#         new_row=pd.Series([pf['symbol'][i],pf['quantity'][i],(-1)*pf['quantity'][i]], index=exit_df.columns)
#         exit_df.loc[len(exit_df.index)]=new_row
#   if exit_df.size!=0:
#     print(exit_df)

#   ######Taking input of the number of stocks ordered in the last timeframe
#   oq[0],oq[1],oq[2],oq[3],oq[4]=input(f"{aff_top5['symbol'][0]}, {aff_top5['symbol'][1]},{aff_top5['symbol'][2]},{aff_top5['symbol'][3]},{aff_top5['symbol'][4]}:  ").split()
#   for i in range(5):
#     orders_quantity[i]=float(oq[i])
#     orders_sym[i]=aff_top5['symbol'][i] #the aff_top5 here is of the last timeframe
#     orders_brokerage[i]=aff_top5['brokerage'][i]*orders_quantity[i]
#     if aff_top5['net_pos'][i]>0:
#       orders_pos[i]=1
#     elif aff_top5['net_pos'][i]<0:
#       orders_pos[i]=-1
#     else:
#       orders_pos[i]=0  
#     order_pri_arr[i]=aff_top5['price'][i]
#     brokerage=brokerage+aff_top5['brokerage'][i]*orders_quantity[i]
#     if (pf['symbol']==aff_top5['symbol'][i]).any() and orders_quantity[i]!=0:
#       r=pf.index[pf['symbol']==aff_top5['symbol'][i]][0]
#       q_old=pf.loc[r].at['quantity']
#       pf.loc[r].at['quantity']=pf.loc[r].at['quantity']+orders_quantity[i]
#       if pf.loc[r].at['quantity']==0:
#         pf=pf.drop(r).reset_index(drop=True)
#       else:
#         pf.loc[r].at['order price']=(pf.loc[r].at['order price']*q_old+aff_top5['price'][i]*orders_quantity[i])/pf.loc[r].at['quantity']
#     else:
#       if orders_quantity[i]!=0:
#         new_row=pd.Series([aff_top5['symbol'][i],orders_quantity[i],aff_top5['price'][i]], index=pf.columns)
#         pf.loc[len(pf.index)]=new_row

#   orders['symbol']=orders_sym
#   orders['position']=orders_pos
#   orders['quantity']=orders_quantity
#   orders['order price']=order_pri_arr
#   orders['brokerage']=orders_brokerage

#   print(orders)
#   print(pf)


#   n_th=n_th+1

#   #time.sleep(260)
#   end = time.time()
#   print(end-begin)

  

# #Things left to do
# #1) We should reduce its weitage if its reaching support or resiastance or if its overbought or oversold
# #2) Keep track of the portfolio
# #3) Decisions including brokerage
# #4) Backtest the complete strategy


