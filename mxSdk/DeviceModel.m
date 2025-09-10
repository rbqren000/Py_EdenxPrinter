//
//  DeviceModel.m
//  Inksi
//
//  Created by rbq on 2024/12/10.
//

#import "DeviceModel.h"

@implementation DeviceModel

- (instancetype)initWithDeviceModel:(NSInteger)deviceType aliases:(NSString *)aliases deviceModel:(nullable NSString *)deviceModel{
    self = [super init];
    if (self) {
        _deviceType = deviceType;
        _aliases = aliases;
        _deviceModel = deviceModel;
    }
    return self;
}

- (NSString *)shortAliases {
    if (!_aliases) {
        return @"";
    }
    NSArray<NSString *> *components = [_aliases componentsSeparatedByString:@"_"];
    return components.firstObject ?: @"";
}

+ (instancetype)createMX02:(NSString *)last4MacStr {
    NSString *aliases = [NSString stringWithFormat:@"%@_%@", MX_02, last4MacStr];
    return [[self alloc] initWithDeviceModel:MX_02_type aliases:aliases deviceModel:NULL];
}

+ (instancetype)createMX06:(NSString *)last4MacStr {
    NSString *aliases = [NSString stringWithFormat:@"%@_%@", MX_06, last4MacStr];
    return [[self alloc] initWithDeviceModel:MX_06_type aliases:aliases deviceModel:NULL];
}

+ (instancetype)createINKSI01:(NSString *)last4MacStr deviceModel:(NSString *)deviceModel {
    NSString *aliases = [NSString stringWithFormat:@"%@_%@", INKSI_01, last4MacStr];
    return [[self alloc] initWithDeviceModel:INKSI_01_type aliases:aliases deviceModel:deviceModel];
}

@end

