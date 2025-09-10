//
//  MxUtils.m
//  Inksi
//
//  Created by rbq on 2024/8/13.
//

#import "MxUtils.h"
#import "NSString+String.h"
#import "ConnectManager.h"

@implementation MxUtils

+(ConnModel *)getModelBySSid:(NSArray<ConnModel *> *)models ssid:(NSString *)ssid {
    // 参数检查
    if (!models || !ssid || ssid.length < 4) {
        return nil;
    }
    // 计算 ssid 的后四位
    NSString *ssid_last_four_mac = [[ssid substringFromIndex:ssid.length - 4] lowercaseString];
    // 遍历 models 数组
    for (ConnModel *model in models) {
        NSString *model_mac = model.mac;
        // 如果 modelMac 为 nil 或长度小于 4，跳过此循环
        if (!model_mac || model_mac.length < 4) {
            continue;
        }
        // 提取 mac 地址的后四位并转换为小写
        NSString *model_last_four_mac = [[model_mac substringFromIndex:model_mac.length - 4] lowercaseString];
        // 如果 mac 的后四位与 ssid 的最后一部分匹配
        if ([ssid_last_four_mac isEqualToString:model_last_four_mac]) {
            return model;
        }
    }
    return nil;
}

+(BOOL)isSSidConnModel:(ConnModel *)model ssid:(NSString *)ssid {
    // 参数检查
    if (!model || !ssid || ssid.length < 4) {
        return NO;
    }
    // 计算 ssid 的后四位
    NSString *ssid_last_four_mac = [[ssid substringFromIndex:ssid.length - 4] lowercaseString];
    
    NSString *model_mac = model.mac;
    // 如果 modelMac 为 nil 或长度小于 4，跳过此循环
    if (!model_mac || model_mac.length < 4) {
        return NO;
    }
    // 提取 mac 地址的后四位并转换为小写
    NSString *model_last_four_mac = [[model_mac substringFromIndex:model_mac.length - 4] lowercaseString];
    // 如果 mac 的后四位与 ssid 的最后一部分匹配
    return [ssid_last_four_mac isEqualToString:model_last_four_mac];
}

+(BOOL)isSSidDevice:(Device *)device ssid:(NSString *)ssid {
    // 参数检查
    if (!device || !ssid || ssid.length < 4) {
        return NO;
    }
    // 计算 ssid 的后四位
    NSString *ssid_last_four_mac = [[ssid substringFromIndex:ssid.length - 4] lowercaseString];
    
    NSString *model_mac = device.mac;
    // 如果 modelMac 为 nil 或长度小于 4，跳过此循环
    if (!model_mac || model_mac.length < 4) {
        return NO;
    }
    // 提取 mac 地址的后四位并转换为小写
    NSString *model_last_four_mac = [[model_mac substringFromIndex:model_mac.length - 4] lowercaseString];
    // 如果 mac 的后四位与 ssid 的最后一部分匹配
    return [ssid_last_four_mac isEqualToString:model_last_four_mac];
}

+(BOOL)isEqualModel:(ConnModel *)model device:(Device *)device {
    if(!model||!device){
        return NO;
    }
    return (model.peripheral && [model.peripheral isEqual:device.peripheral])
    ||(model.mac && [model.mac isEqualToString:device.mac])
    ||(model.ip && [model.ip isEqualToString:device.ip]);
}

+(BOOL)isPrinterAp:(NSString *)ssid{
    return ![NSString isBlankString:ssid]&&[[ssid lowercaseString] containsString:inksi_mobile_printer];
}

@end
