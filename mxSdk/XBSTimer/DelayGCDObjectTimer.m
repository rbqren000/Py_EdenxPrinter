//
//  DelayGCDObjectTimer.m
//  Inksi
//
//  Created by rbq on 2024/6/12.
//

#import "DelayGCDObjectTimer.h"
#import "XBSGCDTimer.h"

@interface DelayGCDObjectTimer()

@property (nonatomic, strong) XBSGCDTimer *scheduledTimer;

@end

@implementation DelayGCDObjectTimer

-(void)clearScheduledTimer{
    if (_scheduledTimer) {
        [_scheduledTimer invalidate];
        _scheduledTimer = nil;
    }
}

-(void)delayScheduledGCDTimerWithSartTime:(void (^)(void))scheduledBlock startTime:(NSTimeInterval)startTime {
    
    [self clearScheduledTimer];
    
    if (!scheduledBlock) return;
    
    _scheduledTimer = [XBSGCDTimer xb_scheduledGCDTimerWithSartTime:startTime interval:0 queue:dispatch_get_main_queue() repeats:NO block:^(XBSGCDTimer *timer) {
        if (scheduledBlock) {
            scheduledBlock();
        }
    }];
}

-(void)delayScheduledGCDTimerWithSartTime:(void (^)(void))scheduledBlock startTime:(NSTimeInterval)startTime repeats:(BOOL)repeats{
    
    [self clearScheduledTimer];
    
    if (!scheduledBlock) return;
    
    _scheduledTimer = [XBSGCDTimer xb_scheduledGCDTimerWithSartTime:startTime interval:0 queue:dispatch_get_main_queue() repeats:repeats block:^(XBSGCDTimer *timer) {
        if (scheduledBlock) {
            scheduledBlock();
        }
    }];
}

- (void)dealloc {
    [self clearScheduledTimer];
}

@end

