#encoding:utf8
import pandas as pd 
from pandas import DataFrame,Series
from pandas.core.common import _coerce_indexer_dtype,is_categorical_dtype
from pandas.core import base
from categorical import SmartCategoricalAccessor
import copy
from header import DataframeHeader

class SmartSeries(Series):
	header=None
	_metadata=['header']
	@property 
	def _constructor(self):
		return SmartSeries
	@property 
	def _constructor_expaddim(self):
		return SmartDataFrame
	def __init__(self,*args,**kwargs):
		header=kwargs.pop('header',None)
		super(SmartSeries,self).__init__(*args,**kwargs)
		self.header=header
	def _make_cat_accessor(self):
		if not is_categorical_dtype(self.dtype):
			raise AttributeError("Can only use .cat accessor with a "
								 "'category' dtype")
		return SmartCategoricalAccessor(self.values, self.index)
	cat= base.AccessorProperty(SmartCategoricalAccessor, _make_cat_accessor)
	def include_value_percent(self):
		'''
		计算有多少值在header.levels中，
		帮助我们判断是否需要将值进行编码
		'''
		return self[self.isin(self.header.levels)].count()/float(self.count())
	def alps_map(self):
		m_a=can_trans_to_alpha(self)
		alps=self[m_a].unique()
		alps_code=to_num(alps)
		return dict(zip(alps,alps_code))
	def errors_map(self):
		m_a=can_trans_to_alpha(self)
		errs=self[~m_a].unique()
		errs_code=code_error(errs,self.header.blank_code,self.header.overflow_code)
		return dict(zip(errs,errs_code))
	def get_values_map(self):
		'''
		将series中的值映射成数字，
		即：
			a-->1
			b-->2
			c-->3
			.....
		'''	
		d=self.alps_map()
		d.update(self.errors_map())
		return d
	def to_num(self,map_dict={}):
		map_dict=map_dict or self.get_values_map()
		m= self.map(map_dict.get)
		m.header=self.header 
		return m
 
class SmartDataFrame(DataFrame):
	_header=None
	_metadata=['_header']
	@property 
	def _constructor(self):
		return SmartDataFrame
	@property 
	def _constructor_sliced(self):
		return SmartSeries
	def __init__(self,*args,**kwargs):
		header=kwargs.pop('header',None)
		super(SmartDataFrame,self).__init__(*args,**kwargs)
		if header:
			self.header=header
		if isinstance(args[0],SmartSeries):
			self.header={self.columns[0]:args[0].header}
	def __getitem__(self,key):
		rt=super(SmartDataFrame,self).__getitem__(key)
		print type(rt)
		if isinstance(rt,Series):
			rt.header=self.header[rt.name]
		elif isinstance(rt,DataFrame):
			rt.header=self.get_header(rt.columns)
		return rt
	def __setitem__(self,key,value):
		if isinstance(value,SmartSeries):
			self.header[key]=value.header
		super(SmartDataFrame,self).__setitem__(key,value)

	@property 
	def header(self):
		return self._header 
	@header.setter
	def header(self,header):
		if header is None:
			return 
		if isinstance(header,DataframeHeader):
			self._header=header
		elif isinstance(header,dict):
			self._header=DataframeHeader(header)
		elif isinstance(header,DataFrame):
			self._header=DataframeHeader.from_dataframe(header)
		cols=self.validate_header(self._header)
		if cols:
			raise ValueError(u'有%d个变量没有定义header（%s）：' % (len(cols),str(cols)))
	def validate_header(self,header):
		'''
		验证header是否包含Dataframe的全部columns
		'''
		cols=[c for c in self.columns if c not in header]
		return cols
	def get_header(self,columns):
		if isinstance(columns,(list,tuple,set,pd.Index)):
			header=DataframeHeader()
			for c in columns:
				header[c]=copy.deepcopy(self.header[c])
		else:
			header=self.header[columns]
		return header


class AlgorMixin(object):
	def category_cols(self):
		'''
		category （分类变量）必须规定值水平（levels），
		否则我们认为他不是一个分类变量
		'''
		return [c for c in self.columns if self.header[c].levels]

	def need_trans_cols(self):
		'''
		筛选需要进行值编码的列
		'''
		cols=[]
		for c in self.category_cols():
			if self[c].include_value_percent()<0.05:
				cols.append(c)
		return cols
	def to_num(self,cols=None):
		cols=cols or need_trans_cols()
		for c in cols:
			self[c]=self[c].to_num()






if __name__=='__main__':
	df=SmartDataFrame({'a':list('abcdefg'),'b':range(7),'c':range(1,8)},columns=list('abc'))
	df.header=dict(a=1,b=2,c=3)
	a=df['a'].copy()
	a.iloc[0]=None
	c=a.astype('category')
	print c.cat.categories,c.cat.codes
	c.cat.codes=[1]*7
	print c.cat.categories,c.cat.codes