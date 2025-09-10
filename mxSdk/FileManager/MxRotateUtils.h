//
//  MxRotateUtils.h
//  Inksi
//
//  Created by rbq on 2024/4/17.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

@interface MxRotateUtils : NSObject

+(CGFloat)rotateValue:(NSString *)version radian:(CGFloat)radian;
+(CGFloat)valueByRotate:(NSString *)version rotate:(CGFloat)rotate;

@end

NS_ASSUME_NONNULL_END
