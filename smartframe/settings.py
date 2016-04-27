#encoding:utf8



#编码手册字段名
CODEBOOK_FIELD_NAMES=dict(
#变量名
VARNAME='var',
#变量标签
VARLABEL='varlabel',
#数据格式
DATATYPE='dtype',

#小数位数
DECMALS='decimals',
#变量集
VARSET='varset',
#水平值
LEVELVALUE='level',
#水平标签
LEVELLABEL='levellabel',
#错误代码
ERROR_CODE='errorcode',
)
ERROR_CODE_DICT=dict(
	NOERROR=0,#没有错误标0
	BLANK=1,#缺失错误
	OVERFLOW=2,#溢出错误
	LOGIC=3,#逻辑错误
)