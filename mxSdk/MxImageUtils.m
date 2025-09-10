//
//  MxImageUtils.m
//  Inksi
//
//  Created by rbq on 2024/6/22.
//

#import "MxImageUtils.h"
#import "RBQLog.h"
#import "XBSTimer.h"
#import "MxFileManager.h"
#import "Compress.h"
#import "RBQLog.h"
#import "RBQDefine.h"
#import "OpenCVUtils.h"
#import <Metal/Metal.h>
#import <CoreGraphics/CoreGraphics.h>
#import <QuartzCore/QuartzCore.h>
#import "UIImage+Image.h"
#import "ZlibUtils.h"

@implementation MxImageUtils

+(void)oldBitmapToGray:(uint32_t *)pixels gray:(uint32_t *)gray width:(int)width height:(int)height{
    
    int tt =1;
    
    for (int row = 0; row <height; row++) {
        
        for (int col =0; col <width; col++) {
            
            uint8_t *rgbaPixel = (uint8_t *)&pixels[row*width+col];
            
            //            int alpha = rgbaPixel[0];
            int red = rgbaPixel[tt];
            int green = rgbaPixel[tt+1];
            int blue = rgbaPixel[tt+2];
            
            int grayValue = (int) ((float) red * 0.3f + (float) green * 0.59f + (float) blue * 0.11f);//灰度值
            //这里取一个接近黑色的值，因为Android中getPixels函数取色并不准，
            //没办法定位黑色和白色，这了是不希望黑色和白色被处理
            //                gray[width * row + col] = red;
            gray[row*width+col] = grayValue;
            
        }
    }
}

// 改进版本
+(void)bitmapToGray:(uint32_t *)pixels gray:(uint32_t *)gray width:(int)width height:(int)height {
    for (int row = 0; row < height; row++) {
        uint32_t *pixelsRow = &pixels[row * width];
        uint32_t *grayRow = &gray[row * width];
        for (int col = 0; col < width; col++) {
            uint8_t *rgbaPixel = (uint8_t *) &pixelsRow[col];
            int red = rgbaPixel[1];
            int green = rgbaPixel[2];
            int blue = rgbaPixel[3];
            //因为浮点型计算较慢，这里改成整数加位移的方式  等效下面的浮点计算
            // int grayValue = (int) ((float) red * 0.3f + (float) green * 0.59f + (float) blue * 0.11f);
            grayRow[col] = (red * 77 + green * 151 + blue * 28) >> 8;
        }
    }
}
/**
 和上边方法功能想同，只是这里是使用index方式进行计算
 */
+(void)bitmapToGrayByIndex:(uint32_t *)pixels gray:(uint32_t *)gray width:(int)width height:(int)height {
    
    for (int row = 0; row < height; row++) {
        
        for (int col = 0; col < width; col++) {
            
            int index = row * width + col;  // 计算像素的全局索引
            
            // 获取像素的 RGBA 值
            uint8_t *rgbaPixel = (uint8_t *)&pixels[index];
            int red = rgbaPixel[1];   // 红色通道
            int green = rgbaPixel[2]; // 绿色通道
            int blue = rgbaPixel[3];  // 蓝色通道

            // 将RGB转为灰度值，采用整数计算
            gray[index] = (red * 77 + green * 151 + blue * 28) >> 8;
        }
    }
}

//Floyd-Steinberg抖动算法  弗洛伊德  美/flɔɪd/
/**
 误差扩散：算法使用Floyd-Steinberg抖动的变体，通过将量化误差分散到周围的像素来减少视觉上的失真。
 双向处理：算法在处理每行像素时会交替改变方向，这有助于更均匀地分散误差。
 预计算的系数：算法使用预计算的误差比例系数来调整相邻像素的值，这些系数基于错误扩散的比例。
 */
/*
 +(void)formatGrayToFloydDithering:(uint32_t *)gray width:(int)width height:(int)height threshold:(int)threshold {
     int e;
     int d = 1; // d为1时，误差从左传递到右侧，为-1时，误差从右传递到左
     
     for (int row = 0; row < height; row++) {
         for (int col = 0; col < width; col++) {
             int index = d == 1 ? width * row + col : width * row + (width - 1) - col;
             int g = gray[index]; // 0-255的一个值
             
             if (g > threshold) {
                 e = g - 255; // 负值
             } else {
                 e = g; // 正值
             }
             
             if (d == 1) {
                 // 计算向右侧像素的误差传递
                 if (col + 1 < width) {
                     gray[width * row + col + 1] += 5 * e / 16;
                 }
                 // 计算向左下方像素的误差传递
                 if (col - 1 > 0 && row + 1 < height) {
                     gray[width * (row + 1) + col - 1] += 3 * e / 16;
                 }
             } else {
                 // 计算向左侧像素的误差传递
                 if (width - col > 2) {
                     gray[width * row + (width - 1) - col - 1] += 5 * e / 16;
                 }
                 // 计算误差向左下侧像素的误差传递
                 if (width - col > 2 && row + 1 < height) {
                     gray[width * (row + 1) + (width - 1) - col - 1] += 3 * e / 16;
                 }
             }
             
             // 计算向下方像素的误差传递
             if (row + 1 < height) {
                 gray[width * (row + 1) + col] += 5 * e / 16;
             }
             // 计算向右下方像素点的误差传递
             if (col + 1 < width && row + 1 < height) {
                 gray[width * (row + 1) + col + 1] += 3 * e / 16;
             }
         }
         d = -d; // 改变误差传递的方向
     }
 }

 */

+ (void)formatGrayToFloydDithering:(uint32_t *)gray width:(int)width height:(int)height threshold:(int)threshold {
    int e;
    for (int row = 0; row < height; row++) {
        for (int col = 0; col < width; col++) {
            int index = row * width + col;
            int oldPixel = gray[index];
            int newPixel = (oldPixel > threshold) ? 255 : 0;
            gray[index] = newPixel;
            
            e = oldPixel - newPixel;
            
            // 将误差分配给右侧像素（权重 7/16）
            if (col + 1 < width) gray[index + 1] += e * 7 / 16;
            // 将误差分配给下一行的像素
            if (row + 1 < height) {
                // 将误差分配给左下角像素（权重 3/16）
                if (col > 0) gray[index + width - 1] += e * 3 / 16;
                // 将误差分配给正下方像素（权重 5/16）
                gray[index + width] += e * 5 / 16;
                // 将误差分配给右下角像素（权重 1/16）
                if (col + 1 < width) gray[index + width + 1] += e * 1 / 16;
            }
        }
    }
}

+ (void)formatGrayToFloydDithering:(uint32_t *)gray width:(int)width height:(int)height threshold:(int)threshold initialErrors:(uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors {
    
    int e;
    // 用于临时保存最后一行的误差
    uint32_t *temp_lastRowErrors = malloc(width * sizeof(uint32_t));
    memset(temp_lastRowErrors, 0, width * sizeof(uint32_t));

    for (int row = 0; row < height; row++) {
        for (int col = 0; col < width; col++) {
            
            int index = row * width + col;
            
            // 初始化当前像素的误差
            if (row == 0 && initialErrors != NULL && initialErrors != nil ) {
                gray[index] += initialErrors[col];
            }
            
            int oldPixel = gray[index];
            int newPixel = (oldPixel > threshold) ? 255 : 0;
            gray[index] = newPixel;

            e = oldPixel - newPixel;

            // 将误差分配给右侧像素（权重 7/16）
            if (col + 1 < width) gray[index + 1] += e * 7 / 16;
            // 将误差分配给下一行的像素
            if (row + 1 < height) {
                // 将误差分配给左下角像素（权重 3/16）
                if (col > 0) gray[index + width - 1] += e * 3 / 16;
                // 将误差分配给正下方像素（权重 5/16）
                gray[index + width] += e * 5 / 16;
                // 将误差分配给右下角像素（权重 1/16）
                if (col + 1 < width) gray[index + width + 1] += e * 1 / 16;
            }

            // 更新最后一行的误差
           if (row == height - 1) {
               if (col > 0) temp_lastRowErrors[col - 1] += e * 3 / 16;
               temp_lastRowErrors[col] += e * 5 / 16;
               if (col + 1 < width) temp_lastRowErrors[col + 1] += e * 1 / 16;
           }
        }
    }
    // 保存最后一行的误差
    if (lastRowErrors != NULL && lastRowErrors != nil) {
        *lastRowErrors = temp_lastRowErrors;
    } else {
        free(temp_lastRowErrors);
    }
}

// Atkinson抖动算法  阿特金森 /ˈætkənsən/
/**
 目的: 将灰度图像转换为抖动模式。
 方法: 使用差分算法，将每个像素与阈值比较，转换为黑白色。
 特点: 利用预计算的误差比例系数来调整相邻像素的值。
 */
+ (void)formatGrayToAtkinsonDithering:(uint32_t *)gray width:(int)width height:(int)height threshold:(int)threshold {
    int error;
    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            int index = y * width + x;
            int oldPixel = gray[index];
            int newPixel = (oldPixel > threshold) ? 255 : 0;
            gray[index] = newPixel;
            
            error = oldPixel - newPixel;
            
            if (x + 1 < width) gray[index + 1] += error * 1/8;
            if (x + 2 < width) gray[index + 2] += error * 1/8;
            if (y + 1 < height) {
                if (x > 0) gray[index + width - 1] += error * 1/8;
                gray[index + width] += error * 1/8;
                if (x + 1 < width) gray[index + width + 1] += error * 1/8;
            }
            if (y + 2 < height) gray[index + 2*width] += error * 1/8;
        }
    }
}

