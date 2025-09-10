//
//  RepeatGCDObjectTimer.m
//  Inksi
//
//  Created by rbq on 2025/4/18.
//

#import "RepeatGCDObjectTimer.h"
#import "XBSGCDTimer.h"

@interface RepeatGCDObjectTimer ()

@property (nonatomic, strong) XBSGCDTimer *timer;
@property (nonatomic, assign) NSInteger remainingCount;

@end

@implementation RepeatGCDObjectTimer

- (void)scheduledRepeatTimerWithBlock:(void (^)(void))scheduledBlock
                            startTime:(NSTimeInterval)startTime
                             interval:(NSTimeInterval)interval
                          repeatCount:(NSInteger)repeatCount {
    
    [self clearScheduledTimer];

    if (!scheduledBlock || repeatCount <= 0) return;
    
    self.remainingCount = repeatCount;

    __weak typeof(self) weakSelf = self;
//    __strong typeof(weakSelf) strongSelf = weakSelf;
    self.timer = [XBSGCDTimer xb_scheduledGCDTimerWithSartTime:startTime
                                                       interval:interval
                                                         queue:dispatch_get_main_queue()
                                                       repeats:YES
                                                         block:^(XBSGCDTimer * _Nonnull timer) {

        if (weakSelf.remainingCount > 0) {
            scheduledBlock();
            weakSelf.remainingCount--;
        }

        if (weakSelf.remainingCount <= 0) {
            [weakSelf clearScheduledTimer];
        }
    }];
}

- (void)clearScheduledTimer {
    if (self.timer) {
        [self.timer invalidate];
        self.timer = nil;
    }
    self.remainingCount = 0;
}

- (void)dealloc {
    [self clearScheduledTimer];
}

@end


