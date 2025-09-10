//
//  AngleConverter.h
//  Inksi
//
//  Created by rbq on 2024/4/1.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

@interface AngleConverter : NSObject

// 将弧度转换为角度  角度度 = 弧度*180/π
// 改进型
+(CGFloat)convertRadianToDegree:(CGFloat)radian;
/**
 将角度转化为弧度
 */
//改进型
+(CGFloat)convertDegreeToRadian:(CGFloat)degree;

@end

NS_ASSUME_NONNULL_END
