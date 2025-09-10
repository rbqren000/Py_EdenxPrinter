//
//  OpenCVUtils.m
//  BelonPrinter
//
//  Created by rbq on 2021/1/21.
//  Copyright © 2021 rbq. All rights reserved.
//

// OpenCV的头文件应该在所有APPLE的头文件之前导入，不然会抛出异常，把OpenCV的头文件import调到最前面即可
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

#import "OpenCVUtils.h"
#import "RBQLog.h"
#import "CropperProcessor.h"


using namespace cv;

@implementation OpenCVUtils

+ (UIImage *)lightClearBackground:(UIImage *)image {
    // 检查image参数是否为空或无效
    NSAssert(image != nil, @"image parameter is nil");
    NSAssert([image isKindOfClass:[UIImage class]], @"image parameter is not a UIImage object");
    
    @autoreleasepool {
        cv::Mat src, gray, fc1, dst, dst3;
        UIImageToMat(image, src);
        size_t elemSize = src.elemSize();
        RBQLog3(@"elemSize:%zu",elemSize);
        if(elemSize == 1) {
            // 本来就是灰度图，直接复制
            src.copyTo(gray);
        } else {
            // 灰度处理
            cvtColor(src, gray, cv::COLOR_RGB2GRAY);
        }
        src.release(); // 释放src对象
        
        gray.convertTo(fc1, CV_32FC1, 1.0 / 255);
        gray.release(); // 释放gray对象
        
        dst = [self reduceBackgroundAlgorithm:fc1];
        fc1.release(); // 释放fc1对象
        
        dst3 = [self colorGradation:dst];
        dst.release(); // 释放dst对象
        
        // 使用自动释放的UIImage对象
        UIImage *newimage = [self RBQMatToUIImage:dst3 scale:image.scale imageOrientation:image.imageOrientation];
        dst3.release(); // 释放dst3对象
        return newimage;
    }
}

+ (UIImage *)deepClearBackground:(UIImage *)image {
    // 检查image参数是否为空或无效
    NSAssert(image != nil, @"image parameter is nil");
    NSAssert([image isKindOfClass:[UIImage class]], @"image parameter is not a UIImage object");
    
    @autoreleasepool {
        cv::Mat src, gray, fc1, dst, dst3, ts;
        UIImageToMat(image, src);
        size_t elemSize = src.elemSize();
        RBQLog3(@"elemSize:%zu",elemSize);
        if(elemSize == 1) {
            // 本来就是灰度图，直接复制
            src.copyTo(gray);
        } else {
            // 灰度处理
            cvtColor(src, gray, cv::COLOR_RGB2GRAY);
        }
        src.release(); // 释放src对象
        
        gray.convertTo(fc1, CV_32FC1, 1.0 / 255);
        gray.release(); // 释放gray对象
        
        dst = [self reduceBackgroundAlgorithm:fc1];
        fc1.release(); // 释放fc1对象
        
        dst3 = [self colorGradation:dst];
        dst.release(); // 释放dst对象
        
        threshold(dst3, ts, 1, 255, cv::THRESH_BINARY | cv::THRESH_OTSU);
        dst3.release(); // 释放dst3对象
        
        // 使用自动释放的UIImage对象
        UIImage *newimage = [self RBQMatToUIImage:ts scale:image.scale imageOrientation:image.imageOrientation];
        ts.release(); // 释放ts对象
        return newimage;
    }
}


+ (UIImage *)lightClearRedBackground:(UIImage *)image {
    // 检查image参数是否为空或无效
    NSAssert(image != nil, @"image parameter is nil");
    NSAssert([image isKindOfClass:[UIImage class]], @"image parameter is not a UIImage object");
    
    @autoreleasepool {
        cv::Mat src, src3channels, hsv, mask1, mask2, maskImg, kernel, result, gray, fc1, dst, dst3;
        UIImageToMat(image, src);
        size_t elemSize = src.elemSize();
        RBQLog3(@"elemSize:%zu",elemSize);
        if(elemSize == 1) {
            // 本来就是灰度图，转换为RGBA格式
            cv::Mat temp;
            cvtColor(src, temp, cv::COLOR_GRAY2RGBA);
            temp.copyTo(src);
            temp.release(); // 释放temp对象
        }
        // 转换为RGB格式
        cvtColor(src, src3channels, cv::COLOR_RGBA2RGB);
        src.release(); // 释放src对象
        
        // 转换为HSV格式
        cvtColor(src3channels, hsv, cv::COLOR_RGB2HSV);
        
        // 根据HSV值筛选红色区域
        inRange(hsv, cv::Scalar(0, 43, 46), cv::Scalar(10, 255, 255), mask1);
        inRange(hsv, cv::Scalar(156, 43, 46), cv::Scalar(180, 255, 255), mask2);
        hsv.release(); // 释放hsv对象
        
        // 合并两个掩码
        add(mask1, mask2, maskImg);
        mask1.release(); // 释放mask1对象
        mask2.release(); // 释放mask2对象
        
        // 创建一个3x3的矩形结构元
        kernel = getStructuringElement(cv::MORPH_RECT, cv::Size(3, 3));
        // 对掩码进行膨胀处理
        dilate(maskImg, maskImg, kernel);
        kernel.release(); // 释放kernel对象
        
        // 对原图进行修复处理，去除红色背景
        inpaint(src3channels, maskImg, result, 2, cv::INPAINT_NS);
        maskImg.release(); // 释放maskImg对象
        src3channels.release(); // 释放src3channels对象
        // 转换为灰度图
        cvtColor(result, gray, cv::COLOR_RGB2GRAY);
        result.release(); // 释放result对象
        // 转换为浮点数类型
        gray.convertTo(fc1, CV_32FC1, 1.0 / 255);
        gray.release(); // 释放gray对象
        // 使用自定义的算法减少背景噪声
        dst = [self reduceBackgroundAlgorithm:fc1];
        fc1.release(); // 释放fc1对象
        
        // 使用自定义的算法增加颜色渐变效果
        dst3 = [self colorGradation:dst];
        dst.release(); // 释放dst对象
        
        // 使用自动释放的UIImage对象
        UIImage *newimage = [self RBQMatToUIImage:dst3 scale:image.scale imageOrientation:image.imageOrientation];
        dst3.release(); // 释放dst3对象
        return newimage;
    }
}


