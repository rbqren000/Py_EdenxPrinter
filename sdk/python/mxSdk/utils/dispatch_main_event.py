from PyQt5.QtCore import QObject, QThread, QTimer, QCoreApplication, QMetaObject, Qt, pyqtSlot
from typing import Callable, Optional
import threading
import weakref

class _MainThreadInvoker(QObject):
    """主线程任务调度器"""

    def __init__(self):
        super().__init__()
        self._func: Optional[Callable] = None
        self._args = ()
        self._kwargs = {}
        self._lock = threading.Lock()

    @pyqtSlot()
    def invoke(self):
        with self._lock:
            if self._func:
                try:
                    self._func(*self._args, **self._kwargs)
                except Exception as e:
                    # 记录异常，避免静默失败
                    print(f"主线程调度执行异常: {e}")
                finally:
                    # 清理引用，避免内存泄漏
                    self._func = None
                    self._args = ()
                    self._kwargs = {}

    def call(self, func: Callable, *args, **kwargs):
        with self._lock:
            self._func = func
            self._args = args
            self._kwargs = kwargs
        QMetaObject.invokeMethod(self, "invoke", Qt.QueuedConnection)

class DispatchMainEvent:
    """
    主线程事件调度器：用于从任意线程将函数安全地派发到主线程执行。
    
    特性：
    - 线程安全
    - 自动初始化
    - 异常处理
    - 内存泄漏防护
    """
    
    _invoker: Optional[_MainThreadInvoker] = None
    _app_ref: Optional[weakref.ReferenceType] = None
    _lock = threading.Lock()

    @classmethod
    def _get_invoker(cls) -> _MainThreadInvoker:
        """获取调度器实例，延迟初始化"""
        if cls._invoker is not None:
            # 检查应用是否还存在
            if cls._app_ref is not None and cls._app_ref() is not None:
                return cls._invoker
            else:
                # 应用已销毁，重置状态
                cls._invoker = None
                cls._app_ref = None
        
        with cls._lock:
            # 双重检查锁定模式
            if cls._invoker is None:
                app = QCoreApplication.instance()
                if app is None:
                    raise RuntimeError(
                        "QCoreApplication 尚未初始化。请确保在创建 QApplication 或 QCoreApplication 后使用此功能。"
                    )
                
                cls._invoker = _MainThreadInvoker()
                cls._invoker.moveToThread(app.thread())
                cls._app_ref = weakref.ref(app)
        
        return cls._invoker

    @classmethod
    def post(cls, func: Callable, *args, **kwargs):
        """
        将函数派发到主线程执行
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Raises:
            RuntimeError: 当 QCoreApplication 未初始化时
        """
        if not callable(func):
            raise TypeError("func 必须是可调用对象")
        
        invoker = cls._get_invoker()
        invoker.call(func, *args, **kwargs)

    @classmethod
    def post_after(cls, ms: int, func: Callable, *args, **kwargs):
        """
        延迟指定毫秒后将函数派发到主线程执行
        
        Args:
            ms: 延迟毫秒数
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Raises:
            ValueError: 当延迟时间为负数时
            RuntimeError: 当 QCoreApplication 未初始化时
        """
        if ms < 0:
            raise ValueError("延迟时间不能为负数")
        
        if not callable(func):
            raise TypeError("func 必须是可调用对象")
            
        def delayed():
            cls.post(func, *args, **kwargs)
            
        QTimer.singleShot(ms, delayed)

    @classmethod
    def is_main_thread(cls) -> bool:
        """检查当前线程是否为主线程"""
        app = QCoreApplication.instance()
        if app is None:
            return False
        return QThread.currentThread() == app.thread()

    @classmethod
    def reset(cls):
        """重置调度器状态（主要用于测试）"""
        with cls._lock:
            cls._invoker = None
            cls._app_ref = None

# 便捷函数
def dispatch_to_main(func: Callable, *args, **kwargs):
    """便捷函数：派发到主线程"""
    DispatchMainEvent.post(func, *args, **kwargs)

def dispatch_to_main_after(ms: int, func: Callable, *args, **kwargs):
    """便捷函数：延迟派发到主线程"""
    DispatchMainEvent.post_after(ms, func, *args, **kwargs)