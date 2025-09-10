//
//  MxRotateUtils.m
//  Inksi
//
//  Created by rbq on 2024/4/17.
//

#import "MxRotateUtils.h"
#import "AngleConverter.h"
#import "NSString+String.h"

@implementation MxRotateUtils

/**根据version返回当前的rotate值**/
+(CGFloat)rotateValue:(NSString *)version radian:(CGFloat)radian{
    RBQLog3(@"【rotateValue】version:%@;rotate:%f",version,radian);
    if ([NSString isBlankString:version]) {
        return radian;
    }
    NSArray<NSString *> *versionArr = [version componentsSeparatedByString:@"."];
    int version_0 = 1;
    if (versionArr.count>0) {
        version_0 = [versionArr.firstObject intValue];
    }
    RBQLog3(@"version_0:%d",version_0);
    //为了和安卓平台统一，从版本2.0.0开始模板中统一存储角度
    if (version_0 >= 2) {
        return [AngleConverter convertRadianToDegree:radian];
    }
    return radian;
}

+(CGFloat)valueByRotate:(NSString *)version rotate:(CGFloat)rotate{
    /**
     这里对角度进行一个360°换算，因为发现安卓端在没旋转角度的情况下保存的是360°，直接赋值，在按住右下角缩放按钮进行缩放时，是反方向缩放。既缩放会向上。
     */
    RBQLog3(@"【valueByRotate】version:%@;rotate:%f",version,rotate);
    if ([NSString isBlankString:version]) {
        return rotate;
    }
    NSArray<NSString *> *versionArr = [version componentsSeparatedByString:@"."];
    int version_0 = 1;
    if (versionArr.count>0) {
        version_0 = [versionArr.firstObject intValue];
    }
    //为了和安卓平台统一，从版本2.0.0开始模板中统一存储角度
    if (version_0 >= 2) {
        CGFloat tempRotate = [AngleConverter convertDegreeToRadian:rotate];
        RBQLog3(@"角度取模后的值为:tempRotate:%f",tempRotate);
        return tempRotate;
    }
    return rotate;
}

@end
