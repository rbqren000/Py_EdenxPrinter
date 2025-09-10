//
//  ConnType.h
//  Inksi
//
//  Created by rbq on 2024/7/31.
//

#ifndef ConnType_h
#define ConnType_h

typedef NS_ENUM(NSUInteger, ConnType) {
    ConnTypeBLE  = 0b00000001 << 0,  // 0x01, BLE 连接
    ConnTypeWiFi = 0b00000001 << 1,  // 0x02, WiFi 连接
    ConnTypeAP   = 0b00000001 << 2,  // 0x04, AP 连接
    // 预留 5 位用于未来扩展
};

#endif /* ConnType_h */