+ (UIImage *)deepClearRedBackground:(UIImage *)image {
    // 检查image参数是否为空或无效
    NSAssert(image != nil, @"image parameter is nil");
    NSAssert([image isKindOfClass:[UIImage class]], @"image parameter is not a UIImage object");
    
    @autoreleasepool {
        cv::Mat src, src3channels, hsv, mask1, mask2, maskImg, kernel, result, gray, fc1, dst, dst3, ts;
        UIImageToMat(image, src);
        size_t elemSize = src.elemSize();
        RBQLog3(@"elemSize:%zu",elemSize);
        if(elemSize == 1) {
            // 本来就是灰度图，转换为RGBA格式
            cv::Mat temp;
            cvtColor(src, temp, cv::COLOR_GRAY2RGBA);
            temp.copyTo(src);
            temp.release(); // 释放temp对象
        }
        // 转换为RGB格式
        cvtColor(src, src3channels, cv::COLOR_RGBA2RGB);
        src.release(); // 释放src对象
        
        // 转换为HSV格式
        cvtColor(src3channels, hsv, cv::COLOR_RGB2HSV);
        
        // 根据HSV值筛选红色区域
        inRange(hsv, cv::Scalar(0, 43, 46), cv::Scalar(10, 255, 255), mask1);
        inRange(hsv, cv::Scalar(156, 43, 46), cv::Scalar(180, 255, 255), mask2);
        hsv.release(); // 释放hsv对象
        
        // 合并两个掩码
        add(mask1, mask2, maskImg);
        mask1.release(); // 释放mask1对象
        mask2.release(); // 释放mask2对象
        
        // 创建一个3x3的矩形结构元
        kernel = getStructuringElement(cv::MORPH_RECT, cv::Size(3, 3));
        // 对掩码进行膨胀处理
        dilate(maskImg, maskImg, kernel);
        kernel.release(); // 释放kernel对象
        
        // 对原图进行修复处理，去除红色背景
        inpaint(src3channels, maskImg, result, 2, cv::INPAINT_NS);
        maskImg.release(); // 释放maskImg对象
        src3channels.release(); // 释放src3channels对象
        // 转换为灰度图
        cvtColor(result, gray, cv::COLOR_RGB2GRAY);
        result.release(); // 释放result对象
        
        // 转换为浮点数类型
        gray.convertTo(fc1, CV_32FC1, 1.0 / 255);
        gray.release(); // 释放gray对象
        
        // 使用自定义的算法减少背景噪声
        dst = [self reduceBackgroundAlgorithm:fc1];
        fc1.release(); // 释放fc1对象
        
        // 使用自定义的算法增加颜色渐变效果
        dst3 = [self colorGradation:dst];
        dst.release(); // 释放dst对象
        
        // 使用OTSU算法对图像进行二值化
        threshold(dst3, ts, 1, 255, cv::THRESH_BINARY | cv::THRESH_OTSU);
        dst3.release(); // 释放dst3对象
        
        // 使用自动释放的UIImage对象
        UIImage *newimage = [self RBQMatToUIImage:ts scale:image.scale imageOrientation:image.imageOrientation];
        ts.release(); // 释放ts对象
        return newimage;
    }
}
/*
+ (UIImage *)processImageForTextDetail:(UIImage *)image {
    // 将UIImage转换为灰度Mat
    Mat src;
    UIImageToMat(image, src, CV_8UC1);
    
    // 检查图像是否加载成功
    if(src.empty()) {
        NSLog(@"Image not loaded.");
        return nil;
    }
    // 转换为灰度图像
    Mat gray;
    if(src.channels() > 1) {
        cvtColor(src, gray, COLOR_BGR2GRAY);
    } else {
        gray = src;
    }
    
    // 应用自适应阈值进行二值化
    Mat binary;
    double maxValue = 255;
    int adaptiveMethod = ADAPTIVE_THRESH_GAUSSIAN_C;
    int thresholdType = THRESH_BINARY;
    int blockSize = 11; // 必须是奇数
    double C = 2; // 从平均值或加权平均值中减去的值
    adaptiveThreshold(gray, binary, maxValue, adaptiveMethod, thresholdType, blockSize, C);
    
    // 应用形态学操作来增强文字的清晰度
    Mat morph;
    Mat element = getStructuringElement(MORPH_RECT, cv::Size(3, 3));
    morphologyEx(binary, morph, MORPH_CLOSE, element);
    
    // 将处理后的Mat转换回UIImage
    UIImage *resultImage = MatToUIImage(morph);
    return resultImage;
}
*/
+ (UIImage *)processImageForTextDetail:(UIImage *)image {
    // 将UIImage转换为灰度Mat
    Mat src;
    UIImageToMat(image, src, CV_8UC1);
    
    // 检查图像是否加载成功
    if(src.empty()) {
        NSLog(@"Image not loaded.");
        return nil;
    }
    // 转换为灰度图像
    Mat gray;
    if(src.channels() > 1) {
        cvtColor(src, gray, COLOR_BGR2GRAY);
    } else {
        gray = src;
    }
    
    // 应用自适应阈值进行二值化，调整C的值以减少文字颜色变浅
    Mat binary;
    double maxValue = 255;
    int adaptiveMethod = ADAPTIVE_THRESH_GAUSSIAN_C;
    int thresholdType = THRESH_BINARY;
    int blockSize = 11; // 必须是奇数
    double C = 10; // 增加这个值以减少文字颜色变浅
    adaptiveThreshold(gray, binary, maxValue, adaptiveMethod, thresholdType, blockSize, C);
    
    // 应用形态学操作来增强文字的清晰度，使用更小的核以避免过度处理
    Mat morph;
    Mat element = getStructuringElement(MORPH_RECT, cv::Size(2, 2)); // 使用更小的核
    morphologyEx(binary, morph, MORPH_CLOSE, element);
    
    // 将处理后的Mat转换回UIImage
    UIImage *newImage = MatToUIImage(morph);
    return newImage;
}


