//
//  Cropper.m
//  OpenCVDemo
//
//  Created by rbq on 2021/5/28.
//  Copyright © 2021 lihuaguang. All rights reserved.
//

// 加上#ifdef __cpluseplus来表示这是 C++ 文件才会编译的
#ifdef __cplusplus
#include <iostream>
#endif

#include <opencv2/opencv.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/imgproc/types_c.h>
#include <opencv2/imgcodecs/ios.h>
#include <algorithm>

#import "Cropper.h"

@implementation Cropper

/**
 *  裁剪图片
 * @param srcBmp   待裁剪的图片
 * @param cropPoints    裁剪区域顶点，顶点坐标以图像大小为准
 * @return  返回裁剪后的图片
 */
+(UIImage *)crop:(UIImage *)srcBmp points:(NSArray<NSString *> *)cropPoints {
    if (!srcBmp||!cropPoints) {
        return srcBmp;
    }
    if (cropPoints.count < 4) {
        return srcBmp;
    }
    
    cv::Mat srcMat;
    UIImageToMat(srcBmp, srcMat);
    
    cv::Mat dstMat;

    CGPoint leftTopPoint = CGPointFromString(cropPoints[0]);
    CGPoint rightTopPoint = CGPointFromString(cropPoints[1]);
    CGPoint rightBottomPoint = CGPointFromString(cropPoints[2]);
    CGPoint leftBottomPoint = CGPointFromString(cropPoints[3]);
    
    cv::Point leftTop = cv::Point(leftTopPoint.x, leftTopPoint.y);
    cv::Point rightTop = cv::Point(rightTopPoint.x, rightTopPoint.y);
    cv::Point rightBottom = cv::Point(rightBottomPoint.x, rightBottomPoint.y);
    cv::Point leftBottom = cv::Point(leftBottomPoint.x, leftBottomPoint.y);
    
    int cropWidth = (int) (pointsDistance(leftTop, rightTop) + pointsDistance(leftBottom, rightBottom))/2;
    int cropHeight = (int) (pointsDistance(leftTop, leftBottom) + pointsDistance(rightTop, rightBottom))/2;
    
    cv::Mat srcTriangleMat = cv::Mat(4, 1, CV_32FC2);
    
    cv::Mat dstTriangleMat = cv::Mat(4, 1, CV_32FC2);
    
    std::vector<cv::Point2f> srcTriangle;
    std::vector<cv::Point2f> dstTriangle;

    //待裁剪部分的区域顶点
    srcTriangle.push_back(cv::Point2f(leftTop.x, leftTop.y));
    srcTriangle.push_back(cv::Point2f(rightTop.x, rightTop.y));
    srcTriangle.push_back(cv::Point2f(leftBottom.x, leftBottom.y));
    srcTriangle.push_back(cv::Point2f(rightBottom.x, rightBottom.y));

    //输出Mat对象的四个顶点
    dstTriangle.push_back(cv::Point2f(0, 0));
    dstTriangle.push_back(cv::Point2f(cropWidth, 0));
    dstTriangle.push_back(cv::Point2f(0, cropHeight));
    dstTriangle.push_back(cv::Point2f(cropWidth, cropHeight));
    
    //计算透视变换矩阵
    cv::Mat transformMat = getPerspectiveTransform(srcTriangle, dstTriangle);
    //透视变换（参数为输入图像、输出图像、3*3变换矩阵、目标图像大小）
    warpPerspective(srcMat, dstMat, transformMat,cv::Size(cropWidth, cropHeight));
    //将Mat转换为bitmap对象
    return MatToUIImage(dstMat);
}

static double pointsDistance(cv::Point p1, cv::Point p2){
    return pointsDistance(p1.x, p1.y, p2.x, p2.y);
}

static double pointsDistance(double x1, double y1, double x2, double y2){
    
    return sqrt(pow(x1 - x2, 2)+pow(y1 - y2, 2));
}

static cv::Point caculateMidPoint(cv::Point onePoint, cv::Point theOtherPoint){
    
    double shorterX = onePoint.x > theOtherPoint.x ? theOtherPoint.x : onePoint.x;
    double shorterY = onePoint.y > theOtherPoint.y ? theOtherPoint.y : onePoint.y;
    
    cv::Point midPoint = cv::Point(double(std::abs(onePoint.x - theOtherPoint.x) / 2) + shorterX,double(std::abs(onePoint.y - theOtherPoint.y) / 2) + shorterY);
    return midPoint;
}

//根据两个点，计算出中点坐标
+(CGPoint)caculateMidPoint:(CGPoint)onePoint other:(CGPoint)theOtherPoint {

    float shorterX = onePoint.x > theOtherPoint.x ? theOtherPoint.x : onePoint.x;
    float shorterY = onePoint.y > theOtherPoint.y ? theOtherPoint.y : onePoint.y;

    return CGPointMake(CGFloat(abs(onePoint.x - theOtherPoint.x) / 2) + shorterX,
                       CGFloat(abs(onePoint.y - theOtherPoint.y) / 2) + shorterY);
}


