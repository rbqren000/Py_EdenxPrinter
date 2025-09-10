//
//  NSString+String.m
//  GsenseMesh
//
//  Created by rbq on 2019/6/26.
//  Copyright © 2019年 rbq. All rights reserved.
//

#import "NSString+String.h"

@implementation NSString (String)

+ (BOOL)isBlankString:(NSString *)string {
    if (!string || [string isKindOfClass:[NSNull class]]) {
        return YES;
    }
    return ([[string stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]] length] == 0);
}

+(BOOL)isValidateByRegex:(NSString *)string regex:(NSString *)regex{
    
    NSPredicate *pre = [NSPredicate predicateWithFormat:@"SELF MATCHES %@",regex];
    return [pre evaluateWithObject:string];
}

+(NSString *)Simplify:(NSString *)str{
    
    str = [str stringByReplacingOccurrencesOfString:@"\r" withString:@""];
    str = [str stringByReplacingOccurrencesOfString:@"\n" withString:@""];
    str = [str stringByReplacingOccurrencesOfString:@"\t" withString:@""];
    str = [str stringByReplacingOccurrencesOfString:@"\b" withString:@""];
    str = [str stringByReplacingOccurrencesOfString:@" " withString:@""];
    return str;
}

+(NSString *)UTF8:(NSString *)str{
    
    str = [str stringByAddingPercentEncodingWithAllowedCharacters:[NSCharacterSet URLQueryAllowedCharacterSet]];
    
    return str;
}

+(NSString *)contain:(NSString *)string keys:(NSMutableArray<NSString *> *)keys{
    
    if (!string||!keys){
        return NULL;
    }
    for (int i=0;i<keys.count;i++){
        
        NSString *key = keys[i];
        //        RBQLog3(@"正在比较关键字:%@",key);
        if ([string containsString:key]) {
            return key;
        }
    }
    return NULL;
}

+ (NSString *)convertDataToHexStr:(NSData *)data {
    if (!data || [data length] == 0) {
        return @"";
    }
    const unsigned char *dataBytes = [data bytes];
    NSMutableString *string = [NSMutableString stringWithCapacity:[data length] * 2];
    for (NSInteger i = 0; i < [data length]; i++) {
        [string appendFormat:@"%02x", dataBytes[i]];
    }
    return string;
}

+ (NSString *)convertDataToHexStr:(NSData *)data withSeparator:(NSString *)separator {
    if (!data || [data length] == 0) {
        return @"";
    }
    const unsigned char *dataBytes = [data bytes];
    NSMutableString *string = [NSMutableString stringWithCapacity:[data length] * 3 - 1];
    for (NSInteger i = 0; i < [data length]; i++) {
        if (i > 0) {
            [string appendString:separator];
        }
        [string appendFormat:@"%02x", dataBytes[i]];
    }
    return string;
}

+ (NSString *)convertBytesToHexStr:(uint8_t *)bytes length:(int)len {
    NSMutableString *string = [NSMutableString stringWithCapacity:len * 2];
    for (int i = 0; i < len; i++) {
        [string appendFormat:@"%02x", bytes[i]];
    }
    return [string uppercaseString];
}

+ (NSString *)convertBytesToHexStr:(uint8_t *)bytes length:(int)len withSeparator:(NSString *)separator {
    NSMutableString *string = [NSMutableString stringWithCapacity:len * 3 - 1];
    for (int i = 0; i < len; i++) {
        if (i > 0) {
            [string appendString:separator];
        }
        [string appendFormat:@"%02x", bytes[i]];
    }
    return [string uppercaseString];
}

+ (NSData *)dataFromHexString:(NSString *)hexString {
    
    if (hexString.length == 0) {
        return nil;
    }
    NSMutableData *data = [[NSMutableData alloc] initWithCapacity:hexString.length / 2];
    unsigned char wholeByte;
    char byteChars[3] = {'\0', '\0', '\0'};

    for (int i = 0; i < hexString.length / 2; i++) {
        byteChars[0] = [hexString characterAtIndex:i * 2];
        byteChars[1] = [hexString characterAtIndex:i * 2 + 1];
        wholeByte = strtol(byteChars, NULL, 16);
        [data appendBytes:&wholeByte length:1];
    }
    
    return data;
}

