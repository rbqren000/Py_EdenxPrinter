//
//  BatteryUtils.h
//  BelonPrinter
//
//  Created by rbq on 2020/11/27.
//  Copyright © 2020 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

#define defaultBatIcon @"icon_bat_default"
#define noConnectIcon @"icon_no_connect_btn"

@interface BatterySyncManager : NSObject

//是否开启自动同步电量
@property (nonatomic, assign) BOOL isStart;

+(BatterySyncManager *)share;

-(NSString *)getIconByValue:(int)value;
-(UIImage *)getIconImageByValue:(int)value;
-(void)startSynchronizationBattery;
-(void)stopSynchronizationBattery;

@end

NS_ASSUME_NONNULL_END