// 实现图片素描处理的方法
// 返回值: 一个UIImage对象，表示素描后的图片，如果失败则返回原图片
+ (UIImage *)sketchImage:(UIImage *)image {
    @autoreleasepool {
        cv::Mat src, blur, edge, kernel, morph, sketch, laplace, sharp;
        UIImageToMat(image, src);
        if (src.elemSize() != 1) {
            cv::cvtColor(src, src, cv::COLOR_BGR2GRAY);
        }
        cv::GaussianBlur(src, blur, cv::Size(5, 5), 1.5);
        src.release(); // 释放src对象
        
        cv::Canny(blur, edge, 30, 90);
        blur.release(); // 释放blur对象
        
        kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(3, 3));
        cv::morphologyEx(edge, morph, cv::MORPH_CLOSE, kernel);
        edge.release(); // 释放edge对象
        kernel.release(); // 释放kernel对象
        
        cv::bitwise_not(morph, sketch);
        morph.release(); // 释放morph对象
        
        cv::Laplacian(sketch, laplace, CV_8U, 3);
        cv::addWeighted(sketch, 1.0, laplace, -0.5, 0, sharp);
        sketch.release(); // 释放sketch对象
        laplace.release(); // 释放laplace对象
        
        UIImage *newImage = [self RBQMatToUIImage:sharp scale:image.scale imageOrientation:image.imageOrientation];
//        sharp.release(); // 释放sharp对象
        return newImage;
    }
}
/**素描**/
+ (UIImage *)sketchEffect:(UIImage *)image {
    @autoreleasepool {
        
        cv::Mat src;
        UIImageToMat(image, src);

//        cv::Mat gray;
//        cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);
        cv::Mat gray;
        if (src.channels() != 1) {
            cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);
        } else {
            gray = src.clone(); // 如果是单通道灰度图像，直接使用src
        }
        src.release(); // 释放src, 因为已经用灰度图gray替换

        cv::Mat blurred;
        cv::GaussianBlur(gray, blurred, cv::Size(3, 3), 0);
        gray.release(); // 释放gray, 因为已经用模糊图blurred替换

        cv::Mat gradientX, gradientY;
        cv::Sobel(blurred, gradientX, CV_16S, 1, 0);
        cv::Sobel(blurred, gradientY, CV_16S, 0, 1);
        blurred.release(); // 释放blurred, 因为已经用梯度图gradientX和gradientY替换

        cv::Mat absGradientX, absGradientY;
        cv::convertScaleAbs(gradientX, absGradientX);
        gradientX.release(); // 释放gradientX, 因为已经用绝对值梯度图absGradientX替换
        cv::convertScaleAbs(gradientY, absGradientY);
        gradientY.release(); // 释放gradientY, 因为已经用绝对值梯度图absGradientY替换

        cv::Mat sketch;
        cv::addWeighted(absGradientX, 0.5, absGradientY, 0.5, 0, sketch);
        absGradientX.release(); // 释放absGradientX, 因为已经用素描图sketch替换
        absGradientY.release(); // 释放absGradientY, 因为已经用素描图sketch替换

        cv::bitwise_not(sketch, sketch); // 反转图像以获得白底的素描效果

        // UIImage *resultImage = MatToUIImage(sketch);
        UIImage *resultImage = [self RBQMatToUIImage:sketch scale:image.scale imageOrientation:image.imageOrientation];
//        sketch.release(); // 释放sketch, 因为已经完成所有操作

        return resultImage;
    }
}

//颜色翻转
+ (UIImage *)invertColor:(UIImage *)image {
    @autoreleasepool {
        cv::Mat src;
        UIImageToMat(image, src);
        
//        cv::Mat gray;
//        cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);
//        src.release(); // 释放src, 因为已经用灰度图gray替换

//        cv::Mat invertedMat;
        // 创建一个与输入图像大小相同的输出图像
        //经测试 bitwise_not 在ios中就是个坑，bitwise_not可能会去计算透明度那个，非透明的图片，经过这个函数运算后把图片变成了透明颜色了
//        cv::bitwise_not(src, invertedMat);
        for (int y = 0; y < src.rows; y++) {
            for (int x = 0; x < src.cols; x++) {
                cv::Vec4b &pixel = src.at<cv::Vec4b>(y, x);
                pixel[0] = 255 - pixel[0]; // 蓝色 channel
                pixel[1] = 255 - pixel[1]; // 绿色 channel
                pixel[2] = 255 - pixel[2]; // 红色 channel
//                pixel[3] = 255 - pixel[3]; // 透明 channel
            }
        }
//        src.release();// 释放gray
        // 转换回 UIImage
        UIImage *newImage = [self RBQMatToUIImage:src scale:image.scale imageOrientation:image.imageOrientation];
        return newImage;
    }
}

+ (UIImage *)invertColors:(UIImage *)image {
    @autoreleasepool {
        // 将 UIImage 转换为 cv::Mat
        cv::Mat src;
        UIImageToMat(image, src);
        // 检查图片是否加载成功
        if (src.empty()) {
            return nil;
        }
        // 分离 alpha 通道
        cv::Mat alphaChannel;
        if (src.channels() == 4) {
            std::vector<cv::Mat> channels;
            cv::split(src, channels);
            alphaChannel = channels[3];
            channels.pop_back();
            cv::merge(channels, src);

            // 释放不必要的通道
            for (cv::Mat& channel : channels) {
                channel.release();
            }
        }
        // 反色处理
        cv::Mat invertedMat;
        cv::bitwise_not(src, invertedMat);
        // 释放原始的 mat
        src.release();
        // 如果有 alpha 通道，合并 alpha 通道
        if (!alphaChannel.empty()) {
            std::vector<cv::Mat> channelsVec;
            cv::split(invertedMat, channelsVec);   // 分离反色后的通道
            channelsVec.push_back(alphaChannel);   // 将 alpha 通道加回
            cv::merge(channelsVec, invertedMat);   // 合并通道
            // 释放不必要的通道
            for (cv::Mat& channel : channelsVec) {
                channel.release();
            }
        }
        // 释放 alpha 通道
        alphaChannel.release();
        // 将处理后的 cv::Mat 转换回 UIImage
        UIImage *invertedImage = MatToUIImage(invertedMat);
        // 释放反色后的 mat
        invertedMat.release();
        return invertedImage;
    }
}



