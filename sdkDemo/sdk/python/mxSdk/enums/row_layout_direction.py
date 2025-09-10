from enum import Enum

class RowLayoutDirection(Enum):
    """行布局方向枚举

    用于指定RowImage生成时的排列方向。

    Attributes:
        VERTICAL (int): 垂直方向排列，图像元素从上到下排列
        HORIZONTAL (int): 水平方向排列，图像元素从左到右排列
    """
    VERTICAL = 0    # 原名为RowLayoutDirectionVert
    HORIZONTAL = 1  # 原名为RowLayoutDirectionHorz

    def __str__(self) -> str:
        """返回格式化的布局方向描述"""
        return self.name.capitalize()

    def __repr__(self) -> str:
        """返回枚举值的程序表示形式"""
        return f"RowLayoutDirection.{self.name}"

    @property
    def is_vertical(self) -> bool:
        """检查是否为垂直布局

        Returns:
            bool: 如果是垂直布局返回True，否则返回False
        """
        return self == RowLayoutDirection.VERTICAL

    @property
    def is_horizontal(self) -> bool:
        """检查是否为水平布局

        Returns:
            bool: 如果是水平布局返回True，否则返回False
        """
        return self == RowLayoutDirection.HORIZONTAL