/**
 * 裁剪图片
 * @param source 待裁剪图片
 * @param points 裁剪区域顶点，顶点坐标以图片大小为准
 * @return 返回裁剪后的图片
 */
+ (UIImage *)cropWithImage:(UIImage *)source area:(NSArray<NSString *> *)points {
    if (source == nil || points == nil) {
        return source;
    }
    if (points.count < 4) {
        return source;
    }
    CGPoint leftTop = CGPointFromString(points[0]);
    CGPoint rightTop = CGPointFromString(points[1]);
    CGPoint rightBottom = CGPointFromString(points[2]);
    CGPoint leftBottom = CGPointFromString(points[3]);
    // 转化为 Mat 对象
    UIImage *image = [self rotate:source imageOrientation:source.imageOrientation];
    cv::Mat srcBitmapMat;
    UIImageToMat(image, srcBitmapMat, false);
    CGImage *cgImage = image.CGImage;
    CGFloat newWidth = CGImageGetWidth(cgImage);
    CGFloat newHeight = CGImageGetHeight(cgImage);
    // 初始化输出Mat对象
    cv::Mat dstBitmapMat = cv::Mat::zeros(newHeight, newWidth, srcBitmapMat.type());
    
    std::vector<cv::Point2f> srcTriangle;
    std::vector<cv::Point2f> dstTriangle;

    //待裁剪部分的区域顶点
    srcTriangle.push_back(cv::Point2f(leftTop.x, leftTop.y));
    srcTriangle.push_back(cv::Point2f(rightTop.x, rightTop.y));
    srcTriangle.push_back(cv::Point2f(leftBottom.x, leftBottom.y));
    srcTriangle.push_back(cv::Point2f(rightBottom.x, rightBottom.y));

    //输出Mat对象的四个顶点
    dstTriangle.push_back(cv::Point2f(0, 0));
    dstTriangle.push_back(cv::Point2f(newWidth, 0));
    dstTriangle.push_back(cv::Point2f(0, newHeight));
    dstTriangle.push_back(cv::Point2f(newWidth, newHeight));

    //计算透视变换矩阵
    cv::Mat transform = getPerspectiveTransform(srcTriangle, dstTriangle);
    //透视变换（参数为输入图像、输出图像、3*3变换矩阵、目标图像大小）
    warpPerspective(srcBitmapMat, dstBitmapMat, transform, dstBitmapMat.size());
    //将Mat转换为bitmap对象
    return MatToUIImage(dstBitmapMat);
}

+ (UIImage*)rotate:(UIImage*)src imageOrientation:(UIImageOrientation)imageOrientation{
    // 获取原始图片的大小和方向
    CGSize srcSize = CGSizeMake(CGImageGetWidth(src.CGImage), CGImageGetHeight(src.CGImage));
    UIImageOrientation orientation = imageOrientation;
    // 根据方向计算旋转后的图片的大小
    CGSize dstSize;
    if (orientation == UIImageOrientationLeft || orientation == UIImageOrientationRight || orientation == UIImageOrientationLeftMirrored || orientation == UIImageOrientationRightMirrored) {
        dstSize = CGSizeMake(srcSize.height, srcSize.width);
    } else {
        dstSize = srcSize;
    }
    // 创建一个bitmap的context
    // 并把它设置成为当前正在使用的context
    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    CGContextRef context = CGBitmapContextCreate(NULL, dstSize.width, dstSize.height, 8, 0, colorSpace, kCGImageAlphaPremultipliedFirst);
    CGColorSpaceRelease(colorSpace);
    // 设置坐标系变换
    CGContextTranslateCTM(context, 0.5 * dstSize.width, 0.5 * dstSize.height);
    CGContextScaleCTM(context, 1.0, -1.0);
    // 根据方向旋转context
    switch (orientation) {
        case UIImageOrientationRight:
            CGContextRotateCTM(context, -M_PI_2);
            break;
        case UIImageOrientationLeft:
            CGContextRotateCTM(context, M_PI_2);
            break;
        case UIImageOrientationDown:
            CGContextRotateCTM(context, M_PI);
            break;
        case UIImageOrientationUp:
            break;
        default:
            break;
    }
    // 绘制原始图片到context上
    CGContextDrawImage(context, CGRectMake(-0.5 * srcSize.width, -0.5 * srcSize.height, srcSize.width, srcSize.height), src.CGImage);
    // 从当前context中创建一个图片
    CGImageRef imageRef = CGBitmapContextCreateImage(context);
    UIImage *img = [UIImage imageWithCGImage:imageRef];
    // 释放资源
    CGContextRelease(context);
    CGImageRelease(imageRef);
    // 返回旋转后的图片
    return img;
}


@end