// 定义一个函数，用于清除图片中的前景文字，返回一个修复后的图片
+ (UIImage *)clearForeground:(UIImage *)image {
    @autoreleasepool {
        cv::Mat src, gray, blurred, edges, kernel, dilated, result, repaired;
        UIImageToMat(image, src);
        
        cvtColor(src, gray, cv::COLOR_RGBA2GRAY);
        src.release(); // 释放src对象
        
        GaussianBlur(gray, blurred, cv::Size(3, 3), 0);
        gray.release(); // 释放gray对象
        
        Canny(blurred, edges, 50, 150);
        blurred.release(); // 释放blurred对象
        
        kernel = getStructuringElement(cv::MORPH_RECT, cv::Size(3, 3));
        dilate(edges, dilated, kernel);
        edges.release(); // 释放edges对象
        
        bitwise_and(src, src, result, dilated);
        dilated.release(); // 释放dilated对象
        
        inpaint(src, result, repaired, 3, cv::INPAINT_TELEA);
        result.release(); // 释放result对象
        
        UIImage *newImage = [self RBQMatToUIImage:repaired scale:image.scale imageOrientation:image.imageOrientation];
        repaired.release(); // 释放repaired对象
        return newImage;
    }
}

/**图像转换为具有渐变效果的图像**/
+(cv::Mat)colorGradation:(cv::Mat)src{
    @autoreleasepool {
        cv::Mat dst;
        cv::Mat rDiff,temp1;
        src.convertTo(src,CV_32FC1);
        int HighLight=255;
        int Shadow=120;
        int Diff=HighLight-Shadow;
        subtract(src,cv::Scalar(Shadow),rDiff);
        rDiff.convertTo(temp1,CV_32FC1, 255.0 / Diff);
        rDiff.release();
        temp1.convertTo(dst,CV_8UC1);
        temp1.release();
        return dst;
    }
}

/**
 blur:均值滤波也成线性滤波
 其采用的主要方法为邻域平均法。线性滤波的基本原理是用原图像中某个像素临近值的均值代替原图像中的像素值。即滤波器的核（kernel）中所有的系数都相等，然后用该核去对图像做卷积。

 优点: 在一定程度上拉小灰度差异，减少噪声影响。对高斯噪声的表现比较好。
 缺点: 对图像的边缘处也做均值，导致边缘处变模糊。对椒盐噪声的表现比较差。
 */
+(cv::Mat)reduceBackgroundAlgorithm:(cv::Mat)src{
    // 检查src参数是否为空或无效
    CV_Assert(!src.empty());
    @autoreleasepool {
        cv::Mat dst3;
        cv::Mat gauss, dst2;
        // 使用均值滤波器模糊图像，减少噪声
        blur(src, gauss, cv::Size(101, 101));
        // 除法函数，增强图像的对比度
        divide(src, gauss, dst2);
        gauss.release();
        // 使用自定义的方法锐化图像，提高图像的清晰度
        dst2 = [self ImageSharp:dst2 amount:101];
        // 转换为8位无符号整数类型，方便显示或保存
        dst2.convertTo(dst3, CV_8UC1, 255);
        dst2.release();
        return dst3;
    }
}

/**
 GaussianBlur 高斯滤波
 高斯滤波是一种线性平滑滤波，适用于消除高斯噪声，对整幅图像进行加权平均的过程，每一个像素点的值，都由其本身和邻域内的其他像素值经过加权平均后得到。

 高斯模糊的卷积核里的数值是满足高斯分布，相当于更重视中间的，离得越近的像素点发挥的作用越大。

 高斯核主要取决于σ。如果σ越小，高斯分布中心区域更加聚集，平滑效果越差；反之，则更离散，平滑效果越明显。
 */
/**
 锐化图片
 */
+ (cv::Mat)ImageSharp:(cv::Mat)src amount:(int)nAmount {
    @autoreleasepool {
        cv::Mat dst;
        cv::Mat imgBlurred, temp_sub;
        double sigma = 3;
        float amount = nAmount / 100.0f;
        GaussianBlur(src, imgBlurred, cv::Size(7, 7), sigma, sigma, 4);
        subtract(src, imgBlurred, temp_sub);
        imgBlurred.release();
        addWeighted(src, 1, temp_sub, amount, 0, dst);
        temp_sub.release();
        return dst;
    }
}

+(UIImage *)createMultiImgToOne:(UIImage *)img imgs:(NSMutableArray<UIImage *> *)images {
    
    cv::Mat src,dst,rs;
    UIImageToMat(img, src);
    size_t elemSize = src.elemSize();
    RBQLog3(@"elemSize:%zu",elemSize);
    int cols = src.cols;
    int rows = src.rows;
    for (UIImage *_img in images) {
        UIImageToMat(_img, dst);
        resize(dst, rs, cv::Size(cols,rows));
        rs.copyTo(src);
    }
    UIImage *newimage = MatToUIImage(src);
    return newimage;
}

