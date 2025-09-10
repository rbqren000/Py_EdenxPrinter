//
//  ConnModel.m
//  Inksi
//
//  Created by rbq on 2024/7/31.
//

#import "ConnModel.h"
#import "NSString+String.h"

@implementation ConnModel

- (instancetype)initConnModel:(nonnull CBPeripheral *)peripheral localName:(NSString *)localName connTypes:(NSUInteger)connTypes firmwareConfigs:(nonnull NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs mac:(nullable NSString *)mac aliases:(nullable NSString *)aliases
{
    return [self initConnModel:peripheral localName:localName connTypes:connTypes firmwareConfigs:firmwareConfigs mac:mac aliases:aliases state:-1];
}

- (instancetype)initConnModel:(nonnull CBPeripheral *)peripheral localName:(NSString *)localName connTypes:(NSUInteger)connTypes firmwareConfigs:(nonnull NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs mac:(nullable NSString *)mac aliases:(nullable NSString *)aliases state:(int)state
{
    self = [super init];
    if (self) {
        _peripheral = peripheral;
        _bluetoothName = peripheral.name;
        _uuidIdentifier = peripheral.identifier.UUIDString;
        _localName = localName;
        _connTypes = connTypes;
        _firmwareConfigs = firmwareConfigs;
        _mac = mac;
        _aliases = aliases;
        _state = state;
        _wifiName = nil;
        _ip = nil;
        _port = 0;
    }
    return self;
}

- (instancetype)initConnModel:(nonnull CBPeripheral *)peripheral localName:(NSString *)localName connTypes:(NSUInteger)connTypes firmwareConfigs:(nonnull NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs mac:(nullable NSString *)mac aliases:(nullable NSString *)aliases wifiName:(NSString *)wifiName ip:(NSString *)ip port:(uint16_t)port{
    self = [super init];
    if (self) {
        _peripheral = peripheral;
        _bluetoothName = peripheral.name;
        _uuidIdentifier = peripheral.identifier.UUIDString;
        _localName = localName;
        _connTypes = connTypes;
        _firmwareConfigs = firmwareConfigs;
        _mac = mac;
        _aliases = aliases;
        _state = -1;
        _wifiName = wifiName;
        _ip = ip;
        _port = port;
    }
    return self;
}

- (instancetype)initConnModel:(nonnull CBPeripheral *)peripheral localName:(NSString *)localName connTypes:(NSUInteger)connTypes firmwareConfigs:(nonnull NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs mac:(nullable NSString *)mac aliases:(nullable NSString *)aliases state:(int)state wifiName:(NSString *)wifiName ip:(NSString *)ip port:(uint16_t)port{
    self = [super init];
    if (self) {
        _peripheral = peripheral;
        _bluetoothName = peripheral.name;
        _uuidIdentifier = peripheral.identifier.UUIDString;
        _localName = localName;
        _connTypes = connTypes;
        _firmwareConfigs = firmwareConfigs;
        _mac = mac;
        _aliases = aliases;
        _state = state;
        _wifiName = wifiName;
        _ip = ip;
        _port = port;
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

- (BOOL)isWifiReady{
    return [NSString isBlankString:self.ip] && self.port != 0;
}

- (BOOL)isEqual:(id)other{
    if (other == self) {
        return YES;
    }
    if (!other) {
        return NO;
    }
    if (![other isKindOfClass:[ConnModel class]]) {
        return NO;
    }
    ConnModel *model = (ConnModel *)other;
    return (self.peripheral && [self.peripheral isEqual:model.peripheral])
    ||(self.mac && [self.mac isEqualToString:model.mac]);
}

- (NSString *)toString {
    return [NSString stringWithFormat:@"<ConnModel: %p, aliases: %@, connTypes: %lu, peripheral: %@, mac: %@, bluetoothName: %@, uuidIdentifier: %@, localName: %@, state: %d, wifiName: %@, ip: %@, port: %u>",
            self,
            self.aliases,
            (unsigned long)self.connTypes,
            self.peripheral,
            self.mac,
            self.bluetoothName,
            self.uuidIdentifier,
            self.localName,
            self.state,
            self.wifiName,
            self.ip,
            self.port];
}


@end
