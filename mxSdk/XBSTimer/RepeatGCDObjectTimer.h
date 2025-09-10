//
//  RepeatGCDObjectTimer.h
//  Inksi
//
//  Created by rbq on 2025/4/18.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

@interface RepeatGCDObjectTimer : NSObject

/// 设置定时器任务（重复次数）
/// @param scheduledBlock 执行的 block
/// @param startTime 延迟启动（秒）
/// @param interval 重复间隔（秒）
/// @param repeatCount 重复次数（>=1）
- (void)scheduledRepeatTimerWithBlock:(void (^)(void))scheduledBlock
                            startTime:(NSTimeInterval)startTime
                             interval:(NSTimeInterval)interval
                          repeatCount:(NSInteger)repeatCount;

/// 清除定时器
- (void)clearScheduledTimer;

@end

NS_ASSUME_NONNULL_END

