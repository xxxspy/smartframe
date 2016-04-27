#encoding:utf8
import unittest
from header import Level,Variable,DataframeHeader
from frame import SmartDataFrame,SmartSeries
import pandas as pd 

# class VariableHeaderTest(unittest.TestCase):
# 	def setUp(self):
# 		print 'setUpppppppppppppp'
# 		lv=Level()
# 		lv.value=1
# 		lv.label='hello world'
# 		lv.isBlankError=True
# 		lv.isLogicError=False
# 		print lv.data()
# 		self.level=lv 
# 	#def test_variable(self):
# 		print 'test_variableeeeeeeeeeeeee'
# 		var=Variable(name='var1')
# 		var.rtype=1
# 		var.levels=[self.level,self.level]
# 		print var.blank_code
# 		print var.data()
# 		self.variable=var
# 	#def test_gener_variable(self):
# 		print 'test_gener_variable'
# 		level={'isBlankError': True, 
# 		'isOverflowError': False, 
# 		'isLogicError': False, 'value': 1,
# 		 'label': u'hello world'}
# 		levels=[level,level]
# 		variabledata={ 'name': u'var1', 'rtype': 1, 'dtype': 0, 'label': u'', 'decimals': 0,'levels':levels}
# 		variable=Variable(**variabledata)
# 		print variable.data()
# 		#self.assertEqual(variable.data(),variabledata)
# 	def test_dataframeheader(self):
# 		dfh=DataframeHeader()
# 		dfh['var1']=self.variable
# 		dfh['var2']=self.variable.data()
# 		print 'dfh.data:',dfh.data()
# 		print dfh.subheader('var1').data()


class FrameTest(unittest.TestCase):
	def setUp(self):
		df=pd.read_excel('test_data.xlsx')
		header=pd.read_excel('test_codebook.unique.xlsx')
		df=SmartDataFrame(df)
		self.df=df 
		self.header=header 
	def test_pickle(self):
		print self.df.__getstate__()
		import pickle as pkl 
		f=open('test.pkl','wb')
		pkl.dump(self.df,f)
		f.close()
		f=open('test.pkl','rb')
		df=pkl.load(f)
		print df.header 

if __name__=='__main__':
	unittest.main()