+(UIImage *)rectifyImg:(UIImage *)image {
    cv::Mat cvImage;
    UIImageToMat(image, cvImage);
    if (cvImage.empty()) {
        return nil;
    }
    
    cv::Mat shrinkPic;
    cv::pyrDown(cvImage, shrinkPic);
    
    int shrinkCount = (image.size.width / 500);
    int multi = 2;
    if (shrinkCount > 1) {
        shrinkCount = shrinkCount / 2;
        multi = pow(2, shrinkCount + 1);
        for (int i = 0; i < shrinkCount; i++) {
            cv::pyrDown(shrinkPic, shrinkPic);
        }
    }
    
    cv::Mat greyPic, sobPic,enhancePic, threshPic;

    cv::cvtColor(shrinkPic, greyPic, cv::COLOR_RGB2GRAY);
    
    // 边缘直方图法，采用sobel算子提取边缘线，然后水平，垂直分别做直方图
    cv::Mat grabX, grabY;
    cv::Sobel(greyPic, grabX, CV_32F, 1, 0);
    cv::Sobel(greyPic, grabY, CV_32F, 0, 1);
    cv::subtract(grabX, grabY, sobPic);
    cv::convertScaleAbs(sobPic, sobPic);
    
    // 填充空白区域，增强对比度
    cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(25, 25));
    cv::morphologyEx(sobPic, enhancePic, cv::MORPH_CLOSE, kernel);
    
    // 去除噪声
    cv::blur(sobPic, threshPic, cv::Size(5,5));
    cv::threshold(threshPic, threshPic, 30, 255, cv::THRESH_BINARY);//90
    
//    return MatToUIImage(threshPic);
    
    // 找出轮廓区域
    std::vector<std::vector<cv::Point>> contours;
    std::vector<cv::Vec4i> hierarchy;
    cv::findContours(threshPic, contours, hierarchy, cv::RETR_CCOMP, cv::CHAIN_APPROX_SIMPLE);
    
    // 求所有形状的最小外接矩形中最大的一个
    cv::RotatedRect box;
    for( int i = 0; i < contours.size(); i++ ) {
        cv::RotatedRect rect = cv::minAreaRect(cv::Mat(contours[i]));
        if (box.size.width < rect.size.width) {
            box = rect;
        }
    }
    
    // 画出来矩形和4个点, 供调试。此部分代码可以不要
    cv::Mat drawing = cv::Mat::zeros(threshPic.rows, threshPic.cols, CV_8UC3);
    cv::Scalar color = cv::Scalar( rand() & 255, rand() & 255, rand() & 255 );
    cv::Point2f rect_points[4];
    box.points( rect_points );
    for (int j = 0; j < 4; j++)
    {
        line( drawing, rect_points[j], rect_points[(j+1)%4], color );
        circle(drawing, rect_points[j], 10, color, 2);
    }
    // 仿射变换
    cv::Point2f corners[4], canvas[4], tmp[4];
    
    // 固定输出尺寸，可以由外部传入
    cv::Size real_size = cv::Size(500, 40);
    
    canvas[0] = cv::Point2f(0, 0);
    canvas[1] = cv::Point2f(real_size.width,0);
    canvas[2] = cv::Point2f(real_size.width, real_size.height);
    canvas[3] = cv::Point2f(0, real_size.height);
    
    box.points(tmp);
    
    bool sorted = false;
    int n = 4;
    while (!sorted){
        for (int i = 1; i < n; i++){
            sorted = true;
            if (tmp[i-1].x > tmp[i].x){
                swap(tmp[i-1], tmp[i]);
                sorted = false;
            }
        }
        n--;
    }
    if (tmp[0].y < tmp[1].y){
        corners[0] = tmp[0];
        corners[3] = tmp[1];
    }
    else{
        corners[0] = tmp[1];
        corners[3] = tmp[0];
    }
    
    if (tmp[2].y < tmp[3].y){
        corners[1] = tmp[2];
        corners[2] = tmp[3];
    }
    else{
        corners[1] = tmp[3];
        corners[2] = tmp[2];
    }
    for (int i = 0; i < 4; i++){
        corners[i] = cv::Point2f(corners[i].x * multi, corners[i].y * multi); //恢复坐标到原图
    }
    
    cv::Mat result;
    cv::Mat M = cv::getPerspectiveTransform(corners, canvas);
    cv::warpPerspective(cvImage, result, M, real_size);
    return MatToUIImage(result);
}

