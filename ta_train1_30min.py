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

n50_symbols=np.array(['NIFTY', 'HINDALCO', 'MARUTI', 'NESTLEIND', 'ONGC', 'TATAMOTORS', 'ITC', 'SUNPHARMA', 'BHARTIARTL', 'CIPLA', 'DIVISLAB', 'JSWSTEEL', 'HINDUNILVR', 'TITAN', 'NTPC', 'TATASTEEL', 'HEROMOTOCO', 'HDFCLIFE', 'ULTRACEMCO', 'SBILIFE', 'TCS', 'BAJFINANCE', 'BRITANNIA', 'AXISBANK', 'TECHM', 'COALINDIA', 'LT', 'DRREDDY', 'M_M', 'APOLLOHOSP', 'ADANIPORTS', 'BAJAJFINSV', 'GRASIM', 'TATACONSUM', 'ICICIBANK', 'HDFC', 'EICHERMOT', 'BPCL', 'ADANIENT', 'UPL', 'POWERGRID', 'HDFCBANK', 'INFY', 'WIPRO', 'RELIANCE', 'INDUSINDBK', 'ASIANPAINT', 'HCLTECH', 'KOTAKBANK', 'BAJAJ_AUTO', 'SBIN'])
#print(n50_symbols)

#####Getting the .xlsx files of the nifty50 stocks#####
# Get the current working directory
current_directory = os.getcwd()



#technical_indicator functions array to  be displayed in dataframe
ta_funcs=['candle_change','ema_last5','ema_last5_mag','ma5','ema200','ema200_trend',"aroon","engulfing",'macd','macd_sig','macd_hist','macd_hist_mag','sar_now','sar_prev','sar_stoploss','atr','atr_stoploss','rsi','ppo','adx',"adx_trending_mark",'bbands_up','bbands_mid','bbands_down','obv_last','obv_avg5']
stpl=['sar_stoploss','atr_stoploss','final_stoploss']

ind_t_df = pd.read_excel('ind_t_data.xlsx')
ind_r_df = pd.read_excel('ind_r_data.xlsx')

col_ta_pos=['ema200','aroon','engulfing','macd','sar','obv','ppo','bbands','rsi','final_pos','final_pos_trending','final_pos_ranging','net_final_pos','net_final_pos_trending','net_final_pos_ranging','net_final_pos_mag','stoploss','trend']

pf_colmns=['symbol','quantity','order price']


balance=8000
brokerage=0



# Sorting by net_final_pos_mag
s_ta_pos=pd.DataFrame()
final_data=pd.DataFrame()

n_th=0 #nth time frame

begin=time.time()

df50_init=[] # All the initial dataframes from tvdatafeed
df50=[] #The dataframes of all the 51 NIFTY50 stocks


begin=time.time()

# index
for j in range(51):
  data_5_min = tv.get_hist(symbol=f'{n50_symbols[j]}',exchange='NSE',interval=Interval.in_30_minute,n_bars=5000)
  df_init=pd.DataFrame(data_5_min)
  df50_init.append(df_init)
  time.sleep(1)
  #print(data)

