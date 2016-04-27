import pandas as pd 
from frame import SmartDataFrame
df=SmartDataFrame(pd.read_excel('test_data_0LLPTJ8.xlsx'))
cb=pd.read_excel('test_codebook.unique_NreyUzz.xlsx')
df.header=cb