+(UIImage *)amendImgByOutLine:(UIImage *)image{
    
    cv::Mat srcImg,gray,binImg;
    UIImageToMat(image, srcImg);
    size_t elemSize = srcImg.elemSize();
    if(elemSize==1){
        //说明本来就是灰度图
        srcImg.copyTo(gray);
    }else{
        // 灰度处理（去除图片的色彩和光亮）
        RBQLog3(@"xxxxx 1");
        cvtColor(srcImg,gray,cv::COLOR_RGB2GRAY);
    }
    //二值化
    threshold(gray, binImg, 100, 200, CV_THRESH_BINARY);

    std::vector<std::vector<cv::Point>> contours;
    std::vector<cv::Vec4i> hierarchy;
    
    //注意第5个参数为CV_RETR_EXTERNAL，只检索外框
    findContours(binImg, contours, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_NONE); //找轮廓
    for (int i = 0; i < contours.size(); i++)
    {
        //需要获取的坐标
        cv::Point2f rectpoint[4];
        cv::RotatedRect rect = cv::minAreaRect(cv::Mat(contours[i]));

        rect.points(rectpoint); //获取4个顶点坐标
        //与水平线的角度
        float angle = rect.angle;

        int line1 = sqrt((rectpoint[1].y - rectpoint[0].y)*(rectpoint[1].y - rectpoint[0].y) + (rectpoint[1].x - rectpoint[0].x)*(rectpoint[1].x - rectpoint[0].x));
        int line2 = sqrt((rectpoint[3].y - rectpoint[0].y)*(rectpoint[3].y - rectpoint[0].y) + (rectpoint[3].x - rectpoint[0].x)*(rectpoint[3].x - rectpoint[0].x));
        //rectangle(binImg, rectpoint[0], rectpoint[3], Scalar(255), 2);
        //面积太小的直接pass
        if (line1 * line2 < 600)
        {
            continue;
        }

        //为了让正方形横着放，所以旋转角度是不一样的。竖放的，给他加90度，翻过来
        if (line1 > line2)
        {
            angle = 90 + angle;
        }

        //新建一个感兴趣的区域图，大小跟原图一样大
        cv::Mat RoiSrcImg = cv::Mat( srcImg.rows,srcImg.cols, CV_8UC3 );//注意这里必须选CV_8UC3
        RoiSrcImg.setTo(0); //颜色都设置为黑色
        //imshow("新建的ROI", RoiSrcImg);
        //对得到的轮廓填充一下
        drawContours(binImg, contours, -1, cv::Scalar(255),cv::FILLED);

        //抠图到RoiSrcImg
        srcImg.copyTo(RoiSrcImg, binImg);

        //创建一个旋转后的图像
        cv::Mat RatationedImg = cv :: Mat(RoiSrcImg.rows,RoiSrcImg.cols, CV_8UC1 );
        RatationedImg.setTo(0);
        //对RoiSrcImg进行旋转
        cv::Point2f center = rect.center;  //中心点
        cv::Mat M2 = getRotationMatrix2D(center, angle, 1);//计算旋转加缩放的变换矩阵
        //仿射变换
        warpAffine(RoiSrcImg, RatationedImg, M2, RoiSrcImg.size(),1, 0, cv::Scalar(0));
        //对旋转后的图片进行轮廓提取
        std::vector<std::vector<cv::Point>> contours2;
        cv::Mat SecondFindImg;
        cvtColor(M2, SecondFindImg, cv::COLOR_BGR2GRAY);  //灰度化
        threshold(SecondFindImg, SecondFindImg, 80, 200, CV_THRESH_BINARY);
        findContours(SecondFindImg, contours2, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_NONE);

        for (int j = 0; j < contours2.size(); j++)
        {
            //这时候其实就是一个长方形了，所以获取rect
            cv::Rect rect = boundingRect(cv::Mat(contours2[j]));
            //面积太小的轮廓直接pass,通过设置过滤面积大小，可以保证只拿到外框
            if (rect.area() < 600)
            {
                continue;
            }
            cv::Mat dstImg = M2(rect);
            
            UIImage *newImage = MatToUIImage(dstImg);
            
            return newImage;
        }
        
    }
    return nil;
}

/**
 缩放图片
 */
+(UIImage *)resizeBitmap:(UIImage*)bitmap width:(int)newWidth height:(int)newHeight {

    int width = bitmap.size.width;
    int height = bitmap.size.height;

    RBQLog3(@"opencv 缩放前 width:%d ;height:%d",width,height);
    
    cv::Mat src,scaleMat;
    UIImageToMat(bitmap, src);
    
    resize(src, scaleMat, cv::Size(newWidth,newHeight));
    
    UIImage *newimage = MatToUIImage(scaleMat);

    return newimage;
}

+(UIImage *)subImage:(UIImage *)image1 image2:(UIImage *)image2{
    
    cv::Mat mat1,mat2,subMat;
    UIImageToMat(image1, mat1);
    UIImageToMat(image2, mat2);
    
//    cv::Rect rect = cv::Rect(0, 0, mat1.cols, mat1.rows);
//    subMat = mat1.submat(rec);
//    subMat = mat1(rect); //设置感兴趣区域
    mat2.copyTo(mat1);
    UIImage *newimage = MatToUIImage(mat1);
    return newimage;
}
/**
 该方法还没写完
 */
+(UIImage *)crop:(UIImage *)srcBitmap rect:(CGRect)rect {

    if (rect.origin.x < 0) {
        rect.origin.x = 0;
    }
    if (rect.origin.y < 0) {
        rect.origin.y = 0;
    }
    if (rect.size.width > srcBitmap.size.width) {
        rect.size.width = srcBitmap.size.width;
    }
    if (rect.size.height > srcBitmap.size.height) {
        rect.size.height = srcBitmap.size.height;
    }

    cv::Mat srcMat,cropMat;
    UIImageToMat(srcBitmap, srcMat);
//    Mat cropMat = new Mat(srcMat, new Range(rect.top, rect.bottom), new Range(rect.left, rect.right));
    
    cropMat = cv::Mat(srcMat, cv::Rect(rect.origin.x,rect.origin.y,rect.size.width,rect.size.height));
    UIImage *cropBitmap = MatToUIImage(cropMat);
    
    return cropBitmap;
}

+ (UIImage *)UIImageFromCVMat:(cv::Mat)cvMat
{
    NSData *data = [NSData dataWithBytes:cvMat.data length:cvMat.elemSize() * cvMat.total()];

    CGColorSpaceRef colorSpace;

    if (cvMat.elemSize() == 1) {
     colorSpace = CGColorSpaceCreateDeviceGray();
    } else {
     colorSpace = CGColorSpaceCreateDeviceRGB();
    }

    CGDataProviderRef provider = CGDataProviderCreateWithCFData((__bridge CFDataRef)data);

    CGImageRef imageRef = CGImageCreate(cvMat.cols,          // Width
             cvMat.rows,          // Height
             8,            // Bits per component
             8 * cvMat.elemSize(),       // Bits per pixel
             cvMat.step[0],         // Bytes per row
             colorSpace,          // Colorspace
             kCGImageAlphaNone | kCGBitmapByteOrderDefault, // Bitmap info flags
             provider,          // CGDataProviderRef
             NULL,           // Decode
             false,           // Should interpolate
             kCGRenderingIntentDefault);      // Intent

    UIImage *image = [[UIImage alloc] initWithCGImage:imageRef];
    CGImageRelease(imageRef);
    CGDataProviderRelease(provider);
    CGColorSpaceRelease(colorSpace);

    return image;
}

+ (cv::Mat)cvMatFromUIImage:(UIImage *)image
{
    CGColorSpaceRef colorSpace = CGImageGetColorSpace(image.CGImage);
    
    CGFloat cols = image.size.height;
    CGFloat rows = image.size.width;

    cv::Mat cvMat(rows, cols, CV_8UC4); // 8 bits per component, 4 channels
    
    // Pointer to backing data
    CGContextRef contextRef = CGBitmapContextCreate(cvMat.data,
                cols,      // Width of bitmap
                rows,      // Height of bitmap
                8,       // Bits per component
                cvMat.step[0],    // Bytes per row
                colorSpace,     // Colorspace
                kCGImageAlphaNoneSkipLast |
                kCGBitmapByteOrderDefault); // Bitmap info flags

    CGContextDrawImage(contextRef, CGRectMake(0, 0, cols, rows), image.CGImage);
    CGContextRelease(contextRef);

    return cvMat;
}

