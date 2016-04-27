#encoding:utf8
import algorithms as algo  
def alpha2num(df):
	mask=~algo.can_trans_to_alpha(df)
	return mask


if __name__=='__main__':
	from frame import SmartSeries,SmartDataFrame
	df=SmartDataFrame()