// Burkes抖动算法  伯克斯  美/bɜrks/
/** 称之为Burkes误差扩散抖动算法或Burkes噪声抖动技术，这样可以更准确地描述其功能和用途。
 目的: 结合自适应阈值处理，改善图像中文字的清晰度。
 方法: 在抖动前应用自适应阈值处理，然后保护文字区域。
 特点: 调整抖动参数，减少对文字区域的影响，保持文字清晰。
 */
+ (void)formatGrayToBurkesDithering:(uint32_t *)gray width:(int)width height:(int)height threshold:(int)threshold {
    int e;
    for (int row = 0; row < height; row++) {
        for (int col = 0; col < width; col++) {
            int index = row * width + col;
            int oldPixel = gray[index];
            // 根据阈值将像素转换为全黑或全白
            int newPixel = (oldPixel > threshold) ? 255 : 0;
            gray[index] = newPixel;
            
            // 计算误差
            e = oldPixel - newPixel;
            
            // 将误差分配给周围的像素，按照Burkes算法的权重
            if (col + 1 < width) gray[index + 1] += e * 8/32;
            if (col + 2 < width) gray[index + 2] += e * 4/32;
            if (row + 1 < height) {
                if (col > 1) gray[index + width - 2] += e * 2/32;
                if (col > 0) gray[index + width - 1] += e * 4/32;
                gray[index + width] += e * 8/32;
                if (col + 1 < width) gray[index + width + 1] += e * 4/32;
                if (col + 2 < width) gray[index + width + 2] += e * 2/32;
            }
        }
    }
}


/*
 +(void)grayToBinary:(uint32_t *)gray
              pixels:(uint32_t *)pixels
               width:(int)width
              height:(int)height
           threshold:(int)threshold {
     
     for (int row = 0; row < height; row++) {
         for (int col = 0; col < width; col++) {
             int g = gray[width * row + col];
             pixels[width * row + col] = g >= threshold ? 0 : 255;
         }
     }
 }
 */
//改进后
/**
 使用 - 符号和 | 位运算符来替代条件运算符。如果 g >= threshold 为真，则 -(g >= threshold) 会得到 0xFFFFFFFF，与 0xFF 进行 | 位运算后结果仍然是 0xFF；如果为假，则 -(g >= threshold) 为 0，与 0xFF 进行 | 位运算后结果为 0。这样就可以用位运算来替代原来的条件运算符，提高代码的执行效率。同时，我们通过缓存 rowIndex 来减少乘法运算的次数。
 */
+(void)grayToBinary:(uint32_t *)gray binary:(uint32_t *)binary width:(int)width height:(int)height threshold:(int)threshold {
    for (int row = 0; row < height; row++) {
        int rowIndex = row * width;
        for (int col = 0; col < width; col++) {
            int g = gray[rowIndex + col];
            binary[rowIndex + col] = -(g >= threshold) | 0xFF;
        }
    }
}

+(void)grayToBinaryIndex:(uint32_t *)gray binary:(uint32_t *)binary width:(int)width height:(int)height threshold:(int)threshold {
    for (int row = 0; row < height; row++) {
        for (int col = 0; col < width; col++) {
            int index = row * width + col;  // 计算当前像素的全局索引
            int g = gray[index];            // 获取当前像素的灰度值
            binary[index] = -(g >= threshold) | 0xFF;  // 根据阈值将灰度转换为二值图像
        }
    }
}


/*
+(NSData *)formatBinary69ToData72:(uint32_t *)pixels width:(int)width height:(int)height topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance{
    
    uint8_t *d69 = (uint8_t *)malloc(width * 69 * sizeof(uint8_t));
    //空像素填充
    memset(d69, 0, width * 69 * sizeof(uint8_t));
    
    for (int col = 0; col < width; col++) {
        
        for (int row = topBeyondDistance; row < height - bottomBeyondDistance; row++) {
            
            int pixel = pixels[col + width * row];// 0xffffffff 或者0xff000000
            int temp_row = row - topBeyondDistance;
            if (pixel == 255) {//有值
                int s = col * 69 + temp_row / 8;
                d69[s] = d69[s] | (0x80 >> (temp_row % 8));
            }
        }
    }
    
    uint8_t *d72 = (uint8_t *)malloc(width *72 *sizeof(uint8_t));
    memset(d72, 0, width *72 *sizeof(uint8_t));
    
    int currentHeight = height - topBeyondDistance - bottomBeyondDistance;
    RBQLog3(@"【formatBinary69ToData72】currentHeight:%d",currentHeight);
    
    //下面将69byte高的图片，转成72byte
    for (int col = 0; col < width; col++) { // 宽度不定
        for (int row = 0; row < currentHeight; row++) { // 高度552
            
            // %6 --> which cycle
            switch (row % 6) {
                    // cycle 1
                case 0:
                    if ((d69[col * 69 + row / 8] & (0x80 >> (row % 8))) != 0 ) {
                        int index = col * 72 + (row / 276) * 6 + ((row % 276) / 6) / 8;
                        d72[index] = d72[index] | (0x80 >> (((row % 276) / 6) % 8));
                    }
                    break;
                    // cycle 2
                case 4:
                    if ((d69[col * 69 + row / 8] & (0x80 >> (row % 8))) != 0 ) {
                        int index = col * 72 + (row / 276) * 6 + 12 + ((row % 276 - 4) / 6) / 8;
                        d72[index] = d72[index] | (0x80 >> (((row % 276) / 6) % 8));
                    }
                    break;
                    // cycle 3
                case 2:
                    if ((d69[col * 69 + row / 8] & (0x80 >> (row % 8))) != 0 ) {
                        int index = col * 72 + (row / 276) * 6 + 24 + ((row % 276 - 2) / 6) / 8;
                        d72[index] = d72[index] | (0x80 >> (((row % 276) / 6) % 8));
                    }
                    break;
                    // cycle 4
                case 5:
                    if ((d69[col * 69 + row / 8] & (0x80 >> (row % 8))) != 0 ) {
                        int index = col * 72 + (row / 276) * 6 + 36 + ((row % 276 - 5) / 6) / 8;
                        d72[index] = d72[index] | (0x80 >> (((row % 276) / 6) % 8));
                    }
                    break;
                    // cycle 5
                case 1:
                    if ((d69[col * 69 + row / 8] & (0x80 >> (row % 8))) != 0 ) {
                        int index = col * 72 + (row / 276) * 6 + 48 + ((row % 276 - 1) / 6) / 8;
                        d72[index] = d72[index] | (0x80 >> (((row % 276) / 6) % 8));
                    }
                    break;
                    //                         cycle 6
                case 3:
                    if ((d69[col * 69 + row / 8] & (0x80 >> (row % 8))) != 0 ) {
                        int index = col * 72 + (row / 276) * 6 + 60 + ((row % 276 - 3) / 6) / 8;
                        d72[index] = d72[index] | (0x80 >> (((row % 276) / 6) % 8));
                    }
                    break;
            }
        }
    }
    free(d69);
    
    NSData *data72 = [NSData dataWithBytes:d72 length:width * 72];
    free(d72);
    
    return data72;
}
 */
