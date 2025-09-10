//
//  Cropper.h
//  OpenCVDemo
//
//  Created by rbq on 2021/5/28.
//  Copyright © 2021 lihuaguang. All rights reserved.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

@interface Cropper : NSObject

+(UIImage *)crop:(UIImage *)source points:(NSArray<NSString *> *)cropPoints;
+(UIImage *)cropWithImage:(UIImage *)source area:(NSArray<NSString *> *)points;

@end

NS_ASSUME_NONNULL_END
