//
//  OpenCVImageTool.h
//  baibao
//
//  Created by 阮巧华 on 2019/11/16.
//  Copyright © 2019 阮巧华. All rights reserved.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

@interface OpenCVImageTool : NSObject

/// 获取文本图片拍照偏移角度
+ (CGFloat)getTextPhotoAngle:(UIImage *)image;
/// 获取旋转后图片
+ (UIImage *)getRotateImage:(UIImage *)image degree:(CGFloat)degree;
/// 获取灰色图片
+ (UIImage *)getGrayImage:(UIImage *)originImage;
/// 获取黑白图片
+ (UIImage *)getBlackWhiteImage:(UIImage *)originImage;
/// 去红后的照片
+ (UIImage *)repayRedImage:(UIImage *)image;
/// 去蓝后的照片
+ (UIImage *)repayBuleImage:(UIImage *)image;
/// 增亮
+ (UIImage *)addLightImage:(UIImage *)originImage;
/// 对比度
+ (UIImage *)addHstackImage:(UIImage *)originImage;
/// 获取矩形Points
+ (NSArray *)getRectanglePoints:(UIImage *)originImage;

@end

NS_ASSUME_NONNULL_END
