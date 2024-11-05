from nacl.public import PrivateKey
from nacl.secret import SecretBox
from nacl.signing import SigningKey, VerifyKey
import nacl.hash
import secrets
import bcrypt


# 根据输入字节串生成HASH值
# 输入明文字节串，生成HASH值返回
# 返回哈希值（字节表示）
def get_hash_from_bytes(file: bytes):
    return nacl.hash.sha256(file)


# 根据输入字符串生成HASH值
# 输入用户密码字符串，使用bcrypt生成安全的HASH值返回
# 返回哈希值（字节表示）
def get_hash_from_str(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


# 根据输入密码，和储存的密码哈希值判断密码是否正确
# 输入得到的密码，储存的密码哈希，判断密码是否正确
# 正确输出True，错误输出False
def check_password_get(password_get: str, password_hash: bytes):
    return bcrypt.checkpw(password_get.encode(), password_hash)


# 生成盐值，派生公私钥对
# 输入用户密码，生成盐值，并用密码和盐值派生用户与服务器传输文件的公私钥对
# 返回一个元组，依次为私钥，公钥，盐值（均为字节表示）
def user_key_generate(password: bytes):
    # 随机生成长度为100的字符串作为盐值
    user_salt = secrets.token_bytes(100)
    # 将密码和盐值进行哈希，将哈希值前32字节作为私钥，构建公私钥对
    user_hash = nacl.hash.sha256(password + user_salt)
    private_key = user_hash[:32]
    # 读取公钥的字节表示
    public_key = PrivateKey(private_key).public_key.encode()
    # 返回用户的公私钥对，以及生成的盐值，并将盐值保存于服务端数据库中
    return private_key, public_key, user_salt


# 用户上传加密
# 输入passphrase（字符串表示），上传的明文，生成盐值，并用密码和盐值派生用户上传文件的对称密钥
# 返回一个字节串，前一百位为盐值，一百零一位开始为密文
def file_upload_encryption(passphrase: bytes, file: bytes):
    salt = secrets.token_bytes(100)

    file_upload_hash = nacl.hash.sha256(passphrase + salt)

    return salt + SecretBox(file_upload_hash[:32]).encrypt(file)


# 用户解密下载
# 输入passphrase，盐值和密文连接的字节串，用密码和盐值派生用户上传文件的对称密钥，解密密文
# 返回明文（字节表示）
def file_download_decryption(passphrase: bytes, salt_file_encrypted: bytes):
    file_download_hash = nacl.hash.sha256(passphrase + salt_file_encrypted[:100])

    return SecretBox(file_download_hash[:32]).decrypt(salt_file_encrypted[100:])


# 用户分享加密
# 输入待分享的明文，生成随机数，并根据随机数派生出对称密钥
# 返回元组，依次为随机数，密文
def file_share_encryption(file: bytes):
    random = secrets.token_bytes(100)

    share_hash = nacl.hash.sha256(random)

    return random, SecretBox(share_hash[:32]).encrypt(file)


# 被分享者解密分享文件
# 输入随机数，待解密的文件，并根据随机数派生出对称密钥，解密
# 返回明文
def file_share_decryption(random: bytes, file_encrypted: bytes):
    share_hash = nacl.hash.sha256(random)

    return SecretBox(share_hash[:32]).decrypt(file_encrypted)


# 用户分享签名
# 输入分享文件ID，过期时间Time,分享序列号Share_id（均为字符串），用户密码，保存的用户盐值，根据密码和盐值派生出用户签名的公私钥对，对前三个信息进行HMAC生成token
# 返回元组，依次为用户签名的公钥，token
def token_generate(
    ID: str, Time: str, Share_id: str, password: bytes, user_salt: bytes
):
    # 还原用户私钥进行签名
    user_hash = nacl.hash.sha256(password + user_salt)
    Sign_box = SigningKey(user_hash[:32])

    return Sign_box.verify_key.encode(), Sign_box.sign((ID + Time + Share_id).encode())


# 签名验证
# 输入分享文件ID，过期时间Time,分享序列号Share_id（均为字符串），token，用户签名的公钥
# 返回真假，如果验证签名成功返回True，否则返回False
def token_verify(ID: str, Time: str, Share_id: str, token: bytes, verify_key: bytes):
    if VerifyKey(verify_key).verify(token).decode() == ID + Time + Share_id:
        return True
    else:
        return False


# 生成不可伪造的散列值
# 输入用户密码，储存的用户盐值，文件，对文件生成HASH值，并使用私钥加密进行签名，生成不可伪造的散列值
# 返回一个元组，依次为验证签名的公钥，不可伪造的散列值
def Hash_get(password: bytes, user_salt: bytes, file: bytes):
    # 对文件生成HASH值
    file_hash = nacl.hash.sha256(file)
    # 根据用户密码，储存的用户盐值，生成用于签名的公私钥对
    user_hash = nacl.hash.sha256(password + user_salt)
    private_key = user_hash[:32]
    Sign_box = SigningKey(private_key)
    # 读取签名验证公钥的字节表示
    verify_public_key = Sign_box.verify_key._key
    Unforgeable_file_hash = Sign_box.sign(file_hash)
    return verify_public_key, Unforgeable_file_hash


# 根据不可伪造的散列值，验证文件完整性
# 输入验证签名的公钥，签名后的散列值，实际收到的文件，使用公钥解密出HASH值，对文件生成HASH值与解密出的HASH值比较，验证完整性
# 返回真假，如果完整性验证成功返回True，否则返回False
def Hash_verify(
    verify_public_key: bytes, Unforgeable_file_hash: bytes, file_get: bytes
):
    # 解签还原应该收到的文件HASH值
    file_hash = VerifyKey(verify_public_key).verify(Unforgeable_file_hash)

    # 对实际收到的文件生成HASH值
    file_get_hash = nacl.hash.sha256(file_get)

    if file_hash == file_get_hash:
        return True
    else:
        return False
