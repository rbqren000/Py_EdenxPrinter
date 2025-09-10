//
//  MultiRowImageDataFactory.m
//  BelonPrinter
//
//  Created by rbq on 2021/7/5.
//  Copyright © 2021 rbq. All rights reserved.
//

#import "MultiRowDataFactory.h"
#import "MxFileManager.h"
#import "UIImage+Image.h"
#import "MxImageUtils.h"
#import "OpenCVUtils.h"
#import "Compress.h"

#define DataSuffix @".data"

@implementation MultiRowDataFactory

+(void)bitmap2MultiRowData:(MultiRowImage *)multiRowImage threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress flipHorizontally:(BOOL)flipHorizontally isSimulation:(BOOL)isSimulation thumbToSimulation:(BOOL)thumbToSimulation onStart:(void (^)(void))onStart onComplete:(void (^)(MultiRowData *multiRowData))onComplete error:(void (^)(void))onError {
    
    __weak typeof(self) weakSelf = self;
    if (!multiRowImage) {
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
        
        MultiRowData *multiRowData = [weakSelf bitmap2MultiRowData:multiRowImage threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress flipHorizontally:flipHorizontally isSimulation:isSimulation thumbToSimulation:thumbToSimulation];
        if (!multiRowData) {
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if(onError){
                    onError();
                }
            });
            return;
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onComplete){
                onComplete(multiRowData);
            }
        });
        
    });
}