/*
+(NSData *)formatBinary69ToData72:(uint32_t *)pixels width:(int)width height:(int)height{
    
    uint8_t *d69 = (uint8_t *)malloc(width * 69 * sizeof(uint8_t));
    //空像素填充
    memset(d69, 0, width * 69 * sizeof(uint8_t));
    
    for (int col = 0; col < width; col++) {
        
        for (int row = 0; row < height; row++) {
            
            int pixel = pixels[col + width * row];// 0xffffffff 或者0xff000000
            
            if (pixel == 255) {//有值
                int s = col * 69 + row / 8;
                d69[s] = d69[s] | (0x80 >> (row % 8));
            }
        }
    }
    
    uint8_t *d72 = (uint8_t *)malloc(width *72 *sizeof(uint8_t));
    memset(d72, 0, width *72 *sizeof(uint8_t));
    
    //下面将69byte高的图片，转成72byte
    for (int col = 0; col < width; col++) { // 宽度不定
        for (int row = 0; row < height; row++) { // 高度552
            
            // %6 --> which cycle
            switch (row % 6) {
                    // cycle 1
                case 0:
                    if ((d69[col * 69 + row / 8] & (0x80 >> (row % 8))) != 0 ) {
                        int index = col * 72 + (row / 276) * 6 + ((row % 276) / 6) / 8;
                        d72[index] = d72[index] | (0x80 >> (((row % 276) / 6) % 8));
                    }
                    break;
                    // cycle 2
                case 4:
                    if ((d69[col * 69 + row / 8] & (0x80 >> (row % 8))) != 0 ) {
                        int index = col * 72 + (row / 276) * 6 + 12 + ((row % 276 - 4) / 6) / 8;
                        d72[index] = d72[index] | (0x80 >> (((row % 276) / 6) % 8));
                    }
                    break;
                    // cycle 3
                case 2:
                    if ((d69[col * 69 + row / 8] & (0x80 >> (row % 8))) != 0 ) {
                        int index = col * 72 + (row / 276) * 6 + 24 + ((row % 276 - 2) / 6) / 8;
                        d72[index] = d72[index] | (0x80 >> (((row % 276) / 6) % 8));
                    }
                    break;
                    // cycle 4
                case 5:
                    if ((d69[col * 69 + row / 8] & (0x80 >> (row % 8))) != 0 ) {
                        int index = col * 72 + (row / 276) * 6 + 36 + ((row % 276 - 5) / 6) / 8;
                        d72[index] = d72[index] | (0x80 >> (((row % 276) / 6) % 8));
                    }
                    break;
                    // cycle 5
                case 1:
                    if ((d69[col * 69 + row / 8] & (0x80 >> (row % 8))) != 0 ) {
                        int index = col * 72 + (row / 276) * 6 + 48 + ((row % 276 - 1) / 6) / 8;
                        d72[index] = d72[index] | (0x80 >> (((row % 276) / 6) % 8));
                    }
                    break;
                    //                         cycle 6
                case 3:
                    if ((d69[col * 69 + row / 8] & (0x80 >> (row % 8))) != 0 ) {
                        int index = col * 72 + (row / 276) * 6 + 60 + ((row % 276 - 3) / 6) / 8;
                        d72[index] = d72[index] | (0x80 >> (((row % 276) / 6) % 8));
                    }
                    break;
            }
        }
    }
    free(d69);
    
    NSData *data72 = [NSData dataWithBytes:d72 length:width * 72];
    free(d72);
    
    return data72;
}
*/

+(void)formatBinary69ToData72ByCol:(uint32_t *)binary d72:(uint8_t *)d72 width:(int)width height:(int)height {
    
    uint8_t *d69 = (uint8_t *)calloc(width * 69, sizeof(uint8_t));
    
    // 提前计算常量
    int cycleOffsets[6] = {0, 48, 24, 60, 12, 36};
    uint8_t bitShiftTable[8] = {0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01};

    // 合并两个循环并简化逻辑
    for (int col = 0; col < width; col++) {
        
        int col69 = col * 69;
        int col72 = col * 72;

        for (int row = 0; row < height; row++) {
            // d69计算
            int pixel = binary[col + width * row];
            if (pixel == 255) {
                int rowDiv8 = row / 8;
                d69[col69 + rowDiv8] |= bitShiftTable[row % 8];
            }
            // d69->d72
            if (d69[col69 + row / 8] & bitShiftTable[row % 8]) {
                int cycle = row % 6;
                int baseIndex = col72 + (row / 276) * 6;
                int cycleIndex = ((row % 276 - cycle) / 6) / 8;
                int dIndex = baseIndex + cycleOffsets[cycle] + cycleIndex;
                d72[dIndex] |= bitShiftTable[((row % 276) / 6) % 8];
            }
        }
    }
    
    free(d69);
}

+(NSData *)formatBinary69ToData72ByCol:(uint32_t *)binary width:(int)width height:(int)height {
    
    NSMutableData *d72Data = [NSMutableData dataWithLength:width * 72];
    uint8_t *d72 = (uint8_t *)d72Data.mutableBytes;
    
    [self formatBinary69ToData72ByCol:binary d72:d72 width:width height:height];
    
    return d72Data;
}

+(void)formatBinary69ToData72ByRow:(uint32_t *)binary d72:(uint8_t *)d72 width:(int)width height:(int)height {
    
    uint8_t *d69 = (uint8_t *)calloc(width * 69, sizeof(uint8_t));
    
    // 提前计算常量
    int cycleOffsets[6] = {0, 48, 24, 60, 12, 36};
    uint8_t bitShiftTable[8] = {0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01};

    // 合并两个循环并简化逻辑
    for (int row = 0; row < height; row++) {
        
        for (int col = 0; col < width; col++) {
            
            int col69 = col * 69;
            int col72 = col * 72;

            // d69计算
            int pixel = binary[col + width * row];
            if (pixel == 255) {
                int rowDiv8 = row / 8;
                d69[col69 + rowDiv8] |= bitShiftTable[row % 8];
            }
            // d69->d72
            if (d69[col69 + row / 8] & bitShiftTable[row % 8]) {
                int cycle = row % 6;
                int baseIndex = col72 + (row / 276) * 6;
                int cycleIndex = ((row % 276 - cycle) / 6) / 8;
                int dIndex = baseIndex + cycleOffsets[cycle] + cycleIndex;
                d72[dIndex] |= bitShiftTable[((row % 276) / 6) % 8];
            }
        }
    }
    
    free(d69);
}

+(NSData *)formatBinary69ToData72ByRow:(uint32_t *)binary width:(int)width height:(int)height {
    
    NSMutableData *d72Data = [NSMutableData dataWithLength:width * 72];
    uint8_t *d72 = (uint8_t *)d72Data.mutableBytes;
    
    [self formatBinary69ToData72ByRow:binary d72:d72 width:width height:height];
    
    return d72Data;
}

