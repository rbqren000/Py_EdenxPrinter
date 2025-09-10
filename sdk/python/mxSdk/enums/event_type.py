# from enum import Enum, unique
# from typing import Callable, Dict, List, Union
# from mxSdk.models.device_info import DeviceInfo

# @unique
# class EventType(str, Enum):
#     # === 设备发现相关事件 ===
#     DEVICE_START_DISCOVER = "device_start_discover"
#     DEVICE_FOUND = "device_found"
#     DEVICE_DISCOVER_FINISHED = "device_discover_finished"
#     DEVICE_STOP_DISCOVER = "device_stop_discover"

#     # === 设备连接相关事件 ===
#     DEVICE_CONNECT_START = "device_connect_start"
#     DEVICE_CONNECT_SUCCEED = "device_connect_succeed"
#     DEVICE_DISCONNECT = "device_disconnect"
#     DEVICE_CONNECT_FAIL = "device_connect_fail"

#     # === 数据传输进度相关事件 ===
#     DEVICE_DATA_TRANSFER_START = "device_data_transfer_start"
#     DEVICE_DATA_TRANSFER = "device_data_transfer"
#     DEVICE_DATA_TRANSFER_FINISH = "device_data_transfer_finish"
#     DEVICE_DATA_TRANSFER_ERROR = "device_data_transfer_error"

#     # === 设备读取属性事件 ===
#     DEVICE_READ_DATA = "device_read_data"                                        # 读取设备数据，通用所有数据都可通过该事件监听
#     DEVICE_READ_BATTERY = "device_read_battery"                                  # 读取设备电池电量
#     DEVICE_READ_CHARGING_STATE = "device_read_charging_state"                    # 读取电池充电状态
#     DEVICE_READ_PRINT_HEAD_PARAMETER = "device_read_print_head_parameter"        # 读取打印头参数
#     DEVICE_READ_CIRCULATION_REPEAT = "device_read_circulation_repeat"            # 读取循环打印次数与重复次数
#     DEVICE_READ_PRINT_DIRECTION_AND_PRINT_HEAD_DIRECTION = "device_read_print_direction_and_print_head_direction"                  # 读取打印方向和打印头方向
#     DEVICE_READ_TEMPERATURE = "device_read_temperature"                          # 读取打印头温度（可作为通用温度）
#     DEVICE_READ_PRINT_HEAD_TEMPERATURE = "device_read_print_head_temperature"    # 读取打印头温度（精确命名）
#     DEVICE_READ_PRINT_HEAD_ID = "device_read_print_head_id"                      # 读取打印头 ID
#     DEVICE_READ_DEVICE_INFO = "device_read_device_info"                          # 读取设备软件/固件信息
#     DEVICE_READ_SILENT_STATE = "device_read_silent_state"                        # 读取静音模式状态
#     DEVICE_READ_AUTO_POWER_OFF_STATE = "device_read_auto_power_off_state"        # 读取自动关机状态
#     DEVICE_READ_CONNECT_STATE = "device_read_connect_state"                      # 读取蓝牙连接状态

#     # === 打印任务相关事件 ===
#     DEVICE_PRINT_START = "device_print_start"
#     DEVICE_PRINT_PROGRESS = "device_print_progress"
#     DEVICE_PRINT_FINISH = "device_print_finish"

#     # === 命令写入相关事件 ===
#     DEVICE_COMMAND_WRITE_SUCCESS = "device_command_write_success"
#     DEVICE_COMMAND_WRITE_ERROR = "device_command_write_error"

#     # === 数据写入相关事件 ===
#     DEVICE_DATA_WRITE_START = "device_data_write_start"
#     DEVICE_DATA_WRITE_PROGRESS = "device_data_write_progress"
#     DEVICE_DATA_WRITE_SUCCESS = "device_data_write_success"
#     DEVICE_DATA_WRITE_ERROR = "device_data_write_error"