//
//  NSString+String.h
//  GsenseMesh
//
//  Created by rbq on 2019/6/26.
//  Copyright © 2019年 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "RBQLog.h"

@interface NSString (String)

+(BOOL)isBlankString:(NSString *)string;
+(BOOL)isValidateByRegex:(NSString *)string regex:(NSString *)regex;
+(NSString *)Simplify:(NSString *)str;//简化字符串，去掉字符串中的空格，tab，换行等字符
+(NSString *)UTF8:(NSString *)str;
+(NSString *)contain:(NSString *)string keys:(NSMutableArray<NSString *> *)keys;

+ (NSString *)convertDataToHexStr:(NSData *)data;
+ (NSString *)convertDataToHexStr:(NSData *)data withSeparator:(NSString *)separator;
+ (NSString *)convertBytesToHexStr:(uint8_t *)bytes length:(int)len;
+ (NSString *)convertBytesToHexStr:(uint8_t *)bytes length:(int)len withSeparator:(NSString *)separator;
+ (NSData *)dataFromHexString:(NSString *)hexString;
+ (NSData *)dataFromHexStringWithSeparator:(NSString *)hexString separator:(NSString *)separator;

+ (NSString *)formatMACAddress:(NSString *)macAddress;

+ (NSString *)selcteStringWithSelect:(NSString *)string Satrt:(NSString *)startStr selecteEnd:(NSString *)endStr;
+(NSString *)randomLetterAndNumber:(int)length;
/**
 *  返回字符串所占用的尺寸
 *  @param font    字体
 *  @param maxSize 最大尺寸
 */
- (CGSize)sizeWithFont:(UIFont *)font maxSize:(CGSize)maxSize;

@end
