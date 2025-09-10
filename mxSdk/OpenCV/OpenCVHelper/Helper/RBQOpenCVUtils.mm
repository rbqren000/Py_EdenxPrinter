//
//  RBQOpenCVUtils.m
//  Inksi
//
//  Created by rbq on 2024/1/18.
//
#ifdef __cplusplus
#include <iostream>
#endif

#include <opencv2/opencv.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/imgproc/types_c.h>
#include <opencv2/imgcodecs/ios.h>
#include <algorithm>

#import "RBQOpenCVUtils.h"

@implementation RBQOpenCVUtils

+ (cv::Mat)grayImageFromPath:(NSString *)path {
    // 读取图片
    cv::Mat img = cv::imread([path UTF8String]);
    // 判断图片是否为空
    if (img.empty()) {
        NSLog(@"Image not found at %@", path);
        return img;
    }
    // 转换为灰度图
    cv::Mat gray;
    cv::cvtColor(img, gray, cv::COLOR_BGR2GRAY);
    // 返回灰度图
    return gray;
}

+ (NSString *)grayImageFromPath:(NSString *)path andSaveTo:(NSString *)savePath {
    // 读取图片
    cv::Mat img = cv::imread([path UTF8String]);
    // 判断图片是否为空
    if (img.empty()) {
        NSLog(@"Image not found at %@", path);
        return nil;
    }
    // 转换为灰度图
    cv::Mat gray;
    cv::cvtColor(img, gray, cv::COLOR_BGR2GRAY);
    // 保存灰度图到指定地址
    cv::imwrite([savePath UTF8String], gray);
    // 返回保存地址
    return savePath;
}

+ (cv::Mat)readGrayImageFromPath:(NSString *)path {
    // 读取灰度图
    cv::Mat gray = cv::imread([path UTF8String], cv::IMREAD_GRAYSCALE);
    // 判断图片是否为空
    if (gray.empty()) {
        NSLog(@"Image not found at %@", path);
        return gray;
    }
    // 返回灰度图
    return gray;
}

+ (cv::Mat)formatGrayToRngDithering:(cv::Mat)gray{
    // 判断图片是否为空
    if (gray.empty()) {
        NSLog(@"Image is empty");
        return gray;
    }
    // 判断图片是否为灰度图
    if (gray.channels() != 1) {
        NSLog(@"Image is not grayscale");
        return gray;
    }
    // 创建一个随机数生成器
    cv::RNG rng;
    // 创建一个抖动后的图像
    cv::Mat dither = gray.clone();
    // 遍历所有像素
    for (int i = 0; i < gray.rows; i++) {
        for (int j = 0; j < gray.cols; j++) {
            // 获取当前像素的灰度值
            int grayVal = gray.at<uchar>(i, j);
            // 生成一个随机数
            int randVal = rng.uniform(0, 256);
            // 如果灰度值大于随机数，就将像素设为白色，否则设为黑色
            dither.at<uchar>(i, j) = grayVal > randVal ? 255 : 0;
        }
    }
    // 返回抖动后的图像
    return dither;
}

