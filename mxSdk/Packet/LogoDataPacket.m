//
//  LogoImageDataPacket.m
//  BelonPrinter
//
//  Created by rbq on 2021/10/21.
//  Copyright © 2021 rbq. All rights reserved.
//

#import "LogoDataPacket.h"
#import "TransportProtocol.h"
#import "CRC16.h"
#import "RBQLog.h"
#import "NSString+String.h"

static const int packetHeadLen = 1;
static const int packetHeadXorLen = 1;
static const int crcLen = 2;

@interface LogoDataPacket()

//记录上次进度条更新的时间
@property (nonatomic, assign) NSTimeInterval lastInvalidateProgressTime;

@end

@implementation LogoDataPacket

- (instancetype)init
{
    self = [super init];
    if (self) {
        [self setUp];
    }
    return self;
}

-(void)setUp{
    
    self.fh = SOH;//默认发送soh包

    self.totalDataLen = 0;//总的数据byte个数
    self.totalPacketCount = 0;//总的包数量
    self.index = -1;//每发送一包，则加1，用来记录已发送包数

    self.usefulPacketDataLength = 124; //有效数据的长度
    self.fullPacketDataLen = 0;//整个数据包的长度

    self.progress = 0;

    self.startTime = 0;//记发送数据包的开始时间
    self.currentTime = 0;//记录当前时间

    self.start = NO;
}

/**
 *
 * @param logoData 数据  使用默认的帧头 SOH  0x1E
 */
-(void)set:(LogoData *)logoData {
    [self set:logoData fh:STX_E];
}

/**
 *
 * @param logoData  数据
 * @param fh  帧头
 */
-(void)set:(LogoData *)logoData fh:(int)fh {
    [self clear];

    self.data = [logoData data];
    self.fh = fh;

    switch (fh){
        case SOH:
            self.usefulPacketDataLength = 128;
            self.progressPrecision = 2;
            break;
        case STX:
            self.usefulPacketDataLength = 512;
            self.progressPrecision = 1;
            break;
        case STX_A:
            self.usefulPacketDataLength = 1024;
            self.progressPrecision = 0;
            break;
        case STX_B:
            self.usefulPacketDataLength = 2048;
            self.progressPrecision = 0;
            break;
        case STX_C:
            self.usefulPacketDataLength = 5120;
            self.progressPrecision = 0;
            break;
        case STX_D:
            self.usefulPacketDataLength = 10240;
            self.progressPrecision = 0;
            break;
        case STX_E:
            self.usefulPacketDataLength = 124;
            self.progressPrecision = 2;
            break;
    }

    self.fullPacketDataLen = self.usefulPacketDataLength + packetHeadLen + packetHeadXorLen + crcLen;
    self.totalDataLen = logoData.dataLength;
    
    if (self.totalDataLen%self.usefulPacketDataLength ==0) {
        self.totalPacketCount = self.totalDataLen/self.usefulPacketDataLength;
    }else{
        self.totalPacketCount = self.totalDataLen/self.usefulPacketDataLength + 1;
    }
    self.index = -1;
    self.progress = 0;
    self.startTime = 0;//记发送数据包的开始时间
    self.currentTime = 0;//记录当前时间

    RBQLog3(@"logo数据 长度:%f k; 共分:%lu 包; usefulPacketDataLength:%ld",self.totalDataLen /1000.0f,(unsigned long)self.totalPacketCount,self.usefulPacketDataLength);
}

-(void)clear {
    
    self.data = nil;

    self.fh = SOH;//默认发送soh包

    self.totalDataLen = 0;//总的数据byte个数
    self.totalPacketCount = 0;//总的包数量
    self.index = -1;//每发送一包，则加1，用来记录已发送包数

    self.usefulPacketDataLength = 124; //有效数据的长度
    self.fullPacketDataLen = 0;//整个数据包的长度

    self.progress = 0;

    self.startTime = 0;//记发送数据包的开始时间
    self.currentTime = 0;//记录当前时间

    [super clear];
}

-(BOOL)hasData{
    if (!self.data){
        return NO;
    }
    return self.data.length > 0;
}

/*
 *   只判断当前packet
 */
-(BOOL)hasNextPacket {
    if (!self.data) {
        return NO;
    }
    return self.totalPacketCount>0 && (self.index +1)<self.totalPacketCount;
}

-(NSData *)getCurrentPacket {
    
    @autoreleasepool {
        
        NSUInteger offset = self.index * self.usefulPacketDataLength;

        if (offset + self.usefulPacketDataLength <= self.totalDataLen) {
            return [self.data subdataWithRange:NSMakeRange(offset, self.usefulPacketDataLength)];
        } else {
            NSUInteger overPackSize = self.totalDataLen - offset;
            NSMutableData *lastPacket = [NSMutableData dataWithLength:self.usefulPacketDataLength];
            [lastPacket replaceBytesInRange:NSMakeRange(0, overPackSize) withBytes:[self.data bytes] + offset];
            memset([lastPacket mutableBytes] + overPackSize, 0x1A, self.usefulPacketDataLength - overPackSize);
            return lastPacket;
        }
    }
}

-(NSData *)getNextPacket {
    
    @autoreleasepool {
        
        self.index++;
        NSUInteger offset = self.index * self.usefulPacketDataLength;

        if (offset + self.usefulPacketDataLength <= self.totalDataLen) {
            return [self.data subdataWithRange:NSMakeRange(offset, self.usefulPacketDataLength)];
        } else {
            NSUInteger overPackSize = self.totalDataLen - offset;
            NSMutableData *lastPacket = [NSMutableData dataWithLength:self.usefulPacketDataLength];
            [lastPacket replaceBytesInRange:NSMakeRange(0, overPackSize) withBytes:[self.data bytes] + offset];
            memset([lastPacket mutableBytes] + overPackSize, 0x1A, self.usefulPacketDataLength - overPackSize);
            return lastPacket;
        }
    }
}

- (NSData *)packetFormat:(NSData *)data {

    @autoreleasepool {
        
        NSUInteger len = data.length;
        // 创建一个长度为fullPacketDataLen的可变数据对象
        NSMutableData *formatData = [NSMutableData dataWithLength:self.fullPacketDataLen];
        uint8_t *formatBytes = (uint8_t *)formatData.mutableBytes;

        int offset = 0;
        // 前缀字节
        formatBytes[offset++] = self.fh;
        // 前缀字节取反
        formatBytes[offset++] = ~self.fh & 0xFF;
        // 复制数据到imageBytes
        memcpy(formatBytes + offset, data.bytes, len);
        offset += len;
        // 计算CRC
        uint16_t crc = [CRC16 crc16_calc:formatBytes dataLength:offset];
        // 将CRC附加到数据末尾
        formatBytes[offset++] = (crc >> 8) & 0xFF;
        formatBytes[offset] = crc & 0xFF;
        // 返回格式化后的数据
        return [formatData copy];
    }
}


- (BOOL)invalidateProgress {
    // pow(10.0, self.progressPrecision) 用于计算 10 的 self.progressPrecision 次幂，从而动态确定保留的小数位数
    CGFloat multiplier = pow(10.0, self.progressPrecision);
    CGFloat progress = roundf((self.index / (CGFloat)self.totalPacketCount) * 100 * multiplier) / multiplier;
    
    NSTimeInterval currentTime = [NSDate date].timeIntervalSince1970;
    
    if (progress != self.progress || currentTime - self.lastInvalidateProgressTime >= 1.0) {
        self.progress = progress;
        self.lastInvalidateProgressTime = currentTime;
        return YES;
    }
    return NO;
}


-(int)getProgress{
    return self.progress;
}

@end
