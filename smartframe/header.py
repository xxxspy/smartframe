#encoding:utf8
from traits import *
import copy
from settings import CODEBOOK_FIELD_NAMES ,ERROR_CODE_DICT
from pandas import isnull
import pandas as pd
CODEBOOK_FIELD_NAMES=copy.deepcopy(CODEBOOK_FIELD_NAMES)
ERROR_CODE_DICT=copy.copy(ERROR_CODE_DICT)

RESPONSE_TYPES={0:u'填空',1:u'选择',2:u'多选'}

BLANK_CODE=-9
BLANK_LABEL=u'缺失'
OVERFLOW_CODE=-8
OVERFLOW_LABEL=u'溢出'
LOGICERROR_CODE=-7
LOGICERROR_LABEL=u'逻辑缺失'
def filter_nan_kwargs(kwargs):
	for k,v in kwargs.items():
		if not isinstance(v,(dict,list)) and isnull(v):
			kwargs.pop(k)




class SerialiserMixin(object):
	'''目前主要是提供了对象序列化的方法data'''
	def data(self):
		data={}
		for n in self.trait_names():
			value=getattr(self,n)
			trait=self.get_trait_object(n)
			if isinstance(trait,Container):
				value=copy.deepcopy(value)
				if isinstance(trait,Dict):
					for k,v in value.item():
						if hasattr(v,'data'):
							value[k]=v.data()
				else:
					for i in range(len(value)):
						if hasattr(value[i],'data'):
							value[i]=value[i].data()
			data[n]=value
		return data
	def get_trait_object(self,name):
		return self.traits()[name]


class Level(SerialiserMixin,HasTraits):
	value=Integer(allow_none=False,help=u'水平值')
	label=Unicode(allow_none=True,help=u'水平标签')
	error=Integer(default_value=0,help=u'错误值')
	_error_code_dict=copy.copy(ERROR_CODE_DICT)
	def __init__(self,*args,**kwargs):
		filter_nan_kwargs(kwargs)
		super(Level,self).__init__(*args,**kwargs)
	def __eq__(self,other):
		try:
			return self.value==other.value
		except AttributeError:
			return self.value==other



class LevelTrait(TraitType):
	_trait=Level
	klass=Level
	default_value=None
	def validate(self,obj,value):
		if value is None and self.allow_none:
			return value
		if isinstance(value,dict):
			filter_nan_kwargs(value)
			value= self._trait(**value)
			return value
		elif isinstance(value,self._trait):
			return value
		else:
			raise TraitError('can not transform value(%s) to level object' % str(value))




RESPONSE_TYPES={0:u'填空',1:u'选择',2:u'多选'}




