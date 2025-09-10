//
//  GCDObjectTimer.h
//  Inksi
//
//  Created by rbq on 2024/6/12.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

@interface GCDObjectTimer : NSObject

-(void)scheduledGCDTimerWithSartTime:(void (^)(void))scheduledBlock startTime:(NSTimeInterval)startTime interval:(NSTimeInterval)interval repeats:(BOOL)repeats;

-(void)clearScheduledTimer;

@end

NS_ASSUME_NONNULL_END
