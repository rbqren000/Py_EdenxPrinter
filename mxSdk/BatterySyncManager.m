//
//  BatteryUtils.m
//  BelonPrinter
//
//  Created by rbq on 2020/11/27.
//  Copyright © 2020 rbq. All rights reserved.
//

#import "BatterySyncManager.h"
#import "ConnectManager.h"
#import "OpCode.h"

static BatterySyncManager *share=nil;

@interface BatterySyncManager()

@property (nonatomic, strong) NSMutableArray<NSString *> *batteryIcons;
@property (nonatomic, strong) GCDObjectTimer *timer;

@end

@implementation BatterySyncManager

- (NSMutableArray<NSString *> *)batteryIcons{
    if(!_batteryIcons){
        _batteryIcons = [[NSMutableArray<NSString *> alloc] initWithObjects:@"icon_horz_bat_low",@"icon_horz_bat_one",@"icon_horz_bat_two",@"icon_horz_bat_three",@"icon_horz_bat_four",@"icon_horz_bat_five", nil];
    }
    return _batteryIcons;
}

- (GCDObjectTimer *)timer{
    if(!_timer){
        _timer = [[GCDObjectTimer alloc] init];
    }
    return _timer;
}

- (instancetype)init
{
    self = [super init];
    if (self) {
        [self config];
    }
    return self;
}

-(void)config{
    self.isStart = NO;
}

+(BatterySyncManager *)share
{
    
    static dispatch_once_t disOnce;
    dispatch_once(&disOnce, ^{
        
        share=[[BatterySyncManager alloc] init];
        
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

-(NSString *)getIconByValue:(int)value{
    
    if (value>=0
        &&value<self.batteryIcons.count){
        
        return self.batteryIcons[value];
    }
    return @"";
}

-(UIImage *)getIconImageByValue:(int)value{
    
    if (value>=0
        &&value<self.batteryIcons.count){
        NSString *imageName = self.batteryIcons[value];
        return [UIImage imageNamed:imageName];
    }
    return nil;
}

-(void)startSynchronizationBattery{
    
    if (self.isStart) {
        return;
    }
    self.isStart = YES;
    __weak typeof(self)  weakSelf = self;
    [self.timer scheduledGCDTimerWithSartTime:^{
        [weakSelf readBattery];
    } startTime:0.5 interval:5*60 repeats:NO];
}

-(void)readBattery{
    
    uint8_t params[1] = {0};
    [ConnectManager_share sendCommand:params lenght:0 opcode:opcode_readBattery tag:300];
    
}

-(void)stopSynchronizationBattery{
    if (!self.isStart) {
        return;
    }
    [self.timer clearScheduledTimer];
}

@end
