//
//  DelayGCDObjectTimer.h
//  Inksi
//
//  Created by rbq on 2024/6/12.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

@interface DelayGCDObjectTimer : NSObject

-(void)delayScheduledGCDTimerWithSartTime:(void (^)(void))scheduledBlock startTime:(NSTimeInterval)startTime;
-(void)delayScheduledGCDTimerWithSartTime:(void (^)(void))scheduledBlock startTime:(NSTimeInterval)startTime repeats:(BOOL)repeats;

-(void)clearScheduledTimer;

@end

NS_ASSUME_NONNULL_END
