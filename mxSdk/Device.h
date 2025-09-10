//
//  Printer.h
//  BelonPrinter
//
//  Created by rbq on 2020/4/22.
//  Copyright © 2020 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <CoreBluetooth/CoreBluetooth.h>
#import "ConnType.h"
#import "FirmwareType.h"

NS_ASSUME_NONNULL_BEGIN

@interface Device : NSObject

@property (nonatomic, strong, readonly) NSString *name;

//设备名称或者叫作别名，因为和设备本身的名字并不对应，UI设计的时候又使用了别的名称
@property (nonatomic, strong, readonly) NSString *aliases;
@property (nonatomic, strong, readonly) NSString *shortAliases;

// 将枚举值存储到connTypes中，用来代表当前设备有哪些连接方式
@property (nonatomic, assign) NSUInteger connTypes;
//用来标志当前设备的连接方式
@property (nonatomic,assign) ConnType connType;

//firmwareConfigs以FirmwareType既固件类型的值作为key，以当前固件类型可以升级的连接方式connTypes作为值，其中firmwareConfigs里边对应的FirmwareType包含的连接方式可以有多种
@property (nonatomic, strong) NSDictionary<NSNumber *,NSNumber *> *firmwareConfigs;

//用来判断当前设备的连接方式
@property (nonatomic,assign,readonly) BOOL isBleConnType;
@property (nonatomic,assign,readonly) BOOL isApConnType;
@property (nonatomic,assign,readonly) BOOL isWifiConnType;
@property (nonatomic,assign,readonly) BOOL isApOrWifiConnType;

@property (nonatomic, strong) CBPeripheral *peripheral;
@property (nonatomic, strong) NSString *bluetoothName;
@property (nonatomic, strong) NSString *localName;
@property (nonatomic, strong) NSString *uuidIdentifier;
@property (nonatomic, assign) int rssi;//蓝牙信号

// ap 模式下 设备显示的名称为 ssid的名称
@property (nonatomic, strong) NSString *ssid;
// wifi 模式下  wifiName 为 udp包中的名称
@property (nonatomic, strong) NSString *wifiName;
// wifi 和 ap 共有属性 以及后期的06及后续机型都带mac
@property (nonatomic, strong) NSString *ip;
@property (nonatomic, strong) NSString *mac;
@property (nonatomic, assign) uint16_t port;
@property (nonatomic, assign) int state;

//电量 默认 -1 （还没获取设备电量时的初始值）
@property (nonatomic,assign) int batteryLevel;

@property (nonatomic,assign) int cycles;
@property (nonatomic,assign) float current_temperature;
@property (nonatomic,assign) int direction;
@property (nonatomic,assign) int distance;
@property (nonatomic,assign) int l_pix;
@property (nonatomic,assign) int oldDirection;
@property (nonatomic,assign) int p_pix;
@property (nonatomic,assign) int printer_head;
@property (nonatomic,strong) NSString *printer_head_id;
@property (nonatomic,assign) int repeat_time;
@property (nonatomic,assign) float temperature;//打印头温度
@property (nonatomic,strong) NSString *mcuName;
@property (nonatomic, assign, getter=isConnected) BOOL isConnected;//是否已连接
@property (nonatomic,assign) BOOL silentState;
@property (nonatomic,assign) BOOL autoPowerOffState;
@property (nonatomic,assign,readonly) BOOL isWifiReady;
@property (nonatomic,assign,readonly) BOOL isEligibleFirmwareTypeMCU;
@property (nonatomic,assign,readonly) BOOL isEligibleFirmwareTypeWiFi;

@property (nonatomic, strong) NSString *mcu_date;

@property (nonatomic, strong) NSString *mcuVersion;
/**设备型号*/
@property (nonatomic, strong) NSString *mcuModel;
/**用于请求更新包的机型*/
@property (nonatomic, strong) NSString *mcu_model;
/**mcu版本号*/
@property (nonatomic, strong) NSString *mcu_version;
/**硬件版本号*/
@property (nonatomic, strong) NSString *mcu_hw_version;
//MX-06_WIFI_HW10_V1.9.1
@property (nonatomic, strong) NSString *wifiVersion;
@property (nonatomic, strong) NSString *wifiModel;
@property (nonatomic, strong) NSString *wifi_model;
@property (nonatomic, strong) NSString *wifi_version;
@property (nonatomic, strong) NSString *wifi_hw_version;

/**禁用init方法*/
- (instancetype)init NS_UNAVAILABLE;
+ (instancetype)new NS_UNAVAILABLE;

- (instancetype)initDeviceWithPeripheral:(CBPeripheral *)peripheral localName:(nullable NSString *)localName mac:(nullable NSString *)mac connTypes:(NSUInteger)connTypes firmwareConfigs:(nonnull NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs aliases:(NSString *)aliases;

- (instancetype)initDeviceWithAp:(NSString *)ssid mac:(nullable NSString *)mac peripheral:(nullable CBPeripheral *)peripheral localName:(nullable NSString *)localName connTypes:(NSUInteger)connTypes firmwareConfigs:(nonnull NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs aliases:(nullable NSString *)aliases;

- (instancetype)initDeviceWithWifi:(NSString *)wifiName ip:(NSString *)ip mac:(NSString *)mac port:(uint16_t)port peripheral:(nullable CBPeripheral *)peripheral localName:(nullable NSString *)localName connTypes:(NSUInteger)connTypes firmwareConfigs:(nonnull NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs aliases:(nullable NSString *)aliases;

- (BOOL)containsConnType:(ConnType)connType;
- (BOOL)containsConnType:(NSUInteger)connTypes connType:(ConnType)connType;
- (void)addConnType:(ConnType)connType;
- (void)removeConnType:(ConnType)connType;

- (BOOL)containsFirmwareType:(FirmwareType)firmwareType;
- (BOOL)containsFirmwareType:(FirmwareType)firmwareType connType:(ConnType)connType;
- (BOOL)containsFirmwareTypeInFirmwareConfigs:(NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs firmwareType:(FirmwareType)firmwareType connType:(ConnType)connType;
- (NSUInteger)connTypesForFirmwareType:(FirmwareType)firmwareType;

- (NSString *)description;

@end

NS_ASSUME_NONNULL_END
