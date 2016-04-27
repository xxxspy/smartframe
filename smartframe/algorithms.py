#encoding:utf8

import pandas as pd
from numpy import vectorize
from smartframe.frame import SmartDataFrame
from smartframe.header import Variable,DataframeHeader
import numpy as np 

@vectorize
def alpha2num_func(alp):
	'''将字母构成的字符串进行清理，
	主要是删除空格和其他字符'''
	if isinstance(alp,(str,unicode)):
		if  len(alp) >1:
			alp=alp.translate(None,' ,.')
		if len(alp)==1 and  alp.isalpha():
			return ord(alp.upper())-64
	return alp


@vectorize
def can_trans_to_alpha(alp):
	'''
	筛选出是字母，或者可以转换为字母的cell，比如['a','a ','a. ']

	'''
	if isinstance(alp,(str,unicode)):
		if  len(alp) >1:
			alp=alp.translate(None,' ,.')
		if len(alp)==1 and  alp.isalpha():
			return True
	return False


@vectorize
def to_num(alp):
	if isinstance(alp,(str,unicode)):
		if  len(alp) >1:
			alp=alp.translate(None,' ,.')
		if len(alp)==1 and  alp.isalpha():
			return alp.upper()-64
	raise ValueError('%s 不能转为数字' % alp)



def is_all_alpha(ser):
	return can_trans_to_alpha(ser).all()




@vectorize
def code_error(value,header):
	'''
	将无法转换成数字的值，编码成缺失值或者溢出值
	'''
	if np.isnull(value) or value in (None,''):
		return header.blank_code
	if value not in header.levels:
		return header.overflow_code
def count_error(sser):
	blank_index=sser.isin([np.nan,np.inf,'',None])
	good_index=sser.isin(sser.header.levels)
	overflow_index=~good_index & ~blank_index
	good_count=len(sser[good_index])
	blank_count=len(sser[blank_index])
	overflow_count=len(sser[overflow_index])
	return good,blank_count,overflow_count



def count_error_overflow(sdf,cols=None):
	sdf=sdf if cols is None else sdf[cols]
	return sdf.apply(count_error)


def get_values_not_alpha(ser):
	'''
	返回非ABC数据构成的Series,并尝试将其编码
	'''
	mask=~can_trans_to_alpha(ser)
	ser_= ser[mask]
	df=pd.DataFrame(ser_)
	df.columns=['value',]
	df['code']=code_error(ser_,ser.header)
	return df

################blank overflow#################
BLANK_VALUES=[None,np.nan,'']
def blank_values(ser):
	'''在blankvalue中的值被认为缺失值'''
	uni=ser.unique()
	bvs=[v for v in uni if v in BLANK_VALUES]
	return bvs
def overflow_values(ser,blank_values=[]):
	#不在header.levels中的值都被认为是溢出值
	#其中包括了缺失值
	#因此我们还需要排除缺失值
	uni=ser.unique()
	ovs=[v for v in uni if v not in ser.header.levels and (v not in blank_values)]
	return ovs 

def blank_over_cols(sdf,cols=None):
	'''
	找到哪些变量包含哪些缺失和溢出值
	缺失值需要在BLANK_VALUES中定义哪些值是缺失
	参数：
		sdf：SmartDataFrame实例
		cols：需要遍历的列名，如果不指定，默认为sdf.header.number_variables 
	'''
	print 'blank_over_cols...'
	cols=cols or sdf.header.number_variables()
	rcols=[]
	blanks=[]
	overs=[]
	for c in cols:
		bvs=blank_values(sdf[c])
		ovs=overflow_values(sdf[c],bvs)
		if bvs or ovs:
			rcols.append(c)
			blanks.append(bvs)
			overs.append(ovs)
	df= pd.DataFrame.from_dict({'variable':rcols,'blank':blanks,'overflow':overs})

	header=DataframeHeader()
	header['blank']=Variable(name='blank')
	header['overflow']=Variable(name='overflow')
	header['variable']=Variable(name='variable',dtype=20)
	print 'end of blank_over_cols'
	return SmartDataFrame(df,header=header)
def code_blank_over(sdf,blank_over_df):
	'''
	参数：
		sdf：SmartDataFrame实例
		blank_over_df:blank_over_df 是在blank_over_cols中生成的
		里面包含哪些变量包含哪些缺失值和溢出值。
	'''
	cols=['variable','blank','overflow']
	result_count=blank_over_df.copy()
	sdf=sdf.copy()
	for i,variable,blanks,overflows in blank_over_df[cols].itertuples():
		header=sdf.header[variable]


		def map_code(x):
			if x in header.levels:
				return x 
			elif x in blanks:
				return header.blank_code
			elif x in overflows:
				return header.overflow_code
		
		bc=sdf[variable][sdf[variable].isin(blanks)].count()
		oc=sdf[variable][sdf[variable].isin(overflows)].count()
		sdf[variable]=sdf[variable].apply(map_code)
		result_count.loc[i,'blank']=bc 
		result_count.loc[i,'overflow']=oc
	return sdf,result_count









def alpha2num():
	pass


if __name__=='__main__' and 0:
	from frame import SmartSeries,SmartDataFrame
	from time import time
	import numpy as np 
	l=list('abbbbdddbdbded1')
	l.append(None)
	s=SmartSeries(l)
	s.iloc[3]=None
	s.iloc[4]=np.inf
	s.iloc[5]=np.nan
	cs=s.astype('category')
	print cs.cat.codes
	print cs.cat.categories


if __name__=='__main__':
	import pandas as pd 
	data=pd.read_excel('test_data.xlsx')
	codebook=pd.read_excel('test_codebook.xlsx')
	print 'ok'