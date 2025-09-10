//
//  ParameterStoreUtils.m
//  BelonPrinter
//
//  Created by rbq on 2021/7/23.
//  Copyright © 2021 rbq. All rights reserved.
//

#import "ParameterUtils.h"
#import "RBQLog.h"

static ParameterUtils *share=nil;

@implementation ParameterUtils

- (instancetype)init
{
    self = [super init];
    if (self) {
        [self config];
    }
    return self;
}

-(void)config{
    
}

+(ParameterUtils *)share
{
    
    static dispatch_once_t disOnce;
    dispatch_once(&disOnce, ^{
        
        share=[[ParameterUtils alloc] init];
        
    });
    
    return share;
}

+(id)allocWithZone:(struct _NSZone *)zone
{
    static dispatch_once_t disOnce;
    dispatch_once(&disOnce, ^{
        
        share = [super allocWithZone:zone];
        
    });
    
    return share;
}
// 为了严谨，也要重写copyWithZone 和 mutableCopyWithZone
-(id)copyWithZone:(NSZone *)zone
{
    return share;
}
-(id)mutableCopyWithZone:(NSZone *)zone
{
    return share;
}

+(BOOL)isNewDirection:(Device *) device{
    if (!device||![ParameterUtils mcuVersionNumberOver1_7_2:device]) {
        return NO;
    }
    int direction = [ParameterUtils direction:device];
    int oldDirection = [ParameterUtils oldDirection:device];
    RBQLog3(@"oldDirection:%d; direction:%d",oldDirection,direction);
    //重新生成数据，并提醒用户重新发送打印数据
    return oldDirection!=direction;
}

+(BOOL)flipHorizontally:(Device *) device{
    if (![ParameterUtils mcuVersionNumberOver1_7_2:device]){
        return NO;
    }
    int direction = [ParameterUtils direction:device];
    return direction != defaultDirection;
}

+(int)printerHead:(Device *) device{
    if (!device){
        return defaultPrinterHead;
    }
    return device.printer_head;
}

+(int)landscapePix:(Device *) device{
    if (!device) return defaultLandscapePix;
    return device.l_pix;
}

+(int)portraitPix:(Device *) device{
    if (!device) return defaultPortraitPix;
    return device.p_pix;
}

+(int)distance:(Device *) device{
    if (!device) return defaultDistance;
    return device.distance;
}

+(int)circulationTime:(Device *) device{
    if (!device||![ParameterUtils mcuVersionNumberOver1_7_2:device]) {
        return defaultCyclesTime;
    }
    return device.cycles;
}

+(int)repeatTime:(Device *) device{

    if (!device||![ParameterUtils mcuVersionNumberOver1_7_2:device]) {
        return defaultRepeatTime;
    }
    return device.repeat_time;
}

+(int)direction:(Device *) device{
    if (!device||![ParameterUtils mcuVersionNumberOver1_7_2:device]) {
        return defaultDirection;
    }
    return device.direction;
}

+(NSString *)directionText:(Device *) device{
    if (!device||![ParameterUtils mcuVersionNumberOver1_7_2:device]){
        return [NSString stringWithFormat:@"%d",defaultDirection];
    }
    int direction = device.direction;
    return [NSString stringWithFormat:@"%d",direction];
}

+(void)synchronizationOldDirection:(Device *) device{
    if (!device||![ParameterUtils mcuVersionNumberOver1_7_2:device]) return;
    device.oldDirection = [ParameterUtils direction:device];
}

+(int)oldDirection:(Device *) device{

    if (!device||![ParameterUtils mcuVersionNumberOver1_7_2:device]) {
        return defaultDirection;
    }
    return device.oldDirection;
}

