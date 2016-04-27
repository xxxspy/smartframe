#encoding:utf8
from pandas.core.categorical import Categorical, CategoricalAccessor
from pandas.core.common import _coerce_indexer_dtype
class SmartCategorical(Categorical):
	pass
	# @property 
	# def codes(self):
	# 	return super(SmartCategorical,self).codes
	# @codes.setter 
	# def codes(self,codes):
	# 	self._codes=_coerce_indexer_dtype(codes,self.categorical.categories)
class SmartCategoricalAccessor(CategoricalAccessor):
	@property 
	def codes(self):
		return super(SmartCategoricalAccessor,self).codes
	@codes.setter 
	def codes(self,codes):
		self.categorical._codes=_coerce_indexer_dtype(codes,self.categorical.categories)
		


SmartCategoricalAccessor._add_delegate_accessors(delegate=SmartCategoricalAccessor,
											accessors=['categories',
													   'ordered'],
											typ='property')
SmartCategoricalAccessor._add_delegate_accessors(delegate=SmartCategoricalAccessor, accessors=[
	'rename_categories', 'reorder_categories', 'add_categories',
	'remove_categories', 'remove_unused_categories', 'set_categories',
	'as_ordered', 'as_unordered'], typ='method')