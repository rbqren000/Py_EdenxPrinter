//
//  OpenCVUtils.h
//  BelonPrinter
//
//  Created by rbq on 2021/1/21.
//  Copyright © 2021 rbq. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

@interface OpenCVUtils : NSObject

+(UIImage *)lightClearBackground:(UIImage *)image;
+(UIImage *)deepClearBackground:(UIImage *)image;
+(UIImage *)lightClearRedBackground:(UIImage *)image;
+(UIImage *)deepClearRedBackground:(UIImage *)image;
+ (UIImage *)processImageForTextDetail:(UIImage *)image;
+ (UIImage *)sketchImage:(UIImage *)inputImage;
+ (UIImage *)sketchEffect:(UIImage *)image;
+ (UIImage *)invertColor:(UIImage *)image;
+ (UIImage *)invertColors:(UIImage *)image;
+ (UIImage *)clearForeground:(UIImage *)image;

+(UIImage *)createMultiImgToOne:(UIImage *)img imgs:(NSMutableArray<UIImage *> *)images;
+(UIImage *)rectifyImg:(UIImage *)image;

+(UIImage *)amendImgByOutLine:(UIImage *)image;
/**
 缩放图片
 */
+(UIImage *)resizeBitmap:(UIImage*)bitmap width:(int)newWidth height:(int)newHeight;

+(UIImage *)subImage:(UIImage *)image1 image2:(UIImage *)image2;

//扫描身份证图片，并进行预处理，定位号码区域图片并返回
- (UIImage *)opencvScanCard:(UIImage *)image;

+ (UIImage *)applySobelEdgeDetection:(UIImage *)image;

/**
 
 */
+ (UIImage *)applyCannyEdgeDetection:(UIImage *)image;

// 直方图均衡化
+ (UIImage *)equalizeHistogram:(UIImage *)image;

// 拉普拉斯算子锐化
+ (UIImage *)laplacianSharpening:(UIImage *)image;

+ (UIImage *)laplacianSharpeningEnhanced:(UIImage *)image;

+ (UIImage *)laplacianSharpeningWithBilateralFilter:(UIImage *)image;

// 对数变换
+ (UIImage *)logTransformation:(UIImage *)image;

// 伽马校正
+ (UIImage *)gammaCorrection:(UIImage *)image gamma:(double)gammaValue;

@end

NS_ASSUME_NONNULL_END
