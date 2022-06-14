# import re
# def repeat_state(s):
#     w = 78
#     end_num = 0
#     num_list = re.findall(r'\d+', s)
#     if s[-1].isdigit():
#         end_num = int(num_list[-1],10)-1
#         s = s[:-(len(num_list[-1]))]
#         num_list.pop()
#     for n in num_list:
#         s = s[:s.find(n)] +  s[s.find(n)+len(n)]*int(n, 10) + s[s.find(n)+len(n)+1:]
#     print(s)
#     if len(s) < w:
#         s = s + 'b' * (w-len(s))
#     new_line = []
#     new_line.append(s)
#     for l in range(end_num):
#         new_line.append('b'*w)
#     return new_line
#
#
# a = '77bo21'
# s = repeat_state(a)
# print(len(s[0]))
# # print(re.findall(r'\d+', '2t56565b2o'))

# class A:
#     def __init__(self):
#         pass
#
#     @staticmethod
#     def prints():
#         print('static method')
#
#     def f(self):
#         self.prints()
#
# a = A()
# a.f()

import os
print(__file__)
print(os.path.abspath(__file__))