+(BOOL)mcuVersionNumberOver1_7_2:(Device *) device{

    if (!device) return NO;
    NSString *mcu_version = device.mcuVersion;
    if (!mcu_version) return NO;
    RBQLog3(@"版本号 mcu_version:%@",mcu_version);
    if ([mcu_version containsString:@"_"]) {
        // MX-06_MCU_HW10_V1.9.9
//        hasprefix 不代表前几位，是表示如果前几位包含字符就会返回成功。
//        用substringWithRange:NSMakeRange(0, 1)] isEqualToString:
//        精确的比较两个字符串的文字
        NSArray<NSString *> *vsArr = [mcu_version componentsSeparatedByString:@"_"];
        if (vsArr.count==4) {
            NSString *str_mcuversion = vsArr[3];
            if ([str_mcuversion hasPrefix:@"v"]) {
                //删除字符串两端的尖括号
                NSMutableString *mString = [NSMutableString stringWithString:str_mcuversion];
                //第一个参数是要删除的字符的索引，第二个是从此位开始要删除的位数
                [mString deleteCharactersInRange:NSMakeRange(0, 1)];
                NSString *version = [mString copy];
                NSArray<NSString *> *vs = [version componentsSeparatedByString:@"."];
                if (vs.count>=3){
                    int v0 = [vs[0] intValue];
                    int v1 = [vs[1] intValue];
                    int v2 = [vs[2] intValue];
                    RBQLog3(@"版本号: v0:%d,v1:%d,v2:%d",v0,v1,v2);
                    return v0 >= 1 && v1 >= 7 && v2 > 2;
                }
                
            }else{
                return NO;
            }
        }
        return NO;
        
    }else{
        // "1.8.6.210817_pul_release" 老版本version格式
        NSArray<NSString *> *vs = [mcu_version componentsSeparatedByString:@"."];
        if (vs.count>=3){
            int v0 = [vs[0] intValue];
            int v1 = [vs[1] intValue];
            int v2 = [vs[2] intValue];
            RBQLog3(@"版本号: v0:%d,v1:%d,v2:%d",v0,v1,v2);
            return v0 >= 1 && v1 >= 7 && v2 > 2;
        }
    }
    return NO;
}

+(int)temperature:(Device *) device{
    if (!device) {
        return defaultTemperature;
    }
    return device.temperature;
}

+(NSString *)textByIntValue:(int)value{
    return [NSString stringWithFormat:@"%d",value];
}

+(BOOL)isFirstRun {
    if (![[NSUserDefaults standardUserDefaults] valueForKey:firstRunAppKey]) {
        return YES;
    }
    return [[[NSUserDefaults standardUserDefaults] valueForKey:firstRunAppKey] boolValue];
}

+(void)saveNotFirstRun {
    [[NSUserDefaults standardUserDefaults] setBool:NO forKey:firstRunAppKey];
    [[NSUserDefaults standardUserDefaults] synchronize];
}

+(void)saveDocSupperDeviceNotReminder{
    [[NSUserDefaults standardUserDefaults] setBool:YES forKey:docSupperDeviceNotReminderKey];
    [[NSUserDefaults standardUserDefaults] synchronize];
}

+(BOOL)isDocSupperDeviceNotReminder{
    if (![[NSUserDefaults standardUserDefaults] valueForKey:docSupperDeviceNotReminderKey]) {
        return YES;
    }
    return ![[[NSUserDefaults standardUserDefaults] valueForKey:docSupperDeviceNotReminderKey] boolValue];
}

+(NSString *)autoConnectDeviceIdentifier {
    NSString *identifier = [[NSUserDefaults standardUserDefaults] valueForKey:autoConnectDeviceIdentifierKey];
    return identifier ? identifier : @""; // 返回空字符串如果 identifier 为空
}
/**保存 WiFi 设备的 mac 或蓝牙设备的 uuidIdentifier*/
+(void)saveIdentifierFromAutoConnectDevice:(nullable NSString *)uuidIdentifier {
    if (uuidIdentifier) {
        [[NSUserDefaults standardUserDefaults] setObject:uuidIdentifier forKey:autoConnectDeviceIdentifierKey];
    } else {
        // 如果 uuidIdentifier 为 null，移除保存的键
        [[NSUserDefaults standardUserDefaults] removeObjectForKey:autoConnectDeviceIdentifierKey];
    }
    [[NSUserDefaults standardUserDefaults] synchronize];
}

+(NSString *)autoConnectDeviceMac {
    NSString *mac = [[NSUserDefaults standardUserDefaults] valueForKey:autoConnectDeviceMacKey];
    return mac ? mac : @""; // 返回空字符串如果 mac 为空
}
/**返回WiFi设备的mac，返回蓝牙设备的uuidIdentifier*/
+(void)saveMacFromAutoConnectDevice:(nullable NSString *)mac{
    if (mac) {
        [[NSUserDefaults standardUserDefaults] setObject:mac forKey:autoConnectDeviceMacKey];
    } else {
        [[NSUserDefaults standardUserDefaults] removeObjectForKey:autoConnectDeviceMacKey]; // 如果 mac 为 null，移除保存的键
    }
    [[NSUserDefaults standardUserDefaults] synchronize];
}

+ (ConnType)autoConnectDeviceConnType {
    // 从 NSUserDefaults 获取保存的 ConnType 值
    NSNumber *connTypeNumber = [[NSUserDefaults standardUserDefaults] objectForKey:autoConnectDeviceConnTypeKey];
    if (connTypeNumber) {
        // 将 NSNumber 转换回 ConnType 并返回
        return [connTypeNumber unsignedIntegerValue];
    } else {
        // 如果没有保存的值，返回一个默认的 ConnType 值
        return 0; // 可以根据需要设置为其他默认类型，如 BLE、WIFI 等
    }
}

