//
//  WifiHelper.h
//  Inksi
//
//  Created by rbq on 2022/6/24.
//

#import <UIKit/UIKit.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <arpa/inet.h>
#import <SystemConfiguration/CaptiveNetwork.h>
#import <NetworkExtension/NetworkExtension.h>
#import <CoreLocation/CoreLocation.h>
#import "RBQLog.h"

NS_ASSUME_NONNULL_BEGIN

@interface HotspotUtil : NSObject

+ (NSString *)getHotspotName;
+ (void)getSSID:(void(^)(NSString *ssid))resultBlock;

@end

NS_ASSUME_NONNULL_END
