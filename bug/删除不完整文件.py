import os
import re


# 所有文件所在的文件夹
# folder_path = "/Users/cht/Documents/files/剩余回复函/"
# folder_path = "/Users/cht/Documents/files/txt/"
folder_path = "/Users/cht/Documents/files/files/"
pattern = re.compile(r"评估|会计师|证券股份|律师|评估师|控股股东|实际控制人|无法回复")

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

files = get_all_files(folder_path)

count = 0
for file in files:
    size = os.path.getsize(file) / 1024
    type = file.split('.')[-1]
    # 根据文件大小来删
    if size < 30 and type == "pdf" or size == 0 and type == "txt":
        os.remove(file)
        print("成功移出{}".format(file))
        count += 1
    # 如果文件名中含有关键字删掉
    elif pattern.search(file):
        os.remove(file)
        print("成功移出{}".format(file))
        count += 1

print("总共移出:{}个文件".format(count))



