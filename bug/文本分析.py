import csv
import sys
from snownlp import SnowNLP
from snownlp import sentiment
import pandas as pd
import jieba
import jieba.posseg as pseg
from string import punctuation
import re
import xlwt  # pip install xlwr
import xlrd  # pip install xlrd
import os
import datetime
import time
from similarity.cosine import Cosine
from similarity.damerau import Damerau
from similarity.jaccard import Jaccard
from similarity.jarowinkler import JaroWinkler
from similarity.levenshtein import Levenshtein
from similarity.longest_common_subsequence import LongestCommonSubsequence
from similarity.metric_lcs import MetricLCS
from similarity.ngram import NGram
from similarity.normalized_levenshtein import NormalizedLevenshtein
from similarity.optimal_string_alignment import OptimalStringAlignment
from similarity.qgram import QGram
from similarity.sorensen_dice import SorensenDice
from similarity.weighted_levenshtein import WeightedLevenshtein, CharacterSubstitutionInterface

##回复率还没解决，整体的描述性统计还没解决！这个可以等重新下数据再来弄，实在不行写论文的时候再弄也可以！问询函的统计应为：问询函-收函日期（如果没收到就定位年末）-是否收函
# 文件夹路径
folder_path = "/Users/cht/Documents/files/"


##解决csv太大读不了的问题
maxInt = sys.maxsize
decrement = True
while decrement:
    # decrease the maxInt value by factor 10   
    # as long as the OverflowError occurs.  

    decrement = False
    try:
        csv.field_size_limit(maxInt)
    except OverflowError:
        maxInt = int(maxInt / 10)
        decrement = True


#####对于日期的问题，把问询函的格式搞成公司、收函日期.....

class CharSub(CharacterSubstitutionInterface):

    def cost(self, c0, c1):
        return 1.0


m = WeightedLevenshtein(character_substitution=CharSub())


