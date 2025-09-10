//
//  CRC16.h
//  BelonPrinter
//
//  Created by rbq on 2020/9/2.
//  Copyright © 2020 rbq. All rights reserved.
//

#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

@interface CRC16 : NSObject

+(uint16_t)crc16_calc:(uint8_t *)crcByte dataLength:(NSInteger)dataLength;
+(uint16_t)crc16_calc:(uint8_t *)crcByte dataLength:(NSInteger)dataLength startPosition:(NSInteger)startPosition endPosition:(NSInteger)endPosition;
+(uint16_t)crc16_calc:(NSData *)crcByteData;
+(uint16_t)crc16_calc:(NSData *)crcByteData startPosition:(NSInteger)startPosition endPosition:(NSInteger)endPosition;

@end

NS_ASSUME_NONNULL_END
