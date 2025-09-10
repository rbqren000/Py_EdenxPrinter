//
//  AngleConverter.m
//  Inksi
//
//  Created by rbq on 2024/4/1.
//

#import "AngleConverter.h"

@implementation AngleConverter

// 将弧度转换为角度  角度度 = 弧度*180/π
// 改进型
+(CGFloat)convertRadianToDegree:(CGFloat)radian{
    // 将弧度值限制在-π到π之间
    radian = fmodf(radian, M_PI*2);
    // 将弧度转换为角度
    return radian * 180 / M_PI;
}

+ (CGFloat)radiansToDegrees:(CGFloat)radians {
    return radians * 180.0 / M_PI;
}

/**
 将角度转化为弧度
 */
//改进型
+(CGFloat)convertDegreeToRadian:(CGFloat)degree{
    // 将角度值限制在0到360度之间
    degree = fmodf(degree, 360);
    // 将角度转换为弧度
    return degree * M_PI / 180;
}

+ (CGFloat)degreesToRadians:(CGFloat)degrees {
    return degrees * M_PI / 180.0;
}

@end
