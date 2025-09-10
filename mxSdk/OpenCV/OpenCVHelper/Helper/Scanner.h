//
//  Scanner.h
//  OpenCVDemo
//
//  Created by rbq on 2021/5/25.
//  Copyright © 2021 lihuaguang. All rights reserved.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

static const int resizeThreshold = 500;
static float resizeScale = 1.0f;

@interface Scanner : NSObject

+(UIImage *)thresholdImage:(UIImage *)srcBitmap;
+(NSArray<NSString *> *)scanPoint:(UIImage *)srcBitmap;

@end

NS_ASSUME_NONNULL_END
