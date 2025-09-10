//
//  Scanner.m
//  OpenCVDemo
//
//  Created by rbq on 2021/5/25.
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
#include <opencv2/core/operations.hpp>
#import <opencv2/core/core_c.h>

#include <algorithm>

#import "Scanner.h"
#import <UIKit/UIKit.h>

@implementation Scanner

+(UIImage *)thresholdImage:(UIImage *)srcBitmap{
    
    cv::Mat srcMat;
    UIImageToMat(srcBitmap, srcMat);
    //  图像缩放
    cv::Mat image,scanImage;
    image = resizeImage(srcMat);
    //图像预处理
    scanImage = preProcessImage(srcMat);
    return MatToUIImage(scanImage);
}

/**
* 扫描图片，并返回检测到的矩形的四个顶点的坐标
*/
+(NSArray<NSString *> *)scanPoint:(UIImage *)srcBitmap{
    
    cv::Mat srcMat;
    UIImageToMat(srcBitmap, srcMat);
    //  图像缩放
    cv::Mat image,scanImage;
    image = resizeImage(srcMat);
    //图像预处理
    scanImage = preProcessImage(srcMat);

    //检测到的轮廓
    std::vector<std::vector<cv::Point>> contours;
    //提取边框
    findContours(scanImage, contours,CV_RETR_EXTERNAL, CV_CHAIN_APPROX_NONE);
//    findContours(scanImage, contours,CV_RETR_LIST, CV_CHAIN_APPROX_NONE);

    //按面积排序，最后只取面积最大的那个
    if (contours.size()==0) {
        
        std::vector<cv::Point> result = fullPoint(image);
        NSMutableArray<NSString *> *points = [[NSMutableArray<NSString *> alloc] init];
        for (int i = 0; i < result.size(); i++) {
            
            [points addObject:NSStringFromCGPoint(CGPointMake(result[i].x, result[i].y))];
        }
        return points;
    }
    //取面积最大的
    //对所有轮廓按面积排序
    std::sort(contours.begin(), contours.end(), sortByArea);
    std::vector<cv::Point> contour = contours[0];
    //计算轮廓的周长,第二个参数表示是否为闭合曲线
    double arc = arcLength(contour, true);
    std::vector<cv::Point> outDP;
    //把连续光滑曲线折线化（参数为输入曲线、输出折线、判断点到相对应的线段的距离阈值，超过阈值舍弃，越小越解决曲线、曲线是否闭合）
    approxPolyDP(cv::Mat(contour), outDP, 0.01 * arc, true);
    //筛选去除相近的点
    std::vector<cv::Point> selectMat = selectPoints(outDP,1);
    
    NSLog(@"查询到点的个数%lu",selectMat.size());
    
    if (selectMat.size() == 4) {
        //  对最终检测出的四个点进行排序：左上、右上、右下、左下
        NSMutableArray<NSString *> *points = [[NSMutableArray<NSString *> alloc] init];
        std::vector<cv::Point> result = sortPointClockwise(selectMat);
        
        for (int i = 0; i < result.size(); i++) {
            
            [points addObject:NSStringFromCGPoint(CGPointMake(result[i].x, result[i].y))];
        }
        return [points copy];
        
    }else{
        
        std::vector<cv::Point> result = fullPoint(image);
        NSMutableArray<NSString *> *points = [[NSMutableArray<NSString *> alloc] init];
        for (int i = 0; i < result.size(); i++) {
            
            [points addObject:NSStringFromCGPoint(CGPointMake(result[i].x, result[i].y))];
        }
        return [points copy];
    }
}

static double angle(cv::Point pt1, cv::Point pt2, cv::Point pt0)
{
    double dx1 = pt1.x - pt0.x;
    double dy1 = pt1.y - pt0.y;
    double dx2 = pt2.x - pt0.x;
    double dy2 = pt2.y - pt0.y;
    return (dx1*dx2 + dy1*dy2)/sqrt((dx1*dx1 + dy1*dy1)*(dx2*dx2 + dy2*dy2) + 1e-10);
}

static std::vector<cv::Point> fullPoint(cv::Mat image)
{
    std::vector<cv::Point> rs;
    rs[0] = cv::Point(0, 0);
    rs[1] = cv::Point(image.cols, 0);
    rs[2] = cv::Point(image.cols, image.rows);
    rs[3] = cv::Point(0, image.rows);
    return rs;
}


/**
 * 计算并比较两种轮廓的面积
 */
static bool sortByArea(const std::vector<cv::Point> &v1, const std::vector<cv::Point> &v2) {
    double v1Area = fabs(contourArea(cv::Mat(v1)));
    double v2Area = fabs(contourArea(cv::Mat(v2)));
    return v1Area > v2Area;
}

/**
 *  为避免处理时间过长，先对图片进行压缩
 */
static cv::Mat resizeImage(cv::Mat src)
{
    int width = src.cols;
    int height = src.rows;
    int maxSize = MAX(width, height);
    if (maxSize > resizeThreshold) {
        float resizeScale = 1.0f * maxSize / resizeThreshold;
        width = (int) (width / resizeScale);
        height = (int) (height / resizeScale);
        cv::Size real_size = cv::Size(width, height);
        cv::Mat resizeMat;
        resize(src, resizeMat, real_size);

        return resizeMat;
    }
    return src;
}

/**
 * 对图像进行预处理：灰度化、高斯模糊、Canny边缘检测
 */
