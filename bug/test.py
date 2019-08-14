import re

pattern_start = re.compile(r"((?:[回复]+|[如下]+)[:：])")


str = "adasd我是!对adasd1!23123回复:外界大王i.dada!wdaw"
group = pattern_start.search(str)
s = pattern_start.split(str)

print(s)
print(group.group())
print(group.groups())

