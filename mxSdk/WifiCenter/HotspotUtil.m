//
//  WifiHelper.m
//  Inksi
//
//  Created by rbq on 2022/6/24.
//

#import "HotspotUtil.h"

@interface HotspotUtil()

@end

@implementation HotspotUtil

/// ios 14 自动请求临时开启一次精确定位权限
+ (void)autoRequestTemporaryFullAccuracyAuthorization {
  
    if (@available(iOS 14.0, *)) {
        // 定位管理器
        CLLocationManager *locationManager = [[CLLocationManager alloc]init];
        locationManager.desiredAccuracy = kCLLocationAccuracyBest;
        locationManager.distanceFilter = 0.1;
        BOOL isFullAccuracy = locationManager.accuracyAuthorization == CLAccuracyAuthorizationFullAccuracy;
        if (isFullAccuracy) {
             RBQLog3(@"当前为精确定位状态,不需要申请临时开启一次精确位置权限.");
        } else {
            RBQLog3(@"当前为模糊定位状态,需要向用户申请临时开启一次精确位置权限.");
            // 向用户申请临时开启一次精确位置权限
            [locationManager requestTemporaryFullAccuracyAuthorizationWithPurposeKey:@"WantsToGetWiFiSSID"];
        }
    } else {
      
    
    }
}

+ (NSString *)getHotspotName {
    // 创建一个 socket
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        return nil;
    }
    // 获取所有的接口信息
    struct ifconf ifc;
    char buf[1024] = {0};
    ifc.ifc_len = 1024;
    ifc.ifc_buf = buf;
    if (ioctl(sockfd, SIOCGIFCONF, &ifc) < 0) {
        return nil;
    }
    // 遍历接口信息，找到以 "ap" 开头的接口名称
    struct ifreq *ifr = (struct ifreq*)buf;
    for (int i = (ifc.ifc_len / sizeof(struct ifreq)); i > 0; i--) {
        if (strncmp(ifr->ifr_name, "ap", 2) == 0) {
            // 将接口名称转换为 NSString 类型并返回
            NSString *name = [NSString stringWithUTF8String:ifr->ifr_name];
            return name;
        }
        ifr = ifr + 1;
    }
    // 没有找到符合条件的接口，返回 nil
    return nil;
}


/**获取SSID*/
+ (void)getSSID:(void(^)(NSString *ssid))resultBlock {
    if (@available(iOS 14.0, *)) {
        [NEHotspotNetwork fetchCurrentWithCompletionHandler:^(NEHotspotNetwork * _Nullable currentNetwork) {
            NSString *ssid = currentNetwork.SSID ?: @"";
            if (resultBlock) {
                dispatch_async(dispatch_get_main_queue(), ^{
                    resultBlock(ssid);
                });
            }
        }];
    } else {
        NSArray *interfaceNames = CFBridgingRelease(CNCopySupportedInterfaces());
        NSDictionary *info = nil;
        for (NSString *interfaceName in interfaceNames) {
            info = CFBridgingRelease(CNCopyCurrentNetworkInfo((__bridge CFStringRef)interfaceName));
            if (info[@"SSID"]) {
                break;
            }
        }
        NSString *ssid = info[@"SSID"] ?: @"";
        if (resultBlock) {
            dispatch_async(dispatch_get_main_queue(), ^{
                resultBlock(ssid);
            });
        }
    }
}

//获取当前热点的Mac地址
+ (NSString *)wifiMac {
    NSArray *ifs = CFBridgingRelease(CNCopySupportedInterfaces());
    id info = nil;
    for (NSString *ifname in ifs) {
        info = (__bridge_transfer id)CNCopyCurrentNetworkInfo((CFStringRef) ifname);
        if (info && [info count]) {
            break;
        }
    }
    if (!info) {
        return @"获取WiFi热点Mac地址失败";
    }
    NSDictionary *dic = (NSDictionary *)info;
    NSString *bssid = [dic objectForKey:@"BSSID"];
    if (!bssid) {
        return @"获取WiFi热点Mac地址失败";
    }
    return bssid;
}



@end
