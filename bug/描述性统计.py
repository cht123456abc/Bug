import os
from snownlp import SnowNLP
import pandas as pd
import jieba
from string import punctuation
import re
import time

"""
    解析每个公司的回复函，将回复内容提取出来进行分析，计算该公司回复的迷雾指数等指标
"""

# 全局变量
# 原pdf文件所在文件夹
original_folder_path = "/Users/cht/Documents/files/剩余回复函/"
# 现txt文件所在的文件夹
folder_path = "/Users/cht/Documents/files/txt/"
# 要存放的excel文件路径
dest_excel_path = "/Users/cht/Documents/files/公司描述性统计.xlsx"
# HSKFINAL
HSKFINAL = '/Users/cht/Documents/files/HSKFINAL.txt'
query_dict = {}
# stopword
STOPWORD = '/Users/cht/Documents/files/上证专用停用词.txt'
stopwords = []

# 二维表格
table = []

# pattern
pattern_answer = re.compile(r"((?:[回复]+|[如下]+)[:：】])|([(（][1-9一二三四五六七八九十][)）])|([一二三四五六七八九十][、.。：:])")
pattern_start = re.compile(r"(([回复]+|[如下]+)[:：】])")
pattern_end = re.compile(r"([一二三四五六七八九十1-9][、.。：:])|(问题[:：])|(([回复]+|[如下]+)[:：】])")
pattern_chinese = re.compile(r"[\u4e00-\u9fa5]{1}")
pattern_date = re.compile(
    r"(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日]?)|([一二三四五六七八九零十〇○]{4}年[一二三四五六七八九零十]{1,2}月[一二三四五六七八九零十]{1,3}日)")

map_year = {
    "零": "0",
    "〇": "0",
    "○": "0",
    "o": "0",
    "Ｏ": "0",
    "一": "1",
    "二": "2",
    "三": "3",
    "四": "4",
    "五": "5",
    "六": "6",
    "七": "7",
    "八": "8",
    "九": "9",
}

map_month = {
    "一": "1",
    "二": "2",
    "三": "3",
    "四": "4",
    "五": "5",
    "六": "6",
    "七": "7",
    "八": "8",
    "九": "9",
    "十": "10",
    "十一": "11",
    "十二": "12"
}

map_day = {
    "一": "1",
    "二": "2",
    "三": "3",
    "四": "4",
    "五": "5",
    "六": "6",
    "七": "7",
    "八": "8",
    "九": "9",
    "十": "10",
    "十一": "11",
    "十二": "12",
    "十三": "13",
    "十四": "14",
    "十五": "15",
    "十六": "16",
    "十七": "17",
    "十八": "18",
    "十九": "19",
    "二十": "20",
    "二十一": "21",
    "二十二": "22",
    "二十三": "23",
    "二十四": "24",
    "二十五": "25",
    "二十六": "26",
    "二十七": "27",
    "二十八": "28",
    "二十九": "29",
    "三十": "30",
    "三十一": "31",

}


# 从文件里面读取文本
def read_from(file_name):
    line = []
    with open(file_name, 'r', encoding="utf8") as f:
        for l in f.readlines():
            line.append(l)
    return line


# 格式化日期
def format_date(date):
    date = date.replace("年", '-')
    date = date.replace("月", '-')
    date = date.replace("日", '')

    # 分割
    group = date.split("-")
    year_str = group[0]
    month_str = group[1]
    day_str = group[2]
    # 如果不是中文,直接返回
    if year_str[0] not in map_year:
        return date
    else:
        year, month, day = "", "", ""
        # 格式化中文年数
        for c in year_str:
            if c in map_year:
                year += map_year[c]
        # 格式化中文月数:
        month = map_month[month_str]
        # 格式化中文日数:
        day = map_day[day_str]
        return "{}-{}-{}".format(year, month, day)


# 解析txt文件
def parse(file_path):
    # 存储解析出来的文本信息
    if os.path.getsize(file_path) > 0:
        text_array = []
        with open(file_path, 'r', encoding="utf8") as f:
            for line in f.readlines():
                text_array.append(line)

        # print("{},{}".format(file_path, text_array))
        # 对解析出来的文本进行处理
        deal_text(text_array, file_path)
    else:
        print("文件{}大小为0\n".format(file_path))


# 对文本进行处理:
def deal_text(text_array, file_path):
    if len(text_array) < 4:
        print("文件{}解析错误\n".format(file_path))
        return
    path = file_path.replace(folder_path, "")
    group = path.split("_")

    # 1.提取回复日期
    replydate = reply_date(text_array, file_path)
    # print("{}回复时间为:{}\n".format(file_path, replydate))

    # 过滤文本
    new_lines = []
    for line in text_array:
        line = line.replace(" ", '')
        # 这里用中文分词来过滤
        # 存在关键词的保留
        if pattern_answer.search(line):
            new_lines.append(line)
        elif len(line) < 15:  # 去掉短行
            continue
        elif pattern_chinese.search(line):  # 去掉不存在中文的行
            new_lines.append(line)
        else:
            continue
    # 连接文本
    text = "".join(new_lines)

    # 对文本进行处理。提取回复。
    original_pdf_path = file_path.replace(folder_path, original_folder_path).replace("txt", "pdf")
    answer = get_answer(text, pattern_answer)
    if len(answer) == 0:
        print("文件{}:".format(file_path))
        print("文件{}没提取回复的原文为:\n".format(original_pdf_path))
        print(text)

    # 2.计算迷雾指数,总词数,总句数, 平均句长
    fog_index, sum_words, sum_sentences, letters_per_sentences = fog(answer)
    # print("{}的迷雾指数为:{},总词数为:{},总句数为:{}，平均句长为:{}\n".format(path, fog_index, sum_words, sum_sentences,
    #                                                       letters_per_sentences))

    # 3.计算情感得分
    sentiments = sentiment(answer)
    # print("{}的情感得分为:{}\n".format(path, sentiments))

    # 4.计算文件大小
    file_size = os.path.getsize(file_path) / 1024
    # print("{}的文件大小为:{}KB\n".format(path, file_size))
    # 创建一个新的行将数据加入到table中
    table.append(
        [group[2], group[3], group[1], group[0], original_pdf_path, replydate, fog_index, sentiments, sum_words,
         sum_sentences,
         letters_per_sentences, file_size])