+(MultiRowData *)bitmap2MultiRowData:(MultiRowImage *)multiRowImage threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress flipHorizontally:(BOOL)flipHorizontally isSimulation:(BOOL)isSimulation thumbToSimulation:(BOOL)thumbToSimulation{
    
    if(!multiRowImage){
        return nil;
    }
    RowLayoutDirection rowLayoutDirection = multiRowImage.rowLayoutDirection;
    BOOL isCroppedImageSet = multiRowImage.isCroppedImageSet;
    NSMutableArray<RowData *> *rowDataArr = [[NSMutableArray<RowData *> alloc] init];
    NSMutableArray<NSString *> *imagePaths = nil;
    NSMutableArray<RowImage *> *rowImageArr = multiRowImage.rowImages;
    RowImage *rowImage;
    UIImage *bitmap;
    CGFloat topBeyondDistance;
    CGFloat bottomBeyondDistance;
    RowData *rowData;
    NSString *imagePath;
    
    // 初始误差（如果有的话），否则为 NULL
    uint32_t *rowData_initialErrors = nil;
    // 用于保存最后一行的误差，确保传递有效指针
    uint32_t *rowData_lastRowErrors = nil;
    
    // 初始误差（如果有的话），否则为 NULL
    uint32_t *simulation_initialErrors = nil;
    // 用于保存最后一行的误差，确保传递有效指针
    uint32_t *simulation_lastRowErrors = nil;
    for (int sm = 0; sm < rowImageArr.count; sm++) {
        @autoreleasepool {
            rowImage = rowImageArr[sm];
            
            NSString *originPath = rowImage.imagePath;
            if(!originPath){
                return nil;
            }
            
            if(rowLayoutDirection == RowLayoutDirectionHorz){
                bitmap = [MxImageUtils rotatedImageWithGraphicsByRadians:[MxFileManager imageFromFilePath:originPath flipHorizontally:flipHorizontally] radians:M_PI_2];
            }else{
                bitmap = [MxFileManager imageFromFilePath:originPath flipHorizontally:flipHorizontally];
            }
            if(!bitmap){
                return nil;
            }
            topBeyondDistance = rowImage.topBeyondDistance;
            bottomBeyondDistance = rowImage.bottomBeyondDistance;
            
            CGFloat width = bitmap.size.width;
            CGFloat height = bitmap.size.height;
            
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
                newBitmap = [UIImage scaleToSize:bitmap size:CGSizeMake(temp_width, temp_height)];
                //这里valid_height不为552则进行缩放，那么缩放后valid_height的值则变为552了
                valid_height = 552;
                new_width = temp_width;
                new_height = temp_height;
                
            }else{
                
                newBitmap = bitmap;
                new_width = floor(width);
                new_height = height;
                new_topBeyondDistance = topBeyondDistance;
                new_bottomBeyondDistance = bottomBeyondDistance;
            }
            
            RBQLog3(@"【createRowData】222 {rowLayoutDirection:%ld;width:%f; height:%f; valid_height:%f; topBeyondDistance:%f; bottomBeyondDistance:%f; new_width:%f; new_height:%f; new_topBeyondDistance:%f; new_bottomBeyondDistance:%f;新->valid_height:%f}",rowLayoutDirection,width,height,(height - topBeyondDistance - bottomBeyondDistance),topBeyondDistance,bottomBeyondDistance,new_width,new_height,new_topBeyondDistance,new_bottomBeyondDistance,valid_height);
            
            if (clearBackground) {
                newBitmap = [OpenCVUtils lightClearBackground:newBitmap];
            }
            
            /*
            // 分配像素数组
            uint32_t *pixels = (uint32_t *)malloc(new_width * new_height * sizeof(uint32_t));

            CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
            CGContextRef context = CGBitmapContextCreate(pixels, new_width, new_height, 8, new_width * sizeof(uint32_t), colorSpace, kCGBitmapByteOrder32Little | kCGImageAlphaPremultipliedLast);
            CGContextDrawImage(context, CGRectMake(0, 0, new_width, new_height), [newBitmap CGImage]);
            CGColorSpaceRelease(colorSpace);
            CGContextRelease(context);

            // 计算起始偏移和拷贝的大小
            int startRow = new_topBeyondDistance;
            int endRow = new_height - new_bottomBeyondDistance;
            int numberOfRows = endRow - startRow;
            int srcOffset = startRow * new_width;
            int copySize = numberOfRows * new_width * sizeof(uint32_t);

            // 分配有效的像素数组，不需要初始化为0
            uint32_t *validPixels = (uint32_t *)malloc(new_width * valid_height * sizeof(uint32_t));

            // 直接拷贝内存块
            memcpy(validPixels, pixels + srcOffset, copySize);

            // 释放原始像素数组
            free(pixels);
            */
            
            // 分配像素数组
            uint32_t *pixels = (uint32_t *)malloc(new_width * new_height * sizeof(uint32_t));
            memset(pixels, 0, new_width * new_height * sizeof(uint32_t));

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

            if(isCroppedImageSet){
                if(rowData_initialErrors != nil){
                    free(rowData_initialErrors);
                    rowData_initialErrors = nil;
                }
                if (rowData_lastRowErrors != nil) {
                    rowData_initialErrors = rowData_lastRowErrors;
                }
                rowData_lastRowErrors = nil;
            }
            
            //像素将画在这个数组
            uint32_t *gray = (uint32_t *)malloc(new_width * valid_height * sizeof(uint32_t));
            //清空像素数组
            memset(gray, 0, new_width * valid_height * sizeof(uint32_t));
            
            [MxImageUtils bitmapToGray:validPixels gray:gray width:new_width height:valid_height];
            
            // 释放原始像素数组
            free(pixels);
            
            if (dithering) {
                [MxImageUtils formatGrayToFloydDithering:gray width:new_width height:valid_height threshold:threshold initialErrors:rowData_initialErrors lastRowErrors:&rowData_lastRowErrors];
            }
            
            uint32_t *binary = (uint32_t *)malloc(new_width * valid_height * sizeof(uint32_t));
            //清空像素数组
            memset(binary, 0, width * height * sizeof(uint32_t));
            
            [MxImageUtils grayToBinary:gray binary:binary width:new_width height:valid_height threshold:threshold];
            
            free(gray);
            
            NSData *data72 = [MxImageUtils formatBinary69ToData72ByCol:binary width:new_width height:valid_height];
            
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
            
            rowData = [[RowData alloc] init];
            rowData.rowDataPath = dataPath;
            rowData.dataLength = data72.length;
            rowData.compress = compress;
            
            
            [rowDataArr addObject:rowData];
            
            if(isCroppedImageSet){
                if(simulation_initialErrors != nil){
                    free(simulation_initialErrors);
                    simulation_initialErrors = nil;
                }
                if (simulation_lastRowErrors != nil) {
                    simulation_initialErrors = simulation_lastRowErrors;
                }
                simulation_lastRowErrors = nil;
            }
            
            if (isSimulation) {
                
                if (!imagePaths) {
                    imagePaths = [[NSMutableArray<NSString *> alloc] init];
                }
                imagePath = [MxImageUtils imageSimulationByBinarySave:binary width:new_width height:valid_height compress:compress rowLayoutDirection:rowLayoutDirection];
                [imagePaths addObject:imagePath];
            }
            
            free(binary);
            
            RBQLog3(@"完成第%d拼数据处理; 图片大小:%@; 图片路径imagePath:%@; dataLength:%ld",sm,NSStringFromCGSize(newBitmap.size),imagePath ? imagePath : @"Null",rowData.dataLength);
        }
    }
    
    if(rowData_initialErrors != nil){
        free(rowData_initialErrors);
        rowData_initialErrors = nil;
    }
    if(rowData_lastRowErrors != nil){
        free(rowData_lastRowErrors);
        rowData_lastRowErrors = nil;
    }
    
    if(simulation_initialErrors != nil){
        free(simulation_initialErrors);
        simulation_initialErrors = nil;
    }
    if(simulation_lastRowErrors != nil){
        free(simulation_lastRowErrors);
        simulation_lastRowErrors = nil;
    }
    
    NSString *thumbPath;
    if(thumbToSimulation && multiRowImage.thumbPath){
        
        UIImage *originThumb = [MxFileManager imageFromFilePath:multiRowImage.thumbPath];
        
        if(originThumb){
            thumbPath = [MxImageUtils imageSimulationWithSave:originThumb threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress topBeyondDistance:0 bottomBeyondDistance:0 isZoomTo552:NO initialErrors:NULL lastRowErrors:NULL];
        }
    }
    
    MultiRowData *multiRowData = [[MultiRowData alloc] initMultiRowData:rowDataArr imagePaths:imagePaths thumbPath:thumbPath compress:compress rowLayoutDirection:rowLayoutDirection];
    
    return multiRowData;
}



