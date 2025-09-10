#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
二进制文件签名验证脚本
用于检查编译后的二进制文件是否被篡改
"""

import os
import sys
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def verify_binary(bin_path, sig_path, pub_key_path):
    """
    验证二进制文件签名
    :param bin_path: 二进制文件路径
    :param sig_path: 签名文件路径
    :param pub_key_path: 公钥文件路径
    :return: bool 验证结果
    """
    try:
        # 读取二进制文件内容
        with open(bin_path, 'rb') as f:
            bin_data = f.read()
        
        # 读取签名
        with open(sig_path, 'rb') as f:
            signature = f.read()
            
        # 读取公钥
        with open(pub_key_path, 'rb') as f:
            pub_key = RSA.import_key(f.read())
            
        # 计算哈希
        h = SHA256.new(bin_data)
        
        # 验证签名
        pkcs1_15.new(pub_key).verify(h, signature)
        return True
        
    except Exception as e:
        print(f"验证失败: {str(e)}")
        return False

def main():
    if len(sys.argv) != 4:
        print("用法: check_binaries.py <binary_file> <signature_file> <public_key>")
        sys.exit(1)
        
    bin_file = sys.argv[1]
    sig_file = sys.argv[2]
    pub_key = sys.argv[3]
    
    if not os.path.exists(bin_file):
        print(f"错误: 二进制文件 {bin_file} 不存在")
        sys.exit(1)
        
    if not os.path.exists(sig_file):
        print(f"错误: 签名文件 {sig_file} 不存在")
        sys.exit(1)
        
    if not os.path.exists(pub_key):
        print(f"错误: 公钥文件 {pub_key} 不存在")
        sys.exit(1)
    
    if verify_binary(bin_file, sig_file, pub_key):
        print("验证成功: 二进制文件签名有效")
        sys.exit(0)
    else:
        print("验证失败: 二进制文件签名无效或已被篡改")
        sys.exit(1)

if __name__ == '__main__':
    main()