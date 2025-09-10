//
//  ConnModel.h
//  Inksi
//
//  Created by rbq on 2024/7/31.
//

#import <UIKit/UIKit.h>
#import <CoreBluetooth/CoreBluetooth.h>
#import "ConnType.h"
#import "FirmwareType.h"

NS_ASSUME_NONNULL_BEGIN
/**
 * 扫描BLE设备模型
 */
@interface ConnModel : NSObject

//设备名称或者叫作别名，因为和设备本身的名字并不对应，UI设计的时候又实用了别的名称
@property (nonatomic, strong) NSString *aliases;

// 将枚举值存储到connTypes中，用来代表当前设备有哪些连接方式
@property (nonatomic, assign) NSUInteger connTypes;

//firmwareConfigs以FirmwareType既固件类型的值作为key，以当前固件类型可以升级的连接方式connTypes作为值，其中firmwareConfigs里边对应的FirmwareType包含的连接方式可以有多种
@property (nonatomic, strong) NSDictionary<NSNumber *,NSNumber *> *firmwareConfigs;

@property (nonatomic, strong) CBPeripheral *peripheral;
@property (nonatomic, strong, nullable) NSString *mac;
@property (nonatomic, strong, readonly) NSString *bluetoothName;
@property (nonatomic, strong) NSString *uuidIdentifier;
@property (nonatomic, strong, readonly) NSString *localName;
@property (nonatomic, assign) int state;

@property (nonatomic, strong) NSString *wifiName;
@property (nonatomic, strong) NSString *ip;
@property (nonatomic, assign) uint16_t port;

@property (nonatomic,assign,readonly) BOOL isWifiReady;

- (instancetype)init NS_UNAVAILABLE;
+ (instancetype)new NS_UNAVAILABLE;

- (instancetype)initConnModel:(nonnull CBPeripheral *)peripheral localName:(NSString *)localName connTypes:(NSUInteger)connTypes firmwareConfigs:(nonnull NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs mac:(nullable NSString *)mac aliases:(nullable NSString *)aliases;

- (instancetype)initConnModel:(nonnull CBPeripheral *)peripheral localName:(NSString *)localName connTypes:(NSUInteger)connTypes firmwareConfigs:(nonnull NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs mac:(nullable NSString *)mac aliases:(nullable NSString *)aliases state:(int)state;

- (instancetype)initConnModel:(nonnull CBPeripheral *)peripheral localName:(NSString *)localName connTypes:(NSUInteger)connTypes firmwareConfigs:(nonnull NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs mac:(nullable NSString *)mac aliases:(nullable NSString *)aliases wifiName:(NSString *)wifiName ip:(NSString *)ip port:(uint16_t)port;

- (instancetype)initConnModel:(nonnull CBPeripheral *)peripheral localName:(NSString *)localName connTypes:(NSUInteger)connTypes firmwareConfigs:(nonnull NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs mac:(nullable NSString *)mac aliases:(nullable NSString *)aliases state:(int)state wifiName:(NSString *)wifiName ip:(NSString *)ip port:(uint16_t)port;

- (BOOL)containsConnType:(ConnType)connType;
- (void)addConnType:(ConnType)connType;
- (void)removeConnType:(ConnType)connType;

- (BOOL)containsFirmwareType:(FirmwareType)firmwareType;
- (BOOL)containsFirmwareTypeWithConnType:(FirmwareType)firmwareType connType:(ConnType)connType;
- (NSUInteger)connTypesForFirmwareType:(FirmwareType)firmwareType;

- (NSString *)toString;

@end

NS_ASSUME_NONNULL_END