# 获取目录下所有文件名称
def get_all_files(dir):
    files_ = []
    list = os.listdir(dir)
    for i in range(0, len(list)):
        path = os.path.join(dir, list[i])
        if os.path.isdir(path):
            files_.extend(get_all_files(path))
        if os.path.isfile(path):
            files_.append(path)
    return files_


# 从文本中提取回复：
def get_answer(text, pattern_answer):
    # 用关键字来分段
    # 这里还有点问题：split()函数会含有所有分组的分割，但只需要第一个分组，即完整的分组来分割
    result = pattern_answer.split(text)
    L = []
    # 过滤
    for x in result:
        # 清理为None
        if x is None:
            continue
        if x.strip() == "":
            continue
        # 清理单行字符数小于10的或者单行含有数字且字符数小于15的
        # xx = x.split('\n')
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # print(x)
        L.append(x)

    # 将”回复如下：“或者”回复：“ 与 ”序号“ 之间部分提取
    answer = []
    left, right = 0, 0
    while right < len(L):
        while pattern_end.search(L[right]) and left < right - 1:
            if pattern_start.search(L[left]):
                answer.append(L[right - 1])
                # print("##############################")
                # print(L[right - 1])
            left += 1
        right += 1

    return answer


# 提取落款时间
def reply_date(text, file_path):
    # 将时间匹配出来
    date = text[-4] + text[-3] + text[-2] + text[-1]
    # x = "二零一八年六月十一日"
    # x = "2018-6-11"
    # x = "2018年6月11日"
    date = date.replace(" ", '')
    result = pattern_date.search(date)
    if result is None:
        print("文件{}没找到时间的原文为:\n".format(file_path))
        print(date)
        return -1
    else:
        return format_date(result.group())


# 计算情感得分
def sentiment(lines):
    if len(lines) == 0:
        return -1
    score = 0.0
    for line in lines:
        score += SnowNLP(line).sentiments
    score = score / len(lines)
    return score


# 计算迷雾指数,总词数，总句数
def fog(lines):
    if len(lines) == 0:
        return -1, -1, -1, -1
    sentences = []  # 总句子数
    tough_words = 0  # 复杂词
    sum_words = 0  # 总词数
    sum_letters = 0  # 总字数
    for line in lines:
        # 调整line
        line = line.replace("\n", '，')
        # 这种做法完全去掉了停用词，来判断，指数值会比不去停用词更小
        # 计算复杂词比例
        words = jieba.cut(line)
        for w in words:
            if w not in stopwords:
                w = str(w).strip()
                if len(w) >= 1:
                    sum_words += 1
                sw = query_dict.get(w, -1)
                if sw == -1:
                    tough_words += 1
        # 计算平均每句词数和平均句长
        sum_letters += len(line)
        sentences.extend(cut_sentences(line))
    length = len(sentences)
    letters_per_sentence = sum_letters / length
    if sum_words > 0 and length > 0:
        words_per_sentence = sum_words / length
        fog_index = (words_per_sentence + tough_words / sum_words) * 0.4
    else:
        fog_index = 0
    return fog_index, sum_words, length, letters_per_sentence


# 计算句子数量
def cut_sentences(line):
    # 这里应该用nlp的分割句子实现
    list = re.split(r"[。.！!?？~]", line)
    if list:
        return list
    return []


# 初始化
def init():
    dict_lines = pd.read_csv(HSKFINAL, sep='\t')

    # 根据HSK词汇表1-3级词汇构建一个词典：【汉字：code】

    for row in dict_lines.values:
        l = str(row)
        l = l.replace('．', ' ')
        l = l.strip(punctuation).split()  # 以上在调整格式
        word_list = l[1]  # 获取词语列
        word_list = word_list.strip(punctuation)  # 以上在调整格式
        code = l[0]  # 编号列
        query_dict[word_list] = code  # 词典格式：词语：编号

    # 停用词
    stopword = read_from(STOPWORD)
    for sw in stopword:
        sw = sw.strip('\n')
        sw = sw.strip(' ')
        stopwords.append(sw)


if __name__ == '__main__':

    # 初始化
    init()

    # 查找文件夹所有文件路径
    files = get_all_files(folder_path)

    # 解析所有txt
    start = time.time()
    for x in files:
        parse(x)
        # break
    end = time.time()
    print("解析所有文件用时:[{}]秒".format(end - start))

    # 写入新的excel
    excel = pd.DataFrame(table, columns=["公司代码", "公司简称", "发函日期", "函件类别", "公司回复", "回复时间", "迷雾指数", "情感得分", "单词数量", "句子数量",
                                         "平均句长", "文件大小"])
    excel.to_excel(dest_excel_path, index=False)
    print("已导入到{}中".format(dest_excel_path))
