from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import numpy as np
import talib as tb
import time
import pywhatkit
import mplfinance as mpf
import plotly.graph_objects as go

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
support_df50=[]
resistance_df50=[]
#########################################

begin=time.time()

n_tf=500 #no of timeframes(no of candles)

# index
#for i in range(1):
data_5_min = tv.get_hist(symbol=f'{n50_symbols[5]}',exchange='NSE',interval=Interval.in_5_minute,n_bars=n_tf) #800 seems to be the best for support as too old support lines will not have much significance
df_init=pd.DataFrame(data_5_min)
df50_init.append(df_init)

df_reset=df_init.reset_index()

fig=go.Figure(data=[go.Candlestick(x=df_reset.index,
                                    open=df_init['open'],
                                    high=df_init['high'],
                                    low=df_init['low'],
                                    close=df_init['close'])])


def is_sup(arr,i):
    for j in range(2):
        if arr[i+j]>=arr[i+j+1]:
            return False
        if arr[i-j]>=arr[i-j-1]:
            return False
    return True    
      
def is_res(arr,i):
    for j in range(3):
        if arr[i+j]<=arr[i+j+1]:
            return False
        if arr[i-j]<=arr[i-j-1]:
            return False
    return True    


for n,df in  enumerate(df50_init):
    #a dataframe to store the data of the support points
    s_df=pd.DataFrame(columns=['index','pullback_price','sup_low','sup_high'])
    #a dataframe to store the data of the resistance points
    r_df=pd.DataFrame(columns=['index','pullback_price','res_low','res_high'])

    #adx
    adx=tb.ADX(df['high'],df['low'],df['close'])
    adx_trend=[]
    for i in range(len(adx)):
        if adx[i]>25:
            adx_trend.append(1)
        else:  
            adx_trend.append(0)



    for i in range(2,len(df.index)-2):
        if is_sup(df['low'],i) and adx_trend[i]:
            s_h=max(df['low'][i+2],df['low'][i-2])
            s_l=df['low'][i]-(s_h-df['low'][i])
            new_row_s=pd.Series([i,df['low'][i],s_l,s_h], index=s_df.columns)
            s_df.loc[len(s_df.index)]=new_row_s

        if is_res(df['high'],i) and adx_trend[i]:
            r_l=min(df['high'][i+2],df['high'][i-2])
            r_h=df['high'][i]+(df['high'][i]-r_l)
            new_row_r=pd.Series([i,df['high'][i],r_l,r_h], index=r_df.columns)
            r_df.loc[len(r_df.index)]=new_row_r

    s_df['index']=s_df['index'].astype(int)
    r_df['index']=r_df['index'].astype(int)        

    
    
    for i_s in range(len(s_df.index)):
        line_trace_mid = go.Scatter(x=[s_df['index'][i_s],n_tf], y=np.full(2,s_df.at[i_s,'pullback_price']), mode='lines', name='Middle line', line=dict(color='blue'))
        fig.add_trace(line_trace_mid)
        line_trace_up = go.Scatter(x=[s_df['index'][i_s],n_tf], y=np.full(2,s_df.at[i_s,'sup_high']) , mode='lines', name='Upper line', line=dict(color='orange'))
        fig.add_trace(line_trace_up)
        line_trace_down = go.Scatter(x=[s_df['index'][i_s],n_tf], y=np.full(2,s_df.at[i_s,'sup_low']), mode='lines', name='Bottom line', line=dict(color='yellow'))
        fig.add_trace(line_trace_down)
        
    print(s_df)
    support_df50.append(s_df)    

    print(r_df)
    resistance_df50.append(r_df) 

fig.update_layout(title='Candlestick Chart with Support and Resistance',
                  xaxis_title='Date',
                  yaxis_title='Price')      

fig.show()



         