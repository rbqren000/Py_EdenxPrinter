//
//  Printer.m
//  BelonPrinter
//
//  Created by rbq on 2020/4/22.
//  Copyright © 2020 rbq. All rights reserved.
//

#import "Device.h"
#import "ParameterUtils.h"
#import "RBQLog.h"
#import "NSString+String.h"

#define defaultPort 35000
#define defaultHost @"192.168.0.10"

@implementation Device

- (instancetype)initDeviceWithPeripheral:(CBPeripheral *)peripheral localName:(nullable NSString *)localName mac:(nullable NSString *)mac connTypes:(NSUInteger)connTypes firmwareConfigs:(nonnull NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs aliases:(NSString *)aliases
{
    self = [super init];
    if (self) {
        _connType = ConnTypeBLE;
        _peripheral = peripheral;
        _bluetoothName = peripheral.name;
        _uuidIdentifier = peripheral ? peripheral.identifier.UUIDString : nil;
        _localName = localName;
        _mac = mac;
        _connTypes = connTypes;
        _firmwareConfigs = firmwareConfigs;
        _aliases = aliases;
        _batteryLevel = -1;
        _printer_head = defaultPrinterHead;
        _l_pix = defaultLandscapePix;
        _p_pix = defaultPortraitPix;
        _distance = defaultDistance;
        _cycles = defaultCyclesTime;
        _repeat_time = defaultRepeatTime;
        _direction = defaultDirection;
        _oldDirection = defaultDirection;
        _mcuVersion = defaultMcuVersion;
        _isConnected = NO;
    }
    return self;
}

- (instancetype)initDeviceWithAp:(NSString *)ssid mac:(nullable NSString *)mac peripheral:(nullable CBPeripheral *)peripheral localName:(nullable NSString *)localName connTypes:(NSUInteger)connTypes firmwareConfigs:(nonnull NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs aliases:(nullable NSString *)aliases
{
    self = [super init];
    if (self) {
        // ap核心参数
        _ssid = ssid;
        _connType = ConnTypeAP;
        _ip = defaultHost;
        _port = defaultPort;
        //可选的蓝牙参数
        _mac = mac;
        _peripheral = peripheral;
        _bluetoothName =  peripheral ? peripheral.name : nil;
        _uuidIdentifier = peripheral ? peripheral.identifier.UUIDString : nil;
        _localName = localName;
        _aliases = aliases;
        _batteryLevel = -1;
        _connTypes = connTypes;
        _firmwareConfigs = firmwareConfigs;
        //基本配置信息
        _printer_head = defaultPrinterHead;
        _l_pix = defaultLandscapePix;
        _p_pix = defaultPortraitPix;
        _distance = defaultDistance;
        _cycles = defaultCyclesTime;
        _repeat_time = defaultRepeatTime;
        _direction = defaultDirection;
        _oldDirection = defaultDirection;
        _mcuVersion = defaultMcuVersion;
        _isConnected = NO;
    }
    return self;
}

- (instancetype)initDeviceWithWifi:(NSString *)wifiName ip:(NSString *)ip mac:(NSString *)mac port:(uint16_t)port peripheral:(nullable CBPeripheral *)peripheral localName:(nullable NSString *)localName connTypes:(NSUInteger)connTypes firmwareConfigs:(nonnull NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs aliases:(nullable NSString *)aliases
{
    self = [super init];
    if (self) {
        //wifi 核心信息
        _wifiName = wifiName;
        _connType = ConnTypeWiFi;
        _ip = ip;
        _mac = mac;
        _port = port;
        //可选值，蓝牙相关信息
        _peripheral = peripheral;
        _bluetoothName =  peripheral ? peripheral.name : nil;
        _uuidIdentifier = peripheral ? peripheral.identifier.UUIDString : nil;
        _localName = localName;
        _connTypes = connTypes;
        _firmwareConfigs = firmwareConfigs;
        _aliases = aliases;
        //基本配置信息
        _batteryLevel = -1;
        _printer_head = defaultPrinterHead;
        _l_pix = defaultLandscapePix;
        _p_pix = defaultPortraitPix;
        _distance = defaultDistance;
        _cycles = defaultCyclesTime;
        _repeat_time = defaultRepeatTime;
        _direction = defaultDirection;
        _oldDirection = defaultDirection;
        _mcuVersion = defaultMcuVersion;
        _isConnected = NO;
    }
    return self;
}

//- (NSString *)name {
//    return self.isBleConnType ? (self.bluetoothName ? : self.localName ? : @"") :
//           self.isApConnType ? self.ssid :
//           self.isWifiConnType ? self.wifiName :
//           @"";
//}

- (NSString *)name {
    if (self.isBleConnType) {
        return self.bluetoothName ? self.bluetoothName : (self.localName ? self.localName : @"");
    } else if (self.isApConnType) {
        return self.ssid;
    } else if (self.isWifiConnType) {
        return self.wifiName;
    } else {
        return @"";
    }
}

- (NSString *)shortAliases{
    if(!_aliases){
        return @"";
    }
    NSArray<NSString *> *components = [_aliases componentsSeparatedByString:@"_"];
    return components.firstObject;
}

- (void)setPeripheral:(CBPeripheral *)peripheral{
    _peripheral = peripheral;
    _bluetoothName =  peripheral ? peripheral.name : nil;
    _uuidIdentifier = peripheral ? peripheral.identifier.UUIDString : nil;
}

- (NSString *)mcuModel {
    if (!_mcuVersion) {
        return @"";
    }
    RBQLog3(@"版本号 mcu_version:%@", _mcuVersion);
    NSString *uppercasedVersion = _mcuVersion.uppercaseString;
    // 检查版本是否符合INKSI格式
    if ([uppercasedVersion containsString:@"_"] && [uppercasedVersion containsString:@"INKSI"]) {
        // 类似于 MX-06_MCU_HW10_V1.9.9 格式处理  inksi-01 MX-06_MCU_BX1.0_V1.0
        NSArray<NSString *> *versionComponents = [_mcuVersion componentsSeparatedByString:@"_"];
        for (NSString *component in versionComponents) {
            if ([component.uppercaseString containsString:@"INKSI"]) {
                return component;
            }
        }
        // 默认返回INKSI-01，如果找不到特定格式的INKSI字符串
        return @"INKSI-01";
    }

    // 检查版本是否符合MX格式
    if ([uppercasedVersion containsString:@"_"] && [uppercasedVersion containsString:@"MX"]) {
        NSArray<NSString *> *versionComponents = [_mcuVersion componentsSeparatedByString:@"_"];
        for (NSString *component in versionComponents) {
            if ([component.uppercaseString containsString:@"MX"]) {
                return component;
            }
        }
        // 默认返回MX-06
        return @"MX-06";
    }
    // "1.8.6.210817_pul_release" 老版本version格式
    return @"MX-02";
}

- (NSString *)mcu_model{
    
    //        hasprefix 不代表前几位，是表示如果前几位包含字符就会返回成功。
    //        用substringWithRange:NSMakeRange(0, 1)] isEqualToString:
    //        精确的比较两个字符串的文字
    if (!_mcuVersion) return @"";
    RBQLog3(@"版本号 mcu_version:%@",_mcuVersion);
    // MX-06_MCU_HW10_V1.9.9(作废)
    //MX-06_MCU_HW10_AR1.0_V2.0
    NSArray<NSString *> *vsArr = [_mcuVersion componentsSeparatedByString:@"_"];
    if (vsArr&&vsArr.count==4) {
        return [NSString stringWithFormat:@"%@",vsArr[2]];
    }
    if (vsArr&&vsArr.count==5) {
        return vsArr[3];
    }
    // "1.8.6.210817_pul_release" 老版本version格式
    return @"MX-02";
}

- (NSString *)mcu_version{
    
    if (!_mcuVersion) return @"";
    RBQLog3(@"版本号 mcu_version:%@",_mcuVersion);
    
    // MX-06_MCU_HW10_V1.9.9(作废)
    //MX-06_MCU_HW10_AR1.0_V2.0
    NSArray<NSString *> *vsArr = [_mcuVersion componentsSeparatedByString:@"_"];
    if (vsArr&&vsArr.count==4) {
        return vsArr[3];
    }
    if (vsArr&&vsArr.count==5) {
        return vsArr[4];
    }
    // "1.8.6.210817_pul_release" 老版本version格式
    if(vsArr&&vsArr.count>0){
        return vsArr[0];
    }
    return _mcuVersion;
}

- (NSString *)mcu_hw_version{
    
    if (!_mcuVersion) return @"";
    RBQLog3(@"版本号 mcu_version:%@",_mcuVersion);
    
    // MX-06_MCU_HW10_V1.9.9(作废)
    //MX-06_MCU_HW10_AR1.0_V2.0
    NSArray<NSString *> *vsArr = [_mcuVersion componentsSeparatedByString:@"_"];
    if (vsArr&&vsArr.count==4) {
        return vsArr[2];
    }
    if (vsArr&&vsArr.count==5) {
        return vsArr[3];
    }
    // "1.8.6.210817_pul_release" 老版本version格式
    if(vsArr&&vsArr.count>0){
        return vsArr[0];
    }
    return _mcuVersion;
}

- (NSString *)wifiModel{
    if (!_wifiVersion) return @"";
    RBQLog3(@"版本号 wifiVersion:%@",_wifiVersion);
    
    // MX-06_WIFI_HW10_V1.9.9(作废)
    //MX-06_WIFI_HW10_AR1.0_V2.0
    //INKSI-01_WIFI_BX1.0_V2.15
    NSArray<NSString *> *vsArr = [_wifiVersion componentsSeparatedByString:@"_"];
    if (vsArr&&vsArr.count==4) {
        return [NSString stringWithFormat:@"%@_%@",vsArr[0],vsArr[2]];
    }
    if (vsArr&&vsArr.count==5) {
        return vsArr[3];
    }
    // "1.8.6.210817_pul_release" 老版本version格式
    return @"MX-02";
}

- (NSString *)wifi_model{
    //        hasprefix 不代表前几位，是表示如果前几位包含字符就会返回成功。
    //        用substringWithRange:NSMakeRange(0, 1)] isEqualToString:
    //        精确的比较两个字符串的文字
    
    if (!_wifiVersion) return @"";
    RBQLog3(@"版本号 wifiVersion:%@",_wifiVersion);
    
    // MX-06_WIFI_HW10_V1.9.9(作废)
    //MX-06_WIFI_HW10_AR1.0_V2.0
    NSArray<NSString *> *vsArr = [_wifiVersion componentsSeparatedByString:@"_"];
    if (vsArr&&vsArr.count==4) {
        return [NSString stringWithFormat:@"%@",vsArr[2]];
    }
    if (vsArr&&vsArr.count==5) {
        return vsArr[3];
    }
    // "1.8.6.210817_pul_release" 老版本version格式
    return @"MX-02";
}
- (NSString *)wifi_version {
    
    if (!_wifiVersion) return @"";
    RBQLog3(@"版本号 wifiVersion:%@",_wifiVersion);
    
    // MX-06_WIFI_HW10_V1.9.9(作废)
    //MX-06_WIFI_HW10_AR1.0_V2.0
    // INKSI-01_WIFI_BX1.0_V2.18
    NSArray<NSString *> *vsArr = [_wifiVersion componentsSeparatedByString:@"_"];
    if (vsArr&&vsArr.count==4) {
        return vsArr[3];
    }
    if (vsArr&&vsArr.count==5) {
        return vsArr[4];
    }
    // "1.8.6.210817_pul_release" 老版本version格式
    if(vsArr&&vsArr.count>0){
        return vsArr[0];
    }
    return _wifiVersion;
}
- (NSString *)wifi_hw_version {
    if (!_wifiVersion) return @"";
    RBQLog3(@"版本号 wifiVersion:%@",_wifiVersion);
    
    // MX-06_WIFI_HW10_V1.9.9(作废)
    //MX-06_WIFI_HW10_AR1.0_V2.0
    NSArray<NSString *> *vsArr = [_wifiVersion componentsSeparatedByString:@"_"];
    if (vsArr&&vsArr.count==4) {
        return vsArr[2];
    }
    if (vsArr&&vsArr.count==5) {
        return vsArr[3];
    }
    // "1.8.6.210817_pul_release" 老版本version格式
    if(vsArr&&vsArr.count>0){
        return vsArr[0];
    }
    return _wifiVersion;
}

- (BOOL)isBleConnType {
    return self.peripheral && self.connType == ConnTypeBLE;
}

- (BOOL)isApConnType {
    return self.connType == ConnTypeAP;
}

- (BOOL)isWifiConnType {
    return self.connType == ConnTypeWiFi;
}

- (BOOL)isApOrWifiConnType {
    return self.connType == ConnTypeWiFi || self.connType == ConnTypeAP;
}

- (BOOL)containsConnType:(ConnType)connType {
    return (self.connTypes & connType) != 0;
}

- (BOOL)containsConnType:(NSUInteger)connTypes connType:(ConnType)connType {
    return (connTypes & connType) != 0;
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

- (BOOL)containsFirmwareType:(FirmwareType)firmwareType connType:(ConnType)connType {
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

- (BOOL)containsFirmwareTypeInFirmwareConfigs:(NSDictionary<NSNumber *,NSNumber *> *)firmwareConfigs firmwareType:(FirmwareType)firmwareType connType:(ConnType)connType {
    if (!firmwareConfigs) {
        return NO;
    }
    NSNumber *connTypesNumber = firmwareConfigs[@(firmwareType)];
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

-(BOOL)isEligibleFirmwareTypeMCU{
    return [self containsFirmwareType:FirmwareTypeMCU connType:self.connType];
}

-(BOOL)isEligibleFirmwareTypeWiFi{
    return [self containsFirmwareType:FirmwareTypeWiFi connType:self.connType];
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
    if (![other isKindOfClass:[Device class]]) {
        return NO;
    }
    Device *u = (Device *)other;
    
    return [self.mac isEqualToString:u.mac]||[self.ip isEqualToString:u.ip]||(self.peripheral&&u.peripheral&&[self.peripheral isEqual:u.peripheral]);
}

- (NSString *)description {
    return [NSString stringWithFormat:@"<Device: %p, name: %@, aliases: %@, shortAliases: %@, connTypes: %lu, connType: %lu, isAP: %@, isBle: %@, isWifi: %@, isNetWork: %@, peripheral: %@, bluetoothName: %@, localName: %@, uuidIdentifier: %@, rssi: %d, ssid: %@, wifiName: %@, ip: %@, mac: %@, port: %u, state: %d>",
            self,
            self.name,
            self.aliases,
            self.shortAliases,
            (unsigned long)self.connTypes,
            (unsigned long)self.connType,
            self.isApConnType ? @"YES" : @"NO",
            self.isBleConnType ? @"YES" : @"NO",
            self.isWifiConnType ? @"YES" : @"NO",
            self.isApOrWifiConnType ? @"YES" : @"NO",
            self.peripheral,
            self.bluetoothName,
            self.localName,
            self.uuidIdentifier,
            self.rssi,
            self.ssid,
            self.wifiName,
            self.ip,
            self.mac,
            self.port,
            self.state];
}


@end
