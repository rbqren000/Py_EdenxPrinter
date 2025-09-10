//
//  OpenCVImageTool.m
//  baibao
//
//  Created by 阮巧华 on 2019/11/16.
//  Copyright © 2019 阮巧华. All rights reserved.
//
#include <opencv2/opencv.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/imgproc/types_c.h>
#include <opencv2/imgcodecs/ios.h>
#include <algorithm>


#import "OpenCVImageTool.h"

using namespace std;
using namespace cv;

@implementation OpenCVImageTool

+ (CGFloat)getTextPhotoAngle:(UIImage *)image {
    
    cv::Mat srcImage;
    UIImageToMat(image, srcImage);
    double value = CalcDegree(srcImage);
    return value;
}
/// 获取旋转后图片
+ (UIImage *)getRotateImage:(UIImage *)image degree:(CGFloat)degree {
    
    CGFloat radians = (M_PI * (-degree) / 180.0);
    // calculate the size of the rotated view's containing box for our drawing space
    UIView *rotatedViewBox = [[UIView alloc] initWithFrame:CGRectMake(0,0,image.size.width, image.size.height)];
    CGAffineTransform t = CGAffineTransformMakeRotation(radians);
    rotatedViewBox.transform = t;
    CGSize rotatedSize = rotatedViewBox.frame.size;
    
    // 创建一个RGB颜色空间对象
    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    // 分配一个足够容纳位图数据的内存缓冲区
    size_t bytesPerRow = rotatedSize.width * 4; // 每个像素占4个字节
    size_t byteCount = bytesPerRow * rotatedSize.height;
    void *bitmapData = malloc(byteCount);
    // 创建一个位图上下文对象，指定缩放因子为1，生成1倍高清图
    CGContextRef context = CGBitmapContextCreate(bitmapData, rotatedSize.width, rotatedSize.height, 8, bytesPerRow, colorSpace, kCGImageAlphaPremultipliedFirst | kCGBitmapByteOrder32Little);
    if (context == nil) {
        // 释放资源
        free(bitmapData);
        CGColorSpaceRelease(colorSpace);
        return nil;
    }
    
    // Move the origin to the middle of the image so we will rotate and scale around the center.
    CGContextTranslateCTM(context, rotatedSize.width/2, rotatedSize.height/2);
    
    // 旋转位图上下文
    CGContextRotateCTM(context, radians);
    
    // Now, draw the rotated/scaled image into the context
    CGContextScaleCTM(context, 1.0, -1.0);
    CGContextDrawImage(context, CGRectMake(-image.size.width / 2, -image.size.height / 2, image.size.width, image.size.height), [image CGImage]);
    
    // 从位图上下文中创建一个CGImage对象
    CGImageRef imageRef = CGBitmapContextCreateImage(context);
    // 从CGImage对象创建一个UIImage对象
    UIImage *newImage = [UIImage imageWithCGImage:imageRef];
    // 释放资源
    CGImageRelease(imageRef);
    CGContextRelease(context);
    free(bitmapData);
    CGColorSpaceRelease(colorSpace);
    
    return newImage;
}


/// 获取灰色图片
+ (UIImage *)getGrayImage:(UIImage *)originImage {
    
    cv::Mat img, grayImg, binImg;
    UIImageToMat(originImage, img);
    //灰度化
    cvtColor(img, grayImg, CV_BGR2GRAY);
    return MatToUIImage(grayImg);
}

/// 获取黑白图片
+ (UIImage *)getBlackWhiteImage:(UIImage *)originImage {
    
    Mat img, grayImg, binImg;
    UIImageToMat(originImage, img);
    // 灰度化
    cvtColor(img, grayImg, CV_BGR2GRAY);
    // 黑白
    threshold(grayImg, binImg, 128, 255, CV_THRESH_BINARY);
    return MatToUIImage(binImg);
}

+ (UIImage *)addLightImage:(UIImage *)originImage {
    
    Mat img, dst;
    UIImageToMat(originImage, img);
    
    add(img, img, dst);
    return MatToUIImage(dst);
}

/// 对比度
+ (UIImage *)addHstackImage:(UIImage *)originImage {
    
    Mat img, grayImg, res;
    UIImageToMat(originImage, img);
    
    cvtColor(img, grayImg, CV_BGR2YCrCb);

    vector<Mat> channels;
    split(grayImg, channels);

    // 直方图均衡化
    equalizeHist(channels[0], channels[0]);

    // 合并
    merge(channels, grayImg);
    
    // 彩色
    cvtColor(grayImg, res, CV_YCrCb2BGR);

    return MatToUIImage(res);
}

