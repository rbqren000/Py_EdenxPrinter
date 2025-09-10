from enum import Enum

class PaperType(Enum):
    """纸张类型枚举

    用于表示不同的标准纸张类型。

    Attributes:
        A4 (int): A4纸张规格 (210 × 297 毫米)
        US_LETTER (int): 美国信纸规格 (215.9 × 279.4 毫米)
        B5 (int): B5纸张规格 (176 × 250 毫米)
    """
    A4 = 0
    US_LETTER = 1  # 原名为UsLetter，改为更符合Python命名规范的US_LETTER
    B5 = 2

    def __str__(self) -> str:
        """返回格式化的纸张类型描述"""
        return self.name.replace('_', ' ')

    def __repr__(self) -> str:
        """返回枚举值的程序表示形式"""
        return f"PaperType.{self.name}"

    @property
    def dimensions_mm(self) -> tuple[float, float]:
        """返回纸张尺寸（宽x高，单位：毫米）

        Returns:
            tuple[float, float]: 包含宽度和高度的元组，单位为毫米
        """
        dimensions = {
            PaperType.A4: (210.0, 297.0),
            PaperType.US_LETTER: (215.9, 279.4),
            PaperType.B5: (176.0, 250.0)
        }
        return dimensions[self]