+ (void)saveConnTypeFromAutoConnectDevice:(ConnType)connType {
    // 将 ConnType 转换为 NSNumber 并保存到 NSUserDefaults
    [[NSUserDefaults standardUserDefaults] setObject:@(connType) forKey:autoConnectDeviceConnTypeKey];
    // 同步保存
    [[NSUserDefaults standardUserDefaults] synchronize];
}


+ (void)saveAutoConnectDeviceWithUUID:(nullable NSString *)uuidIdentifier mac:(nullable NSString *)mac connType:(NSInteger)connType {
    [self saveIdentifierFromAutoConnectDevice:uuidIdentifier];
    [self saveMacFromAutoConnectDevice:mac];
    [self saveConnTypeFromAutoConnectDevice:connType];
}

/** 保存 WiFi 名称 **/
+(void)saveSsidName:(nullable NSString *)name {
    if (name) {
        [[NSUserDefaults standardUserDefaults] setObject:name forKey:wifiNameKey];
    } else {
        [[NSUserDefaults standardUserDefaults] removeObjectForKey:wifiNameKey]; // 如果 name 为 null，移除保存的键
    }
    [[NSUserDefaults standardUserDefaults] synchronize];
}

+(NSString *)ssidName {
    NSString *name = [[NSUserDefaults standardUserDefaults] objectForKey:wifiNameKey];
    return name ? name : @""; // 如果 name 为 null，返回空字符串
}

/**保存WiFi密码**/
+(void)saveWifiPassword:(nullable NSString *)password {
    if (password) {
        [[NSUserDefaults standardUserDefaults] setObject:password forKey:wifiPasswordKey];
    } else {
        [[NSUserDefaults standardUserDefaults] removeObjectForKey:wifiPasswordKey]; // 如果 password 为 null，移除保存的键
    }
    [[NSUserDefaults standardUserDefaults] synchronize];
}

+(NSString *)wifiPassword {
    NSString *password = [[NSUserDefaults standardUserDefaults] objectForKey:wifiPasswordKey];
    return password ? password : @""; // 如果 password 为 null，返回空字符串
}

+(BOOL)exitEditNotReminder{
    if (![[NSUserDefaults standardUserDefaults] valueForKey:exitEditNotReminderKey]) {
        return NO;
    }
    return [[[NSUserDefaults standardUserDefaults] valueForKey:exitEditNotReminderKey] boolValue];
}
+(void)saveExitNotReminder:(BOOL)notReminder{
    [[NSUserDefaults standardUserDefaults] setBool:notReminder forKey:exitEditNotReminderKey];
    [[NSUserDefaults standardUserDefaults] synchronize];
}

+(BOOL)apNotReminder{
    if (![[NSUserDefaults standardUserDefaults] valueForKey:apNotReminderKey]) {
        return NO;
    }
    return [[[NSUserDefaults standardUserDefaults] valueForKey:apNotReminderKey] boolValue];
}
+(void)saveApNotReminder:(BOOL)noReminder{
    [[NSUserDefaults standardUserDefaults] setBool:noReminder forKey:apNotReminderKey];
    [[NSUserDefaults standardUserDefaults] synchronize];
}

+(BOOL)isFirstTimeRequestDataNetworkPermission{
    if (![[NSUserDefaults standardUserDefaults] valueForKey:firstTimeRequestDataNetworkPermissionKey]) {
        return YES;
    }
    return [[[NSUserDefaults standardUserDefaults] valueForKey:firstTimeRequestDataNetworkPermissionKey] boolValue];
}
+(void)saveFirstTimeRequestDataNetworkPermission:(BOOL)firstTime{
    [[NSUserDefaults standardUserDefaults] setBool:firstTime forKey:apNotReminderKey];
    [[NSUserDefaults standardUserDefaults] synchronize];
}

+(BOOL)autoPowerOffNotReminder{
    if (![[NSUserDefaults standardUserDefaults] valueForKey:autoPowerOffNotReminderKey]) {
        return NO;
    }
    return [[[NSUserDefaults standardUserDefaults] valueForKey:autoPowerOffNotReminderKey] boolValue];
}
+(void)saveAutoPowerOffNotReminder:(BOOL)notReminder{
    [[NSUserDefaults standardUserDefaults] setBool:notReminder forKey:autoPowerOffNotReminderKey];
    [[NSUserDefaults standardUserDefaults] synchronize];
}

@end