+ (NSArray<NSString *> *)getRectanglePoints:(UIImage *)originImage{
    
    Mat img, grayPic, binPic, cannyPic, res;
    UIImageToMat(originImage, img);
    // 灰度化
    cvtColor(img, grayPic, COLOR_BGR2GRAY);
    // 中值滤波
    medianBlur(grayPic, grayPic, 7);
    // 转为二值图片
    threshold(grayPic, binPic, 80, 255, THRESH_BINARY);
    // Canny边缘检测
    Canny(binPic, cannyPic, 200, 200*2.5);
    // 获取轮廓
    vector<vector<cv::Point>> contours;
    findContours(cannyPic, contours, RETR_CCOMP, CHAIN_APPROX_SIMPLE);
    // 获取最大的矩形
    vector<vector<cv::Point>> polyContours(contours.size());
    int maxArea = 0;
    for (int index = 0; index < contours.size(); index++){
        if (contourArea(contours[index]) > contourArea(contours[maxArea]))
            maxArea = index;
        approxPolyDP(contours[index], polyContours[index], 10, true);
    }
    // 获取顶点
    vector<int> hull;
    convexHull(polyContours[maxArea], hull, false);
    
    NSMutableArray<NSString *> *points = [NSMutableArray<NSString *> array];
    for (int i = 0; i < hull.size(); ++i){
        cv::Point point = polyContours[maxArea][i];
        CGPoint cgPoint = CGPointMake(point.x, point.y);
        [points addObject:NSStringFromCGPoint(cgPoint)];
    }
    
    if (points.count < 4 || points.count > 5) {
        return [self getRectanglePoints:originImage];
    }
    return points;
}

//度数转换
double DegreeTrans(double theta)
{
    double res = theta / CV_PI * 180;
    return res;
}
//通过霍夫变换计算角度
double CalcDegree(const cv::Mat &srcImage)
{
    cv::Mat midImage, dstImage;

    Canny(srcImage, midImage, 50, 200, 3);
    cvtColor(midImage, dstImage, CV_GRAY2BGR);

    //通过霍夫变换检测直线
    std::vector<cv::Vec2f> lines;
    HoughLines(midImage, lines, 1, CV_PI / 180, 300, 0, 0);//第5个参数就是阈值，阈值越大，检测精度越高
    //cout << lines.size() << endl;
    NSLog(@"总共有%lu行文本",lines.size());
    //由于图像不同，阈值不好设定，因为阈值设定过高导致无法检测直线，阈值过低直线太多，速度很慢
    //所以根据阈值由大到小设置了三个阈值，如果经过大量试验后，可以固定一个适合的阈值。

    if (!lines.size())
    {
        HoughLines(midImage, lines, 1, CV_PI / 180, 200, 0, 0);
    }
    //cout << lines.size() << endl;

    if (!lines.size())
    {
        HoughLines(midImage, lines, 1, CV_PI / 180, 150, 0, 0);
    }
    //cout << lines.size() << endl;
    if (!lines.size())
    {
        return 0;
    }

    float sum = 0;
    
    for (size_t i = 0; i < lines.size(); i++)
    {
        float theta = lines[i][1];
        //只选角度最小的作为旋转角度
        sum += theta;
    }
    
    float average = sum / lines.size(); //对所有角度求平均，这样做旋转效果会更好

    double angle = DegreeTrans(average) - 90;

    return angle;
}

+ (UIImage *)repayRedImage:(UIImage *)image {
    
    Mat img;
    UIImageToMat(image, img);
    
    Mat rbg;
    cvtColor(img, rbg, CV_RGBA2BGR);
        
    vector<Mat> channels;
    split(rbg, channels);
    Mat red = channels[2];
    Mat blue = channels[0];
    Mat green = channels[1];

    Mat red_binary;
    threshold(red, red_binary, 120, 255, CV_THRESH_BINARY);
    
    return MatToUIImage(red_binary);
}

+ (UIImage *)repayBuleImage:(UIImage *)image {
    
    Mat img;
    UIImageToMat(image, img);
    
    Mat rbg;
    cvtColor(img, rbg, CV_RGBA2BGR);
        
    vector<Mat> channels;
    split(rbg, channels);
    Mat red = channels[2];
    Mat blue = channels[0];
    Mat green = channels[1];

    Mat red_binary;
    threshold(blue, red_binary, 120, 255, CV_THRESH_BINARY);
    
    return MatToUIImage(red_binary);
}

@end
