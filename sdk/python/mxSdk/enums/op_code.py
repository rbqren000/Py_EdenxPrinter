from enum import IntFlag

class OpCode(IntFlag):
    """打印机操作码枚举类"""

    # === 打印头相关指令 (0x0000 ~ 0x00FF) ===
    WRITE_PRINTER_PARAMETERS = 0x0002                      # 设置打印机参数（打印头配置）
    READ_PRINTER_PARAMETERS = 0x0003                       # 读取打印机参数
    WRITE_CIRCULATION_AND_REPEAT_TIMES = 0x0005            # 设置循环次数与重复打印次数
    READ_CIRCULATION_AND_REPEAT_TIMES = 0x0006             # 读取循环与重复打印次数
    WRITE_PRINT_DIRECTION = 0x0007                         # 设置打印方向（如左→右、右→左）
    READ_PRINT_DIRECTION = 0x0008                          # 读取当前打印方向
    CLEAR_PRINT_HEAD = 0x0009                              # 执行打印头清洗
    WRITE_PRINT_TEMPERATURE = 0x0012                       # 设置打印头温度（2 字节整型）
    READ_PRINT_TEMPERATURE = 0x0013                        # 读取打印头温度（固定索引 0）
    READ_CARTRIDGE_ID = 0x0014                             # 读取打印墨盒 ID
    READ_BATTERY = 0x0018                                  # 读取设备电量百分比
    READ_RECHARGE_STATE = 0x0019                           # 读取是否正在充电（0/1）

    # === 图片传输类指令 ===
    TRANSMIT_PICTURE_DATA = 0x0100                         # 传输图片到打印机（位图数据）
    OEM_TRANSMIT_PICTURE_DATA = 0x0101                     # OEM：传输 Stamp 图像

    # === 设备维护/升级指令 (0x0200 ~ 0x02FF) ===
    READ_SOFTWARE_INFO = 0x0200                            # 获取设备软硬件信息
    RESTART_DEVICE = 0x0201                                # 重启设备
    READ_BLUETOOTH_CONNECT_STATE = 0x0202                  # 查询蓝牙连接状态
    WRITE_PRINTER_CONNECT_STATE = 0x0202                   # 设置连接状态（0: 断开, 1: 连接）
    UPDATE_MCU = 0x0203                                    # 启动 MCU 固件升级
    WRITE_LOGO_DATA = 0x0204                               # 烧录/更新 LOGO 图像

    # oem 指令
    OEM_TRANSMIT_TEST_PICTURE_DATA = 0x0205                # OEM：传输测试图像（≤ 131040 字节）
    OEM_READ_ALL_PRINT_COUNT = 0x0206                      # OEM：获取设备总打印次数
    OEM_READ_PRINT_RECORD = 0x0207                         # OEM：读取历史打印记录
    OEM_CLEAR_PRINT_RECORD = 0x0208                        # OEM：清除打印记录

    # === 打印任务控制类指令 ===
    PRINT_PICTURE = 0x0300                                 # 执行图片打印命令
    WRITE_SILENT_STATE = 0x0303                            # 设置静音模式（0: 否, 1: 是）
    READ_SILENT_STATE = 0x0304                             # 查询当前静音状态
    WRITE_AUTO_POWER_OFF_STATE = 0x0305                    # 设置自动关机状态
    READ_AUTO_POWER_OFF_STATE = 0x0306                     # 获取自动关机设定
    WRITE_PRINT_START_COMMAND = 0x0307                     # 手动触发打印（等效于实体按键）

    # === 打印状态通知类指令 (0x1000 ~) ===
    PRINT_START = 0x1000                                   # 打印开始通知
    PRINT_COMPLETED = 0x1001                               # 打印完成通知
    OVER_TEMP_TERMINATION = 0x1010                         # 打印被过温中断
    NOT_INSTALLED_IN_CARTRIDGE = 0x1011                    # 墨盒未安装
    ID_VERIFICATION_FAILED = 0x1012                        # 墨盒 ID 校验失败

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"

