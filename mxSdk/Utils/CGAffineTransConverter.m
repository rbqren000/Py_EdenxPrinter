//
//  CGAffineTransConverter.m
//  Inksi
//
//  Created by rbq on 2024/4/1.
//

#import "CGAffineTransConverter.h"

@implementation CGAffineTransConverter

//改进型   计算弧度
+(CGFloat)CGAffineTransformToRadian:(CGAffineTransform)trans{
    
    CGFloat radian = atan2f(trans.b, trans.a);
    // 旋转180度后，需要处理弧度的变化
    if (radian < 0) {
        radian = M_PI*2 + radian;
    }
    return radian;
}

// 改进后
+(CGFloat)CGAffineTransformToDegree:(CGAffineTransform)trans{
    
    CGFloat radian = atan2f(trans.b, trans.a);
    // 旋转180度后，需要处理弧度的变化
    if (radian < 0) {
        radian = M_PI*2 + radian;
    }
    // 将弧度转换为角度
    return radian * 180 / M_PI;
}

@end