+ (NSData *)dataFromHexStringWithSeparator:(NSString *)hexString separator:(NSString *)separator {
    if (hexString.length == 0) {
        return nil;
    }

    NSArray<NSString *> *components = [hexString componentsSeparatedByString:separator];
    NSMutableData *data = [[NSMutableData alloc] initWithCapacity:components.count];

    unsigned char wholeByte;
    char byteChars[3] = {'\0', '\0', '\0'};

    for (NSString *component in components) {
        byteChars[0] = [component characterAtIndex:0];
        byteChars[1] = [component characterAtIndex:1];
        wholeByte = strtol(byteChars, NULL, 16);
        [data appendBytes:&wholeByte length:1];
    }

    return data;
}

+ (NSString *)formatMACAddress:(NSString *)macAddress {
    // 确保 MAC 地址长度为 12 个字符
    if (macAddress.length != 12) {
        //如果长度不为12，则返回原字符串自身
        return macAddress;
    }
    NSMutableString *formattedMAC = [NSMutableString string];
    // 遍历字符串并插入冒号
    for (NSInteger i = 0; i < macAddress.length; i += 2) {
        if (i > 0) {
            [formattedMAC appendString:@":"];
        }
        NSString *segment = [macAddress substringWithRange:NSMakeRange(i, 2)];
        [formattedMAC appendString:segment];
    }
    return formattedMAC;
}



/*
 startStr 要从哪几个字符开始截取,如果从第0个字符开始截,输入nil或@""
 endStr   要从哪几个字符结束,如果截到最后输入nil或@""
 例: 我喜欢abc123还有跳跳跳舞  startStr:欢a  endStr:有跳跳   输出结果是:bc123还
 */
+ (NSString *)selcteStringWithSelect:(NSString *)string Satrt:(NSString *)startStr selecteEnd:(NSString *)endStr {
    
    NSString *startRegStr = [startStr stringByReplacingOccurrencesOfString:@"[" withString:@"\\["];//转义[
    NSString *endRegStr = [endStr stringByReplacingOccurrencesOfString:@"[" withString:@"\\["];//转义[
    NSString *regStr = [NSString stringWithFormat:@"%@.*?%@",startRegStr,endRegStr];//拼接正则字符
    if (endStr.length == 0 ) {
        regStr = [NSString stringWithFormat:@"%@.*",startRegStr];
    }
    if (startStr.length == 0) {
        regStr = [NSString stringWithFormat:@".*?%@",endStr];
    }
    //正则方法截取字符串
    NSRange codeRange = [string rangeOfString:regStr options:NSRegularExpressionSearch];
    
    NSString *return_code;
    
    if (codeRange.location != NSNotFound){
        
        return_code = [string substringWithRange:codeRange];
        
        if (startStr.length) {
            return_code = [return_code stringByReplacingOccurrencesOfString:startStr withString:@""];
        }
        if (endStr.length) {
            return_code = [return_code stringByReplacingOccurrencesOfString:endStr withString:@""];
        }
    }else{
//        return_code = @"字符串截取失败";
        return_code = @"";
    }
    return return_code;
}

//返回16位大小写字母和数字
+(NSString *)return16LetterAndNumber{
    //定义一个包含数字，大小写字母的字符串
    NSString * strAll = @"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    //定义一个结果
    NSString *result = [[NSMutableString alloc]initWithCapacity:16];
    for (int i = 0; i < 16; i++)
    {
        //获取随机数
        NSInteger index = arc4random() % (strAll.length-1);
        char tempStr = [strAll characterAtIndex:index];
        result = (NSMutableString *)[result stringByAppendingString:[NSString stringWithFormat:@"%c",tempStr]];
    }
    return result;
}

+(NSString *)randomLetterAndNumber:(int)length{
    //定义一个包含数字，大小写字母的字符串
    NSString *strAll = @"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    //定义一个结果
    NSString * result = [[NSMutableString alloc]initWithCapacity:length];
    for (int i = 0; i < length; i++)
    {
        //获取随机数
        NSInteger index = arc4random() % (strAll.length-1);
        char tempStr = [strAll characterAtIndex:index];
        result = (NSMutableString *)[result stringByAppendingString:[NSString stringWithFormat:@"%c",tempStr]];
    }
    return result;
}

- (CGSize)sizeWithFont:(UIFont *)font maxSize:(CGSize)maxSize
{
    NSDictionary *attrs = @{NSFontAttributeName:font};
    return [self boundingRectWithSize:maxSize options:NSStringDrawingUsesLineFragmentOrigin attributes:attrs context:nil].size;
}

@end
