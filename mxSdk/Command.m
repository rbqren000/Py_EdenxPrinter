//
//  Command.m
//  BelonPrinter
//
//  Created by rbq on 2021/10/19.
//  Copyright © 2021 rbq. All rights reserved.
//

#import "Command.h"

@implementation Command

- (instancetype)initCommand:(NSData *)data
{
    self = [super init];
    if (self) {
        self.index = -1;
        self.data = data;
        self.tag = -1;
        self.createTime = -1;//指令生成时间，单位时间戳
        self.delayTime = -1;//延时时间，秒
        self.isLossOnTimeout = NO;//超时时是否继续发送，默认false表示继续发送，当期值为true时，则不再发送该指令
    }
    return self;
}

- (instancetype)initCommand:(NSData *)data delayTime:(NSTimeInterval)delayTime{
    self = [super init];
    if (self) {
        self.index = -1;
        self.data = data;
        self.tag = -1;
        self.createTime = [[NSDate date] timeIntervalSince1970];//指令生成时间，单位时间戳
        self.delayTime = delayTime;//延时时间，秒
        self.isLossOnTimeout = NO;//超时时是否继续发送，默认false表示继续发送，当期值为true时，则不再发送该指令
    }
    return self;
}

- (instancetype)initCommand:(NSData *)data delayTime:(NSTimeInterval)delayTime withTag:(int)tag{
    self = [super init];
    if (self) {
        self.index = -1;
        self.data = data;
        self.tag = tag;
        self.createTime = [[NSDate date] timeIntervalSince1970];//指令生成时间，单位时间戳
        self.delayTime = delayTime;//延时时间，秒
        self.isLossOnTimeout = NO;//超时时是否继续发送，默认false表示继续发送，当期值为true时，则不再发送该指令
    }
    return self;
}

- (instancetype)initCommand:(NSData *)data withTag:(int)tag
{
    self = [super init];
    if (self) {
        self.index = -1;
        self.data = data;
        self.tag = tag;
        self.createTime = -1;//指令生成时间，单位时间戳
        self.delayTime = -1;//延时时间，秒
        self.isLossOnTimeout = NO;//超时时是否继续发送，默认false表示继续发送，当期值为true时，则不再发送该指令
    }
    return self;
}

- (instancetype)initCommand:(NSData *)data withTag:(int)tag delayTime:(NSTimeInterval)delayTime{
    self = [super init];
    if (self) {
        self.index = -1;
        self.data = data;
        self.tag = tag;
        self.createTime = [[NSDate date] timeIntervalSince1970];//指令生成时间，单位时间戳
        self.delayTime = delayTime;//延时时间，秒
        self.isLossOnTimeout = NO;//超时时是否继续发送，默认false表示继续发送，当期值为true时，则不再发送该指令
    }
    return self;
}

- (instancetype)initCommand:(NSData *)data index:(int)index withTag:(int)tag delayTime:(NSTimeInterval)delayTime{
    self = [super init];
    if (self) {
        self.index = index;
        self.data = data;
        self.tag = tag;
        self.createTime = [[NSDate date] timeIntervalSince1970];//指令生成时间，单位时间戳
        self.delayTime = delayTime;//延时时间，秒
        self.isLossOnTimeout = NO;//超时时是否继续发送，默认false表示继续发送，当期值为true时，则不再发送该指令
    }
    return self;
}

@end
