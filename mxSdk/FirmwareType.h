//
//  SoftwareType.h
//  Inksi
//
//  Created by rbq on 2024/10/15.
//

#ifndef FirmwareType_h
#define FirmwareType_h
/**
 用来表示打印机上可升级的固件类型
 */
typedef NS_ENUM(NSUInteger, FirmwareType) {
    FirmwareTypeMCU  = 0b00000001 << 8,  // 0x100, MCU 芯片
    FirmwareTypeWiFi = 0b00000001 << 9,  // 0x200, WiFi 芯片
    // 预留 6 位用于未来扩展
};

#endif /* FirmwareType_h */
