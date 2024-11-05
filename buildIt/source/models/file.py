from os import path, mkdir
from config import storage_path
import re, os
import Encryption_and_decryption as ed
from urllib.parse import quote
import sqlite3
from db import add_file

filename_pattern = re.compile(r"[^\u4e00-\u9fa5]+")

# 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(current_dir, "..", "instance")
db_path = os.path.join(db_dir, "6dac.db")


# 定义基本和VIP用户的允许的文件后缀列表
basic_allowed_file_suffix_list = {
    "doc", "docx", "ppt", "pptx", "xls", "xlsx", 
    "pdf", "png", "jpg", "jpeg", "gif", "txt",
}

vip_allowed_file_suffix_list = {
    "doc", "docx", "ppt", "pptx", "xls", "xlsx", 
    "pdf", "png", "jpg", "jpeg", "gif", "txt", 
    "mp4", "mp3", "avi", "mkv", "mov"
}

# 文件资源表
class File:
    def __init__(
        self,
        file_id,
        user_id,
        file_name_,
        description_,
        file_signature_,
        static_hash,
        public_key_,
    ):
        self.file_id = file_id
        self.user_id = user_id
        self.file_name = file_name_
        self.file_signature = file_signature_
        self.static_hash = static_hash
        self.public_key = public_key_
        self.description = description_

    # 用于在数据库中查询文件
    @classmethod
    def get_by(cls, **kwargs):
        conditions = " AND ".join(f"{key} = ?" for key in kwargs.keys())
        query = f"SELECT * FROM file WHERE {conditions}"
        values = tuple(kwargs.values())

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query, values)
        result = cursor.fetchall()  # 使用 fetchall 获取所有匹配记录
        conn.close()

        if result:
            return [cls(*row) for row in result]  # 返回类实例的列表
        return []

    # 类的内置函数
    @classmethod
    def upload_file(cls, user, data, description):
        # 文件名验证操作：
        filename = data.filename

        # 检查文件的后缀是否在允许的文件后缀列表中
        filename_suffix = filename.rsplit(".", maxsplit=1)[-1]

        # 检查用户是否是VIP，并设置相应的文件后缀列表和大小限制
        if user.is_vip:
            allowed_file_suffix_list = vip_allowed_file_suffix_list
            max_file_size = 50 * 1024 * 1024  # 50MB
        else:
            allowed_file_suffix_list = basic_allowed_file_suffix_list
            max_file_size = 10 * 1024 * 1024  # 10MB

        assert filename_suffix in allowed_file_suffix_list, "banned file type"
        content = data.read()
        assert len(content) < max_file_size, "file too large"

        # 创建单个用户的文件夹路径
        user_id = str(user.user_id) + "/"
        if not path.exists(storage_path + user_id):
            if not path.exists(storage_path):
                mkdir(storage_path)
            mkdir(storage_path + user_id)

        # 用户id
        user_id_ = user.user_id
        # 生成盐值
        user_salt = user.user_salt
        # 密钥哈希值
        hash_password_ = user.hash_password
        # 利用对称加密生成密文
        file_info_ = ed.file_upload_encryption(hash_password_, content)
        # 静态散列值
        static_hash = ed.get_hash_from_bytes(content)
        # 对密文的签名
        file_signature_ = ed.Hash_get(hash_password_, user_salt, file_info_)[1]

        # 验证文件完整性公钥
        public_key_ = ed.Hash_get(hash_password_, user_salt, file_info_)[0]

        # 文件上传：
        # 将加密后的文件保存到用户文件夹中
        file_path = os.path.join(storage_path + str(user_id_), filename)
        with open(file_path, "wb") as f:
            f.write(file_info_)

        add_file(
            user_id_, filename, file_signature_, static_hash, public_key_, description
        )

    @classmethod
    def download_file(cls, user, filename, type):
        from flask import make_response

        find_file = None
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM file WHERE user_id = ? AND file_name = ?",
                (user.user_id, filename),
            )
            find_file = cursor.fetchone()

        if not find_file:
            return "File not found."

        # 读取加密后的文件内容
        file_path = os.path.join(storage_path + str(user.user_id), filename)
        with open(file_path, "rb") as f:
            file_content = f.read()

        # 加密文件：
        encrypted_file = file_content

        # 密钥哈希值
        hash_password_ = user.hash_password

        print(find_file)
        # 完整性验证部分
        # if ed.Hash_verify(find_file.public_key,find_file.file_signature,encrypted_file):
        if ed.Hash_verify(find_file[6], find_file[4], encrypted_file):
            # 利用对称密钥对密文解密,获取明文
            decrypted_file = ed.file_download_decryption(hash_password_, file_content)
        else:
            return "完整性验证失败！"

        # 判断要下载的类型
        if type == "hashvalue":
            # content = find_file.static_hash
            content = find_file[5]
            filename = "hash_" + filename

            # 创建content 响应对象
            response = make_response(content)
            # 去掉文件名本身的后缀
            file_basename = os.path.splitext(filename)[0]
            # 对文件名进行URL编码，并设置为附件的下载文件名
            url_filename = quote(file_basename) + ".txt"
            response.headers["Content-Disposition"] = (
                f'attachment; filename="{url_filename}"'
            )
            # 返回响应对象，完成下载功能
            return response

        elif type == "signature":
            # 读取签名
            # content = find_file.file_signature
            content = find_file[4]
            filename = "sig_" + filename

            # 创建content 响应对象
            response = make_response(content)
            # 去掉文件名本身的后缀
            file_basename = os.path.splitext(filename)[0]
            # 对文件名进行URL编码，并设置为附件的下载文件名
            url_filename = quote(file_basename) + ".txt"
            response.headers["Content-Disposition"] = (
                f'attachment; filename="{url_filename}"'
            )
            # 返回响应对象，完成下载功能
            return response

        else:
            if type == "plaintext":
                # 解密并下载
                content = decrypted_file
                filename = "decrypted_" + filename

                # 创建content 响应对象
                response = make_response(content)
                # 对文件名进行URL编码，并设置为附件的下载文件名
                url_filename = quote(filename)
                response.headers["Content-Disposition"] = (
                    f'attachment; filename="{url_filename}"'
                )
                # 返回响应对象，完成下载功能
                return response

            elif type == "encrypted":
                content = encrypted_file
                filename = "encrypted_" + filename

                # 创建content 响应对象
                response = make_response(content)
                # 对文件名进行URL编码，并设置为附件的下载文件名
                url_filename = quote(filename)
                response.headers["Content-Disposition"] = (
                    f'attachment; filename="{url_filename}"'
                )
                # 返回响应对象，完成下载功能
                return response