+(RowData *)createRowData:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors{
    
    CGFloat width = image.size.width;
    CGFloat height = image.size.height;
    
    UIImage *newBitmap;
    CGFloat valid_height = height - topBeyondDistance - bottomBeyondDistance;
    CGFloat new_width;
    CGFloat new_height;
    CGFloat new_topBeyondDistance;
    CGFloat new_bottomBeyondDistance;
    //如果高度不为552，则缩放到552
    if(valid_height != 552.0f ){
        
        CGFloat scale = 552.0f/valid_height;
        
        new_topBeyondDistance = topBeyondDistance * scale;
        new_bottomBeyondDistance = bottomBeyondDistance * scale;
        
        CGFloat temp_width = floor(width * scale);
        CGFloat temp_height = 552.0f + new_topBeyondDistance + new_bottomBeyondDistance;
        newBitmap = [UIImage scaleToSize:image size:CGSizeMake(temp_width, temp_height)];
        //这里valid_height不为552则进行缩放，那么缩放后valid_height的值则变为552了
        valid_height = 552;
        new_width = temp_width;
        new_height = temp_height;
        
    }else{
        
        newBitmap = image;
        new_width = floor(width);
        new_height = height;
        new_topBeyondDistance = topBeyondDistance;
        new_bottomBeyondDistance = bottomBeyondDistance;
    }
    
    RBQLog3(@"【createRowData】{width:%f; height:%f; valid_height:%f; topBeyondDistance:%d; bottomBeyondDistance:%d; new_width:%f; new_height:%f; new_topBeyondDistance:%f; new_bottomBeyondDistance:%f;新->valid_height:%f}",width,height,(height - topBeyondDistance - bottomBeyondDistance),topBeyondDistance,bottomBeyondDistance,new_width,new_height,new_topBeyondDistance,new_bottomBeyondDistance,valid_height);
    
    if (clearBackground) {
        newBitmap = [OpenCVUtils lightClearBackground:newBitmap];
    }
    
    /*
    //像素将画在这个数组
    uint32_t *pixels = (uint32_t *)malloc(new_width * new_height * sizeof(uint32_t));
    //清空像素数组
    memset(pixels, 0, new_width * new_height * sizeof(uint32_t));
    
    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    
    CGContextRef context =CGBitmapContextCreate(pixels, new_width, new_height, 8, new_width * sizeof(uint32_t), colorSpace, kCGBitmapByteOrder32Little | kCGImageAlphaPremultipliedLast);
    CGContextDrawImage(context, CGRectMake(0, 0, new_width, new_height), [newBitmap CGImage]);
    CGColorSpaceRelease(colorSpace);
    
    //取出有效的pix
    uint32_t *validPixs = (uint32_t *)malloc(new_width * valid_height * sizeof(uint32_t));
    memset(validPixs, 0, new_width * valid_height * sizeof(uint32_t));
//    for (int col = 0; col < new_width; col++) {
//        for (int row = new_topBeyondDistance; row < new_height - new_bottomBeyondDistance; row++) {
//            int pixel = pixels[col + new_width * row]; // 0xffffffff 或者0xff000000
//            int temp_row = row - new_topBeyondDistance;
//            validPixs[col + new_width * temp_row] = pixel;
//        }
//    }
//    //释放pixels
//    free(pixels);
    // 计算起始偏移和拷贝的大小
    int startRow = new_topBeyondDistance;
    int endRow = new_height - new_bottomBeyondDistance;
    int numberOfRows = endRow - startRow;
    int srcOffset = startRow * new_width;
    int dstOffset = 0;
    int copySize = numberOfRows * new_width * sizeof(uint32_t);
    // 直接拷贝内存块
    memcpy(&validPixs[dstOffset], &pixels[srcOffset], copySize);

    // 释放pixels
    free(pixels);
     */
    // 分配像素数组
    uint32_t *pixels = (uint32_t *)malloc(new_width * new_height * sizeof(uint32_t));

    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    CGContextRef context = CGBitmapContextCreate(pixels, new_width, new_height, 8, new_width * sizeof(uint32_t), colorSpace, kCGBitmapByteOrder32Little | kCGImageAlphaPremultipliedLast);
    CGContextDrawImage(context, CGRectMake(0, 0, new_width, new_height), [newBitmap CGImage]);
    CGColorSpaceRelease(colorSpace);
    CGContextRelease(context);

    // 计算起始偏移和拷贝的大小
    int startRow = new_topBeyondDistance;
//            int endRow = new_height - new_bottomBeyondDistance;
//            int numberOfRows = endRow - startRow;
    int srcOffset = startRow * new_width;
//            int copySize = numberOfRows * new_width * sizeof(uint32_t);

    // 直接使用原始像素数组的有效部分
    uint32_t *validPixels = pixels + srcOffset;
    
    RowData *rowData = [self createRowData:validPixels width:new_width height:valid_height threshold:threshold dithering:dithering compress:compress initialErrors:initialErrors lastRowErrors:lastRowErrors];
    
    // 释放原始像素数组
    free(pixels);
    
    return rowData;
}

+(RowData *)createRowData:(nonnull uint32_t *)pixels width:(int)width height:(int)height threshold:(int)threshold dithering:(BOOL)dithering compress:(BOOL)compress initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors{
    
    //像素将画在这个数组
    uint32_t *gray = (uint32_t *)malloc(width * height * sizeof(uint32_t));
    //清空像素数组
    memset(gray, 0, width * height * sizeof(uint32_t));
    
    [self bitmapToGray:pixels gray:gray width:width height:height];
    
    if (dithering) {
        [self formatGrayToFloydDithering:gray width:width height:height threshold:threshold initialErrors:initialErrors lastRowErrors:lastRowErrors];
    }
    
    uint32_t *binary = (uint32_t *)malloc(width * height * sizeof(uint32_t));
    //清空像素数组
    memset(binary, 0, width * height * sizeof(uint32_t));
    
    [self grayToBinary:gray binary:binary width:width height:height threshold:threshold];
    
    free(gray);
    
    NSData *data72 = [self formatBinary69ToData72ByCol:binary width:width height:height];
    
    free(binary);
    
    if(compress){
        data72 = [Compress compressRowData:data72];
    }
    
    //对data72进行压缩
    //    NSData *commpressData = [ZlibUtils compressData:data72];
    //    NSData *uncommpressData = [ZlibUtils uncompressData:commpressData];
    //    CGFloat size = [data72 length]/1024.0f;
    //    CGFloat csize = [commpressData length]/1024.0f;
    //    CGFloat ucsize = [uncommpressData length]/1024.0f;
    //    RBQLog3(@"【单行原始数据-压缩-解压】原数据->size:%fk; 压缩数据->csize:%fk; 解压数据->ucsize:%fk",size,csize,ucsize);
    
    NSString *dataPath = [MxFileManager saveDataToDataCacheFile:data72];
    
    RowData *rowData = [[RowData alloc] init];
    rowData.rowDataPath = dataPath;
    rowData.dataLength = data72.length;
    rowData.compress = compress;
    
    return rowData;
}


+(void)imageSimulationWithSave:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors onStart:(void (^)(void))onStart onComplete:(void (^)(NSString *simulationPath))onComplete error:(void (^)(void))onError{
    
    __weak typeof(self) weakSelf = self;
    if (!image) {
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onError){
                onError();
            }
        });
        return;
    }
    
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onStart){
                onStart();
            }
        });
        
        NSString *simulationPath = [weakSelf imageSimulationWithSave:image threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress topBeyondDistance:topBeyondDistance bottomBeyondDistance:bottomBeyondDistance isZoomTo552:isZoomTo552 initialErrors:initialErrors lastRowErrors:lastRowErrors];
        if (!simulationPath) {
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if(onError){
                    onError();
                }
            });
            return;
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onComplete){
                onComplete(simulationPath);
            }
        });
        
    });
    
}

+(NSString *)imageSimulationWithSave:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors{
    UIImage *simulationImage = [self imageSimulation:image threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress topBeyondDistance:topBeyondDistance bottomBeyondDistance:bottomBeyondDistance isZoomTo552:isZoomTo552 rowLayoutDirection:RowLayoutDirectionVert initialErrors:initialErrors lastRowErrors:lastRowErrors];
    NSString *simulationPath = [MxFileManager saveImageToCache:simulationImage];
    return simulationPath;
}

+(void)imageSimulationWithSave:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors onStart:(void (^)(void))onStart onComplete:(void (^)(NSString *simulationPath))onComplete error:(void (^)(void))onError{
    
    __weak typeof(self) weakSelf = self;
    if (!image) {
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onError){
                onError();
            }
        });
        return;
    }
    
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onStart){
                onStart();
            }
        });
        
        NSString *simulationPath = [weakSelf imageSimulationWithSave:image threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress topBeyondDistance:topBeyondDistance bottomBeyondDistance:bottomBeyondDistance isZoomTo552:isZoomTo552 rowLayoutDirection:rowLayoutDirection initialErrors:initialErrors lastRowErrors:lastRowErrors];
        if (!simulationPath) {
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if(onError){
                    onError();
                }
            });
            return;
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onComplete){
                onComplete(simulationPath);
            }
        });
        
    });
    
}

+(NSString *)imageSimulationWithSave:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors {
    UIImage *simulationImage = [self imageSimulation:image threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress topBeyondDistance:topBeyondDistance bottomBeyondDistance:bottomBeyondDistance isZoomTo552:isZoomTo552 rowLayoutDirection:rowLayoutDirection initialErrors:initialErrors lastRowErrors:lastRowErrors];
    NSString *simulationPath = [MxFileManager saveImageToCache:simulationImage];
    return simulationPath;
}

+(NSString *)imageSimulationWithSave:(uint32_t *)pixels width:(CGFloat)width height:(CGFloat)height threshold:(int)threshold dithering:(BOOL)dithering compress:(BOOL)compress  rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors{
    UIImage *simulationImage = [self imageSimulation:pixels width:width height:height threshold:threshold dithering:dithering compress:compress rowLayoutDirection:rowLayoutDirection initialErrors:initialErrors lastRowErrors:lastRowErrors];
    NSString *simulationPath = [MxFileManager saveImageToCache:simulationImage];
    return simulationPath;
}

+(void)imageSimulation:(UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors onStart:(void (^)(void))onStart onComplete:(void (^)(UIImage *simulationImage))onComplete error:(void (^)(void))onError{
    
    __weak typeof(self) weakSelf = self;
    if (!image) {
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onError){
                onError();
            }
        });
        return;
    }
    
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onStart){
                onStart();
            }
        });
        
        UIImage *simulationImage = [weakSelf imageSimulation:image threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress topBeyondDistance:topBeyondDistance bottomBeyondDistance:bottomBeyondDistance isZoomTo552:isZoomTo552 rowLayoutDirection:RowLayoutDirectionVert initialErrors:initialErrors lastRowErrors:lastRowErrors];
        if (!simulationImage) {
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if(onError){
                    onError();
                }
            });
            return;
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onComplete){
                onComplete(simulationImage);
            }
        });
        
    });
    
}

