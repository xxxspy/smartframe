#encoding:utf8
import os.path
from django.utils.encoding import smart_unicode
dirpath=os.path.dirname(os.path.realpath(__file__))



def is_chinese(uchar):
    """helper function判断一个unicode是否是汉字"""
    if not isinstance(uchar,unicode):uchar=smart_unicode(uchar)
    if len(uchar)>1:
        for u in uchar:
            if u<u'\u4e00' or u >u'\u9fa5':
                return False
            return True
    if uchar>=u'\u4e00' and uchar <=u'\u9fa5':
        return True
    else:
        return False
class PinYin(object):
    def __init__(self, dict_file='hanzi2pinyin.data'):
        self.word_dict = {}
        self.dict_file =os.path.join(dirpath, dict_file)


    def load_word(self,dict_file=''):
        if not dict_file:dict_file=self.dict_file
        if (not os.path.exists(dict_file)):
            raise IOError("NotFoundFile")
        with file(self.dict_file) as f_obj:
            for f_line in f_obj.readlines():
                try:
                    line = f_line.split('    ')
                    self.word_dict[line[0]] = line[1]
                except:
                    line = f_line.split('   ')
                    self.word_dict[line[0]] = line[1]


    def hanzi2pinyin(self, string=""):
        result = []
        if not isinstance(string, unicode):
            string=smart_unicode(smart_unicode)

        for char in string:
            if is_chinese(char):
                key = '%X' % ord(char)
                result.append(self.word_dict.get(key, char).split()[0][:-1].lower())
            else:
                result.append(char)
        return result


    def hanzi2pinyin_join(self, string="", split=""):
        result = self.hanzi2pinyin(string=string)
        return split.join(result)


pinyin=PinYin()
pinyin.load_word()
