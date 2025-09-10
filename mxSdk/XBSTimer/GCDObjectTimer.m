//
//  GCDObjectTimer.m
//  Inksi
//
//  Created by rbq on 2024/6/12.
//

#import "GCDObjectTimer.h"
#import "XBSGCDTimer.h"

@interface GCDObjectTimer()

@property (nonatomic, strong) XBSGCDTimer *scheduledTimer;

@end

@implementation GCDObjectTimer

-(void)clearScheduledTimer{
    if (_scheduledTimer) {
        [_scheduledTimer invalidate];
        _scheduledTimer = nil;
    }
}

-(void)scheduledGCDTimerWithSartTime:(void (^)(void))scheduledBlock startTime:(NSTimeInterval)startTime interval:(NSTimeInterval)interval repeats:(BOOL)repeats{
    
    [self clearScheduledTimer];
    
    if (!scheduledBlock) return;
    
    _scheduledTimer = [XBSGCDTimer xb_scheduledGCDTimerWithSartTime:startTime interval:interval queue:dispatch_get_main_queue() repeats:repeats block:^(XBSGCDTimer *timer) {
        if (scheduledBlock) {
            scheduledBlock();
        }
    }];
}

- (void)dealloc {
    [self clearScheduledTimer];
}

@end
