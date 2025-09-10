//
//  Device1.h
//  Inksi
//
//  Created by rbq on 2024/11/1.
//

#import <UIKit/UIKit.h>
#import "ConnectionStrategy.h"

typedef NS_ENUM(NSUInteger, DeviceConnectionType) {
    DeviceConnectionTypeNone     = 0,
    DeviceConnectionTypeBLE      = 1 << 0,
    DeviceConnectionTypeTCP      = 1 << 1,
    DeviceConnectionTypeBoth     = DeviceConnectionTypeBLE | DeviceConnectionTypeTCP
};


NS_ASSUME_NONNULL_BEGIN

@interface Device1 : NSObject

@property (nonatomic, strong) NSString *deviceID;
@property (nonatomic, strong) NSString *deviceName;
@property (nonatomic, assign) DeviceConnectionType connectionType;

// 连接策略属性
@property (nonatomic, strong, nullable) id<ConnectionStrategy> bleConnectionStrategy;
@property (nonatomic, strong, nullable) id<ConnectionStrategy> tcpConnectionStrategy;

// 初始化方法
- (instancetype)initWithDeviceID:(NSString *)deviceID
                      deviceName:(NSString *)deviceName
                 connectionType:(DeviceConnectionType)connectionType;

// 管理连接的方法
- (void)startConnection;
- (void)stopConnection;
- (void)sendData:(NSData *)data;
- (void)receiveData:(NSData *)data;

// BLE 特有的方法
- (void)scanForDevicesIfPossible;
- (void)stopScanningIfPossible;

// TCP 特有的方法
- (void)startListeningForUDPIfPossible;
- (void)stopListeningForUDPIfPossible;

@end

NS_ASSUME_NONNULL_END