+(UIImage *)RBQMatToUIImage:(cv::Mat)mat scale:(CGFloat)scale imageOrientation:(UIImageOrientation)imageOrientation {
    
    NSData *data = [NSData dataWithBytes:mat.data length:mat.step.p[0] * mat.rows];

    CGColorSpaceRef colorSpace;

    if (mat.elemSize() == 1) {
        colorSpace = CGColorSpaceCreateDeviceGray();
    } else {
        colorSpace = CGColorSpaceCreateDeviceRGB();
    }

    CGDataProviderRef provider = CGDataProviderCreateWithCFData((__bridge CFDataRef)data);

    bool alpha = mat.channels() == 4;
    CGBitmapInfo bitmapInfo = (alpha ? kCGImageAlphaLast : kCGImageAlphaNone) | kCGBitmapByteOrderDefault;

    CGImageRef imageRef = CGImageCreate(mat.cols,
                                        mat.rows,
                                        8 * mat.elemSize1(),
                                        8 * mat.elemSize(),
                                        mat.step.p[0],
                                        colorSpace,
                                        bitmapInfo,
                                        provider,
                                        NULL,
                                        false,
                                        kCGRenderingIntentDefault
                                        );


    UIImage *finalImage = [UIImage imageWithCGImage:imageRef scale:scale orientation:imageOrientation];
    CGImageRelease(imageRef);
    CGDataProviderRelease(provider);
    CGColorSpaceRelease(colorSpace);

    return finalImage;
}

+(cv::Mat)RBQUIImageToMat:(UIImage *)image alpha:(BOOL)alphaExist {

    cv::Mat mat;

    CGColorSpaceRef colorSpace = CGImageGetColorSpace(image.CGImage);
    CGFloat cols = CGImageGetWidth(image.CGImage);
    CGFloat rows = CGImageGetHeight(image.CGImage);

    CGContextRef contextRef;
    CGBitmapInfo bitmapInfo = kCGImageAlphaPremultipliedLast;
    if (CGColorSpaceGetModel(colorSpace) == kCGColorSpaceModelMonochrome)
    {
        mat.create(rows, cols, CV_8UC1);
        bitmapInfo = kCGImageAlphaNone;
        if (!alphaExist)
            bitmapInfo = kCGImageAlphaNone;
        else
            mat = cv::Scalar(0);
        contextRef = CGBitmapContextCreate(mat.data, mat.cols, mat.rows, 8,
                                           mat.step[0], colorSpace,
                                           bitmapInfo);
    }else {
        
        mat.create(rows, cols, CV_8UC4); // 8 bits per component, 4 channels
        if (!alphaExist)
            bitmapInfo = kCGImageAlphaNoneSkipLast |
            kCGBitmapByteOrderDefault;
        else
            mat = cv::Scalar(0);
        contextRef = CGBitmapContextCreate(mat.data, mat.cols, mat.rows, 8,
                                           mat.step[0], colorSpace,
                                           bitmapInfo);
        CGContextDrawImage(contextRef, CGRectMake(0, 0, cols, rows),
                           image.CGImage);
        CGContextRelease(contextRef);
    }
    
    return mat;
}


//扫描身份证图片，并进行预处理，定位号码区域图片并返回
- (UIImage *)opencvScanCard:(UIImage *)image {
    
    //将UIImage转换成Mat
    cv::Mat resultImage;
    UIImageToMat(image, resultImage);
    //转为灰度图
    cvtColor(resultImage, resultImage, cv::COLOR_BGR2GRAY);
    //利用阈值二值化
    cv::threshold(resultImage, resultImage, 100, 255, CV_THRESH_BINARY);
    //腐蚀，填充（腐蚀是让黑色点变大）
    cv::Mat erodeElement = getStructuringElement(cv::MORPH_RECT, cv::Size(26,26));
    cv::erode(resultImage, resultImage, erodeElement);
    //轮廊检测
    std::vector<std::vector<cv::Point>> contours;//定义一个容器来存储所有检测到的轮廊
    cv::findContours(resultImage, contours, CV_RETR_TREE, CV_CHAIN_APPROX_SIMPLE, cvPoint(0, 0));
    //cv::drawContours(resultImage, contours, -1, cv::Scalar(255),4);
    //取出身份证号码区域
    std::vector<cv::Rect> rects;
    cv::Rect numberRect = cv::Rect(0,0,0,0);
    std::vector<std::vector<cv::Point>>::const_iterator itContours = contours.begin();
    for ( ; itContours != contours.end(); ++itContours) {
        cv::Rect rect = cv::boundingRect(*itContours);
        rects.push_back(rect);
        //算法原理
        if (rect.width > numberRect.width && rect.width > rect.height * 5) {
            numberRect = rect;
        }
    }
    //身份证号码定位失败
    if (numberRect.width == 0 || numberRect.height == 0) {
        return nil;
    }
    //定位成功成功，去原图截取身份证号码区域，并转换成灰度图、进行二值化处理
    cv::Mat matImage;
    UIImageToMat(image, matImage);
    resultImage = matImage(numberRect);
    cvtColor(resultImage, resultImage, cv::COLOR_BGR2GRAY);
    cv::threshold(resultImage, resultImage, 80, 255, CV_THRESH_BINARY);
    //将Mat转换成UIImage
    UIImage *numberImage = MatToUIImage(resultImage);
    return numberImage;
}

