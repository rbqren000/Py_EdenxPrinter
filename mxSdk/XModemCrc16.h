//
//  XModemCrc16.h
//  BelonPrinter
//
//  Created by rbq on 2020/9/2.
//  Copyright © 2020 rbq. All rights reserved.
//

#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

@interface XModemCrc16 : NSObject

+(uint32_t)crc16_calc:(uint8_t *)crcByte lenght:(int)len;

@end

NS_ASSUME_NONNULL_END