- (cv::Mat)formatGrayToDithering:(cv::Mat)gray width:(int)width height:(int)height {
    // 判断图片是否为空
    if (gray.empty()) {
        NSLog(@"Image is empty");
        return gray;
    }
    // 判断图片是否为灰度图
    if (gray.channels() != 1) {
        NSLog(@"Image is not grayscale");
        return gray;
    }
    // 转换为二值图
    cv::Mat bin;
    cv::threshold(gray, bin, 0, 255, cv::THRESH_BINARY | cv::THRESH_OTSU);
    // 创建一个误差图
    cv::Mat err = cv::Mat::zeros(height, width, CV_32SC1);
    // 创建一个抖动后的图像
    cv::Mat dither = bin.clone();
    // 定义误差
    int e;
    // 定义方向
    int d = 1; // d为1时，误差从左传递到右侧，为-1时，误差从右传递到左
    // 遍历所有像素
    for (int row = 0; row < height; row++) {
        for (int col = 0; col < width; col++) {
            if (d == 1) {
                // 获取当前像素的索引
                int index = width * row + col;
                // 获取当前像素的灰度值
                int g = gray.at<uchar>(row, col);
                // 获取当前像素的二值值
                int b = bin.at<uchar>(row, col);
                // 计算误差
                e = g - b + err.at<int>(row, col);
                // 判断误差的正负
                if (e > 127) {
                    e = e - 255; // 负值
                } else {
                    e = e; // 正值
                }
                // 计算向右侧像素的误差传递
                index = width * row + col + 1;
                if (col + 1 < width) {
                    err.at<int>(row, col + 1) += 5 * e / 16;
                }
                // 计算向左下方像素的误差传递
                index = width * (row + 1) + col - 1;
                if (col - 1 > 0 && row + 1 < height) {
                    err.at<int>(row + 1, col - 1) += 3 * e / 16;
                }
                // 计算向下方像素的误差传递
                index = width * (row + 1) + col;
                if (row + 1 < height) {
                    err.at<int>(row + 1, col) += 5 * e / 16;
                }
                // 计算向右下方像素的误差传递
                index = width * (row + 1) + col + 1;
                if (col + 1 < width && row + 1 < height) {
                    err.at<int>(row + 1, col + 1) += 3 * e / 16;
                }
            } else {
                // 获取当前像素的索引
                int index = width * row + (width - 1) - col;
                // 获取当前像素的灰度值
                int g = gray.at<uchar>(row, width - 1 - col);
                // 获取当前像素的二值值
                int b = bin.at<uchar>(row, width - 1 - col);
                // 计算误差
                e = g - b + err.at<int>(row, width - 1 - col);
                // 判断误差的正负
                if (e > 127) {
                    e = e - 255; // 负值
                } else {
                    e = e; // 正值
                }
                // 计算向左侧像素的误差传递
                index = width * row + (width - 1) - col - 1;
                if (width - col > 2) {
                    err.at<int>(row, width - 2 - col) += 5 * e / 16;
                }
                // 计算向左下方像素的误差传递
                index = width * (row + 1) + (width - 1) - col - 1;
                if (width - col > 2 && row + 1 < height) {
                    err.at<int>(row + 1, width - 2 - col) += 3 * e / 16;
                }
                // 计算向下方像素的误差传递
                index = width * (row + 1) + (width - 1) - col;
                if (row + 1 < height) {
                    err.at<int>(row + 1, width - 1 - col) += 5 * e / 16;
                }
                // 计算向右下方像素的误差传递
                index = width * (row + 1) + width - col;
                if (row + 1 < height && col > 0) {
                    err.at<int>(row + 1, width - col) += 3 * e / 16;
                }
            }
        }
        // 改变方向
        d = -d;
    }
    // 返回抖动后的图像
    return dither;
}

+ (cv::Mat)thresholdImageFromGrayImage:(cv::Mat)gray andThreshold:(double)threshold {
    // 判断图片是否为空
    if (gray.empty()) {
        NSLog(@"Image is empty");
        return gray;
    }
    // 判断图片是否为灰度图
    if (gray.channels() != 1) {
        NSLog(@"Image is not grayscale");
        return gray;
    }
    // 使用cv2.threshold()函数将图片转为二值图
    cv::Mat dither;
    cv::threshold(gray, dither, threshold, 255, cv::THRESH_BINARY);
    // 返回抖动后的图像
    return dither;
}

+ (cv::Mat)adaptiveThresholdImageFromGrayImage:(cv::Mat)gray andBlockSize:(int)blockSize andC:(double)C {
    // 判断图片是否为空
    if (gray.empty()) {
        NSLog(@"Image is empty");
        return gray;
    }
    // 判断图片是否为灰度图
    if (gray.channels() != 1) {
        NSLog(@"Image is not grayscale");
        return gray;
    }
    // 使用cv2.adaptiveThreshold()函数将图片转为二值图
    cv::Mat dither;
    cv::adaptiveThreshold(gray, dither, 255, cv::ADAPTIVE_THRESH_MEAN_C, cv::THRESH_BINARY, blockSize, C);
    // 返回抖动后的图像
    return dither;
}


@end
