//
//  MxUtils.h
//  Inksi
//
//  Created by rbq on 2024/8/13.
//

#import <UIKit/UIKit.h>
#import "ConnModel.h"
#import "Device.h"

NS_ASSUME_NONNULL_BEGIN

@interface MxUtils : NSObject

+(ConnModel *)getModelBySSid:(NSArray<ConnModel *> *)models ssid:(NSString *)ssid;
+(BOOL)isSSidConnModel:(ConnModel *)model ssid:(NSString *)ssid;
+(BOOL)isSSidDevice:(Device *)device ssid:(NSString *)ssid;
+(BOOL)isEqualModel:(ConnModel *)model device:(Device *)device;
+(BOOL)isPrinterAp:(NSString *)ssid;

@end

NS_ASSUME_NONNULL_END
