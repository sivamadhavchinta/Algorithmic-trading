from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import numpy as np
import talib as tb
import time
import os
#import pywhatkit
import matplotlib.pyplot as plt

begin = time.time()

timeframe=input("Timeframe for analysis: ")

folder_name=f'Nifty50_train_{timeframe}min'
current_directory = os.getcwd()

# Construct the folder path
folder_path = os.path.join(current_directory, folder_name)

# List all files in the folder
files = os.listdir(folder_path)

# Initialize an empty list to store the DataFrames
df50 = []

# Iterate over the files in the folder
for file_name in os.listdir(folder_path):
    # Check if the file is an Excel file
    if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
        # Construct the full file path
        file_path = os.path.join(folder_path, file_name)
        
        # Read the Excel file into a DataFrame
        df = pd.read_excel(file_path)
        
        # Append the DataFrame to the list
        df50.append(df)

# Now you have a list of DataFrames, each representing an Excel file
# You can perform further operations on the DataFrames as needed





balance=8000

total_tests=0
total_wins=0
total_profit=0

for i in range(200,5000):
  ta_each=pd.DataFrame(columns=['symbol','price','norm_pos','net_pos','net_pos_mag','net_profit'])
  s_ta_each=pd.DataFrame()
  for df in df50:
    new_row = pd.Series([df['symbol'][i], df['close'][i], df['norm_pos'][i], df['net_pos'][i], df['net_pos_mag'][i], df['net_profit'][i]],index=ta_each.columns)
    ta_each.loc[len(ta_each.index)]=new_row
    s_ta_each=ta_each.sort_values(['net_pos_mag','norm_pos'], ascending=False).reset_index(drop=True)
  
  is_all_nan = ta_each['net_pos'].isna().all()

  if not is_all_nan:
    total_tests+=1
    aff_top5=pd.DataFrame(columns=s_ta_each.columns)
    k=0
    n_i=0
    while k<1 and n_i<51:  
      if s_ta_each['price'][n_i]<balance:
        new_row_top5=pd.Series(s_ta_each.loc[n_i].values, index=aff_top5.columns)
        aff_top5.loc[len(aff_top5.index)]=new_row_top5
        k+=1
        
      n_i+=1  

    aff_top5['quantity']=aff_top5['net_pos_mag'] #For now we are just considering them equal
    #aff_top5['net_profit_q']=aff_top5['quantity']*aff_top5['net_profit']

    profit_each=aff_top5['net_profit'].sum()
    if profit_each>0:
      total_wins+=1

    total_profit+=profit_each  

print(f'Total tests: {total_tests}')
print(f'Total wins: {total_wins}')
win_rate= (total_wins/total_tests)*100
print(f'Win rate: {win_rate}')   
print(total_profit)

end = time.time()
print(f'Total time taken: {end-begin}')