for data in df50_init:  

  data['norm_pos']=np.nan
  data['net_pos']=np.nan
  data['net_pos_mag']=np.nan
  data['exit_change_price']=np.nan
  data['exit_change%']=np.nan
  data['brokerage_price']=data['close']*0.0005
  data['net_profit']=np.nan
      
  #print(data)

  df=pd.DataFrame()
  df=data.copy()
  #print(df)

  #df.to_csv(f"{n50_symbols[i]}_5_min.csv")
  #print(df) 

  ta=pd.DataFrame(index=data.index,columns=ta_funcs)
  ta_pos=pd.DataFrame(index=data.index,columns=col_ta_pos)



  ###All variables
  ta['ema200_trend']=np.nan
  ta_pos['aroon']=np.nan
  ta_pos['sar']=np.nan
  ta_pos['obv']=np.nan
  ta_pos['macd']=np.nan
  ta['engulfing']=np.nan
  ta['adx_trending_mark']=np.nan
  ta_pos['final_pos_trending']=np.nan
  ta_pos['final_pos_ranging']=np.nan
  ta_pos['net_final_pos_trending']=np.nan
  ta_pos['net_final_pos_ranging']=np.nan
  ta_pos['net_final_pos']=np.nan
  
  ind=len(data.index)
  for i in range(1,ind):
    ta['candle_change'][i]=((df['close'][i]/df['close'][i-1])-1)*100

  #ema of last 5 candle changes
  ta['ema_last5']=tb.EMA(ta['candle_change'],5)
  for i in range(ind):
    ta['ema_last5_mag'][i]=ta['ema_last5'][i] if ta['ema_last5'][i]>=0 else (-1)*ta['ema_last5'][i]

  # #total change in last 5 candles
  # ta_change_last5=((df['close'][-1]/df['close'][-6])-1)*100
  # if ta_change_last5<0:
  #   ta_change_last5_mag=ta_change_last5*(-1)
  # else:
  #   ta_change_last5_mag=ta_change_last5  




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
  ta['ma5']= tb.MA(df['close'], 5)

  # #ta_pos['close]
  # ta_pos['close']=df['close'][-1]
  # ta_pos['close5']=df['close'][-6]
  # ta_pos['diff5']=df['close'][-1]-df['close'][-6]


  #ema
  ta['ema200']=tb.EMA(df['close'], 200)
  

  #aroon
  ta['aroon']=tb.AROONOSC(df['high'],df['low'],timeperiod=14)
  #ta_aroon"]=ta_each['aroon'][-1]
  
  ##aroon

  #engulfing
  #ta_each["engulfing"]=tb.CDLENGULFING(df['open'],df['high'],df['low'],df['close'])
  #ta_engulfing"]=ta_each['engulfing'][-1]
  #ta_pos['engulfing']=int(ta_each['engulfing'][-1]/100)

  #engulfing without using talib to save time
  ta["engulfing"]=tb.CDLENGULFING(df['open'],df['high'],df['low'],df['close'])
  ta_pos['engulfing']=ta['engulfing']/100

  #macd
  ta['macd']=tb.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)[0]
  ta['macd_sig']=tb.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)[1]
  ta['macd_hist']=tb.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)[2]


  ta['macd_hist_last']=tb.MACD(df['close'][:-1], fastperiod=12, slowperiod=26, signalperiod=9)[2]


  #OBV indicator
  ta['obv_last']=tb.OBV(df['close'],df['open'])
  

  #sar
  ta['sar_now']=tb.SAR(df['high'],df['low'],0.02,0.2)[-(i+1)]
  #ta_sar_prev=tb.SAR(df['high'],df['low'],0.02,0.2)[-(i+2)]


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
  ta['adx']=tb.ADX(df['high'],df['low'],df['close'])
 

  #bbands
  ta['bbands_up']=tb.BBANDS(df['close'],5,2,2,0)[0]
  ta['bbands_mid']=tb.BBANDS(df['close'],5,2,2,0)[1]
  ta['bbands_down']=tb.BBANDS(df['close'],5,2,2,0)[2]


  #rsi
  ta['rsi']=tb.RSI(df['close'])

  #PPO
  ta['ppo']=tb.PPO(df['close'], fastperiod=12, slowperiod=26, matype=0)


  for i in range(len(data.index)):
    
    #ema200
    if df['close'][i]>ta['ema200'][i]:
      ta['ema200_trend'][i]=1
    elif df['close'][i]<ta['ema200'][i]:
      ta['ema200_trend'][i]=-1
    else:
      ta['ema200_trend'][i]=0     
  
    #aroon
    if ta['aroon'][i]>=90 and ta['ema200_trend'][i]==1:
      ta_pos['aroon'][i]=1
    elif ta['aroon'][i]<=-90 and ta['ema200_trend'][i]==-1:
      ta_pos['aroon'][i]=-1
    else:
      ta_pos['aroon'][i]=0

    #macd
    ta['macd_hist_mag'][i]=ta['macd_hist'][i] if ta['macd_hist'][i]>0 else (-1)*ta['macd_hist'][i]

    if ta['macd_hist'][i]>0 and ta['macd_hist_last'][i]<0 and ta['macd'][i]<0 and ta['macd_sig'][i]<0:
      ta_pos['macd'][i]=1
    elif ta['macd_hist'][i]<0 and ta['macd_hist_last'][i]>0 and ta['macd'][i]>0 and ta['macd_sig'][i]>0:  
      ta_pos['macd'][i]=-1
    elif ta['macd_hist'][i]>0 and ta['macd_hist_last'][i]>0 and ta['macd_hist'][i]>ta['macd_hist_last'][i]:    #######Multiply with the strength of macd#######
      ta_pos['macd'][i]=1
    elif ta['macd_hist'][i]<0 and ta['macd_hist_last'][i]<0 and ta['macd_hist'][i]<ta['macd_hist_last'][i]:  
      ta_pos['macd'][i]=-1
    else:
      ta_pos['macd'][i]=0    

    #obv
    ta['obv_avg5'][i]=(ta['obv_last'][i]+ta['obv_last'][i-1]+ta['obv_last'][i-2]+ta['obv_last'][i-3]+ta['obv_last'][i-4])/5   

    if ta['obv_last'][i]>ta['obv_avg5'][i]:
      ta_pos['obv'][i]=1
    elif ta['obv_last'][i]<ta['obv_avg5'][i]:
      ta_pos['obv'][i]=-1
    else:
      ta_pos['obv'][i]=0

    #sar  
    if ta['sar_now'][i]<df['close'][i] and ta['ema200_trend'][i]==1:
      ta_pos['sar'][i]=1
    elif ta['sar_now'][i]>df['close'][i] and ta['ema200_trend'][i]==-1:
      ta_pos['sar'][i]=-1
    else:
      ta_pos['sar'][i]=0 

    #adx
    if ta['adx'][i]>30:
      ta['adx_trending_mark'][i]=1
    else:  
      ta['adx_trending_mark'][i]=0

    #bbands  
    if df['high'][i]>ta['bbands_up'][i]:
      ta_pos['bbands'][i]=-1
    elif df['low'][i]<ta['bbands_down'][i]:
      ta_pos['bbands'][i]=1
    else:
      ta_pos['bbands'][i]=0

    #rsi
    if ta['rsi'][i]>70:
      ta_pos['rsi'][i]=-1
    elif ta['rsi'][i]<30:
      ta_pos['rsi'][i]=1
    else:
      ta_pos['rsi'][i]=0

    #ppo
    if ta['ppo'][i]>0 and ta['ema200_trend'][i]==1:
      ta_pos['ppo'][i]=1
    elif ta['ppo'][i]<0 and ta['ema200_trend'][i]==-1:
      ta_pos['ppo'][i]=-1
    else:
      ta_pos['ppo'][i]=0 

  ta_pos['ema200']=ta['ema200_trend']

  # print(ta)
  # print(ta_pos)

  ############# No indicators after this #############

  #### Multiply the final pos with the average of the last 5 percentage changes in the price to know how good it is (be careful with the start of the day as it might be very high)

  for i in range(len(data.index)):
  
    #final_pos
    ta_pos['final_pos'][i]=0
    if ta['adx_trending_mark'][i]==1:
      ta_pos['final_pos'][i]=ta_pos['final_pos'][i]+ta_pos['ema200'][i]*0.56*5.5*6.4+ta_pos['aroon'][i]*0.4*4*1+ta_pos['engulfing'][i]*0.55*5*4+ta_pos['macd'][i]*0.78*8*7+ta_pos['sar'][i]*0.42*4.2*2+ta_pos['ppo'][i]*0.58*6*6
      ta_pos['final_pos_trending'][i]=ta_pos['final_pos'][i]
    else: 
      ta_pos['final_pos'][i]=np.nan
      #ta_pos['final_pos=ta_pos['final_pos+ta_pos['bbands*0.55
      #ta_pos['final_pos_ranging=ta_pos['final_pos  

    #final_pos*slope_last5
    if ta_pos['final_pos'][i]*ta['ema_last5'][i]>0:
      ta_pos['net_final_pos'][i]= ta_pos['final_pos'][i]*ta['ema_last5_mag'][i]        #*(ta['macd_hist'][i]_mag/ta_ema200)
    else:
      ta_pos['net_final_pos'][i]=np.nan  
  # if ta_pos['final_pos_trending*ta_change_last5>0:
  #   ta_pos['net_final_pos_trending=ta_pos['final_pos_trending*ta_change_last5_mag
  # else:
  #   ta_pos['net_final_pos_trending=np.nan
  #   ta_pos['net_final_pos_ranging=ta_pos['final_pos_ranging*ta_change_last5_mag

  #storing the net_pos at each timeframe
  data['net_pos']=ta_pos['net_final_pos']
  data['norm_pos']=ta_pos['final_pos']
  

  for n_ind in range(len(data.index)): 
    data['net_pos_mag'][n_ind]=data['net_pos'][n_ind] if data['net_pos'][n_ind]>=0 else (-1)*data['net_pos'][n_ind]
  
  #print(data)

  store_data=pd.DataFrame()
  store_data=data.copy() ### Stores the data before eliminating nan values
  
  data = data.dropna(subset=['net_pos'])

  temp_data=data.reset_index()
  sign_change = temp_data.index[(temp_data['net_pos'].shift(1) * temp_data['net_pos']) <= 0 ].tolist()

  dpk=0
  scx=0
  while dpk<len(data.index) and scx<len(sign_change):
    if sign_change[scx]>dpk:
      data['exit_change_price'][dpk]=data['close'][sign_change[scx]]-data['close'][dpk]
      data['exit_change%'][dpk]=((data['close'][sign_change[scx]]/data['close'][dpk])-1)*100
      if data['net_pos'][dpk]<0: ##short selling##
        data['net_profit'][dpk]=-data['exit_change%'][dpk]-0.05 ######brokerage %####
      else:
        data['net_profit'][dpk]=data['exit_change%'][dpk]-0.05 ######brokerage %####
         
      dpk=dpk+1  
    else:
      scx=scx+1

  #print(data)    

  for ite_i in range(len(data.index)):
    r=store_data.index.get_loc(data.index[ite_i])
    store_data['exit_change_price'][r]=data['exit_change_price'][ite_i]
    store_data['exit_change%'][r]=data['exit_change%'][ite_i]
    store_data['net_profit'][r]=data['net_profit'][ite_i]

  data=store_data.copy()
  


  df50.append(data)  #### But we are deleting the rows with naN net_pos values    

  #data=data.dropna()

  print(data)
  print(len(data.index))
  print(len(data[data['net_profit']>0]))

  # total_n=len(data.index)
  # wins=len(data[data['net_profit']>0])
  # win_rate=wins*100/total_n
  # print(win_rate)

