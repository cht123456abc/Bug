import re

pattern_start = re.compile(r"(([回复]+|[如下]+)[:：])")


str = "adasd我是!对adasd1!23123回复:外界大王i.dada!wdaw"
# list = re.split(r"[。.！!?？~]", str)
# if list:
#     print(list)
print(pattern_start.search(str))

