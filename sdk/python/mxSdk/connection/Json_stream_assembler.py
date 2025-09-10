import json
import threading
from typing import Callable, Optional, List
from .gcd_style_timer import GCDStyleTimer
from ..utils.rbq_log import RBQLog

class JsonStreamAssembler:
    def __init__(self, on_json_complete: Callable[[str], None], timeout_sec: float = 5.0):
        """
        用于流式接收分段 JSON 数据，并自动拼接与解析完成后的回调。

        :param on_json_complete: 完整 JSON 数据拼接成功时触发的回调函数
        :param timeout_sec: 超时时间（秒），超过此时间未完成拼接则自动清除缓存
        """
        self._on_json_complete = on_json_complete
        self._timeout_sec = timeout_sec
        self._buffer: List[str] = []  # 存储待拼接的 JSON 片段
        self._receiving = False       # 当前是否处于接收 JSON 状态
        self._bracket_count = 0       # 跟踪花括号嵌套层级
        self._timeout_timer: Optional[GCDStyleTimer] = None  # 计时器实例
        self._timer_name = "JsonStreamTimeout"

    def reset(self):
        """清空缓存状态并停止超时计时器"""
        self._buffer.clear()
        self._receiving = False
        self._bracket_count = 0
        if self._timeout_timer:
            self._timeout_timer.clear()
            self._timeout_timer = None
        RBQLog.log_debug("JSON状态已重置")

    def _try_dispatch(self, raw: str):
        """尝试解析 JSON 字符串并触发回调，非法则记录日志"""
        try:
            # 验证是否为有效的JSON
            json.loads(raw)
            RBQLog.log_debug(f"成功解析JSON: {raw[:200]}{'...' if len(raw) > 200 else ''}")
            self._on_json_complete(raw)
            # 成功解析后重置状态
            self.reset()
            return True
        except json.JSONDecodeError as e:
            RBQLog.log_warning(f"JSON解析失败: {e}, 数据: {raw[:50]}{'...' if len(raw) > 50 else ''}")
            return False

    def _start_timer(self):
        """每次收到片段时重置超时定时器"""
        if self._timeout_timer:
            self._timeout_timer.clear()

        self._timeout_timer = GCDStyleTimer(
            start=self._timeout_sec,
            interval=0,
            callback=self.reset,      # 超时后清空状态
            repeats=False,
            name=self._timer_name
        )
        self._timeout_timer.fire()
        RBQLog.log_debug(f"启动JSON超时计时器: {self._timeout_sec}秒")

    def _count_brackets(self, text: str) -> int:
        """计算文本中的花括号平衡情况"""
        count = 0
        for char in text:
            if char == '{':
                count += 1
            elif char == '}':
                count -= 1
        return count

    def feed(self, data: bytes):
        """
        接收来自设备或串口的数据片段，自动解析出 JSON 包。

        :param data: 字节流数据（通常为 UTF-8 编码）
        """
        try:
            read_data = data.decode("utf-8").strip()
            RBQLog.log_debug(f"JSON接收数据: {read_data[:50]}{'...' if len(read_data) > 50 else ''}")
        except UnicodeDecodeError:
            RBQLog.log_warning("接收到非UTF-8编码数据，已跳过")
            return  # 非法数据跳过

        # 启用超时机制
        self._start_timer()

        # ① 完整 JSON，直接派发
        if read_data.startswith("{") and read_data.endswith("}"):
            # 检查是否是嵌套的完整JSON
            bracket_balance = self._count_brackets(read_data)
            if bracket_balance == 0:  # 花括号平衡，是完整JSON
                RBQLog.log_debug("检测到完整JSON")
                self._try_dispatch(read_data)
                return
            else:
                RBQLog.log_debug(f"看似完整但花括号不平衡，可能是嵌套JSON: {bracket_balance}")
                # 继续处理为不完整JSON

        # ② 有花括号，但前后有垃圾干扰，尝试提取完整JSON
        if "{" in read_data and "}" in read_data:
            RBQLog.log_debug("检测到可能包含JSON的数据")
            
            # 尝试提取最外层的完整JSON对象
            start_idx = read_data.find("{")
            current_level = 0
            complete_json = None
            
            for i in range(start_idx, len(read_data)):
                if read_data[i] == '{':
                    current_level += 1
                elif read_data[i] == '}':
                    current_level -= 1
                    
                if current_level == 0 and i > start_idx:  # 找到匹配的结束括号
                    complete_json = read_data[start_idx:i+1]
                    break
            
            if complete_json:
                RBQLog.log_debug(f"提取到可能的完整JSON: {complete_json[:50]}{'...' if len(complete_json) > 50 else ''}")
                if self._try_dispatch(complete_json):
                    return
        
        # ③ 出现新起点 {，认为新 JSON 开始
        if "{" in read_data and "}" not in read_data:
            if self._receiving:
                RBQLog.log_debug("检测到新的JSON开始标记，重置之前的缓冲区")
                self.reset()
            
            read_data = read_data[read_data.find("{"):]
            self._receiving = True
            self._bracket_count = self._count_brackets(read_data)  # 计算初始括号平衡
            self._buffer.clear()
            self._buffer.append(read_data)
            RBQLog.log_debug(f"开始接收新JSON，初始括号平衡: {self._bracket_count}")
            return

        # ④ 继续接收 JSON 内容
        if self._receiving:
            self._buffer.append(read_data)
            self._bracket_count += self._count_brackets(read_data)
            joined = "".join(self._buffer)
            
            RBQLog.log_debug(f"继续接收JSON片段，当前括号平衡: {self._bracket_count}")
            
            # 检查是否有完整的JSON（括号平衡且有结束括号）
            if "}" in read_data and self._bracket_count <= 0:
                # 尝试找到第一个有效的JSON对象
                start_idx = joined.find("{")
                current_level = 0
                end_idx = -1
                
                for i in range(start_idx, len(joined)):
                    if joined[i] == '{':
                        current_level += 1
                    elif joined[i] == '}':
                        current_level -= 1
                        
                    if current_level == 0 and i > start_idx:  # 找到匹配的结束括号
                        end_idx = i
                        break
                
                if end_idx > 0:
                    fragment = joined[start_idx:end_idx+1]
                    RBQLog.log_debug(f"找到可能的完整JSON: {fragment[:50]}{'...' if len(fragment) > 50 else ''}")
                    dispatch_success = self._try_dispatch(fragment)
                    
                    # 处理剩余部分
                    remaining = joined[end_idx+1:]
                    if "{" in remaining:
                        # 还有新的JSON开始，重新开始接收
                        read_data = remaining[remaining.find("{"):]
                        self._receiving = True
                        self._bracket_count = self._count_brackets(read_data)
                        self._buffer.clear()
                        self._buffer.append(read_data)
                        RBQLog.log_debug(f"处理剩余部分，开始接收新JSON，初始括号平衡: {self._bracket_count}")
                    else:
                        # 没有新的JSON开始，如果_try_dispatch没有成功（没有调用reset），才重置状态
                        if not dispatch_success:
                            self.reset()