//
//  DeviceModel.h
//  Inksi
//
//  Created by rbq on 2024/12/10.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

#define MX_02 @"MX-02"
#define MX_06 @"MX-06"
#define INKSI_01 @"INKSI-01"

#define MX_02_type 1
#define MX_06_type 2
#define INKSI_01_type 3

@interface DeviceModel : NSObject

@property (nonatomic, readonly) NSInteger deviceType;
@property (nonatomic, strong) NSString *aliases;
@property (nonatomic, readonly) NSString *shortAliases;
@property (nonatomic, readonly) NSString *deviceModel;

- (instancetype)initWithDeviceModel:(NSInteger)deviceType aliases:(NSString *)aliases deviceModel:(nullable NSString *)deviceModel;

+ (instancetype)createMX02:(NSString *)last4MacStr;
+ (instancetype)createMX06:(NSString *)last4MacStr;
+ (instancetype)createINKSI01:(NSString *)last4MacStr deviceModel:(NSString *)deviceModel;

@end

NS_ASSUME_NONNULL_END
