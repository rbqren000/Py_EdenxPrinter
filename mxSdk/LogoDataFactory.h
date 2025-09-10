//
//  LogoDataFactory.h
//  Inksi
//
//  Created by rbq on 2024/6/21.
//

#import <UIKit/UIKit.h>
#import "LogoImage.h"
#import "LogoData.h"

NS_ASSUME_NONNULL_BEGIN

@interface LogoDataFactory : NSObject

+(void)logoImageToData:(LogoImage *)logoImage threshold:(int)threshold  onStart:(void (^)(void))onStart onComplete:(void (^)(LogoData *logoData))onComplete error:(void (^)(void))onError;
+ (LogoData *)logoImageToData:(LogoImage *)logoImage threshold:(int)threshold;

+(void)mergeLogoImageToData:(LogoImage *)logoImage threshold:(int)threshold  onStart:(void (^)(void))onStart onComplete:(void (^)(LogoData *logoData))onComplete error:(void (^)(void))onError;
+ (LogoData *)mergeLogoImageToData:(LogoImage *)logoImage threshold:(int)threshold;

@end

NS_ASSUME_NONNULL_END
