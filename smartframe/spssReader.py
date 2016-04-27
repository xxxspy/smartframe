
from savReaderWriter import SavReader
from savReaderWriter.generic import *
from pinyin import pinyin ,is_chinese
from pandas import DataFrame,concat
class _Generic(Generic):

	def openSavFile(self,savFileName,mode=b"rb",refSavFileName=None):
		
		if self._savFile is None:
			return super(_Generic,self).openSavFile(savFileName,mode,refSavFileName)
		else:
			savFileName = os.path.abspath(savFileName)
			try:
				fdopen = self.libc._fdopen  # Windows
			except AttributeError:
				fdopen = self.libc.fdopen   # Linux and others
			fdopen.argtypes, fdopen.restype = [c_int, c_char_p], c_void_p
			fdopen.errcheck = self.errcheck
			mode_ = b"wb" if mode == b"cp" else mode
			f=self._savFile
			self.fd = fdopen(f.fileno(), mode_)
			if mode == b"rb":
				spssOpen = self.spssio.spssOpenRead
			elif mode == b"wb":
				spssOpen = self.spssio.spssOpenWrite
			elif mode == b"cp":
				spssOpen = self.spssio.spssOpenWriteCopy
			elif mode == b"ab":
				spssOpen = self.spssio.spssOpenAppend

			savFileName = self._encodeFileName(savFileName)
			refSavFileName = self._encodeFileName(refSavFileName)
			sav = c_char_py3k(savFileName)
			fh = c_int(self.fd)
			if mode == b"cp":
				retcode = spssOpen(sav, c_char_py3k(refSavFileName), pointer(fh))
			else:
				retcode = spssOpen(sav, pointer(fh))

			msg = "Problem opening file %r in mode %r" % (savFileName, mode)
			checkErrsWarns(msg, retcode)
			return fh.value

def create_savreader(savFileName='', savFile=None,returnHeader=False, recodeSysmisTo=None,
                 verbose=False, selectVars=None, idVar=None, rawMode=False,
                 ioUtf8=False, ioLocale=None):
	savFileName=savFileName if savFile is None else savFile.name
	mro=[]
	for m in SavReader.mro():
		if m==Generic:
			mro.append(_Generic)
		else:
			mro.append(m)
	return type('SavFileReader',tuple(mro),{'_savFile':savFile})(savFileName, returnHeader, recodeSysmisTo,
                 verbose, selectVars, idVar, rawMode,
                 ioUtf8, ioLocale)
def clean_varnames(varnames):
	'''helper function for invalid column names for dataframe'''
	clean_vnames=[]
	change_map={}
	for varname in varnames:
		c_varname=pinyin.hanzi2pinyin_join(string=varname)
		clean_vnames.append(c_varname)
		if c_varname != varname:
			change_map[varname]=c_varname
	return clean_vnames,change_map


def sav2dataframe(savFileName='',savFile=None,chunksize=10000):
	reader=create_savreader(savFileName=savFileName,savFile=savFile,ioUtf8=True)
	casenum=reader.numberofCases
	loopnum=int(casenum/chunksize)
	dfs=[]
	varnames,change_map=clean_varnames(reader.header)
	for n in range(loopnum):
		print n/float(loopnum)
		df=DataFrame(reader[n*chunksize:(n+1)*chunksize],columns=varnames)
		dfs.append(df)

	if casenum-loopnum*chunksize>0 and loopnum>0:
		df=DataFrame(reader[(n+1)*chunksize:],columns=varnames)
		dfs.append(df)
	elif loopnum==0:

		df=DataFrame(reader.all(),columns=varnames)
		dfs=[df]
	reader.close()
	return concat(dfs),change_map




if __name__=='__main__':
	import time
	f=file('testdata.sav',b'rb')
	print dir(f)
	df,ns=sav2dataframe(savFile=f)
	time0=time.time()
	df.to_csv('test.csv')
	time1=time.time()
	df.to_pickle('test.pkl')
	time2=time.time()
	print 'csv:', time1-time0
	print 'pkl:',time2-time1
	f.close()