+(void)mergeBitmap2MultiRowData:(MultiRowImage *)multiRowImage threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress flipHorizontally:(BOOL)flipHorizontally isSimulation:(BOOL)isSimulation thumbToSimulation:(BOOL)thumbToSimulation onStart:(void (^)(void))onStart onComplete:(void (^)(MultiRowData *multiRowData))onComplete error:(void (^)(void))onError {
    
    __weak typeof(self) weakSelf = self;
    if (!multiRowImage) {
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
        
        MultiRowData *multiRowData = [weakSelf mergeBitmap2MultiRowData:multiRowImage threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress flipHorizontally:flipHorizontally isSimulation:isSimulation thumbToSimulation:thumbToSimulation];
        if (!multiRowData) {
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if(onError){
                    onError();
                }
            });
            return;
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onComplete){
                onComplete(multiRowData);
            }
        });
        
    });
}


+(MultiRowData *)mergeBitmap2MultiRowData:(MultiRowImage *)multiRowImage threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress flipHorizontally:(BOOL)flipHorizontally isSimulation:(BOOL)isSimulation thumbToSimulation:(BOOL)thumbToSimulation{
    
    if(!multiRowImage){
        return nil;
    }
    RowLayoutDirection rowLayoutDirection = multiRowImage.rowLayoutDirection;
    BOOL isCroppedImageSet = multiRowImage.isCroppedImageSet;
    NSMutableArray<RowData *> *rowDataArr = [[NSMutableArray<RowData *> alloc] init];
    NSMutableArray<NSString *> *imagePaths = nil;
    NSMutableArray<RowImage *> *rowImageArr = multiRowImage.rowImages;
    RowImage *rowImage;
    UIImage *bitmap;
    CGFloat topBeyondDistance;
    CGFloat bottomBeyondDistance;
    RowData *rowData;
    NSString *imagePath;
    
    // 初始误差（如果有的话），否则为 NULL
    uint32_t *rowData_initialErrors = nil;
    // 用于保存最后一行的误差，确保传递有效指针
    uint32_t *rowData_lastRowErrors = nil;
    
    // 初始误差（如果有的话），否则为 NULL
    uint32_t *simulation_initialErrors = nil;
    // 用于保存最后一行的误差，确保传递有效指针
    uint32_t *simulation_lastRowErrors = nil;
    for (int sm = 0; sm < rowImageArr.count; sm++) {
        @autoreleasepool {
            rowImage = rowImageArr[sm];
            
            NSString *originPath = rowImage.imagePath;
            if(!originPath){
                return nil;
            }
            
            if(rowLayoutDirection == RowLayoutDirectionHorz){
                bitmap = [MxImageUtils rotatedImageWithGraphicsByRadians:[MxFileManager imageFromFilePath:originPath flipHorizontally:flipHorizontally] radians:M_PI_2];
            }else{
                bitmap = [MxFileManager imageFromFilePath:originPath flipHorizontally:flipHorizontally];
            }
            if(!bitmap){
                return nil;
            }
            topBeyondDistance = rowImage.topBeyondDistance;
            bottomBeyondDistance = rowImage.bottomBeyondDistance;
            
            CGFloat width = bitmap.size.width;
            CGFloat height = bitmap.size.height;
            
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
                newBitmap = [UIImage scaleToSize:bitmap size:CGSizeMake(temp_width, temp_height)];
                //这里valid_height不为552则进行缩放，那么缩放后valid_height的值则变为552了
                valid_height = 552;
                new_width = temp_width;
                new_height = temp_height;
                
            }else{
                
                newBitmap = bitmap;
                new_width = floor(width);
                new_height = height;
                new_topBeyondDistance = topBeyondDistance;
                new_bottomBeyondDistance = bottomBeyondDistance;
            }
            
            RBQLog3(@"【createRowData】222 {rowLayoutDirection:%ld;width:%f; height:%f; valid_height:%f; topBeyondDistance:%f; bottomBeyondDistance:%f; new_width:%f; new_height:%f; new_topBeyondDistance:%f; new_bottomBeyondDistance:%f;新->valid_height:%f}",rowLayoutDirection,width,height,(height - topBeyondDistance - bottomBeyondDistance),topBeyondDistance,bottomBeyondDistance,new_width,new_height,new_topBeyondDistance,new_bottomBeyondDistance,valid_height);
            
            if (clearBackground) {
                newBitmap = [OpenCVUtils lightClearBackground:newBitmap];
            }
            
            /*
            // 分配像素数组
            uint32_t *pixels = (uint32_t *)malloc(new_width * new_height * sizeof(uint32_t));

            CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
            CGContextRef context = CGBitmapContextCreate(pixels, new_width, new_height, 8, new_width * sizeof(uint32_t), colorSpace, kCGBitmapByteOrder32Little | kCGImageAlphaPremultipliedLast);
            CGContextDrawImage(context, CGRectMake(0, 0, new_width, new_height), [newBitmap CGImage]);
            CGColorSpaceRelease(colorSpace);
            CGContextRelease(context);

            // 计算起始偏移和拷贝的大小
            int startRow = new_topBeyondDistance;
            int endRow = new_height - new_bottomBeyondDistance;
            int numberOfRows = endRow - startRow;
            int srcOffset = startRow * new_width;
            int copySize = numberOfRows * new_width * sizeof(uint32_t);

            // 分配有效的像素数组，不需要初始化为0
            uint32_t *validPixels = (uint32_t *)malloc(new_width * valid_height * sizeof(uint32_t));

            // 直接拷贝内存块
            memcpy(validPixels, pixels + srcOffset, copySize);

            // 释放原始像素数组
            free(pixels);
            */
            
            // 分配像素数组
            uint32_t *pixels = (uint32_t *)malloc(new_width * new_height * sizeof(uint32_t));
            memset(pixels, 0, new_width * new_height * sizeof(uint32_t));

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

            if(isCroppedImageSet){
                if(rowData_initialErrors != nil){
                    free(rowData_initialErrors);
                    rowData_initialErrors = nil;
                }
                if (rowData_lastRowErrors != nil) {
                    rowData_initialErrors = rowData_lastRowErrors;
                }
                rowData_lastRowErrors = nil;
            }
            
            uint32_t *binary = (uint32_t *)malloc(new_width * valid_height * sizeof(uint32_t));
            memset(binary, 0, new_width * valid_height * sizeof(uint32_t));
            
            [MxImageUtils mergeBitmapToGrayFloydDitheringBinary:validPixels binary:binary width:new_width height:valid_height threshold:threshold dithering:dithering compress:compress initialErrors:rowData_initialErrors lastRowErrors:&rowData_lastRowErrors];
            
            // 释放原始像素数组
            free(pixels);
            
            // 将二值图像数据转换为所需格式
            NSData *data72 = [MxImageUtils formatBinary69ToData72ByCol:binary width:new_width height:valid_height];
            
            // 如果需要压缩，则压缩数据
            if (compress) {
                data72 = [Compress compressRowData:data72];
            }
            
            // 将数据保存到缓存文件中
            NSString *dataPath = [MxFileManager saveDataToDataCacheFile:data72];
            
            // 创建 RowData 对象并返回
            rowData = [[RowData alloc] init];
            rowData.rowDataPath = dataPath;
            rowData.dataLength = data72.length;
            rowData.compress = compress;
            
            
            [rowDataArr addObject:rowData];
            
            if(isCroppedImageSet){
                if(simulation_initialErrors != nil){
                    free(simulation_initialErrors);
                    simulation_initialErrors = nil;
                }
                if (simulation_lastRowErrors != nil) {
                    simulation_initialErrors = simulation_lastRowErrors;
                }
                simulation_lastRowErrors = nil;
            }
            
            if (isSimulation) {
                
                if (!imagePaths) {
                    imagePaths = [[NSMutableArray<NSString *> alloc] init];
                }
                imagePath = [MxImageUtils imageSimulationByBinarySave:binary width:new_width height:valid_height compress:compress rowLayoutDirection:rowLayoutDirection];
                [imagePaths addObject:imagePath];
            }
            
            // 释放分配的内存
            free(binary);
            
            RBQLog3(@"完成第%d拼数据处理; 图片大小:%@; 图片路径imagePath:%@; dataLength:%ld",sm,NSStringFromCGSize(newBitmap.size),imagePath ? imagePath : @"Null",rowData.dataLength);
        }
    }
    
    if(rowData_initialErrors != nil){
        free(rowData_initialErrors);
        rowData_initialErrors = nil;
    }
    if(rowData_lastRowErrors != nil){
        free(rowData_lastRowErrors);
        rowData_lastRowErrors = nil;
    }
    
    if(simulation_initialErrors != nil){
        free(simulation_initialErrors);
        simulation_initialErrors = nil;
    }
    if(simulation_lastRowErrors != nil){
        free(simulation_lastRowErrors);
        simulation_lastRowErrors = nil;
    }
    
    NSString *thumbPath;
    if(thumbToSimulation && multiRowImage.thumbPath){
        
        UIImage *originThumb = [MxFileManager imageFromFilePath:multiRowImage.thumbPath];
        
        if(originThumb){
            thumbPath = [MxImageUtils mergeImageSimulationWithSave:originThumb threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress topBeyondDistance:0 bottomBeyondDistance:0 isZoomTo552:NO initialErrors:NULL lastRowErrors:NULL];
        }
    }
    
    MultiRowData *multiRowData = [[MultiRowData alloc] initMultiRowData:rowDataArr imagePaths:imagePaths thumbPath:thumbPath compress:compress rowLayoutDirection:rowLayoutDirection];
    
    return multiRowData;
}