# for df in df50:
#   print(df)
#   nan_count = df['net_pos'].isna().sum()
#   print(5000-nan_count)


#Storing the dataframes as .xlsx files in NIfty50_train_5min folder

# Specify the folder name
folder_name = f'Nifty50_train_30min'

for i, df in enumerate(df50):
  file_name = f'{n50_symbols[i]}_train.xlsx'
  file_path = os.path.join(folder_name, file_name)
  df.to_excel(file_path, index=False)  # Use mode='w' to overwrite the file if it exists


end=time.time()
print(f"Time take: {end-begin}")
################



  #######################you gotta get the magnitude of net_pos

  # plt.scatter(data['net_pos'],data['net_profit'])
  # plt.xlabel('net_pos')
  # plt.ylabel('profit')
  # plt.show()





###########################################################################



      
#     #final_pos_mag
#     if ta['pos['net_final_pos']<0:
#       ta['pos['net_final_pos_mag']=(-1)*ta['pos['net_final_pos']
#     else:
#       ta['pos['net_final_pos_mag']=ta['pos['net_final_pos']
    
#     #atr
#     ta['atr"]=tb.ATR(df['high'],df['low'],df['close'])[-1]
#     if ta['pos['final_pos']>0:
#       ta['atr_stoploss"]=df['close'][-1]-2*(ta['atr"])
#     elif ta['pos['final_pos']<0:
#       ta['atr_stoploss"]=df['close'][-1]+2*(ta['atr"])
#     else:
#       ta['atr_stoploss"]=df['close'][-1]
#     ta['stpl.loc[i].at["atr_stoploss"]=ta['atr_stoploss"]

