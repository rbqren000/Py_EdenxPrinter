//
//  XModemCrc16.m
//  BelonPrinter
//
//  Created by rbq on 2020/9/2.
//  Copyright © 2020 rbq. All rights reserved.
//

#import "XModemCrc16.h"

@implementation XModemCrc16
+(uint32_t)crc16_calc:(uint8_t *)crcByte lenght:(int)len{
    
    int crc;
    char i;
    crc = 0;
    while (--len >= 0)
    {
      crc = crc ^ (int) *crcByte++ << 8;
      i = 8;
      do
      {
          if (crc & 0x8000)
              crc = crc << 1 ^ 0x1021;
          else
              crc = crc << 1;
      } while (--i);
    }
    return (crc);
}

@end