+(UIImage *)imageSimulation:(UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors {
    return [self imageSimulation:image threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress topBeyondDistance:topBeyondDistance bottomBeyondDistance:bottomBeyondDistance isZoomTo552:isZoomTo552 rowLayoutDirection:RowLayoutDirectionVert initialErrors:initialErrors lastRowErrors:lastRowErrors];
}

+(void)imageSimulation:(UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors onStart:(void (^)(void))onStart onComplete:(void (^)(UIImage *simulationImage))onComplete error:(void (^)(void))onError{
    
    __weak typeof(self) weakSelf = self;
    if (!image) {
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onError){
                onError();
            }
        });
        return;
    }
    
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onStart){
                onStart();
            }
        });
        
        UIImage *simulationImage = [weakSelf imageSimulation:image threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress topBeyondDistance:topBeyondDistance bottomBeyondDistance:bottomBeyondDistance isZoomTo552:isZoomTo552 rowLayoutDirection:rowLayoutDirection initialErrors:initialErrors lastRowErrors:lastRowErrors];
        if (!simulationImage) {
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if(onError){
                    onError();
                }
            });
            return;
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onComplete){
                onComplete(simulationImage);
            }
        });
        
    });
    
}

+(UIImage *)imageSimulation:(UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors {
    
    CGFloat width = image.size.width;
    CGFloat height = image.size.height;
    
    UIImage *newBitmap;
    CGFloat valid_height = height - topBeyondDistance - bottomBeyondDistance;
    int new_width;
    int new_height;
    CGFloat new_topBeyondDistance = topBeyondDistance;
    CGFloat new_bottomBeyondDistance = bottomBeyondDistance;
    //如果高度不为552，则缩放到552
    if(valid_height != 552.0f && isZoomTo552 ){
        
        CGFloat scale = 552.0f/valid_height;
        
        new_topBeyondDistance = topBeyondDistance * scale;
        new_bottomBeyondDistance = bottomBeyondDistance * scale;
        
        CGFloat temp_width = floor(width * scale);
        CGFloat temp_height = 552.0f + new_topBeyondDistance + new_bottomBeyondDistance;
        newBitmap = [UIImage scaleToSize:image size:CGSizeMake(temp_width, temp_height)];
        //这里valid_height不为552则进行缩放，那么缩放后valid_height的值则变为552了
        valid_height = 552;
        new_width = temp_width;
        new_height = temp_height;
        
    }else{
        
        newBitmap = image;
        new_width = floor(width);
        new_height = floor(height);
        new_topBeyondDistance = topBeyondDistance;
        new_bottomBeyondDistance = bottomBeyondDistance;
    }
    
    if (clearBackground) {
        newBitmap = [OpenCVUtils lightClearBackground:newBitmap];
    }
    
    RBQLog3(@"【imageSimulation】width:%f;height:%f;new_width:%d;new_height:%d;topBeyondDistance:%d;bottomBeyondDistance:%d;new_topBeyondDistance:%f;new_bottomBeyondDistance:%f;valid_height:%f",width,height,new_width,new_height,topBeyondDistance,bottomBeyondDistance,new_topBeyondDistance,new_bottomBeyondDistance,valid_height);
    
    /*
    uint32_t *pixels = (uint32_t *)malloc(new_width * new_height * sizeof(uint32_t));
    memset(pixels, 0, new_width * new_height * sizeof(uint32_t));
    
    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    // CGBitmapContextCreate  该函数带入的参数不能带小数，故上边都进行了取余运算
    CGContextRef context = CGBitmapContextCreate(pixels, new_width, new_height, 8, new_width * sizeof(uint32_t), colorSpace, kCGBitmapByteOrder32Little | kCGImageAlphaPremultipliedLast);
    CGContextDrawImage(context, CGRectMake(0, 0, new_width, new_height), [newBitmap CGImage]);
    CGContextRelease(context);
    CGColorSpaceRelease(colorSpace);
    
    //取出有效的pix
    uint32_t *validPixels = (uint32_t *)malloc(new_width * valid_height * sizeof(uint32_t));
    memset(validPixels, 0, new_width * valid_height * sizeof(uint32_t));
    
    // 计算起始偏移和拷贝的大小
    int startRow = new_topBeyondDistance;
    int endRow = new_height - new_bottomBeyondDistance;
    int numberOfRows = endRow - startRow;
    int srcOffset = startRow * new_width;
    int dstOffset = 0;
    int copySize = numberOfRows * new_width * sizeof(uint32_t);
    // 直接拷贝内存块
    memcpy(&validPixels[dstOffset], &pixels[srcOffset], copySize);
    
    free(pixels);
     */
    uint32_t *pixels = (uint32_t *)malloc(new_width * new_height * sizeof(uint32_t));

    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    CGContextRef context = CGBitmapContextCreate(pixels, new_width, new_height, 8, new_width * sizeof(uint32_t), colorSpace, kCGBitmapByteOrder32Little | kCGImageAlphaPremultipliedLast);
    CGContextDrawImage(context, CGRectMake(0, 0, new_width, new_height), [newBitmap CGImage]);
    CGColorSpaceRelease(colorSpace);
    CGContextRelease(context);

    // 计算起始偏移和拷贝的大小
    int startRow = new_topBeyondDistance;
//            int endRow = new_height - new_bottomBeyondDistance;
//            int numberOfRows = endRow - startRow;
    int srcOffset = startRow * new_width;
//            int copySize = numberOfRows * new_width * sizeof(uint32_t);

    // 直接使用原始像素数组的有效部分
    uint32_t *validPixels = pixels + srcOffset;
    
    UIImage *result = [self imageSimulation:validPixels width:new_width height:valid_height threshold:threshold dithering:dithering compress:compress rowLayoutDirection:rowLayoutDirection initialErrors:initialErrors lastRowErrors:lastRowErrors];
    
    free(pixels);
    
    return result;
}

+(UIImage *)imageSimulation:(uint32_t *)pixels width:(CGFloat)width height:(CGFloat)height threshold:(int)threshold dithering:(BOOL)dithering compress:(BOOL)compress rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors {
    
    uint32_t *gray = (uint32_t *)malloc(width * height * sizeof(uint32_t));
    memset(gray, 0, width * height * sizeof(uint32_t));
    
    [self bitmapToGray:pixels gray:gray width:width height:height];
    
    if (dithering) {
        [self formatGrayToFloydDithering:gray width:width height:height threshold:threshold initialErrors:initialErrors lastRowErrors:lastRowErrors];
    }
    
    uint32_t *binary = (uint32_t *)malloc(width * height * sizeof(uint32_t));
    //清空像素数组
    memset(binary, 0, width * height * sizeof(uint32_t));
    
    [self grayToBinary:gray binary:binary width:width height:height threshold:threshold];
    free(gray);
    
    UIImage *resultImage = [self imageSimulationByBinary:binary width:width height:height compress:compress rowLayoutDirection:rowLayoutDirection];
    free(binary);
    
    return resultImage;
}

+(NSString *)imageSimulationByBinarySave:(uint32_t *)binary width:(CGFloat)width height:(CGFloat)height compress:(BOOL)compress rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection{
    UIImage *simulationImage = [self imageSimulationByBinary:binary width:width height:height compress:compress rowLayoutDirection:rowLayoutDirection];
    NSString *simulationPath = [MxFileManager saveImageToCache:simulationImage];
    return simulationPath;
}

+(UIImage *)imageSimulationByBinary:(uint32_t *)binary width:(CGFloat)width height:(CGFloat)height compress:(BOOL)compress rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection {
    
    UIImage *resultImage = nil;
    if (compress) {
        
        uint32_t *uncompress = (uint32_t *)malloc(width * height * sizeof(uint32_t));
        memset(uncompress, 0, width * height * sizeof(uint32_t));
        
        [Compress mergeSimulationCompressWithUncompress:binary uncompress:uncompress width:width height:height];
        
        CGColorSpaceRef compressColorSpace = CGColorSpaceCreateDeviceRGB();
        CGContextRef compressContext = CGBitmapContextCreate(uncompress, width, height, 8, width * sizeof(uint32_t), compressColorSpace, kCGBitmapByteOrder32Little | kCGImageAlphaPremultipliedLast);
        CGImageRef compressImageRef = CGBitmapContextCreateImage(compressContext);
        CGContextRelease(compressContext);
        CGColorSpaceRelease(compressColorSpace);
        resultImage = [UIImage imageWithCGImage:compressImageRef];
        CGImageRelease(compressImageRef);
        
        free(uncompress);
        
    } else {
        
        CGColorSpaceRef pixelsColorSpace = CGColorSpaceCreateDeviceRGB();
        CGContextRef pixelsContext = CGBitmapContextCreate(binary, width, height, 8, width * sizeof(uint32_t), pixelsColorSpace, kCGBitmapByteOrder32Little | kCGImageAlphaPremultipliedLast);
        CGImageRef pixelsImageRef = CGBitmapContextCreateImage(pixelsContext);
        CGContextRelease(pixelsContext);
        CGColorSpaceRelease(pixelsColorSpace);
        resultImage = [UIImage imageWithCGImage:pixelsImageRef];
        CGImageRelease(pixelsImageRef);
        
    }
    if(rowLayoutDirection == RowLayoutDirectionHorz){
        resultImage = [self rotatedImageWithGraphicsByRadians:resultImage radians:-M_PI_2];
    }
    return resultImage;
}

//
#pragma mark 第二套merge合并计算的api ----begin----
+(void)mergeBitmapToGrayFloydDitheringBinary:(nonnull uint32_t *)pixels binary:(nonnull uint32_t *)binary width:(int)width height:(int)height threshold:(int)threshold dithering:(BOOL)dithering compress:(BOOL)compress initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors {
    
    // 分配灰度图像和二值图像的内存  这个也没必要重新申请内存了，和binary存储数据类型相同，直接使用binary即可
//    uint32_t *gray = (uint32_t *)malloc(width * height * sizeof(uint32_t));
//    memset(gray, 0, width * height * sizeof(uint32_t));
    
    //缓存处理当下一行变成当前行时，将下一行数据交换到该缓存
    uint32_t *currentRowErrors = (uint32_t *)malloc(width * sizeof(uint32_t));
    memset(currentRowErrors, 0, width * sizeof(uint32_t));
    
    // 缓存下一行的差值
    uint32_t *nextRowErrors = (uint32_t *)malloc(width * sizeof(uint32_t));
    memset(nextRowErrors, 0, width * sizeof(uint32_t));
    
    uint32_t rightError = 0;
    
    for (int row = 0; row < height; row++) {
        //每次重新起行的时候，将右边差值值0
        rightError = 0;
        
        for (int col = 0; col < width; col++) {
            
            int index = row * width + col;
            
            // 将RGB转换为灰度值
            uint8_t *rgbaPixel = (uint8_t *)&pixels[index];
            int red = rgbaPixel[1];
            int green = rgbaPixel[2];
            int blue = rgbaPixel[3];
            binary[index] = (red * 77 + green * 151 + blue * 28) >> 8;
            
            // 如果有初始误差，应用到第一行
            if (row == 0 && initialErrors != NULL && initialErrors != nil) {
                binary[index] += initialErrors[col];
            }
            
            if (dithering) {
                // 获取当前像素值并加上误差 int oldPixel = gray[index];
                int oldPixel = binary[index] + rightError + currentRowErrors[col];
                int newPixel = (oldPixel > threshold) ? 255 : 0;
                binary[index] = newPixel;
                
                rightError = 0;
                
                // 计算误差并进行传播
                int error = oldPixel - newPixel;
                // 将误差分配给右侧像素（权重 7/16）  if (col + 1 < width) gray[index + 1] += e * 7 / 16;
                if (col + 1 < width) rightError = error * 7 / 16;
//                if (row + 1 < height) {  // 这里计算下一行的误差，由于有单独的误差传递机制，则无需再加该条件，直接将误差传递到缓存当中
                    if (col > 0) nextRowErrors[col - 1] += error * 3 / 16;
                    nextRowErrors[col] += error * 5 / 16;
                    if (col + 1 < width) nextRowErrors[col + 1] += error * 1 / 16;
//                }
            }
            // 根据阈值将灰度值转换为二值图像
            binary[index] = -(binary[index] >= threshold) | 0xFF;
            
        }
        
        // 交换缓存，准备处理下一行
        memcpy(currentRowErrors, nextRowErrors, width * sizeof(uint32_t));
        memset(nextRowErrors, 0, width * sizeof(uint32_t));
    }
    
//    free(gray);
    free(nextRowErrors);
    
    // 保存最后一行的误差
    if (lastRowErrors != NULL && lastRowErrors != nil) {
        *lastRowErrors = currentRowErrors;
    } else {
        free(currentRowErrors);
    }
    
}

+(RowData *)mergeCreateRowData:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors{
    
    CGFloat width = image.size.width;
    CGFloat height = image.size.height;
    
    UIImage *newBitmap;
    CGFloat valid_height = height - topBeyondDistance - bottomBeyondDistance;
    CGFloat new_width;
    CGFloat new_height;
    CGFloat new_topBeyondDistance;
    CGFloat new_bottomBeyondDistance;
    //如果高度不为552，则缩放到552
    if(valid_height != 552.0f ){
        
        CGFloat scale = 552.0f/valid_height;
        
        new_topBeyondDistance = topBeyondDistance * scale;
        new_bottomBeyondDistance = bottomBeyondDistance * scale;
        
        CGFloat temp_width = floor(width * scale);
        CGFloat temp_height = 552.0f + new_topBeyondDistance + new_bottomBeyondDistance;
        newBitmap = [UIImage scaleToSize:image size:CGSizeMake(temp_width, temp_height)];
        //这里valid_height不为552则进行缩放，那么缩放后valid_height的值则变为552了
        valid_height = 552;
        new_width = temp_width;
        new_height = temp_height;
        
    }else{
        
        newBitmap = image;
        new_width = floor(width);
        new_height = height;
        new_topBeyondDistance = topBeyondDistance;
        new_bottomBeyondDistance = bottomBeyondDistance;
    }
    
    RBQLog3(@"【createRowData】{width:%f; height:%f; valid_height:%f; topBeyondDistance:%d; bottomBeyondDistance:%d; new_width:%f; new_height:%f; new_topBeyondDistance:%f; new_bottomBeyondDistance:%f;新->valid_height:%f}",width,height,(height - topBeyondDistance - bottomBeyondDistance),topBeyondDistance,bottomBeyondDistance,new_width,new_height,new_topBeyondDistance,new_bottomBeyondDistance,valid_height);
    
    if (clearBackground) {
        newBitmap = [OpenCVUtils lightClearBackground:newBitmap];
    }
    
    // 分配像素数组
    uint32_t *pixels = (uint32_t *)malloc(new_width * new_height * sizeof(uint32_t));

    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    CGContextRef context = CGBitmapContextCreate(pixels, new_width, new_height, 8, new_width * sizeof(uint32_t), colorSpace, kCGBitmapByteOrder32Little | kCGImageAlphaPremultipliedLast);
    CGContextDrawImage(context, CGRectMake(0, 0, new_width, new_height), [newBitmap CGImage]);
    CGColorSpaceRelease(colorSpace);
    CGContextRelease(context);

    // 计算起始偏移和拷贝的大小
    int startRow = new_topBeyondDistance;
//            int endRow = new_height - new_bottomBeyondDistance;
//            int numberOfRows = endRow - startRow;
    int srcOffset = startRow * new_width;
//            int copySize = numberOfRows * new_width * sizeof(uint32_t);

    // 直接使用原始像素数组的有效部分
    uint32_t *validPixels = pixels + srcOffset;
    
    RowData *rowData = [self mergeCreateRowData:validPixels width:new_width height:valid_height threshold:threshold dithering:dithering compress:compress initialErrors:initialErrors lastRowErrors:lastRowErrors];
    
    // 释放原始像素数组
    free(pixels);
    
    return rowData;
    
}

+(RowData *)mergeCreateRowData:(nonnull uint32_t *)pixels width:(int)width height:(int)height threshold:(int)threshold dithering:(BOOL)dithering compress:(BOOL)compress initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors {
    
    uint32_t *binary = (uint32_t *)malloc(width * height * sizeof(uint32_t));
    memset(binary, 0, width * height * sizeof(uint32_t));
    
    [self mergeBitmapToGrayFloydDitheringBinary:pixels binary:binary width:width height:height threshold:threshold dithering:dithering compress:compress initialErrors:initialErrors lastRowErrors:lastRowErrors];
    
    // 将二值图像数据转换为所需格式
    NSData *data72 = [self formatBinary69ToData72ByCol:binary width:width height:height];
    
    // 释放分配的内存
    free(binary);
    
    // 如果需要压缩，则压缩数据
    if (compress) {
        data72 = [Compress compressRowData:data72];
    }
    
    // 将数据保存到缓存文件中
    NSString *dataPath = [MxFileManager saveDataToDataCacheFile:data72];
    
    // 创建 RowData 对象并返回
    RowData *rowData = [[RowData alloc] init];
    rowData.rowDataPath = dataPath;
    rowData.dataLength = data72.length;
    rowData.compress = compress;
    
    return rowData;
}

+(void)mergeImageSimulationWithSave:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors onStart:(void (^)(void))onStart onComplete:(void (^)(NSString *simulationPath))onComplete error:(void (^)(void))onError{
    
    __weak typeof(self) weakSelf = self;
    if (!image) {
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onError){
                onError();
            }
        });
        return;
    }
    
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onStart){
                onStart();
            }
        });
        
        NSString *simulationPath = [weakSelf mergeImageSimulationWithSave:image threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress topBeyondDistance:topBeyondDistance bottomBeyondDistance:bottomBeyondDistance isZoomTo552:isZoomTo552 initialErrors:initialErrors lastRowErrors:lastRowErrors];
        if (!simulationPath) {
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if(onError){
                    onError();
                }
            });
            return;
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onComplete){
                onComplete(simulationPath);
            }
        });
        
    });
    
}

