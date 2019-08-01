# encoding: utf-8
import os
import time
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal, LAParams
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed

'''
 解析pdf 文本，转存到txt中
'''

# 全局变量
# 所有pdf文件所在的文件夹
folder_path = "E:/files/剩余回复函/"
# pdf文件转txt文件的目标文件夹
txt_folder_path = "E:/files/txt/"


# 解析pdf文件
def parse(file_path):
    # file_path = folder_path + "半年报问询函_2018-09-10_300275_梅安森_NMK30027523331945HF.pdf"
    dest_path = file_path.replace(folder_path, txt_folder_path).replace("pdf", "txt")
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1024:
        print("文件[{}]已存在\n".format(dest_path))
        return
    L = []
    type = file_path.split(".")[-1]
    if type == 'pdf':
        with open(file_path, 'rb') as fp:  # 以二进制读模式打开
            # 用文件对象来创建一个pdf文档分析器
            parser = PDFParser(fp)
            # 连接分析器 与文档对象
            doc = PDFDocument()
            parser.set_document(doc)  # 创建一个PDF文档
            # 创建PDf 资源管理器 来管理共享资源
            rsrcmgr = PDFResourceManager()
            # 创建一个PDF设备对象
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            try:
                doc.set_parser(parser)
                # 提供初始化密码
                # 如果没有密码 就创建一个空的字符串
                doc.initialize()

                # 创建一个PDF解释器对象
                interpreter = PDFPageInterpreter(rsrcmgr, device)

                # 检测文档是否提供txt转换，不提供就忽略
                if not doc.is_extractable:
                    raise PDFTextExtractionNotAllowed
                else:
                    # 循环遍历列表，每次处理一个page的内容
                    for page in doc.get_pages():  # doc.get_pages() 获取page列表
                        interpreter.process_page(page)
                        # 接受该页面的LTPage对象
                        layout = device.get_result()
                        # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等 想要获取文本就获得对象的text属性，
                        for x in layout:
                            if isinstance(x, LTTextBoxHorizontal):
                                L.append(x.get_text())
                                print(x.get_text())
            except Exception as exc:
                print("文件{},{}\n".format(file_path, exc))
            finally:
                device.close()
    # else:  # 为doc文件
    #     with open(file_path, 'r', encoding='utf8') as fp:
    #         for line in fp.readlines():
    #             L.append(line)

    file2txt(dest_path, L)


# 转pdf为txt
def file2txt(dest_path, L):
    # 将每个文件文本转存到txt文件中
    with open(dest_path, 'w', encoding="utf8") as f:
        for line in L:
            f.write(line)
    print("文件{}已转为txt\n".format(dest_path))


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


if __name__ == '__main__':

    files = get_all_files(folder_path)
    start = time.time()
    # 转所有pdf
    for x in files:
        parse(x)
    end = time.time()
    print("转所有pdf为txt用时:[{}]秒".format(end - start))