static cv::Mat preProcessImage(cv::Mat src)
{
    cv::Mat grayMat;
    //  注意RGB和BGR，影响很大
    cv::cvtColor(src, grayMat, cv::COLOR_RGBA2GRAY);

    cv::Mat blurMat;
    GaussianBlur(grayMat, blurMat, cv::Size(5,5),0);

    cv::Mat cannyMat;
    Canny(blurMat, cannyMat, 0, 5);

    cv::Mat thresholdMat;
    cv::threshold(cannyMat, thresholdMat, 0, 255, cv::THRESH_OTSU);
    
    return thresholdMat;
}

static std::vector<cv::Point> selectPoints(std::vector<cv::Point> points, int selectTimes) {
    if (points.size() > 4) {
        double arc = arcLength(points, true);
        std::vector<cv::Point>::iterator itor = points.begin();
        while (itor != points.end()) {
            if (points.size() == 4) {
                return points;
            }
            cv::Point &p = *itor;
            if (itor != points.begin()) {
                cv::Point &lastP = *(itor - 1);
                double pointLength = sqrt(pow((p.x-lastP.x),2) + pow((p.y-lastP.y),2));
                if(pointLength < arc * 0.01 * selectTimes && points.size() > 4) {
                    itor = points.erase(itor);
                    continue;
                }
            }
            itor++;
        }
        if (points.size() > 4) {
            return selectPoints(points, selectTimes + 1);
        }
    }
    return points;
}


/**
 * 对顶点进行排序
 */
static std::vector<cv::Point> sortPointClockwise(std::vector<cv::Point> &points) {
    
    if (points.size() != 4) {
            return points;
    }

    cv::Point unFoundPoint;
    std::vector<cv::Point> result = {unFoundPoint, unFoundPoint, unFoundPoint, unFoundPoint};

    long minDistance = -1;
    for(int j = 0; j < points.size(); j++) {
        cv::Point point = points[j];
        long distance = point.x * point.x + point.y * point.y;
        if(minDistance == -1 || distance < minDistance) {
            result[0] = point;
            minDistance = distance;
        }
    }
    if (result[0] != unFoundPoint) {
        cv::Point &leftTop = result[0];
        points.erase(std::remove(points.begin(), points.end(), leftTop));
        if ((pointSideLine(leftTop, points[0], points[1]) * pointSideLine(leftTop, points[0], points[2])) < 0) {
            result[2] = points[0];
        } else if ((pointSideLine(leftTop, points[1], points[0]) * pointSideLine(leftTop, points[1], points[2])) < 0) {
            result[2] = points[1];
        } else if ((pointSideLine(leftTop, points[2], points[0]) * pointSideLine(leftTop, points[2], points[1])) < 0) {
            result[2] = points[2];
        }
    }
    if (result[0] != unFoundPoint && result[2] != unFoundPoint) {
        cv::Point &leftTop = result[0];
        cv::Point &rightBottom = result[2];
        points.erase(std::remove(points.begin(), points.end(), rightBottom));
        if (pointSideLine(leftTop, rightBottom, points[0]) > 0) {
            result[1] = points[0];
            result[3] = points[1];
        } else {
            result[1] = points[1];
            result[3] = points[0];
        }
    }

    if (result[0] != unFoundPoint && result[1] != unFoundPoint && result[2] != unFoundPoint && result[3] != unFoundPoint) {
        return result;
    }

    return points;
}

static float pointSideLine(cv::Point lineP1, cv::Point lineP2, cv::Point point) {
    double x1 = lineP1.x;
    double y1 = lineP1.y;
    double x2 = lineP2.x;
    double y2 = lineP2.y;
    double x = point.x;
    double y = point.y;
    return (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1);
}



+(cv::Mat)cvMatWithImage:(UIImage *)image
{
    CGColorSpaceRef colorSpace = CGImageGetColorSpace(image.CGImage);
    CGFloat cols = image.size.width;
    CGFloat rows = image.size.height;
 
    cv::Mat cvMat(rows,cols,CV_8UC4); // 8 bits per component,4 channels
 
    CGContextRef contextRef = CGBitmapContextCreate(cvMat.data,// Pointer to backing data
                                                    cols,// WIDth of bitmap
                                                    rows,// Height of bitmap
                                                    8,// Bits per component
                                                    cvMat.step[0],// Bytes per row
                                                    colorSpace,// colorspace
                                                    kCGImageAlphaNoneSkipLast |
                                                    kCGBitmapByteOrderDefault); // Bitmap info flags
 
    CGContextDrawImage(contextRef,CGRectMake(0,0,cols,rows),image.CGImage);
    CGContextRelease(contextRef);
 
    return cvMat;
}
+(UIImage *)UIImageFromCVMat:(cv::Mat)cvMat
{
    NSData *data = [NSData dataWithBytes:cvMat.data length:cvMat.elemSize()*cvMat.total()];
    CGColorSpaceRef colorSpace;
    if ( cvMat.elemSize() == 1 ) {
        colorSpace = CGColorSpaceCreateDeviceGray();
    }
    else {
        colorSpace = CGColorSpaceCreateDeviceRGB();
    }
 
    //CFDataRef data;
    CGDataProviderRef provIDer = CGDataProviderCreateWithCFData( (CFDataRef) data ); // It SHOulD BE (__brIDge CFDataRef)data
    CGImageRef imageRef = CGImageCreate( cvMat.cols,cvMat.rows,8,8 * cvMat.elemSize(),cvMat.step[0],colorSpace,kCGImageAlphaNone|kCGBitmapByteOrderDefault,provIDer,nil,false,kCGRenderingIntentDefault );
    UIImage *finalimage = [UIImage imageWithCGImage:imageRef];
    CGImageRelease( imageRef );
    CGDataProviderRelease( provIDer );
    CGColorSpaceRelease( colorSpace );
    return finalimage;
}

@end
