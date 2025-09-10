"""
GCDStyleTimer 类

该类实现了基于 GCD 定时器的功能，支持延迟启动、重复执行和取消定时器等操作。

"""
import threading
import time
import logging
from typing import Callable, Optional, Union, Any
from enum import Enum
from dataclasses import dataclass
from weakref import finalize

class TimerState(Enum):
    """定时器状态枚举"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    CANCELLED = "cancelled"

@dataclass
class TimerStats:
    """定时器统计信息"""
    created_at: float
    fire_count: int = 0
    total_runtime: float = 0.0
    last_fire_time: Optional[float] = None
    pause_count: int = 0
    resume_count: int = 0
    error_count: int = 0

class GCDStyleTimer:
    """
    基于 GCD 风格的高精度定时器类
    
    特性：
    - 线程安全
    - 支持暂停/恢复
    - 高精度时间补偿
    - 完善的错误处理
    - 统计信息收集
    """
    
    # 类级别的默认配置
    DEFAULT_PRECISION = 0.001  # 默认时间精度 1ms
    MAX_TIMER_COUNT = 1000     # 最大定时器数量限制
    
    # 类级别计数器
    _instance_count = 0
    _active_timers = set()
    _class_lock = threading.RLock()
    
    def __init__(
        self, 
        start: float, 
        interval: float = 0.0, 
        callback: Optional[Callable[[], None]] = None,
        repeats: bool = False, 
        name: Optional[str] = None,
        precision: float = DEFAULT_PRECISION,
        error_handler: Optional[Callable[[Exception], None]] = None,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """
        初始化定时器
        
        Args:
            start: 初始延迟时间（秒）
            interval: 重复间隔时间（秒）
            callback: 回调函数
            repeats: 是否重复执行
            name: 定时器名称
            precision: 时间精度（秒）
            error_handler: 自定义错误处理函数
            logger: 自定义日志记录器
        """
        # 参数验证
        self._validate_parameters(start, interval, repeats, precision)
        
        # 基本属性
        self._start = max(0.0, start)
        self._interval = max(0.0, interval)
        self._callback = callback
        self._repeats = repeats
        self._precision = max(0.001, precision)
        self._error_handler = error_handler
        
        # 生成唯一ID和名称
        with self.__class__._class_lock:
            self.__class__._instance_count += 1
            self._instance_id = self.__class__._instance_count
            
        self._name = name or f"Timer-{self._instance_id}"
        
        # 日志配置
        self._logger = logger or self._setup_logger()
        
        # 状态管理
        self._lock = threading.RLock()
        self._state = TimerState.IDLE
        self._timer: Optional[threading.Timer] = None
        
        # 时间追踪
        self._schedule_time: Optional[float] = None
        self._remaining_time: Optional[float] = None
        self._last_interval: Optional[float] = None
        
        # 统计信息
        self._stats = TimerStats(created_at=time.time())
        
        # 资源清理注册
        self._finalizer = finalize(self, self._cleanup_resources, 
                                 self._timer, self._name, self.__class__._active_timers)
        
        # 注册到活动定时器集合
        with self.__class__._class_lock:
            if len(self.__class__._active_timers) >= self.__class__.MAX_TIMER_COUNT:
                raise RuntimeError(f"超过最大定时器数量限制: {self.__class__.MAX_TIMER_COUNT}")
            self.__class__._active_timers.add(self)
        
        self._logger.debug(f"[{self._name}] Timer created with start={start}s, interval={interval}s")
    
    def _validate_parameters(self, start: float, interval: float, repeats: bool, precision: float) -> None:
        """参数验证"""
        if not isinstance(start, (int, float)) or start < 0:
            raise ValueError("start 必须是非负数")
        
        if not isinstance(interval, (int, float)) or interval < 0:
            raise ValueError("interval 必须是非负数")
            
        if repeats and interval <= 0:
            raise ValueError("重复定时器的间隔时间必须大于 0")
            
        if not isinstance(precision, (int, float)) or precision <= 0:
            raise ValueError("precision 必须是正数")
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(f"GCDTimer.{self._name}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _handler(self) -> None:
        """定时器回调处理函数"""
        with self._lock:
            if self._state not in (TimerState.RUNNING,):
                return
            
            # 更新统计信息
            current_time = time.time()
            self._stats.fire_count += 1
            self._stats.last_fire_time = current_time
            
            if self._schedule_time:
                self._stats.total_runtime += current_time - self._schedule_time
        
        # 执行回调（在锁外执行避免死锁）
        if self._callback:
            try:
                callback_start = time.perf_counter()
                self._callback()
                callback_duration = time.perf_counter() - callback_start
                
                if callback_duration > 0.1:  # 如果回调执行超过100ms，记录警告
                    self._logger.warning(f"[{self._name}] Callback took {callback_duration:.3f}s")
                    
            except Exception as e:
                with self._lock:
                    self._stats.error_count += 1
                
                self._logger.error(f"[{self._name}] Callback error: {e}")
                
                if self._error_handler:
                    try:
                        self._error_handler(e)
                    except Exception as handler_error:
                        self._logger.error(f"[{self._name}] Error handler failed: {handler_error}")
        
        # 处理重复执行
        with self._lock:
            if self._repeats and self._state == TimerState.RUNNING:
                # 时间补偿：考虑回调执行时间
                actual_interval = self._interval
                if self._schedule_time:
                    elapsed = time.perf_counter() - self._schedule_time
                    drift = elapsed - self._last_interval if self._last_interval else 0
                    if abs(drift) > self._precision:
                        actual_interval = max(self._precision, self._interval - drift)
                        self._logger.debug(f"[{self._name}] Time drift compensation: {drift:.3f}s")
                
                self._schedule(actual_interval)
    
    def _schedule(self, delay: float) -> None:
        """调度定时器执行"""
        self._schedule_time = time.perf_counter()
        self._last_interval = delay
        self._timer = threading.Timer(delay, self._handler)
        self._timer.daemon = True
        self._timer.start()
        
        self._logger.debug(f"[{self._name}] Scheduled to fire in {delay:.3f}s")
    
    def fire(self) -> None:
        """启动定时器"""
        with self._lock:
            if self._state == TimerState.CANCELLED:
                raise RuntimeError("无法启动已取消的定时器")
            
            self._stop_current_timer()
            self._state = TimerState.RUNNING
            self._remaining_time = None
            self._schedule(self._start)
            
        self._logger.info(f"[{self._name}] Timer fired")
    
    def invalidate(self) -> None:
        """取消定时器"""
        with self._lock:
            old_state = self._state
            self._state = TimerState.CANCELLED
            self._stop_current_timer()
            
        if old_state != TimerState.CANCELLED:
            self._logger.info(f"[{self._name}] Timer invalidated")
    
    def pause(self) -> bool:
        """
        暂停定时器
        
        Returns:
            bool: 是否成功暂停
        """
        with self._lock:
            if self._state != TimerState.RUNNING or not self._timer or not self._timer.is_alive():
                return False
            
            # 计算剩余时间
            if self._schedule_time:
                elapsed = time.perf_counter() - self._schedule_time
                expected_delay = self._last_interval or self._interval
                self._remaining_time = max(self._precision, expected_delay - elapsed)
            else:
                self._remaining_time = self._interval
            
            self._state = TimerState.PAUSED
            self._stats.pause_count += 1
            self._stop_current_timer()
            
        self._logger.info(f"[{self._name}] Timer paused, remaining: {self._remaining_time:.3f}s")
        return True
    
    def resume(self) -> bool:
        """
        恢复定时器
        
        Returns:
            bool: 是否成功恢复
        """
        with self._lock:
            if self._state != TimerState.PAUSED:
                return False
            
            self._state = TimerState.RUNNING
            self._stats.resume_count += 1
            delay = self._remaining_time or self._interval
            self._remaining_time = None
            self._schedule(delay)
            
        self._logger.info(f"[{self._name}] Timer resumed")
        return True
    
    def update(
        self, 
        *, 
        interval: Optional[float] = None, 
        callback: Optional[Callable[[], None]] = None, 
        start: Optional[float] = None,
        error_handler: Optional[Callable[[Exception], None]] = None
    ) -> None:
        """动态更新定时器参数"""
        with self._lock:
            if self._state == TimerState.CANCELLED:
                raise RuntimeError("无法更新已取消的定时器")
            
            old_values = {}
            
            if interval is not None:
                if self._repeats and interval <= 0:
                    raise ValueError("重复定时器的间隔时间必须大于 0")
                old_values['interval'] = self._interval
                self._interval = max(0.0, interval)
            
            if callback is not None:
                old_values['callback'] = self._callback
                self._callback = callback
            
            if start is not None:
                old_values['start'] = self._start
                self._start = max(0.0, start)
                
            if error_handler is not None:
                old_values['error_handler'] = self._error_handler
                self._error_handler = error_handler
            
            # 如果定时器正在运行，重新启动
            if self._state == TimerState.RUNNING:
                self.fire()
        
        self._logger.info(f"[{self._name}] Timer updated: {old_values}")
    
    def _stop_current_timer(self) -> None:
        """停止当前定时器（内部方法，需要在锁内调用）"""
        if self._timer and self._timer.is_alive():
            self._timer.cancel()
        self._timer = None
    
    # 状态查询方法
    def is_running(self) -> bool:
        """检查定时器是否正在运行"""
        with self._lock:
            return self._state == TimerState.RUNNING and self._timer is not None and self._timer.is_alive()
    
    def is_paused(self) -> bool:
        """检查定时器是否已暂停"""
        with self._lock:
            return self._state == TimerState.PAUSED
    
    def is_cancelled(self) -> bool:
        """检查定时器是否已取消"""
        with self._lock:
            return self._state == TimerState.CANCELLED
    
    def get_state(self) -> TimerState:
        """获取当前状态"""
        with self._lock:
            return self._state
    
    def get_remaining_time(self) -> Optional[float]:
        """获取剩余时间"""
        with self._lock:
            if self._state == TimerState.PAUSED:
                return self._remaining_time
            elif self._state == TimerState.RUNNING and self._schedule_time:
                elapsed = time.perf_counter() - self._schedule_time
                expected_delay = self._last_interval or self._interval
                return max(0.0, expected_delay - elapsed)
            return None
    
    def get_stats(self) -> TimerStats:
        """获取统计信息"""
        with self._lock:
            return TimerStats(
                created_at=self._stats.created_at,
                fire_count=self._stats.fire_count,
                total_runtime=self._stats.total_runtime,
                last_fire_time=self._stats.last_fire_time,
                pause_count=self._stats.pause_count,
                resume_count=self._stats.resume_count,
                error_count=self._stats.error_count
            )
    
    def clear(self) -> None:
        """清理定时器资源"""
        with self._lock:
            self.invalidate()
            self._callback = None
            self._error_handler = None
            self._start = 0
            self._interval = 0
            self._repeats = False
            self._remaining_time = None
        
        # 从活动定时器集合中移除
        with self.__class__._class_lock:
            self.__class__._active_timers.discard(self)
        
        self._logger.info(f"[{self._name}] Timer cleared")
    
    @staticmethod
    def _cleanup_resources(timer, name, active_timers):
        """静态清理方法，用于 weakref.finalize"""
        if timer and hasattr(timer, 'cancel'):
            timer.cancel()
        active_timers.discard(timer)
    
    @classmethod
    def get_active_timer_count(cls) -> int:
        """获取活动定时器数量"""
        with cls._class_lock:
            return len(cls._active_timers)
    
    @classmethod
    def cleanup_all_timers(cls) -> int:
        """清理所有活动定时器"""
        with cls._class_lock:
            timers_to_cleanup = list(cls._active_timers)
            count = len(timers_to_cleanup)
        
        for timer in timers_to_cleanup:
            try:
                timer.clear()
            except Exception as e:
                logging.error(f"Error cleaning up timer {timer._name}: {e}")
        
        return count
    
    def __str__(self) -> str:
        with self._lock:
            return (f"GCDStyleTimer(name='{self._name}', state={self._state.value}, "
                   f"start={self._start}s, interval={self._interval}s, repeats={self._repeats})")
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __del__(self):
        """析构函数"""
        try:
            if hasattr(self, '_finalizer'):
                self._finalizer.detach()
            self.clear()
        except Exception:
            pass  # 忽略析构函数中的异常

