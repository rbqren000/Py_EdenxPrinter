//
//  ConnectionFactory.m
//  Inksi
//
//  Created by rbq on 2024/11/1.
//

#import "ConnectionFactory.h"

@implementation ConnectionFactory

+ (id<ConnectionStrategy>)connectionStrategyForType:(ConnectionType)type {
    switch (type) {
        case ConnectionTypeBLE:
            return [[BLEConnection alloc] init];
        case ConnectionTypeTCP:
            return [[TCPConnection alloc] init];
        default:
            return nil;
    }
}

@end
