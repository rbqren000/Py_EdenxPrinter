//
//  LogoImage.m
//  Inksi
//
//  Created by rbq on 2024/6/21.
//

#import "LogoImage.h"

@implementation LogoImage

- (instancetype)initLogoImage:(NSString *)imagePath
{
    self = [super init];
    if (self) {
        _imagePath = imagePath;
    }
    return self;
}

@end