+(NSString *)mergeImageSimulationWithSave:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors{
    UIImage *simulationImage = [self mergeImageSimulation:image threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress topBeyondDistance:topBeyondDistance bottomBeyondDistance:bottomBeyondDistance isZoomTo552:isZoomTo552 rowLayoutDirection:RowLayoutDirectionVert initialErrors:initialErrors lastRowErrors:lastRowErrors];
    NSString *simulationPath = [MxFileManager saveImageToCache:simulationImage];
    return simulationPath;
}

+(void)mergeImageSimulationWithSave:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors onStart:(void (^)(void))onStart onComplete:(void (^)(NSString *simulationPath))onComplete error:(void (^)(void))onError{
    
    __weak typeof(self) weakSelf = self;
    if (!image) {
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onError){
                onError();
            }
        });
        return;
    }
    
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onStart){
                onStart();
            }
        });
        
        NSString *simulationPath = [weakSelf mergeImageSimulationWithSave:image threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress topBeyondDistance:topBeyondDistance bottomBeyondDistance:bottomBeyondDistance isZoomTo552:isZoomTo552 rowLayoutDirection:rowLayoutDirection initialErrors:initialErrors lastRowErrors:lastRowErrors];
        if (!simulationPath) {
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if(onError){
                    onError();
                }
            });
            return;
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onComplete){
                onComplete(simulationPath);
            }
        });
        
    });
    
}

