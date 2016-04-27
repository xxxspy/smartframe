#D:/myPythonEnv/dataSmarter/Scripts/python
#encoding:utf8
from pandas import DataFrame,Series
import re
from savReaderWriter import SavHeaderReader,SavWriter
import copy
import numpy as np
import pandas as pd
class VarHeader(dict):
	def __getattr__(self,name):
		return self[name]
	def __setattr__(self,name,value):
		self[name]=value


class SmartSeries(Series):
	varheader=None
	def __init__(self,*args,**kwargs):
		self.varheader=kwargs.pop('varheader',{})
		super(SmartSeries,self).__init__(*args,**kwargs)
		self.cache={}
	def clean(self):
		self.clean_blank()
		self.clean_overflow()
		self.clean_duoxuan()
		self.varheader.is_cleaned=True
	def clean_blank(self):
		if self.varheader.blank_code:
			self.fillna(self.varheader.blank_code)
	def clean_overflow(self):
		if self.varheader.validvalues and self.varheader.overflow_code:
			self[self.isin(self.varheader.validvalues)]=self.VarHeader.overflow_code
	def clean_duoxuan(self):
		pass
	def alpha2num(self):
		def func(alp):
			if isinstance(alp,(str,unicode)):
				if  len(alp) >1:
					alp=alp.strip()
				if len(alp)==1 and  alp.isalpha():
					return ord(alp.upper())-64
			return alp
		return self.map(func)

	def reverse_var(self):
		if self.varheader.levels:
			ignore_levels=[self.varheader.blank_code,self.varheader.overflow_code,self.varheader.duoxuan_code]
			levels =[ l for l in self.varheader.levels if l not in ignore_levels]
			levels_key=sorted(levels,reverse=False)
			levels_value=sorted(levels,reverse=True)
			levels_key.extend(ignore_levels)
			levels_value.extend(ignore_levels)
			dic=dict(zip(levels_key,levels_value))
			return SmartSeries(self.map(dic))
		return self


	def split_multiselection(self,spliter=',',name=''):
		'''将一列数据分成多列'''
		name=name or self.name
		pattern=re.compile('\((?P<nums>\d+\+\d+)\)')
		m=pattern.search(name)
		if m:
			m=m.group('nums')
			splited=self.str.split(spliter)
			df=DataFrame(self)
			nums=[int(x) for x in m.split('+')]
			for i in range(nums[0]):
				lower=chr(i+97)
				upper=chr(i+65)
				df[name+'_'+upper]=splited.apply(lambda x:1 if upper in unicode(x) or lower in unicode(x) else 0)
			df[name + '_' + 'other']=splited.apply(lambda x: spliter.join(filter(lambda z:not unicode.isalpha(z),unicode(x))))
			del df[name]
			return df
	def cache_value(self,key,kwargs={}):
		if key in self.cache:
			return self.cache[key]
		else:
			func=getattr(self,key)
			value=func(**kwargs)
			self.cache[key]=value
			return value

	def value_count(self,value=None):
		ret=None
		if value:
			try:
				vcs=self.cache_value(self,'value_counts',kwargs={'dropna':False})
				ret= vcs.loc[value]
			except KeyError:
				ret= 0
		return ret
	def missing_count(self,m=None):
		m=m or self.header['missingvalue']
		return self.value_count(value=m)


class SmartFrame(DataFrame):
	'''header:
		missingValues
	'''
	varproperties=['missingValues','varset','valueLabels','varNames','varTypes','varLabels']
	header=None
	varset={}
	def __init__(self,*args,**kwargs):
		self.header=kwargs.pop('header',{})
		self.varset=kwargs.pop('varset',{})
		super(SmartFrame,self).__init__(*args,**kwargs)
	@property
	def valuelabels(self):
		return self.sav_header.get('valuelabels',{})

	@valuelabels.setter
	def valuelabels(self,labels):
		self.sav_header['valuelabels']=labels
	def get_varlabel(self,colname):
		return self.header['varLabels'].get(colname)
	@property
	def missingvalues(self):
		return self.sav_header['missingvalues']
	def __getitem__(self,key):
		rt=super(SmartFrame,self).__getitem__(key)
		if isinstance(rt,Series):
			varheader=self.get_varheader(rt.name)
			rt=SmartSeries(rt,varheader=varheader)
		elif isinstance(rt,DataFrame):
			rt.header=self.get_header(rt.columns)
		return rt
	def get_header(self,vars):
		rheader={}
		header=copy.copy(self.header)
		for p in header:
			if p in ['valueLabels', 'varTypes', 'varLabels', 'missingValues']:
				if p not in rheader:rheader[p]={}
				for v in header[p]:
					if v in vars:
						rheader[p][v]=header[p][v]
		return rheader

	def sum_vars(self,vars,new_name=None):
		if new_name is None:
			new_name='+'.join(vars)
		while  new_name in self.columns:
			new_name +='n'
		df[new_name]=df[vars].sum(axis=1)
		return new_name
	def insert_cols(self,name_or_index,df):
		'''在指定列（name_or_index）的前面插入df'''
		if name_or_index in self.columns:
			name=name_or_index
			columns=self.columns.tolist()
			index=columns.index(name)
			for c in df.columns:
				index +=1
				self.insert(index,c,df[c])
	def header_from_sav(self,filename):
		header= SavHeaderReader(filename,ioUtf8=True)
		self.header={}
		key=self.varproperties
		for key in self.varproperties:
			self.header[key]=getattr(header,key)
		self.validate_header(self.header)
		header.close()
		return self
	def get_varheader(self,varname):
		header={}
		for p in self.varproperties:
			if p not in ['varNames','varset']:
				header[p]=self.header[p].get(varname)
		return header
	def validate_header(self,header):
		for c in self.columns:
			if c not in header['varNames']:
				print '%s not in header[varNames]' % c
				raise


	def to_sav(self,filename=None,varnames=None):
		filename=filename or 'new_sav_file_from_dataframe.sav'

		if varnames is None:
			varnames=self.columns
		kwargs=self.get_header(varnames)
		#print kwargs
		kwargs['varNames']=varnames
		kwargs['ioUtf8']=True
		with SavWriter(savFileName=filename,**kwargs) as writer:
			for r,values in self.iterrows():
				print r
				writer.writerow(values.values)
		print 'finished wiriting'





def count_compare(ss,header=None,percent=False,dfnames=[]):
	dfnames=dfnames or ['column'+ i for i in range(len(ss))]
	header=header or ss[0].varheader
	values=header['valueLabels']
	df=pd.DataFrame(pd.Series(values),columns=[u'值标签'])
	i=0

	for s in ss:
		column=dfnames[i]
		count=s.value_counts(dropna=False)

		if percent:
			count=count/count.sum()*100

		df.insert(i+1,column,count)

		i +=1

	df[dfnames].fillna(0,inplace=True)
	df.reset_index(inplace=True)
	df.rename(columns={'index':u'值'},inplace=True)
	return df

def compare_columns(dfs,columns,names,header=None):
	if len(dfs) !=len(names):raise ValueError('len(dfs) should be equal to len(names)')
	header=header or dfs[0].header
	rdfs=[]
	for c in columns:
		ss=[df[c] for df in dfs]
		rdf=count_compare(ss,percent=True,dfnames=names)
		rdf[u'变量']=c
		rdf[u'变量标签']=header['varLabels'].get(c) or c
		rdfs.append(rdf)
	return rdfs
def data_from_sav(filename):
	return df