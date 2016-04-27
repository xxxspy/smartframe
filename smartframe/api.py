#encoding:utf8
from frame import SmartDataFrame,SmartSeries
from header import DataframeHeader
import algorithms as alg


__all__=['NotSmart','get_alpha_cols','alpha2num']
class NotSmart(ValueError):
	'''如果Dataframe或者Series不是SmartDataFrame或者SmartSeries，
	就会引发这个错误'''

class Api(object):
	_prepare_funcs={}
	_execute_funcs={}
	def register(self,alg_name,func_name,func):
		'''
		参数：
			func_name:prepare/execute 
			alg_name:命令菜单中的ID属性或者算法框的name属性，他们是一样的
		'''
		if func_name=='prepare':
			self._prepare_funcs[alg_name]=func
		elif func_name=='execute':
			self._execute_funcs[alg_name]=func
		else:
			raise ValueError(u'没有指定的过程算法 %s' % func_name)
	def prepare_func(self,alg_name):
		return self._prepare_funcs[alg_name]
	def execute_func(self,alg_name):
		return self._execute_funcs[alg_name]


def get_alpha_cols(df,columns=None,percent=0):
	'''
	筛选需要进行字母转数字的列名
	'''
	header=df.header
	#筛选出单选题和数字类型题目
	numvars=columns or [c for c in header if header[c].dtype==0 and header[c].rtype==1]
	cols=[]
	counts=[]
	percents=[]
	for c in numvars:
		ser=df[c]
		mask=can_trans_to_alpha(ser)
		ct1=ser[mask].count()
		ct2=ser.count()
		p=float(ct1)/ct2
		if p>percent:
			percents.append(p)
			cols.append(c)
			counts.append(ct1)
	resp={
		'columns':cols,
		'counts':counts,
		'percents':percents,
		}
	header=DataframeHeader()
	header['columns']=VariableHeader(name='columns',dtype='20')
	header['counts']=VariableHeader(name='counts',dtype=0)
	header['percents']=VariableHeader(name='percents',dtype=0,decimals=3)
	return SmartDataFrame(resp,header=header)

def filter_alpha_cols(cols ,counts,percents,percent):
	index=[i for i ,p in enumerate(percents) if p>percent]
	rcols=[cols[i] for i in index]
	rcounts=[counts[i] for i in index]
	rpercents=[percents[i] for i in index]
	return rcols,rcounts,rpercents



def ser_alpha2num(ser):
	# if not isinstance(ser,SmartSeries):
	# 	raise NotSmart('传入的Series不是SmartSeries')
	alpha2num_func



def alpha2num(df,cols=None):
	'''
	将字母转换为数字，并输出转换结果
	不能转换的值保留，没有进行处理
	'''
	for c in cols:
		df[c]=alpha2num_func(df[c])
	return df




###################register#############################
api=Api()
api.register('value-transfor','prepare',get_alpha_cols)
api.register('clean-value','prepare',alg.blank_over_cols)
api.register('clean-value','execute',alg.code_blank_over)
