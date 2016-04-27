#encoding:utf8
from traitlets import HasTraits,Unicode,Integer,Bool,List,TraitType,Container,Dict,TraitError,Set
import sys


class ChoiceMixin(object):
	def __init__(self,*args,**kwargs):
		self.choices=kwargs.pop('choices',None)
		super(ChoiceMixin,self).__init__(*args,**kwargs)
	def validate(self,obj,value):
		if self.choices :
			if value not in self.choices:
				raise TraitError('值不在预设的选项中')
		return super(ChoiceMixin,self).validate(obj,value)


class Integer(ChoiceMixin,Integer):
	def validate(self, obj, value):
		if isinstance(value, int):
			return value
		if isinstance(value,float):
			return int(value)
		if isinstance(value, long):
			# downcast longs that fit in int:
			# note that int(n > sys.maxint) returns a long, so
			# we don't need a condition on this cast
			return int(value)
		if sys.platform == "cli":
			from System import Int64
			if isinstance(value, Int64):
				return int(value)
		try:
			return int(value)
		except:
			
			self.error(obj, value)


class Unicode(Unicode):
	def validate(self,obj,value):
		try:
			return unicode(value)
		except:
			return super(Unicode,self).validate()

if __name__=='__main__':
	i=Integer(1.0)
	ii=Integer(1.2)
	print dir(ii)
	print ii.default_value
	print ii