class Variable(SerialiserMixin,HasTraits):
	name=Unicode(allow_none=False,help=u'')
	label=Unicode(help=u'',default_value=u'')
	dtype=Integer(default_value=0,help=u'数据类型')#0代码数字，大于0表示字符串
	decimals=Integer(default_value=0,help=u'')
	rtype=Integer(default_value=0,help=u'反应类型',choices=RESPONSE_TYPES.keys())
	levels=List(LevelTrait(allow_none=True),allow_none=True,default_value=None)
	varset=Unicode(allow_none=True,help=u'变量集')
	_error_codes=dict(blank_code=None,overflow_code=None,logicerror_code=None)

	def __init__(self,*args,**kwargs):
		filter_nan_kwargs(kwargs)
		self._cfns=CODEBOOK_FIELD_NAMES
		keys=self._error_codes.keys()
		for key in keys:
			if key in kwargs:
				self._error_codes[key]=kwargs.pop(key)
		super(Variable,self).__init__(*args,**kwargs)
		self._validate_levels()#验证level唯一性
		for key,value in self._error_codes.items():
			if value is not None:
				try:
					setattr(self,key,value)
				except ValueError:
					pass
	def __str__(self):
		return str(self.data())
	def _validate_levels(self):
		'''验证level唯一性'''
		for lv in self.levels:
			c=self.levels.count(lv)
			if c>1:
				raise TraitError('level(%d) in variable(%s) should be unique,but the count is %d' %(lv.value,self.name,c))
	@property
	def jsgrid_field(self):
		type='numnber' if self.dtype==0 else 'text'
		return {
		'name':self.name,
		'type':type,
		}


	def add_level(self,level,exist_raise=False):
		'''
		增加水平
		'''
		if isinstance(level,dict):
			level=Level(**level)
		elif isinstance(level,Level):
			pass 
		else:
			raise ValueError('level is not isinstance of Level or dict,it is %s' % type(level))
		while level in self.levels:#验证要添加的level是否已经存在于levels中
			if exist_raise:#如果存在，是引发错误还是自动将level值减一？
				raise ValueError('level has already in levels')
			else:
				level.value-=1
		self.levels.append(level)
	@property
	def blank_code(self):
		for lv in self.levels:
			if lv.error==lv._error_code_dict['BLANK']:
				return lv.value
		lv=Level(value=BLANK_CODE,label=BLANK_LABEL,error=ERROR_CODE_DICT['BLANK'])
		self.add_level(lv,exist_raise=False)
		return lv.value


	def get_level(self,level):
		for lv in self.levels:
			if lv.value==level:
				return lv

	@blank_code.setter
	def blank_code(self,level):
		value=int(level)
		level=self.get_level(value)
		if level:
			level.error=level._error_code_dict['BLANK']
		else:
			raise ValueError('can not find a level which value is %d' % value)


	@property
	def overflow_code(self):
		for lv in self.levels:
			if lv.error==lv._error_code_dict['OVERFLOW']:
				return lv.value
		lv=Level(value=OVERFLOW_CODE,label=OVERFLOW_LABEL,error=ERROR_CODE_DICT['OVERFLOW'])
		self.add_level(lv,exist_raise=False)
		return lv.value


	@overflow_code.setter
	def overflow_code(self,level):
		value=int(level)
		level=self.get_level(value)
		if level:
			level.error=level._error_code_dict['OVERFLOW']
		else:
			raise ValueError('can not find a level which value is %d' % value)
	@property
	def logicerror_code(self):
		
		for lv in self.levels:
			if lv.error==lv._error_code_dict['LOGIC']:
				return lv.value
		lv=Level(value=LOGICERROR_CODE,label=LOGICERROR_LABEL,error=ERROR_CODE_DICT['LOGIC'])
		self.add_level(lv,exist_raise=False)
		return lv.value
	@logicerror_code.setter
	def logicerror_code(self,level):#to do:test this function
		value=int(level)
		level=self.get_level(value)
		if level:
			level.error=level._error_code_dict['LOGIC']
		else:
			raise ValueError('can not find a level which value is %d' % value)

	def data(self):
		data=super(Variable,self).data()
		data['blank_code']=self.blank_code or BLANK_CODE
		data['overflow_code']=self.overflow_code or OVERFLOW_CODE
		data['logicerror_code']=self.logicerror_code or LOGICERROR_CODE
		return data
	def level_records(self):
		'''helper function used in self.to_record'''
		cfn=self._cfns
		levels=[]
		if self.levels:
			for lv in self.levels:
				levels.append(
					{
					cfn['LEVELVALUE']:lv.value,
					cfn['LEVELLABEL']:lv.label,
					cfn['ERROR_CODE']:lv.error,
					}
				)
		return levels

	def to_record(self):
		cfn=self._cfns
		records=[]
		var={cfn['VARNAME']:self.name,
		cfn['VARLABEL']:self.label,
		cfn['DATATYPE']:self.dtype,
		cfn['DECMALS']:self.decimals,
		cfn['VARSET']:self.varset,
		}
		if self.levels :
			for lv in self.level_records():
				var_=copy.copy(var)
				var_.update(lv)
				records.append(var_)
		else:
			records.append(var)
		return records
	@classmethod
	def from_dataframe(cls,df):
		cfn=CODEBOOK_FIELD_NAMES
		df=df.drop_duplicates()
		n_row,n_col=df.shape
		# if (df[cfn['LEVELVALUE']].value_counts()>1).any():
		# 	raise TraitError('levels in variable(%s) should unique' % df[cfn['VARNAME']].iloc[0])
		cols=[cfn['VARNAME'],cfn['VARLABEL'],cfn['DATATYPE'],cfn['DECMALS'],cfn['VARSET']]
		var_df=df[cols]
		var_df.columns=['name','label','dtype','decimals','varset']
		var_dic=var_df.to_dict('record')[0]
		if n_row>1:
			levels=[]
			cols=[cfn['LEVELVALUE'],cfn['LEVELLABEL'],cfn['ERROR_CODE'],]
			level_df=df[cols]
			level_df.columns=['value','label','error']
			lvs=level_df.to_dict('record')
			for lv in lvs:
				levels.append(Level(**lv))
			var_dic['levels']=levels
		return cls(**var_dic)








class DataframeHeader(dict):

	def __setitem__(self,key,value):
		if isinstance(value,dict):
			value=Variable(**value)
		if not isinstance(value,Variable):
			raise TraitError('value should be dict or Variable')
		super(DataframeHeader,self).__setitem__(key,value)
	def data(self):
		data={}
		for key in self.keys():
			data[key]=self[key].data()
		return data
	def subheader(self,vars,inplace=True):
		header=DataframeHeader()
		if not isinstance(vars,(list,set,tuple,pd.core.index.Index)):
			vars=[vars,]
		for v in vars:
			if inplace:
				header[v]=self[v]
			else:
				header[v]=copy.deepcopy(self[v])
		return header
	def jsgrid_fields(self,vars=None):
		header=self.subheader(vars) if vars is not None else self
		fields=[]
		for v in header:
			fields.append(header[v].jsgrid_field)
		return fields

	@classmethod
	def from_dataframe(self,df):
		header={}
		df=df.drop_duplicates([CODEBOOK_FIELD_NAMES['VARNAME'],CODEBOOK_FIELD_NAMES['LEVELVALUE']])
		gp_df=df.groupby([CODEBOOK_FIELD_NAMES['VARNAME']])
		for varname,var_df in gp_df:
			var=Variable.from_dataframe(var_df)
			header[varname]=var
		return header

	def to_dataframe(self):
		from pandas import DataFrame 
		if self:
			records=[]
			for varname in self:
				records.extend(self[varname].to_record())
			return DataFrame.from_dict(records)
		else:
			return DataFrame(columns=CODEBOOK_FIELD_NAMES.values())
 
	def number_variables(self):
		vs=[]
		for v in self:
			if self[v].dtype==0:
				vs.append(v)
		return vs





			


if __name__=='__main__':
	import pandas as pd
	import pickle as pkl
	df=pd.read_excel('variables(math).xlsxzs.xlsx','math')
	df.drop_duplicates(['var','level'],inplace=True)
	header=DataframeHeader.from_dataframe(df)
	f=open('d:/test.pkl','wb')
	pkl.dump(header,f)
	f.close()
	f=open('d:/test.pkl','rb')
	h2=pkl.load(f)
	print h2[u'MTC12']



