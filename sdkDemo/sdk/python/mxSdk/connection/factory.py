# -*- coding: utf-8 -*-
"""
连接策略工厂

根据连接类型创建相应的连接策略实例。
采用工厂模式设计，简化连接策略的创建过程。

作者: RBQ
版本: 1.0.0
创建时间: 2025
Python版本: 3.9+
"""

from typing import Dict, Type, Optional
from .strategy import ConnectionStrategy
from .usb import UsbConnectionStrategy
from .serial import SerialConnectionStrategy
from ..enums import ConnType
from ..utils.rbq_log import RBQLog


class ConnectionStrategyFactory:
    """连接策略工厂类

    根据连接类型创建相应的连接策略实例。
    采用工厂模式设计，简化连接策略的创建过程。

    Attributes:
        _strategy_classes: 连接策略类字典
    """

    _strategy_classes: Dict[ConnType, Type[ConnectionStrategy]] = {
        ConnType.USB: UsbConnectionStrategy,
        ConnType.SERIAL: SerialConnectionStrategy,
    }

    @classmethod
    def create_strategy(cls, conn_type: ConnType) -> Optional[ConnectionStrategy]:
        """创建连接策略实例

        Args:
            conn_type: 连接类型

        Returns:
            Optional[ConnectionStrategy]: 连接策略实例，如果类型不支持则返回None
        """
        try:
            strategy_class = cls._strategy_classes.get(conn_type)
            if strategy_class is None:
                RBQLog.log(f"不支持连接类型: {conn_type}")
                return None

            return strategy_class()
        except Exception as e:
            RBQLog.log(f"创建连接策略失败: {str(e)}")
            return None

    @classmethod
    def register_strategy(cls, conn_type: ConnType, strategy_class: Type[ConnectionStrategy]) -> bool:
        """注册自定义连接策略

        Args:
            conn_type: 连接类型
            strategy_class: 连接策略类

        Returns:
            bool: 注册成功返回True，失败返回False
        """
        try:
            if not issubclass(strategy_class, ConnectionStrategy):
                RBQLog.log(f"策略类必须继承自ConnectionStrategy: {strategy_class}")
                return False

            cls._strategy_classes[conn_type] = strategy_class
            RBQLog.log(f"成功注册连接策略: {conn_type} -> {strategy_class.__name__}")
            return True
        except Exception as e:
            RBQLog.log(f"注册连接策略失败: {str(e)}")
            return False