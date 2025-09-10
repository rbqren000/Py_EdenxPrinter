//
//  ConnectionManager1.h
//  Inksi
//
//  Created by rbq on 2024/11/1.
//

#import <UIKit/UIKit.h>
#import "ConnectionStrategy.h"
#import "ConnectionFactory.h"

NS_ASSUME_NONNULL_BEGIN

@interface ConnectionManager1 : NSObject

@property (nonatomic, strong) id<ConnectionStrategy> connectionStrategy;

- (instancetype)initWithConnectionType:(ConnectionType)type;
- (void)connect;
- (void)disConnect;
- (void)sendData:(NSData *)data;
- (void)receiveData:(NSData *)data;

// 处理 BLE 特有行为
- (void)scanForDevicesIfPossible;
- (void)stopScanningIfPossible;

// 处理 TCP 特有行为
- (void)startListeningForUDPIfPossible;
- (void)stopListeningForUDPIfPossible;

@end

NS_ASSUME_NONNULL_END