+ (UIImage *)applySobelEdgeDetection:(UIImage *)image {
    // 将UIImage转换为Mat
    Mat src, src_gray;
    UIImageToMat(image, src);
    cvtColor(src, src_gray, COLOR_BGR2GRAY);
    
    // Sobel边缘检测
    Mat grad_x, grad_y;
    Mat abs_grad_x, abs_grad_y;
    Sobel(src_gray, grad_x, CV_16S, 1, 0, 3);
    Sobel(src_gray, grad_y, CV_16S, 0, 1, 3);
    
    // 计算梯度的绝对值
    convertScaleAbs(grad_x, abs_grad_x);
    convertScaleAbs(grad_y, abs_grad_y);
    
    // 结合梯度
    Mat grad;
    addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0, grad);
    
    // 将Mat转换回UIImage
    UIImage *resultImage = MatToUIImage(grad);
    return resultImage;
}

/**
 
 */
+ (UIImage *)applyCannyEdgeDetection:(UIImage *)image {
    // 将UIImage转换为Mat
    Mat src, detected_edges;
    UIImageToMat(image, src);
    cvtColor(src, detected_edges, COLOR_BGR2GRAY);
    
    // 使用Canny算子进行边缘检测
    Canny(detected_edges, detected_edges, 50, 150, 3);
    
    // 将Mat转换回UIImage
    UIImage *resultImage = MatToUIImage(detected_edges);
    return resultImage;
}


// 直方图均衡化
+ (UIImage *)equalizeHistogram:(UIImage *)image {
    Mat matImage;
    UIImageToMat(image, matImage, false);
    
    // 转换为灰度图
    cvtColor(matImage, matImage, COLOR_BGR2GRAY);
    // 应用直方图均衡化
    equalizeHist(matImage, matImage);
    
    // 将灰度图转换为RGB
    Mat newImage;
    cvtColor(matImage, newImage, COLOR_GRAY2BGR);
    
    // 转换回UIImage
    UIImage *resultImage = MatToUIImage(newImage);
    return resultImage;
}

// 拉普拉斯算子锐化
+ (UIImage *)laplacianSharpening:(UIImage *)image {
    Mat matImage;
    UIImageToMat(image, matImage, false);
    
    // 转换为灰度图
    cvtColor(matImage, matImage, COLOR_BGR2GRAY);
    // 应用拉普拉斯算子
    Mat sharpened;
    Laplacian(matImage, sharpened, CV_8U, 1, 1, 0, BORDER_DEFAULT);
    matImage = matImage - 0.5 * sharpened;
    
    // 将灰度图转换为RGB
    Mat newImage;
    cvtColor(matImage, newImage, COLOR_GRAY2BGR);
    
    // 转换回UIImage
    UIImage *resultImage = MatToUIImage(newImage);
    return resultImage;
}

+ (UIImage *)laplacianSharpeningEnhanced:(UIImage *)image {
    Mat matImage;
    UIImageToMat(image, matImage, false);
    
    // 转换为灰度图
    cvtColor(matImage, matImage, COLOR_BGR2GRAY);
    // 应用拉普拉斯算子
    Mat sharpened;
    Laplacian(matImage, sharpened, CV_8U, 1, 1, 0, BORDER_DEFAULT);
    // 增加锐化权重
    Mat enhancedImage = matImage - 1.0 * sharpened;
    
    // 将灰度图转换为RGB
    Mat newImage;
    cvtColor(enhancedImage, newImage, COLOR_GRAY2BGR);
    
    // 转换回UIImage
    UIImage *resultImage = MatToUIImage(newImage);
    return resultImage;
}


+ (UIImage *)laplacianSharpeningWithBilateralFilter:(UIImage *)image {
    Mat matImage;
    UIImageToMat(image, matImage, false);
    
    // 转换为灰度图
    cvtColor(matImage, matImage, COLOR_BGR2GRAY);
    // 应用拉普拉斯算子
    Mat sharpened;
    Laplacian(matImage, sharpened, CV_8U, 1, 1, 0, BORDER_DEFAULT);
    // 增加锐化权重
    Mat enhancedImage = matImage - 0.5 * sharpened;
    
    // 应用双边滤波器进行抗锯齿
    Mat bilateral;
    bilateralFilter(enhancedImage, bilateral, 9, 75, 75);
    
    // 将灰度图转换为RGB
    Mat rgbImage;
    cvtColor(bilateral, rgbImage, COLOR_GRAY2BGR);
    
    // 转换回UIImage
    UIImage *resultImage = MatToUIImage(rgbImage);
    return resultImage;
}



// 对数变换
+ (UIImage *)logTransformation:(UIImage *)image {
    Mat matImage;
    UIImageToMat(image, matImage, false);
    
    // 转换为灰度图
    cvtColor(matImage, matImage, COLOR_BGR2GRAY);
    // 应用对数变换
    Mat logImage;
    matImage.convertTo(logImage, CV_32F);
    logImage = logImage + Scalar(1);
    log(logImage, logImage);
    logImage = logImage * (255/log(1 + 255));
    
    // 转换回UIImage
    logImage.convertTo(logImage, CV_8U);
    
    // 将灰度图转换为RGB
    Mat newImage;
    cvtColor(logImage, newImage, COLOR_GRAY2BGR);
    
    UIImage *resultImage = MatToUIImage(newImage);
    return resultImage;
}

// 伽马校正
+ (UIImage *)gammaCorrection:(UIImage *)image gamma:(double)gammaValue {
    Mat matImage;
    UIImageToMat(image, matImage, false);
    
    // 转换为灰度图
    cvtColor(matImage, matImage, COLOR_BGR2GRAY);
    // 应用伽马校正
    Mat gammaImage;
    matImage.convertTo(gammaImage, CV_32F);
    pow(gammaImage / 255.0, gammaValue, gammaImage);
    gammaImage = gammaImage * 255;
    
    // 转换回UIImage
    gammaImage.convertTo(gammaImage, CV_8U);
    
    // 将灰度图转换为RGB
    Mat newImage;
    cvtColor(gammaImage, newImage, COLOR_GRAY2BGR);
    
    UIImage *resultImage = MatToUIImage(newImage);
    return resultImage;
}


@end
