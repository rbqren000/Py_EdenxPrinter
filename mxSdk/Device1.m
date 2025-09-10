//
//  Device1.m
//  Inksi
//
//  Created by rbq on 2024/11/1.
//

#import "Device1.h"
#import "ConnectionFactory.h"

@implementation Device1

- (instancetype)initWithDeviceID:(NSString *)deviceID
                      deviceName:(NSString *)deviceName
                 connectionType:(DeviceConnectionType)connectionType {
    self = [super init];
    if (self) {
        _deviceID = deviceID;
        _deviceName = deviceName;
        _connectionType = connectionType;
        
        // 根据设备的连接类型创建连接策略
        if (connectionType & DeviceConnectionTypeBLE) {
            _bleConnectionStrategy = [ConnectionFactory connectionStrategyForType:ConnectionTypeBLE];
        }
        if (connectionType & DeviceConnectionTypeTCP) {
            _tcpConnectionStrategy = [ConnectionFactory connectionStrategyForType:ConnectionTypeTCP];
        }
    }
    return self;
}

- (void)startConnection {
    if (self.bleConnectionStrategy) {
        [self.bleConnectionStrategy connect];
    }
    if (self.tcpConnectionStrategy) {
        [self.tcpConnectionStrategy connect];
    }
}

- (void)stopConnection {
    if (self.bleConnectionStrategy) {
        [self.bleConnectionStrategy disConnect];
    }
    if (self.tcpConnectionStrategy) {
        [self.tcpConnectionStrategy disConnect];
    }
}

- (void)sendData:(NSData *)data {
    if (self.bleConnectionStrategy) {
        [self.bleConnectionStrategy sendData:data];
    }
    if (self.tcpConnectionStrategy) {
        [self.tcpConnectionStrategy sendData:data];
    }
}

- (void)receiveData:(NSData *)data {
    if (self.bleConnectionStrategy) {
        [self.bleConnectionStrategy receiveData:data];
    }
    if (self.tcpConnectionStrategy) {
        [self.tcpConnectionStrategy receiveData:data];
    }
}

// BLE 特有的方法
- (void)scanForDevicesIfPossible {
    if (self.bleConnectionStrategy && [self.bleConnectionStrategy conformsToProtocol:@protocol(BLEConnectionStrategy)]) {
        id<BLEConnectionStrategy> bleStrategy = (id<BLEConnectionStrategy>)self.bleConnectionStrategy;
        [bleStrategy scanForDevices];
    } else {
        NSLog(@"Current device does not support BLE scanning.");
    }
}

- (void)stopScanningIfPossible {
    if (self.bleConnectionStrategy && [self.bleConnectionStrategy conformsToProtocol:@protocol(BLEConnectionStrategy)]) {
        id<BLEConnectionStrategy> bleStrategy = (id<BLEConnectionStrategy>)self.bleConnectionStrategy;
        [bleStrategy stopScanning];
    } else {
        NSLog(@"Current device does not support stopping BLE scanning.");
    }
}

// TCP 特有的方法
- (void)startListeningForUDPIfPossible {
    if (self.tcpConnectionStrategy && [self.tcpConnectionStrategy conformsToProtocol:@protocol(TCPConnectionStrategy)]) {
        id<TCPConnectionStrategy> tcpStrategy = (id<TCPConnectionStrategy>)self.tcpConnectionStrategy;
        [tcpStrategy startListeningUdp];
    } else {
        NSLog(@"Current device does not support UDP listening.");
    }
}

- (void)stopListeningForUDPIfPossible {
    if (self.tcpConnectionStrategy && [self.tcpConnectionStrategy conformsToProtocol:@protocol(TCPConnectionStrategy)]) {
        id<TCPConnectionStrategy> tcpStrategy = (id<TCPConnectionStrategy>)self.tcpConnectionStrategy;
        [tcpStrategy stopListeningUdp];
    } else {
        NSLog(@"Current device does not support stopping UDP listening.");
    }
}


@end