+(void)betterMergeBitmap2MultiRowData:(MultiRowImage *)multiRowImage threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress flipHorizontally:(BOOL)flipHorizontally isSimulation:(BOOL)isSimulation thumbToSimulation:(BOOL)thumbToSimulation onStart:(void (^)(void))onStart onComplete:(void (^)(MultiRowData *multiRowData))onComplete error:(void (^)(void))onError {
    
    __weak typeof(self) weakSelf = self;
    if (!multiRowImage) {
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
        
        MultiRowData *multiRowData = [weakSelf betterMergeBitmap2MultiRowData:multiRowImage threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress flipHorizontally:flipHorizontally isSimulation:isSimulation thumbToSimulation:thumbToSimulation];
        if (!multiRowData) {
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if(onError){
                    onError();
                }
            });
            return;
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onComplete){
                onComplete(multiRowData);
            }
        });
        
    });
}


+(MultiRowData *)betterMergeBitmap2MultiRowData:(MultiRowImage *)multiRowImage threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress flipHorizontally:(BOOL)flipHorizontally isSimulation:(BOOL)isSimulation thumbToSimulation:(BOOL)thumbToSimulation {
    
    if(!multiRowImage){
        return nil;
    }
    RowLayoutDirection rowLayoutDirection = multiRowImage.rowLayoutDirection;
    BOOL isCroppedImageSet = multiRowImage.isCroppedImageSet;
    NSMutableArray<RowData *> *rowDataArr = [[NSMutableArray<RowData *> alloc] init];
    NSMutableArray<NSString *> *imagePaths = nil;
    NSMutableArray<RowImage *> *rowImageArr = multiRowImage.rowImages;
    RowImage *rowImage;
    UIImage *bitmap;
    CGFloat topBeyondDistance;
    CGFloat bottomBeyondDistance;
    RowData *rowData;
    NSString *imagePath;
    
    // 初始误差（如果有的话），否则为 NULL
    uint32_t *rowData_initialErrors = nil;
    // 用于保存最后一行的误差，确保传递有效指针
    uint32_t *rowData_lastRowErrors = nil;
    
    // 初始误差（如果有的话），否则为 NULL
    uint32_t *simulation_initialErrors = nil;
    // 用于保存最后一行的误差，确保传递有效指针
    uint32_t *simulation_lastRowErrors = nil;
    for (int sm = 0; sm < rowImageArr.count; sm++) {
        @autoreleasepool {
            rowImage = rowImageArr[sm];
            
            NSString *originPath = rowImage.imagePath;
            if(!originPath){
                return nil;
            }
            
            if(rowLayoutDirection == RowLayoutDirectionHorz){
                bitmap = [MxImageUtils rotatedImageWithGraphicsByRadians:[MxFileManager imageFromFilePath:originPath flipHorizontally:flipHorizontally] radians:M_PI_2];
            }else{
                bitmap = [MxFileManager imageFromFilePath:originPath flipHorizontally:flipHorizontally];
            }
            if(!bitmap){
                return nil;
            }
            topBeyondDistance = rowImage.topBeyondDistance;
            bottomBeyondDistance = rowImage.bottomBeyondDistance;
            
            CGFloat width = bitmap.size.width;
            CGFloat height = bitmap.size.height;
            
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
                newBitmap = [UIImage scaleToSize:bitmap size:CGSizeMake(temp_width, temp_height)];
                //这里valid_height不为552则进行缩放，那么缩放后valid_height的值则变为552了
                valid_height = 552;
                new_width = temp_width;
                new_height = temp_height;
                
            }else{
                
                newBitmap = bitmap;
                new_width = floor(width);
                new_height = height;
                new_topBeyondDistance = topBeyondDistance;
                new_bottomBeyondDistance = bottomBeyondDistance;
            }
            
            RBQLog3(@"【createRowData】222 {rowLayoutDirection:%ld;width:%f; height:%f; valid_height:%f; topBeyondDistance:%f; bottomBeyondDistance:%f; new_width:%f; new_height:%f; new_topBeyondDistance:%f; new_bottomBeyondDistance:%f;新->valid_height:%f}",rowLayoutDirection,width,height,(height - topBeyondDistance - bottomBeyondDistance),topBeyondDistance,bottomBeyondDistance,new_width,new_height,new_topBeyondDistance,new_bottomBeyondDistance,valid_height);
            
            if (clearBackground) {
                newBitmap = [OpenCVUtils lightClearBackground:newBitmap];
            }
            
            // 分配像素数组
            uint32_t *pixels = (uint32_t *)malloc(new_width * new_height * sizeof(uint32_t));
            memset(pixels, 0, new_width * new_height * sizeof(uint32_t));

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

            if(isCroppedImageSet){
                if(rowData_initialErrors != nil){
                    free(rowData_initialErrors);
                    rowData_initialErrors = nil;
                }
                if (rowData_lastRowErrors != nil) {
                    rowData_initialErrors = rowData_lastRowErrors;
                }
                rowData_lastRowErrors = nil;
            }
            
            uint32_t *binary = (uint32_t *)malloc(new_width * valid_height * sizeof(uint32_t));
            memset(binary, 0, new_width * valid_height * sizeof(uint32_t));
            
            uint8_t *d72 = (uint8_t *)malloc(new_width * 72 * sizeof(uint8_t));
            memset(d72, 0, new_width * 72 * sizeof(uint8_t));
            
            [MxImageUtils betterMergeBitmapToData72:validPixels binary:binary d72:d72 width:new_width height:valid_height threshold:threshold dithering:dithering compress:compress initialErrors:rowData_initialErrors lastRowErrors:&rowData_lastRowErrors];
            
            // 释放原始像素数组
            free(pixels);
            
            NSData *data72;
            
            // 如果需要压缩，则压缩数据
            if (compress) {
                data72 = [Compress compressRowData:d72 d72Len:new_width * 72];
            }else{
                data72 = [NSData dataWithBytes:d72 length:new_width * 72];
            }
            
            free(d72);
            
            // 将数据保存到缓存文件中
            NSString *dataPath = [MxFileManager saveDataToDataCacheFile:data72];
            
            // 创建 RowData 对象并返回
            rowData = [[RowData alloc] init];
            rowData.rowDataPath = dataPath;
            rowData.dataLength = data72.length;
            rowData.compress = compress;
            
            [rowDataArr addObject:rowData];
            
            if(isCroppedImageSet){
                if(simulation_initialErrors != nil){
                    free(simulation_initialErrors);
                    simulation_initialErrors = nil;
                }
                if (simulation_lastRowErrors != nil) {
                    simulation_initialErrors = simulation_lastRowErrors;
                }
                simulation_lastRowErrors = nil;
            }
            
            if (isSimulation) {
                
                if (!imagePaths) {
                    imagePaths = [[NSMutableArray<NSString *> alloc] init];
                }
                imagePath = [MxImageUtils imageSimulationByBinarySave:binary width:new_width height:valid_height compress:compress rowLayoutDirection:rowLayoutDirection];
                [imagePaths addObject:imagePath];
            }
            
            RBQLog3(@"完成第%d拼数据处理; 图片大小:%@; 图片路径imagePath:%@; dataLength:%ld",sm,NSStringFromCGSize(newBitmap.size),imagePath ? imagePath : @"Null",rowData.dataLength);
            // 释放分配的内存
            free(binary);
            
        }
    }
    
    if(rowData_initialErrors != nil){
        free(rowData_initialErrors);
        rowData_initialErrors = nil;
    }
    if(rowData_lastRowErrors != nil){
        free(rowData_lastRowErrors);
        rowData_lastRowErrors = nil;
    }
    
    if(simulation_initialErrors != nil){
        free(simulation_initialErrors);
        simulation_initialErrors = nil;
    }
    if(simulation_lastRowErrors != nil){
        free(simulation_lastRowErrors);
        simulation_lastRowErrors = nil;
    }
    
    NSString *thumbPath;
    if(thumbToSimulation && multiRowImage.thumbPath){
        
        UIImage *originThumb = [MxFileManager imageFromFilePath:multiRowImage.thumbPath];
        
        if(originThumb){
            thumbPath = [MxImageUtils mergeImageSimulationWithSave:originThumb threshold:threshold clearBackground:clearBackground dithering:dithering compress:compress topBeyondDistance:0 bottomBeyondDistance:0 isZoomTo552:NO initialErrors:NULL lastRowErrors:NULL];
        }
    }
    
    MultiRowData *multiRowData = [[MultiRowData alloc] initMultiRowData:rowDataArr imagePaths:imagePaths thumbPath:thumbPath compress:compress rowLayoutDirection:rowLayoutDirection];
    
    return multiRowData;
}

@end
