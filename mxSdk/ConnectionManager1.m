//
//  ConnectionManager1.m
//  Inksi
//
//  Created by rbq on 2024/11/1.
//

#import "ConnectionManager1.h"

@implementation ConnectionManager1

- (instancetype)initWithConnectionType:(ConnectionType)type {
    self = [super init];
    if (self) {
        _connectionStrategy = [ConnectionFactory connectionStrategyForType:type];
    }
    return self;
}

- (void)connect {
    [self.connectionStrategy connect];
}

- (void)disConnect {
    [self.connectionStrategy disConnect];
}

- (void)sendData:(NSData *)data {
    [self.connectionStrategy sendData:data];
}

- (void)receiveData:(NSData *)data {
    [self.connectionStrategy receiveData:data];
}

// 处理 BLE 特有行为
- (void)scanForDevicesIfPossible {
    if ([self.connectionStrategy conformsToProtocol:@protocol(BLEConnectionStrategy)]) {
        id<BLEConnectionStrategy> bleStrategy = (id<BLEConnectionStrategy>)self.connectionStrategy;
        [bleStrategy scanForDevices];
    } else {
        NSLog(@"Current connection does not support scanning for devices.");
    }
}

- (void)stopScanningIfPossible {
    if ([self.connectionStrategy conformsToProtocol:@protocol(BLEConnectionStrategy)]) {
        id<BLEConnectionStrategy> bleStrategy = (id<BLEConnectionStrategy>)self.connectionStrategy;
        [bleStrategy stopScanning];
    } else {
        NSLog(@"Current connection does not support stopping scanning.");
    }
}

// 处理 TCP 特有行为
- (void)startListeningForUDPIfPossible {
    if ([self.connectionStrategy conformsToProtocol:@protocol(TCPConnectionStrategy)]) {
        id<TCPConnectionStrategy> tcpStrategy = (id<TCPConnectionStrategy>)self.connectionStrategy;
        [tcpStrategy startListeningUdp];
    } else {
        NSLog(@"Current connection does not support UDP listening.");
    }
}

- (void)stopListeningForUDPIfPossible {
    if ([self.connectionStrategy conformsToProtocol:@protocol(TCPConnectionStrategy)]) {
        id<TCPConnectionStrategy> tcpStrategy = (id<TCPConnectionStrategy>)self.connectionStrategy;
        [tcpStrategy stopListeningUdp];
    } else {
        NSLog(@"Current connection does not support stopping UDP listening.");
    }
}

@end
