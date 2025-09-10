//
//  ParameterStoreUtils.h
//  BelonPrinter
//
//  Created by rbq on 2021/7/23.
//  Copyright © 2021 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "Device.h"

NS_ASSUME_NONNULL_BEGIN

#define ParameterShare [ParameterUtils share] //获取单例类对象

static NSString* const firstRunAppKey = @"firstRunAppKey";
static int const defaultPrinterHead = 0;
static int const defaultLandscapePix = 600;
static int const defaultPortraitPix = 600;
static int const defaultDistance = 0;
static int const defaultCyclesTime = -1;
static int const defaultRepeatTime = 1;
static int const defaultDirection = 1;
static NSString* const defaultMcuVersion = @"0.0.0";
static int const defaultTemperature = 42;

static NSString* const autoConnectDeviceIdentifierKey = @"autoConnectDeviceIdentifierKey";
static NSString* const autoConnectDeviceMacKey = @"autoConnectDeviceMacKey";
static NSString* const autoConnectDeviceConnTypeKey = @"autoConnectDeviceConnTypeKey";

static NSString* const wifiNameKey = @"wifiNameKey";
static NSString* const wifiPasswordKey = @"wifiPasswordKey";

static NSString* const exitEditNotReminderKey = @"exitEditNotReminderKey";
static NSString* const apNotReminderKey = @"apNotReminderKey";
static NSString* const docSupperDeviceNotReminderKey = @"docSupperDeviceNotReminderKey";

static NSString* const firstTimeRequestDataNetworkPermissionKey = @"firstTimeRequestDataNetworkPermissionKey";

static NSString* const autoPowerOffNotReminderKey = @"autoPowerOffNotReminderKey";

@interface ParameterUtils : NSObject

+(ParameterUtils *)share;

+(BOOL)isNewDirection:(Device *) device;

+(BOOL)flipHorizontally:(Device *) device;

+(int)printerHead:(Device *) device;

+(int)landscapePix:(Device *) device;

+(int)portraitPix:(Device *) device;

+(int)distance:(Device *) device;

+(int)circulationTime:(Device *) device;

+(int)repeatTime:(Device *) device;

+(int)direction:(Device *) device;

+(NSString *)directionText:(Device *) device;

+(void)synchronizationOldDirection:(Device *) device;

+(int)oldDirection:(Device *) device;

+(BOOL)mcuVersionNumberOver1_7_2:(Device *) device;

+(int)temperature:(Device *) device;

+(NSString *)textByIntValue:(int)value;

+(BOOL)isFirstRun;
+(void)saveNotFirstRun;

+(void)saveDocSupperDeviceNotReminder;
+(BOOL)isDocSupperDeviceNotReminder;

+(NSString *)autoConnectDeviceIdentifier ;
//+(void)saveIdentifierFromAutoConnectDevice:(nullable NSString *)uuidIdentifier;
+(NSString *)autoConnectDeviceMac;
//+(void)saveMacFromAutoConnectDevice:(nullable NSString *)mac;
+(ConnType)autoConnectDeviceConnType;
//+(void)saveConnTypeFromAutoConnectDevice:(ConnType)connType;

//上边3个方法统一到一个里边去调用
+ (void)saveAutoConnectDeviceWithUUID:(nullable NSString *)uuidIdentifier mac:(nullable NSString *)mac connType:(NSInteger)connType;

+(void)saveSsidName:(nullable NSString *)name;
+(NSString *)ssidName;
+(void)saveWifiPassword:(nullable NSString *)password;
+(NSString *)wifiPassword;

+(BOOL)exitEditNotReminder;
+(void)saveExitNotReminder:(BOOL)notReminder;

+(BOOL)apNotReminder;
+(void)saveApNotReminder:(BOOL)notReminder;

+(BOOL)isFirstTimeRequestDataNetworkPermission;
+(void)saveFirstTimeRequestDataNetworkPermission:(BOOL)firstTime;

+(BOOL)autoPowerOffNotReminder;
+(void)saveAutoPowerOffNotReminder:(BOOL)notReminder;

@end

NS_ASSUME_NONNULL_END
