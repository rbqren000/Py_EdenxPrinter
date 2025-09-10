#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字符串处理工具类

提供字符串验证、格式化、十六进制转换等功能的工具类，专为PC端Python环境设计。
"""

import re
import random
import string
from typing import Optional, List
from urllib.parse import quote


class StringUtils:
    """字符串处理工具类
    
    提供字符串验证、格式化、十六进制转换、正则表达式匹配等功能。
    """
    
    @staticmethod
    def is_blank_string(input_string: Optional[str]) -> bool:
        """检查字符串是否为空或只包含空白字符
        
        Args:
            input_string (Optional[str]): 要检查的字符串
            
        Returns:
            bool: 如果字符串为空或只包含空白字符返回True，否则返回False
        """
        if input_string is None:
            return True
        return len(input_string.strip()) == 0
    
    @staticmethod
    def is_validate_by_regex(input_string: str, regex: str) -> bool:
        """使用正则表达式验证字符串
        
        Args:
            input_string (str): 要验证的字符串
            regex (str): 正则表达式模式
            
        Returns:
            bool: 如果字符串匹配正则表达式返回True，否则返回False
        """
        try:
            pattern = re.compile(regex)
            return bool(pattern.fullmatch(input_string))
        except re.error:
            return False
    
    @staticmethod
    def simplify(input_string: str) -> str:
        """简化字符串，去掉字符串中的空格、tab、换行等字符
        
        Args:
            input_string (str): 要简化的字符串
            
        Returns:
            str: 简化后的字符串
        """
        if input_string is None:
            return ""
        
        # 去掉回车、换行、制表符、退格符和空格
        simplified = input_string.replace('\r', '')
        simplified = simplified.replace('\n', '')
        simplified = simplified.replace('\t', '')
        simplified = simplified.replace('\b', '')
        simplified = simplified.replace(' ', '')
        
        return simplified
    
    @staticmethod
    def utf8_encode(input_string: str) -> str:
        """对字符串进行UTF-8 URL编码
        
        Args:
            input_string (str): 要编码的字符串
            
        Returns:
            str: URL编码后的字符串
        """
        if input_string is None:
            return ""
        return quote(input_string, safe='')
    
    @staticmethod
    def contain(input_string: str, keys: List[str]) -> Optional[str]:
        """检查字符串是否包含指定的关键字列表中的任意一个
        
        Args:
            input_string (str): 要检查的字符串
            keys (List[str]): 关键字列表
            
        Returns:
            Optional[str]: 如果找到匹配的关键字则返回该关键字，否则返回None
        """
        if not input_string or not keys:
            return None
        
        for key in keys:
            if key in input_string:
                return key
        
        return None
    
    @staticmethod
    def convert_data_to_hex_str(data: bytes) -> str:
        """将字节数据转换为十六进制字符串
        
        Args:
            data (bytes): 要转换的字节数据
            
        Returns:
            str: 十六进制字符串（小写）
        """
        if not data:
            return ""
        return data.hex()
    
    @staticmethod
    def convert_data_to_hex_str_with_separator(data: bytes, separator: str) -> str:
        """将字节数据转换为带分隔符的十六进制字符串
        
        Args:
            data (bytes): 要转换的字节数据
            separator (str): 分隔符
            
        Returns:
            str: 带分隔符的十六进制字符串（小写）
        """
        if not data:
            return ""
        hex_str = data.hex()
        # 每两个字符插入一个分隔符
        return separator.join(hex_str[i:i+2] for i in range(0, len(hex_str), 2))
    
    @staticmethod
    def convert_bytes_to_hex_str(data: bytes) -> str:
        """将字节数据转换为十六进制字符串（大写）
        
        Args:
            data (bytes): 要转换的字节数据
            
        Returns:
            str: 十六进制字符串（大写）
        """
        if not data:
            return ""
        return data.hex().upper()
    
    @staticmethod
    def convert_bytes_to_hex_str_with_separator(data: bytes, separator: str) -> str:
        """将字节数据转换为带分隔符的十六进制字符串（大写）
        
        Args:
            data (bytes): 要转换的字节数据
            separator (str): 分隔符
            
        Returns:
            str: 带分隔符的十六进制字符串（大写）
        """
        if not data:
            return ""
        hex_str = data.hex().upper()
        # 每两个字符插入一个分隔符
        return separator.join(hex_str[i:i+2] for i in range(0, len(hex_str), 2))
    
    @staticmethod
    def data_from_hex_string(hex_string: str) -> Optional[bytes]:
        """将十六进制字符串转换为字节数据
        
        Args:
            hex_string (str): 十六进制字符串
            
        Returns:
            Optional[bytes]: 转换后的字节数据，转换失败返回None
        """
        if not hex_string or len(hex_string) % 2 != 0:
            return None
        
        try:
            return bytes.fromhex(hex_string)
        except ValueError:
            return None
    
    @staticmethod
    def data_from_hex_string_with_separator(hex_string: str, separator: str) -> Optional[bytes]:
        """将带分隔符的十六进制字符串转换为字节数据
        
        Args:
            hex_string (str): 带分隔符的十六进制字符串
            separator (str): 分隔符
            
        Returns:
            Optional[bytes]: 转换后的字节数据，转换失败返回None
        """
        if not hex_string:
            return None
        
        try:
            # 移除分隔符
            clean_hex = hex_string.replace(separator, '')
            return bytes.fromhex(clean_hex)
        except ValueError:
            return None
    
    @staticmethod
    def format_mac_address(mac_address: str) -> str:
        """格式化MAC地址，在每两个字符之间插入冒号
        
        Args:
            mac_address (str): 原始MAC地址字符串（12个字符）
            
        Returns:
            str: 格式化后的MAC地址（如：AA:BB:CC:DD:EE:FF）
        """
        if len(mac_address) != 12:
            return mac_address
        
        formatted_parts = []
        for i in range(0, len(mac_address), 2):
            formatted_parts.append(mac_address[i:i+2])
        
        return ':'.join(formatted_parts)
    
    @staticmethod
    def select_string_with_start_end(input_string: str, start_str: Optional[str], end_str: Optional[str]) -> str:
        """从字符串中截取指定开始和结束标记之间的内容
        
        Args:
            input_string (str): 原始字符串
            start_str (Optional[str]): 开始标记，None或空字符串表示从头开始
            end_str (Optional[str]): 结束标记，None或空字符串表示到末尾结束
            
        Returns:
            str: 截取的字符串，如果未找到匹配则返回空字符串
        """
        if not input_string:
            return ""
        
        # 转义特殊字符
        def escape_regex(s):
            if s:
                return re.escape(s)
            return s
        
        start_escaped = escape_regex(start_str) if start_str else None
        end_escaped = escape_regex(end_str) if end_str else None
        
        # 构建正则表达式
        if start_escaped and end_escaped:
            pattern = f"{start_escaped}(.*?){end_escaped}"
        elif start_escaped:
            pattern = f"{start_escaped}(.*)"
        elif end_escaped:
            pattern = f"(.*?){end_escaped}"
        else:
            return input_string
        
        try:
            match = re.search(pattern, input_string)
            if match:
                return match.group(1)
            else:
                return ""
        except re.error:
            return ""
    
    @staticmethod
    def random_letter_and_number(length: int) -> str:
        """生成指定长度的随机字母和数字字符串
        
        Args:
            length (int): 字符串长度
            
        Returns:
            str: 随机生成的字符串
        """
        if length <= 0:
            return ""
        
        # 包含数字、小写字母、大写字母
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    @staticmethod
    def return_16_letter_and_number() -> str:
        """返回16位随机字母和数字字符串
        
        Returns:
            str: 16位随机字符串
        """
        return StringUtils.random_letter_and_number(16)
    
    @staticmethod
    def calculate_text_size(text: str, font_size: float, max_width: float = float('inf'), max_height: float = float('inf')) -> tuple:
        """计算文本在指定字体大小下的尺寸
        
        注意：这是一个简化的实现，实际的文本尺寸计算需要考虑具体的字体和渲染环境。
        在实际应用中，建议使用专门的文本渲染库如PIL、matplotlib等。
        
        Args:
            text (str): 要计算的文本
            font_size (float): 字体大小
            max_width (float): 最大宽度
            max_height (float): 最大高度
            
        Returns:
            tuple: (width, height) 文本尺寸
        """
        if not text:
            return (0.0, 0.0)
        
        # 简化计算：假设每个字符的平均宽度约为字体大小的0.6倍
        # 高度约等于字体大小
        char_width = font_size * 0.6
        line_height = font_size * 1.2  # 包含行间距
        
        lines = text.split('\n')
        max_line_width = 0
        
        for line in lines:
            line_width = len(line) * char_width
            if line_width > max_width:
                # 如果超过最大宽度，需要换行
                chars_per_line = int(max_width / char_width)
                if chars_per_line > 0:
                    line_count = (len(line) + chars_per_line - 1) // chars_per_line
                    line_width = min(len(line) * char_width, max_width)
                else:
                    line_count = 1
                    line_width = max_width
            else:
                line_count = 1
            
            max_line_width = max(max_line_width, line_width)
        
        total_lines = len(lines)
        total_height = total_lines * line_height
        
        # 限制在最大尺寸内
        final_width = min(max_line_width, max_width)
        final_height = min(total_height, max_height)
        
        return (final_width, final_height)