class hudonge:
    def read_from(self, file_name):
        line = []
        with open(file_name, 'r',encoding="utf8") as f:
            line.append(f.readline())
        return line

    def read(self, file_name):
        csv = open(file_name, encoding='gb18030')
        data_cl = pd.read_csv(csv, low_memory=False)
        return data_cl

    def read_from_book(self, file_name):
        book1 = xlrd.open_workbook(file_name)
        self.sheet1 = book1.sheet_by_name('Sheet1')

    def FindToken(self, cutlist, char):
        if char in cutlist:
            return True
        else:
            return False

    ###分句
    def cut_sentences(self, line):
        l = []
        lines = []
        cutlist = u'。！？~'
        for i in line:
            if self.FindToken(cutlist, i):

                lines.append(i)
                l.append("".join(lines))
                lines = []
            else:
                lines.append(i)
        return l

    ###计算迷雾指数
    def fog_index(self, lines):  ##这种做法完全去掉了停用词，来判断，指数值会比不去停用词更小
        ###根据HSK词汇表1-3级词汇构建一个词典：【汉字：code】
        data_lines = pd.read_table(folder_path + 'HSKFINAL.txt')
        query_dict = {}  # 定义一个字典
        for line in data_lines.values:
            l = str(line)
            l = l.replace('．', ' ')
            l = l.strip(punctuation).split()  # 以上在调整格式
            word_list = l[1]  # 获取词语列
            word_list = word_list.strip(punctuation)  # 以上在调整格式
            code = l[0]  # 编号列
            query_dict[word_list] = code  # 词典格式：词语：编号
        ##计算复杂词比例
        stopword = self.read_from(folder_path + '上证专用停用词.txt')
        stopwords = []
        x = 0  # 复杂词
        y = 0  # 总次数
        for sw in stopword:
            sw = sw.strip('\n')
            sw = sw.strip(' ')
            stopwords.append(sw)
        words = jieba.cut(str(lines))
        for w in words:
            if (w not in stopwords):
                w = str(w).strip()
                if len(str(w).strip()) >= 1:
                    y = y + 1
                sw = query_dict.get(w, -1)
                if sw == -1:
                    x = x + 1
        # print(x)
        # print(y)
        ##计算平均每句词数   
        sentence = self.cut_sentences(str(lines))
        lenth = len(list(sentence))

        # print(lenth)
        # print(y/lenth+x/y)
        if y > 0 and lenth > 0:
            average = y / lenth
            fog_index = (average + x / y) * 0.4
        else:
            fog_index = u'none'
        return fog_index

    ##计算相似度
    def similarity(self, question, answer):

        stopword = self.read_from(folder_path + '上证专用停用词.txt')
        stopwords = []
        for sw in stopword:
            sw = sw.strip('\n')
            sw = sw.strip(' ')
            stopwords.append(sw)
        # print(stopwords)

        meaningful_words1 = []
        meaningful_words2 = []

        words2 = jieba.cut(str(question))
        words3 = jieba.cut(str(answer))
        for word in words2:
            if word not in stopwords:
                meaningful_words1.append(word)
        for word in words3:
            if word not in stopwords:
                meaningful_words2.append(word)
        s2 = ''.join(meaningful_words1)
        # print(s2)
        s3 = ''.join(meaningful_words2)
        a1 = Cosine(1)
        b1 = Damerau()
        c1 = Jaccard(1)
        d1 = JaroWinkler()
        e1 = Levenshtein()
        f1 = LongestCommonSubsequence()
        g1 = MetricLCS()
        h1 = NGram(2)
        i1 = NormalizedLevenshtein()
        j1 = OptimalStringAlignment()
        k1 = QGram(1)
        l1 = SorensenDice(2)
        m1 = WeightedLevenshtein(character_substitution=CharSub())

        line_sim = []

        cos_s = a1.similarity(s2, s3)
        line_sim.append(cos_s)
        cos_d = a1.distance(s2, s3)
        line_sim.append(cos_d)
        dam = b1.distance(s2, s3)
        line_sim.append(dam)
        jac_d = c1.distance(s2, s3)
        line_sim.append(jac_d)
        jac_s = c1.similarity(s2, s3)
        line_sim.append(jac_s)
        jar_d = d1.distance(s2, s3)
        line_sim.append(jar_d)
        jar_s = d1.similarity(s2, s3)
        line_sim.append(jar_s)
        lev = e1.distance(s2, s3)
        line_sim.append(lev)
        lon = f1.distance(s2, s3)
        line_sim.append(lon)
        met = g1.distance(s2, s3)
        line_sim.append(met)
        ngr = h1.distance(s2, s3)
        line_sim.append(ngr)
        nor_d = i1.distance(s2, s3)
        line_sim.append(nor_d)
        nor_s = i1.similarity(s2, s3)
        line_sim.append(nor_s)
        opt = j1.distance(s2, s3)
        line_sim.append(opt)
        qgr = k1.distance(s2, s3)
        line_sim.append(qgr)
        sor_d = l1.distance(s2, s3)
        line_sim.append(sor_d)
        sor_s = l1.similarity(s2, s3)
        line_sim.append(sor_s)
        wei = m1.distance(s2, s3)
        line_sim.append(wei)

        return line_sim

    ##打开csv表格
    def add_csv(self, file_name):
        path = file_name
        with open(path, 'wb') as f:
            csv_write = csv_writer(f)
            csv_head = ['code', 'cl_time', 'cl', 'cl_days', 'answ_rate', 'answer_rate_before', 'answer_rate_after',
                        'num_q_total', 'num_q_befor', 'num_q_after', 'senti_before', 'a_days_before', 'a_days_ater',
                        'a_days_total', 'word_dalta_before', 'word_delta_after', 'fog_index_before', 'fog_index_after',
                        'cos_s_before', 'cos_s_after']
            csv_write.writerow(csv_head)

    ###读取csv表格

    def read_csv(self, csv_name):  # 读取
        csv = open(csv_name, encoding='gb18030')
        data = pd.read_csv(csv, low_memory=False)
        self.data = data

    ###转换表格中的时间格式

    def cut_transfer_csv(self, index, symbol, i):  # 切割并转换

        data = self.data
        dd = data[index].map(lambda x: str(x).split(symbol)[i])

        dd = pd.to_datetime(dd, format='%Y年%m月%d日')
        # print(dd)
        return dd

    ###回复率描述性统计
    def describe_data(self):  # 回复率整体描述性统计
        # self.read_csv()
        data = self.data
        ##计算全体样本总回复率：
        ans_rate_total_total = data['ans_time'].count() / len(data)
        b = data['ans'].count() / len(data)
        ##计算每一年样本总回复率：
        data['ques_year'] = data['que_time'].str.split('年', expand=True)[0]

        ans_rate_total_year = []
        for i in range(2014, 2019):
            data1 = data[(data['ques_year'] == i)]
            if len(data1) > 0:
                ans_rate = data1['ans_time'].count() / len(data1)
            else:
                ans_rate = u'none'
            ans_rate_total_year.append(ans_rate)
        self.data2 = data

    ###提问回复率计算及调整数据格式
    def answer_rate(self, cl_name):  # 样本回复率

        self.describe_data()
        data = self.data2
        data['ques_time'] = self.cut_transfer_csv('que_time', ' ', 0)
        year_control = datetime.datetime.strptime('2012年12月31', "%Y年%m月%d")
        data = data[data['ques_time'] > year_control]

        ##计算每一家公司每一年、问询函前、后样本回复率
        data_cl = self.read(cl_name)
        ans_r = []
        ans_r_before = []
        ans_r_after = []
        cl_day = []
        for n in range(len(data_cl)):

            code = data_cl['code'][n]
            # print(int(code))
            # print(data['code'])
            compare_time = data_cl['cl_time'][n]

            ##年初至收到问询函的天数
            compare_time_first = compare_time.replace(str(compare_time[5:7]), '01')
            compare_time_first = compare_time_first.replace(compare_time_first[-2:], '01')
            compare_time_first = datetime.datetime.strptime(compare_time_first, "%Y年%m月%d")
            # print(compare_time_first)
            compare_year = str(compare_time)[0:4]
            # print(compare_year)
            compare_time = datetime.datetime.strptime(str(compare_time), "%Y年%m月%d")
            cl_days = (compare_time - compare_time_first).days
            cl_day.append(cl_days)

            # data6 = data[data['code']==int(code)]
            # print(data6)
            # print(data['ques_year'])
            data2 = data[(data['code'] == int(code)) & (data['ques_year'] == compare_year)]
            # print(data[data['code']==int(code)])
            data3 = data[
                (data['code'] == int(code)) & (data['ques_year'] == compare_year) & (data['ques_time'] < compare_time)]
            data4 = data[
                (data['code'] == int(code)) & (data['ques_year'] == compare_year) & (data['ques_time'] > compare_time)]

            if len(data2) > 0:
                ans_rate = data2['ans_time'].count() / len(data2)
                # print(ans_rate)
            else:
                ans_rate = u'none'
            ans_r.append(ans_rate)
            if len(data3) > 0:
                ans_rate_before = data3['ans_time'].count() / len(data3)
            else:
                ans_rate_before = u'none'
            # print(ans_rate_before)
            ans_r_before.append(ans_rate_before)
            if len(data4) > 0:
                ans_rate_after = data4['ans_time'].count() / len(data4)
            else:
                ans_rate_after = u'none'
            # print(ans_rate_after)
            ans_r_after.append(ans_rate_after)
        # print(ans_r)
        # print(cl_day)
        self.data1 = data
        self.ans_r_b = ans_r_before
        self.ans_r_a = ans_r_after
        self.ans_r = ans_r
        self.cl_day = cl_day
        self.data_cl = data_cl

    def run(self, cl_name, file_name):  # 计数并计算回复时间、回复天数、提问的情感倾向、回复的迷雾指数
        path = file_name

        # self.answer_rate(cl_name)
        data_cl = self.read(cl_name)
        data = self.data

        data['code'] = pd.to_numeric(data['code'], errors='coerce', downcast='float')

        data['ques_year'] = data['que_time'].str.split('年', expand=True)[0]

        data['ques_time'] = self.cut_transfer_csv('que_time', ' ', 0)

        data['answ_year'] = data['ans_time'].str.split('年', expand=True)[0]
        data['answ_time'] = self.cut_transfer_csv('ans_time', ' ', 0)

        # print(u'数据处理Ok')

        # data_cl = self.data_cl
        # print(data['code'])

        with open(path, 'w', newline='', encoding='gb18030') as f:
            csv_write = csv.writer(f)
            csv_head = ['code', '时间窗口', 'cl_time', 'CL', 'QUE_NUM', 'SENTI', 'DAYS', 'FOG', 'COS']
            csv_write.writerow(csv_head)

            for n in range(len(data_cl)):
                for ff in [60]:
                    compare_time = data_cl['cl_time'][n]
                    code = data_cl['code'][n]
                    compare_time1 = datetime.datetime.strptime(str(compare_time), "%Y/%m/%d")
                    t_1 = compare_time1 + datetime.timedelta(days=-ff)

                    cl = data_cl['cl'][n]
                    days_before = 0

                    senti = 0

                    b = data[(data['code'] == code) & (t_1 <= data['ques_time']) & (data['ques_time'] <= compare_time)]

                    num_q_before = len(b)
                    # print('收函前提问数量'+str(len(b)))
                    b_a_t = list(b['answ_time'])
                    b_q_t = list(b['ques_time'])
                    b_q = list(b['que'])
                    # print(len(b))
                    for i2 in range(len(b)):
                        days_b = (b_a_t[i2] - b_q_t[i2]).days
                        days_before = days_before + days_b
                        # print(b_q[i1])
                        score = SnowNLP((b_q[i2])).sentiments
                        # print(score)
                        senti = senti + score
                        # print(score)
                        # print((b_q[i2]))
                    if len(b) > 0:
                        a_days_before = days_before / len(b)
                        senti_before = senti / len(b)
                    else:
                        a_days_before = u'none'
                        senti_before = u'none'

                    # print('情感得分计算完毕')

                    ##收到问询函之前，回复的迷雾指数，字数统计、相似度
                    s = data[(data['code'] == code) & (t_1 <= data['answ_time']) & (data['answ_time'] <= compare_time)]
                    # mm = s['ans']
                    # mm = s['ans'][0]
                    # print(mm)

                    fog_index = 0.00
                    words = 0
                    cos_s = 0.00
                    s_a = list(s['ans'])
                    s_q = list(s['que'])
                    for i4 in range(len(s)):

                        # print(s['ans'][0])
                        # print(s_a[i4])
                        # print(self.fog_index(s_a[i4]))

                        f_i = self.fog_index(s_a[i4])
                        # print(f_i)

                        # print(f_i)
                        if f_i != 'none':
                            fog_index = fog_index + f_i
                        word_a = len(str(s_a[i4]).replace(' ', '').strip(punctuation))
                        words = words + word_a
                        simi = self.similarity(str(s_q[i4]), str(s_a[i4]))[0]
                        # print(simi)
                        # print(s_a[i4])
                        cos_s = cos_s + simi
                    if len(s) > 0:
                        fog_index_before = fog_index / len(s)

                        cos_s_before = cos_s / len(s)
                    else:
                        fog_index_before = u'none'

                        cos_s_before = u'none'

                    # print('回复质量计算完毕'+str(fog_index_before))

                    # print(fog_index_before)

                    # self.add_csv('第一次尝试.csv')

                    row = [code, ff, compare_time, cl, num_q_before, senti_before, a_days_before, fog_index_before,
                           cos_s_before]
                    csv_write.writerow(row)
                # print('第'+str(n)+'行也是肖毅斌的小宝贝呢！！！！！！！')


try1 = hudonge()
cl_name = (folder_path + '上海.csv')
try1.read_csv(folder_path + '上证互动——已加日期.csv')
try1.run(cl_name, folder_path + '上证第五次匹配后收函公司数据-副本.csv')
# cl_name = (r'飞哥哥.csv')
# try1.read_csv(r'肖毅斌.csv')
# try1.run(cl_name,'深证互动数据提取.csv')
