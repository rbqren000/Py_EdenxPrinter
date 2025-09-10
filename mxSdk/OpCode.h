//
//  OpCode.h
//  BelonLight
//
//  Created by rbq on 2019/8/19.
//  Copyright © 2019 rbq. All rights reserved.
//

#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

/**
 以下为打印机相关的opcode常量
 */

#pragma mark 打印机相关常量开始位置

/**
 打印头相关指令（0x0000~0x00FF）
 */
//设置打印头温度（0x0012),温度值2byte(int)
#define opcode_writePrinterHeadTemperature 0x0012
//读取打印头温度（0x0013),打印头索引1byte(uint_8),打印头索引：固定值，为 0
#define opcode_readPrinterHeadTemperature 0x0013
//读取打印头 ID（0x0014),打印头索引1byte(uint_8),打印头索引：固定值，为 0
#define opcode_readPrinterHeadId 0x0014

/**
 设备相关指令（0x0200~0x02FF）
 */

//读取设备信息（0x0200）数据 0byte
#define opcode_readSoftwareInfo 0x0200
//设备重启（0x0201）数据 0byte
#define opcode_restart 0x0201
//MCU 升级（IAP）（0x0203）数据 0byte
#define opcode_updateMcu 0x0203
//打印参数设置指令
#define opcode_writePrinterParameters 0x0002

#define opcode_transmitPicture 0x0100

#define opcode_transmitLogo 0x0204

#define opcode_printPicture 0x0300 //打印图片

#define opcode_readBattery 0x0018 //读取电量

#define opcode_readBatteryChargingState 0x0019 //读取充电状态

#define opcode_bluetoothConnectState 0x0202//读取蓝牙连接状态

#define opcode_readPrinterParameters 0x0003//读取打印机设置的参数

#define opcode_writeCirculationAndRepeatTime 0x0005 //循环次数和重复打印次数

#define opcode_readPrinterCirculationAndRepeatTime 0x0006 //读取循环打印次数和重复打印次数

#define opcode_writeDirectionAndPrintHeadDirection 0x0007 //设置打印方向

#define opcode_readPrinterDirectionAndPrintHeadDirection 0x0008 //读取打印方向

#define opcode_cleaningPrinterHead 0x0009 //清洗打印头

#define opcode_readPrintStart 0x1000 //打印开始

#define opcode_readPrintCompleted 0x1001 //打印结束

#define opcode_writePrinterConnectState 0x0202// 连接状态 0 已断开 1 已连接

#define opcode_writeSilentState 0x0303//静音模式指令
#define opcode_readSilentState 0x0304//读取静音模式指令

#define opcode_writeAutoPowerOffState 0x0305//自动关机式指令
#define opcode_readAutoPowerOffState 0x0306//读取自动关机状态式指令

#pragma mark 打印机相关常量 结束位置

@interface OpCode : NSObject

@end

NS_ASSUME_NONNULL_END
