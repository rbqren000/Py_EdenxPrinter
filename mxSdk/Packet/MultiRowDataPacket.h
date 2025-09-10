//
//  MultiRowImageDataPacket.h
//  BelonPrinter
//
//  Created by rbq on 2021/7/8.
//  Copyright © 2021 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "MultiRowData.h"
#import "RowData.h"
#import "BasePacket.h"

NS_ASSUME_NONNULL_BEGIN

@interface MultiRowDataPacket : BasePacket

//压缩方式
@property (nonatomic, assign) int compress; //0不压缩，1压缩

@property (nonatomic, strong, nullable) MultiRowData *multiRowImageData;
@property (nonatomic, strong, nullable) RowData *currentSingleRowImageData;
@property (nonatomic, strong, nullable) NSData *currentRowImageByteData;

@property (nonatomic, assign) int fh;

@property (nonatomic, assign) NSUInteger totalDataLen;//总的数据byte个数
@property (nonatomic, assign) NSUInteger totalPacketCount;//总的包数量
@property (nonatomic, assign) NSUInteger totalRowCount;
@property (nonatomic, assign) int index;//每发送一包，则加1，用来记录已发送包数

@property (nonatomic, assign) NSUInteger usefulPacketDataLength; //有效数据的长度
@property (nonatomic, assign) NSUInteger fullPacketDataLen;//整个数据包的长度

@property (nonatomic, assign) CGFloat progress;
//进度条保留的有效小数位数
@property (nonatomic, assign) NSInteger progressPrecision;

@property (nonatomic, assign) NSUInteger currentRow;
@property (nonatomic, assign) NSUInteger currentRowDataLength;
@property (nonatomic, assign) NSUInteger currentRowTotalPacketCount;
@property (nonatomic, assign) int indexInCurrentRowPacket;

@property (nonatomic, assign) NSTimeInterval startTime;//记发送数据包的开始时间
@property (nonatomic, assign) NSTimeInterval currentTime;//记录当前时间

-(void)set:(MultiRowData *)multiRowData;
/**
 *
 * @param multiRowData  数据
 * @param fh  帧头
 */
-(void)set:(MultiRowData *)multiRowData fh:(int)fh;
-(void)clear;
-(BOOL)hasData;
-(NSUInteger)getCurrentRow;
/*
 *   只判断当前packet
 */
-(BOOL)hasNextPacketWithCurrentRow;
-(BOOL)hasNextRow;
/**
 * 移动到下一个行
 */
-(BOOL)cursorMoveToNext;
-(NSData *)getCurrentPacket;
-(NSData *)getNextPacket;
-(NSData *)packetFormat:(NSData *)data;
-(BOOL)invalidateProgress;

@end

NS_ASSUME_NONNULL_END
