//
//  OtaDataPacket.h
//  BelonPrinter
//
//  Created by rbq on 2021/10/22.
//  Copyright © 2021 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "BasePacket.h"

NS_ASSUME_NONNULL_BEGIN

@interface OtaDataPacket : BasePacket

@property (nonatomic, strong, nullable) NSData *data;

@property (nonatomic, assign) int fh;

@property (nonatomic, assign) NSUInteger totalDataLen;//总的数据byte个数
@property (nonatomic, assign) NSUInteger totalPacketCount;//总的包数量
@property (nonatomic, assign) int index;//每发送一包，则加1，用来记录已发送包数

@property (nonatomic, assign) NSUInteger usefulPacketDataLength; //有效数据的长度
@property (nonatomic, assign) NSUInteger fullPacketDataLen;//整个数据包的长度

@property (nonatomic, assign) CGFloat progress;
//进度条保留的有效小数位数
@property (nonatomic, assign) NSInteger progressPrecision;

@property (nonatomic, assign) NSTimeInterval startTime;//记发送数据包的开始时间
@property (nonatomic, assign) NSTimeInterval currentTime;//记录当前时间

-(void)set:(NSData *)data;

-(void)set:(NSData *)data fh:(int)fh;

-(BOOL)hasData;

-(BOOL)hasNextPacket;

-(void)clear;

-(NSData *)getCurrentPacket;

-(NSData *)getNextPacket;

-(NSData *)packetFormat:(NSData *)data;

-(BOOL)invalidateProgress;

-(int)getProgress;

@end

NS_ASSUME_NONNULL_END
