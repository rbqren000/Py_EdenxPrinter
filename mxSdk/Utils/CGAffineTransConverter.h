//
//  CGAffineTransConverter.h
//  Inksi
//
//  Created by rbq on 2024/4/1.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

@interface CGAffineTransConverter : NSObject

//改进型   计算弧度
+(CGFloat)CGAffineTransformToRadian:(CGAffineTransform)trans;

// 改进后
+(CGFloat)CGAffineTransformToDegree:(CGAffineTransform)trans;

@end

NS_ASSUME_NONNULL_END