#     #final_stoploss
#     s_stpl=0
#     den=0
#     for n in range(len(stpl)):
#       if ta['pos['final_pos']>0 and ta['stpl.loc[i].at[stpl[n]]<df['close'][-1]:
#         s_stpl=s_stpl+ ta['stpl.loc[i].at[stpl[n]]
#         den=den+1
#       elif ta['pos['final_pos']<0 and ta['stpl.loc[i].at[stpl[n]]>df['close'][-1] :   
#         s_stpl=s_stpl+ ta['stpl.loc[i].at[stpl[n]]
#         den=den+1
#       if den!=0:
#         ta['stpl.loc[i].at["final_stoploss"]=s_stpl/den

#   ta['pos['stoploss']=ta['stpl['final_stoploss']
#   ta['pos['trend']=ta['adx_trending_mark']
  
#   s_ta['pos=ta['pos.sort_values(['net_final_pos_mag','final_pos'], ascending=False).reset_index(drop=True)
#   #sorted df
  
  
#   #This is for the new timeframe 
#   final_data['symbol']=s_ta['pos['symbol']
#   final_data['normal_pos']=s_ta['pos['final_pos']
#   final_data['net_pos']=s_ta['pos['net_final_pos']
#   final_data['trend']=s_ta['pos['trend']
#   final_data['price']=s_ta['pos['close']
#   final_data['stoploss']=s_ta['pos['stoploss']
#   final_data['brokerage']=final_data['price']*0.0005
#   for i in range(51):
#     if final_data['brokerage'][i]>20:
#       final_data['brokerage']=20


#   #print(ta)
#   #print(s_ta['pos)
#   #print(final_data)
#   #print(ta['stpl) 
  

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
#       net_pos:{final_data['net_pos'][i]}
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


