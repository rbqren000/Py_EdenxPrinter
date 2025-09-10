//
//  DistributionNetworkDevice.h
//  Inksi
//
//  Created by rbq on 2022/4/15.
//

#import <UIKit/UIKit.h>
#import <CoreBluetooth/CoreBluetooth.h>
#import "ConnType.h"
#import "FirmwareType.h"

NS_ASSUME_NONNULL_BEGIN

@interface DistNetDevice : NSObject

//设备名称或者叫作别名，因为和设备本身的名字并不对应，UI设计的时候又实用了别的名称
@property (nonatomic, strong, readonly) NSString *aliases;

// 将枚举值存储到数组中，用来代表当前设备有哪些连接方式
@property (nonatomic, assign) NSUInteger connTypes;

//firmwareConfigs以FirmwareType既固件类型的值作为key，以当前固件类型可以升级的连接方式connTypes作为值，其中firmwareConfigs里边对应的FirmwareType包含的连接方式可以有多种
@property (nonatomic, strong) NSDictionary<NSNumber *,NSNumber *> *firmwareConfigs;

@property (nonatomic, strong, readonly) CBPeripheral *peripheral;
@property (nonatomic, strong, readonly) NSString *mac;
@property (nonatomic, strong, readonly) NSString *bluetoothName;
@property (nonatomic, strong, readonly) NSString *localName;
@property (nonatomic, assign, readonly) BOOL state;//配网状态

- (instancetype)init NS_UNAVAILABLE;
+ (instancetype)new NS_UNAVAILABLE;

- (instancetype)initDistNetDevice:(nonnull CBPeripheral *)peripheral localName:(NSString *)localName mac:(NSString *)mac state:(int)state connTypes:(NSUInteger)connTypes firmwareConfigs:(nonnull NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs aliases:(NSString *)aliases;

- (BOOL)containsConnType:(ConnType)connType;
- (void)addConnType:(ConnType)connType;
- (void)removeConnType:(ConnType)connType;

@end

NS_ASSUME_NONNULL_END
