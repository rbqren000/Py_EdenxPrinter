//
//  DistributionNetworkDevice.m
//  Inksi
//
//  Created by rbq on 2022/4/15.
//

#import "DistNetDevice.h"

@implementation DistNetDevice

- (instancetype)initDistNetDevice:(nonnull CBPeripheral *)peripheral localName:(NSString *)localName mac:(NSString *)mac state:(int)state connTypes:(NSUInteger)connTypes firmwareConfigs:(nonnull NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs aliases:(NSString *)aliases
{
    self = [super init];
    if (self) {
        _peripheral = peripheral;
        _bluetoothName = peripheral.name;
        _localName = localName;
        _mac = mac;
        _state = state;
        _connTypes = connTypes;
        _firmwareConfigs = firmwareConfigs;
        _aliases = aliases;
    }
    return self;
}

- (BOOL)containsConnType:(ConnType)connType {
    return (self.connTypes & connType) != 0;
}

- (void)addConnType:(ConnType)connType {
    self.connTypes |= connType;
}

- (void)removeConnType:(ConnType)connType {
    self.connTypes &= ~connType;
}

- (BOOL)containsFirmwareType:(FirmwareType)firmwareType {
    if (!self.firmwareConfigs) {
        return NO;
    }
    return self.firmwareConfigs[@(firmwareType)] != nil;
}

- (BOOL)containsFirmwareTypeWithConnType:(FirmwareType)firmwareType connType:(ConnType)connType {
    if (!self.firmwareConfigs) {
        return NO;
    }
    NSNumber *connTypesNumber = self.firmwareConfigs[@(firmwareType)];
    if (!connTypesNumber) {
        return NO;
    }
    NSUInteger connTypes = connTypesNumber.unsignedIntegerValue;
    return (connTypes & connType) != 0;
}

- (NSUInteger)connTypesForFirmwareType:(FirmwareType)firmwareType {
    if (!self.firmwareConfigs) {
        return 0;
    }
    NSNumber *connTypesNumber = self.firmwareConfigs[@(firmwareType)];
    return connTypesNumber ? connTypesNumber.unsignedIntegerValue : 0;
}

- (BOOL)isEqual:(id)other
{
    if (other == self) {
        return YES;
    }
    if (!other) {
        return NO;
    }
    if (![other isKindOfClass:[DistNetDevice class]]) {
        return NO;
    }
    DistNetDevice *u = (DistNetDevice *)other;
    if ([u.mac isEqualToString:self.mac]) {
        return YES;
    }
    return NO;
}

@end
