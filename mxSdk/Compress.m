//
//  Compress.m
//  BelonPrinter
//
//  Created by rbq on 2020/11/2.
//  Copyright © 2020 rbq. All rights reserved.
//

#import "Compress.h"

@implementation Compress

+(NSMutableArray<NSData *> *)compressRowDataArr:(NSMutableArray<NSData *> *)data72Arr {
    
    // 检查输入数组的有效性
    if (!data72Arr || data72Arr.count == 0) return [NSMutableArray array];

    NSMutableArray<NSData *> *compress_data72_arr = [NSMutableArray arrayWithCapacity:data72Arr.count];

    for (NSData *_data72 in data72Arr) {

        const uint8_t *d72 = (const uint8_t *)[_data72 bytes];
        NSInteger d72Len = [_data72 length];

        NSInteger width = d72Len / 72;
        NSInteger cWidth = (width + 1) / 2; // 向上取整计算压缩后的宽度

        NSMutableData *c72 = [NSMutableData dataWithLength:cWidth * 72];

        for (int c = 0; c < cWidth; c++) {
            for (int r = 0; r < 72; r++) {
                if (c < cWidth - 1) {
                    uint8_t bt_0 = d72[r + (c * 2) * 72];
                    uint8_t bt_1 = d72[r + (c * 2 + 1) * 72];
                    ((uint8_t *)c72.mutableBytes)[r + c * 72] = bt_0 | bt_1;
                } else {
                    ((uint8_t *)c72.mutableBytes)[r + c * 72] = d72[r + (c * 2) * 72];
                }
            }
        }

        [compress_data72_arr addObject:c72];
    }

    return compress_data72_arr;
}

+(NSData *)compressRowData:(uint8_t *)d72 d72Len:(NSInteger)d72Len{
    
    NSInteger width = d72Len / 72;
    NSInteger cWidth = (width + 1) / 2; // 向上取整

    NSMutableData *c72 = [NSMutableData dataWithLength:cWidth * 72];
    uint8_t *cPtr = (uint8_t *)c72.mutableBytes;

    for (int c = 0; c < cWidth; c++) {
        for (int r = 0; r < 72; r++) {
            if (c * 2 + 1 < width) {
                uint8_t bt_0 = d72[r + (c * 2) * 72];
                uint8_t bt_1 = d72[r + (c * 2 + 1) * 72];
                cPtr[r + c * 72] = bt_0 | bt_1;
            } else {
                cPtr[r + c * 72] = d72[r + (c * 2) * 72];
            }
        }
    }

    return c72;
}

+(NSData *)compressRowData:(NSData *)data72{
    
    uint8_t *d72 = (uint8_t *)data72.bytes;
    NSInteger d72Len = data72.length;
    
    NSInteger width = d72Len / 72;
    NSInteger cWidth = (width + 1) / 2; // 向上取整

    NSMutableData *c72 = [NSMutableData dataWithLength:cWidth * 72];
    uint8_t *cPtr = (uint8_t *)c72.mutableBytes;

    for (int c = 0; c < cWidth; c++) {
        for (int r = 0; r < 72; r++) {
            if (c * 2 + 1 < width) {
                uint8_t bt_0 = d72[r + (c * 2) * 72];
                uint8_t bt_1 = d72[r + (c * 2 + 1) * 72];
                cPtr[r + c * 72] = bt_0 | bt_1;
            } else {
                cPtr[r + c * 72] = d72[r + (c * 2) * 72];
            }
        }
    }

    return c72;
}

/*
 模拟压缩和解压图片
 */
+(void)simulationCompressWithUncompress:(uint32_t*)pixels uncompress:(uint32_t *)uncompress width:(int)width height:(int)height {
    
    // 检查宽度和高度的有效性
    if (width <= 0 || height <= 0) return;

    // 向上取整计算压缩后的宽度
    int cWidth = (width + 1) / 2;
    uint32_t *c72 = (uint32_t *)malloc(cWidth * height * sizeof(uint32_t));
    memset(c72, 0, cWidth * height * sizeof(uint32_t));

    for (int r = 0; r < height; r++) {
        for (int cw = 0; cw < cWidth; cw++) {
            int bt_0 = pixels[r * width + (cw * 2)];
            int bt_1 = (cw < cWidth - 1) ? pixels[r * width + (cw * 2 + 1)] : 255;
            c72[r * cWidth + cw] = (bt_0 == 255 || bt_1 == 255) ? 255 : 0;
        }
    }

    for (int r = 0; r < height; r++) {
        for (int cw = 0; cw < cWidth; cw++) {
            int color = c72[r * cWidth + cw];
            uncompress[r * width + (cw * 2)] = color;
            if (cw < cWidth - 1) {
                uncompress[r * width + (cw * 2 + 1)] = color;
            }
        }
    }

    free(c72);
}

+(void)mergeSimulationCompressWithUncompress:(uint32_t*)pixels uncompress:(uint32_t *)uncompress width:(int)width height:(int)height {
    
    // 检查宽度和高度的有效性
    if (width <= 0 || height <= 0) return;
    
    // 向上取整计算压缩后的宽度
    int cWidth = (width + 1) / 2;
    uint32_t *c72 = (uint32_t *)malloc(cWidth * height * sizeof(uint32_t));
    memset(c72, 0, cWidth * height * sizeof(uint32_t));

    for (int r = 0; r < height; r++) {
        for (int cw = 0; cw < cWidth; cw++) {
            int bt_0 = pixels[r * width + (cw * 2)];
            int bt_1 = (cw * 2 + 1 < width) ? pixels[r * width + (cw * 2 + 1)] : 255;
            
            // 压缩
            int compressedValue = (bt_0 == 255 || bt_1 == 255) ? 255 : 0;
            c72[r * cWidth + cw] = compressedValue;

            // 解压
            uncompress[r * width + (cw * 2)] = compressedValue;
            if (cw < cWidth - 1) {
                uncompress[r * width + (cw * 2 + 1)] = compressedValue;
            }
        }
    }

    free(c72);
}


@end