+(NSString *)mergeImageSimulationWithSave:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors {
    UIImage *simulationImage = [self mergeImageSimulation:image threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress topBeyondDistance:topBeyondDistance bottomBeyondDistance:bottomBeyondDistance isZoomTo552:isZoomTo552 rowLayoutDirection:rowLayoutDirection initialErrors:initialErrors lastRowErrors:lastRowErrors];
    NSString *simulationPath = [MxFileManager saveImageToCache:simulationImage];
    return simulationPath;
}

+(NSString *)mergeImageSimulationWithSave:(uint32_t *)pixels width:(CGFloat)width height:(CGFloat)height threshold:(int)threshold dithering:(BOOL)dithering compress:(BOOL)compress  rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors{
    UIImage *simulationImage = [self mergeImageSimulation:pixels width:width height:height threshold:threshold dithering:dithering compress:compress rowLayoutDirection:rowLayoutDirection initialErrors:initialErrors lastRowErrors:lastRowErrors];
    NSString *simulationPath = [MxFileManager saveImageToCache:simulationImage];
    return simulationPath;
}

+(void)mergeImageSimulation:(UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors onStart:(void (^)(void))onStart onComplete:(void (^)(UIImage *simulationImage))onComplete error:(void (^)(void))onError{
    
    __weak typeof(self) weakSelf = self;
    if (!image) {
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onError){
                onError();
            }
        });
        return;
    }
    
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onStart){
                onStart();
            }
        });
        
        UIImage *simulationImage = [weakSelf mergeImageSimulation:image threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress topBeyondDistance:topBeyondDistance bottomBeyondDistance:bottomBeyondDistance isZoomTo552:isZoomTo552 rowLayoutDirection:RowLayoutDirectionVert initialErrors:initialErrors lastRowErrors:lastRowErrors];
        if (!simulationImage) {
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if(onError){
                    onError();
                }
            });
            return;
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onComplete){
                onComplete(simulationImage);
            }
        });
        
    });
    
}

+(UIImage *)mergeImageSimulation:(UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors {
    return [self mergeImageSimulation:image threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress topBeyondDistance:topBeyondDistance bottomBeyondDistance:bottomBeyondDistance isZoomTo552:isZoomTo552 rowLayoutDirection:RowLayoutDirectionVert initialErrors:initialErrors lastRowErrors:lastRowErrors];
}

+(void)mergeImageSimulation:(UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors onStart:(void (^)(void))onStart onComplete:(void (^)(UIImage *simulationImage))onComplete error:(void (^)(void))onError{
    
    __weak typeof(self) weakSelf = self;
    if (!image) {
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onError){
                onError();
            }
        });
        return;
    }
    
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onStart){
                onStart();
            }
        });
        
        UIImage *simulationImage = [weakSelf mergeImageSimulation:image threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress topBeyondDistance:topBeyondDistance bottomBeyondDistance:bottomBeyondDistance isZoomTo552:isZoomTo552 rowLayoutDirection:rowLayoutDirection initialErrors:initialErrors lastRowErrors:lastRowErrors];
        if (!simulationImage) {
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if(onError){
                    onError();
                }
            });
            return;
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onComplete){
                onComplete(simulationImage);
            }
        });
        
    });
    
}

