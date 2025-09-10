//
//  Command.h
//  BelonPrinter
//
//  Created by rbq on 2021/10/19.
//  Copyright © 2021 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

@interface Command : NSObject

@property (nonatomic, assign) int index;//指令号  一版为随机数
@property (nonatomic, strong) NSData *data;
@property (nonatomic, assign) int tag;
@property (nonatomic, assign) NSTimeInterval createTime;//指令生成时间，单位时间戳
@property (nonatomic, assign) NSTimeInterval delayTime;//延时时间，秒  如果值为-1，则为立即发送，如果值大于0，则延时发送
@property (nonatomic, assign) BOOL isLossOnTimeout;//超时时是否继续发送，默认false表示继续发送，当期值为true时，则不再发送该指令

- (instancetype)initCommand:(NSData *)data;

- (instancetype)initCommand:(NSData *)data delayTime:(NSTimeInterval)delayTime;

- (instancetype)initCommand:(NSData *)data delayTime:(NSTimeInterval)delayTime withTag:(int)tag;

- (instancetype)initCommand:(NSData *)data withTag:(int)tag;

- (instancetype)initCommand:(NSData *)data withTag:(int)tag delayTime:(NSTimeInterval)delayTime;

- (instancetype)initCommand:(NSData *)data index:(int)index withTag:(int)tag delayTime:(NSTimeInterval)delayTime;

@end

NS_ASSUME_NONNULL_END