+(UIImage *)mergeImageSimulation:(UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors {
    
    CGFloat width = image.size.width;
    CGFloat height = image.size.height;
    
    UIImage *newBitmap;
    CGFloat valid_height = height - topBeyondDistance - bottomBeyondDistance;
    int new_width;
    int new_height;
    CGFloat new_topBeyondDistance = topBeyondDistance;
    CGFloat new_bottomBeyondDistance = bottomBeyondDistance;
    //如果高度不为552，则缩放到552
    if(valid_height != 552.0f && isZoomTo552 ){
        
        CGFloat scale = 552.0f/valid_height;
        
        new_topBeyondDistance = topBeyondDistance * scale;
        new_bottomBeyondDistance = bottomBeyondDistance * scale;
        
        CGFloat temp_width = floor(width * scale);
        CGFloat temp_height = 552.0f + new_topBeyondDistance + new_bottomBeyondDistance;
        newBitmap = [UIImage scaleToSize:image size:CGSizeMake(temp_width, temp_height)];
        //这里valid_height不为552则进行缩放，那么缩放后valid_height的值则变为552了
        valid_height = 552;
        new_width = temp_width;
        new_height = temp_height;
        
    }else{
        
        newBitmap = image;
        new_width = floor(width);
        new_height = floor(height);
        new_topBeyondDistance = topBeyondDistance;
        new_bottomBeyondDistance = bottomBeyondDistance;
    }
    
    if (clearBackground) {
        newBitmap = [OpenCVUtils lightClearBackground:newBitmap];
    }
    
    RBQLog3(@"【imageSimulation】width:%f;height:%f;new_width:%d;new_height:%d;topBeyondDistance:%d;bottomBeyondDistance:%d;new_topBeyondDistance:%f;new_bottomBeyondDistance:%f;valid_height:%f",width,height,new_width,new_height,topBeyondDistance,bottomBeyondDistance,new_topBeyondDistance,new_bottomBeyondDistance,valid_height);
    
    /*
    uint32_t *pixels = (uint32_t *)malloc(new_width * new_height * sizeof(uint32_t));
    memset(pixels, 0, new_width * new_height * sizeof(uint32_t));
    
    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    // CGBitmapContextCreate  该函数带入的参数不能带小数，故上边都进行了取余运算
    CGContextRef context = CGBitmapContextCreate(pixels, new_width, new_height, 8, new_width * sizeof(uint32_t), colorSpace, kCGBitmapByteOrder32Little | kCGImageAlphaPremultipliedLast);
    CGContextDrawImage(context, CGRectMake(0, 0, new_width, new_height), [newBitmap CGImage]);
    CGContextRelease(context);
    CGColorSpaceRelease(colorSpace);
    
    //取出有效的pix
    uint32_t *validPixels = (uint32_t *)malloc(new_width * valid_height * sizeof(uint32_t));
    memset(validPixels, 0, new_width * valid_height * sizeof(uint32_t));
    
    // 计算起始偏移和拷贝的大小
    int startRow = new_topBeyondDistance;
    int endRow = new_height - new_bottomBeyondDistance;
    int numberOfRows = endRow - startRow;
    int srcOffset = startRow * new_width;
    int dstOffset = 0;
    int copySize = numberOfRows * new_width * sizeof(uint32_t);
    // 直接拷贝内存块
    memcpy(&validPixels[dstOffset], &pixels[srcOffset], copySize);
    
    free(pixels);
     */
    uint32_t *pixels = (uint32_t *)malloc(new_width * new_height * sizeof(uint32_t));

    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    CGContextRef context = CGBitmapContextCreate(pixels, new_width, new_height, 8, new_width * sizeof(uint32_t), colorSpace, kCGBitmapByteOrder32Little | kCGImageAlphaPremultipliedLast);
    CGContextDrawImage(context, CGRectMake(0, 0, new_width, new_height), [newBitmap CGImage]);
    CGColorSpaceRelease(colorSpace);
    CGContextRelease(context);

    // 计算起始偏移和拷贝的大小
    int startRow = new_topBeyondDistance;
//            int endRow = new_height - new_bottomBeyondDistance;
//            int numberOfRows = endRow - startRow;
    int srcOffset = startRow * new_width;
//            int copySize = numberOfRows * new_width * sizeof(uint32_t);

    // 直接使用原始像素数组的有效部分
    uint32_t *validPixels = pixels + srcOffset;
    
    UIImage *result = [self mergeImageSimulation:validPixels width:new_width height:valid_height threshold:threshold dithering:dithering compress:compress rowLayoutDirection:rowLayoutDirection initialErrors:initialErrors lastRowErrors:lastRowErrors];
    
    free(pixels);
    
    return result;
}

+(UIImage *)mergeImageSimulation:(uint32_t *)pixels width:(CGFloat)width height:(CGFloat)height threshold:(int)threshold dithering:(BOOL)dithering compress:(BOOL)compress rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors {
    
    uint32_t *binary = (uint32_t *)malloc(width * height * sizeof(uint32_t));
    //清空像素数组
    memset(binary, 0, width * height * sizeof(uint32_t));
    
    [self mergeBitmapToGrayFloydDitheringBinary:pixels binary:binary width:width height:height threshold:threshold dithering:dithering compress:compress initialErrors:initialErrors lastRowErrors:lastRowErrors];
    
    UIImage *resultImage = [self imageSimulationByBinary:binary width:width height:height compress:compress rowLayoutDirection:rowLayoutDirection];
    free(binary);
    return resultImage;
}

#pragma mark 第二套merge合并计算的api ----end----

+ (UIImage *)rotatedImageWithGraphicsByRadians:(UIImage *)image radians:(CGFloat)radians {
    if(!image){
        return nil;
    }
    CGRect rotatedRect = CGRectApplyAffineTransform(CGRectMake(0, 0, image.size.width, image.size.height), CGAffineTransformMakeRotation(radians));
    
    CGSize rotatedSize = CGSizeMake(floor(rotatedRect.size.width), floor(rotatedRect.size.height));

//    CGFloat roundedWidth = floor(rotatedSize.width * 1000000) / 1000000;
//    CGFloat roundedHeight = floor(rotatedSize.height * 1000000) / 1000000;
//    CGSize rotatedSize = CGSizeMake(roundedWidth, roundedHeight);
    
    RBQLog3(@"【rotatedImageWithGraphicsByRadians】rotatedSize:%@",NSStringFromCGSize(rotatedSize))
    
    UIGraphicsBeginImageContextWithOptions(rotatedSize, NO, image.scale);
    CGContextRef context = UIGraphicsGetCurrentContext();
    
    CGContextTranslateCTM(context, rotatedSize.width / 2, rotatedSize.height / 2);
    CGContextRotateCTM(context, radians);
    CGContextTranslateCTM(context, -image.size.width / 2, -image.size.height / 2);
    
    [image drawInRect:CGRectMake(0, 0, image.size.width, image.size.height)];
    
    UIImage *rotatedImage = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    
    return rotatedImage;
}

#pragma mark  betterMerge 相关方法开始位置，这里代表更强大的融合
+(void)betterMergeBitmapToData72:(nonnull uint32_t *)pixels binary:(nonnull uint32_t *)binary d72:(nonnull uint8_t *)d72 width:(int)width height:(int)height threshold:(int)threshold dithering:(BOOL)dithering compress:(BOOL)compress initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors {
    
    uint8_t *d69 = (uint8_t *)calloc(width * 69, sizeof(uint8_t));
    memset(d69, 0, width * 69 * sizeof(uint8_t));
    
    //缓存处理当下一行变成当前行时，将下一行数据交换到该缓存
    uint32_t *currentRowErrors = (uint32_t *)malloc(width * sizeof(uint32_t));
    memset(currentRowErrors, 0, width * sizeof(uint32_t));
    
    // 缓存下一行的差值
    uint32_t *nextRowErrors = (uint32_t *)malloc(width * sizeof(uint32_t));
    memset(nextRowErrors, 0, width * sizeof(uint32_t));
    
    uint32_t rightError = 0;
    
    // 提前计算常量
    int cycleOffsets[6] = {0, 48, 24, 60, 12, 36};
    uint8_t bitShiftTable[8] = {0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01};
    
    for (int row = 0; row < height; row++) {
        //每次重新起行的时候，将右边差值值0
        rightError = 0;
        
        for (int col = 0; col < width; col++) {
            
            int index = row * width + col;
            
            // 将RGB转换为灰度值
            uint8_t *rgbaPixel = (uint8_t *)&pixels[index];
            int red = rgbaPixel[1];
            int green = rgbaPixel[2];
            int blue = rgbaPixel[3];
            binary[index] = (red * 77 + green * 151 + blue * 28) >> 8;
            
            // 如果有初始误差，应用到第一行
            if (row == 0 && initialErrors != NULL && initialErrors != nil) {
                binary[index] += initialErrors[col];
            }
            
            if (dithering) {
                // 获取当前像素值并加上误差 int oldPixel = gray[index];
                int oldPixel = binary[index] + rightError + currentRowErrors[col];
                int newPixel = (oldPixel > threshold) ? 255 : 0;
                binary[index] = newPixel;
                
                rightError = 0;
                
                // 计算误差并进行传播
                int error = oldPixel - newPixel;
                // 将误差分配给右侧像素（权重 7/16）  if (col + 1 < width) gray[index + 1] += e * 7 / 16;
                if (col + 1 < width) rightError = error * 7 / 16;
//                if (row + 1 < height) {  // 这里计算下一行的误差，由于有单独的误差传递机制，则无需再加该条件，直接将误差传递到缓存当中
                    if (col > 0) nextRowErrors[col - 1] += error * 3 / 16;
                    nextRowErrors[col] += error * 5 / 16;
                    if (col + 1 < width) nextRowErrors[col + 1] += error * 1 / 16;
//                }
            }
            // 根据阈值将灰度值转换为二值图像
            binary[index] = -(binary[index] >= threshold) | 0xFF;
            
            
            // d69计算
            int pixel = binary[col + width * row];
            
            if (pixel == 255) {
                int rowDiv8 = row / 8;
                d69[col * 69 + rowDiv8] |= bitShiftTable[row % 8];
            }
            
            // d69->d72
            if (d69[col * 69 + row / 8] & bitShiftTable[row % 8]) {
                int cycle = row % 6;
                int baseIndex = col * 72 + (row / 276) * 6;
                int cycleIndex = ((row % 276 - cycle) / 6) / 8;
                int dIndex = baseIndex + cycleOffsets[cycle] + cycleIndex;
                d72[dIndex] |= bitShiftTable[((row % 276) / 6) % 8];
            }
            
        }
        
        // 交换缓存，准备处理下一行
        memcpy(currentRowErrors, nextRowErrors, width * sizeof(uint32_t));
        memset(nextRowErrors, 0, width * sizeof(uint32_t));
    }
    free(d69);
//    free(binary);
    free(nextRowErrors);
    
    // 保存最后一行的误差
    if (lastRowErrors != NULL && lastRowErrors != nil) {
        *lastRowErrors = currentRowErrors;
    } else {
        free(currentRowErrors);
    }
    
}

@end
