//
//  LogoDataFactory.m
//  Inksi
//
//  Created by rbq on 2024/6/21.
//

#import "LogoDataFactory.h"
#import "RBQLog.h"
#import "OpenCVUtils.h"
#import "MxImageUtils.h"
#import "MxFileManager.h"

@implementation LogoDataFactory

+(void)logoImageToData:(LogoImage *)logoImage threshold:(int)threshold onStart:(void (^)(void))onStart onComplete:(void (^)(LogoData *logoData))onComplete error:(void (^)(void))onError {
    
    __weak typeof(self) weakSelf = self;
    if (!logoImage) {
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
        
        LogoData *logoData = [weakSelf logoImageToData:logoImage threshold:threshold];
        if (!logoData) {
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if(onError){
                    onError();
                }
            });
            return;
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onComplete){
                onComplete(logoData);
            }
        });
        
    });
}

+ (LogoData *)logoImageToData:(LogoImage *)logoImage threshold:(int)threshold {
    
    if (!logoImage||!logoImage.imagePath) {
        return nil;
    }
    
    UIImage *image = [MxFileManager imageFromFilePath:logoImage.imagePath];
    
    if (!image) {
        return nil;
    }
    
    int width = image.size.width;
    int height = image.size.height;
    
    RBQLog3(@" ***** 取图 bitmap width:%d; height:%d",width,height);
    
    if (width != 2000 || height != 552){
        image = [self processImage:image];
        
        width = image.size.width;
        height = image.size.height;
    }
    
    //像素将画在这个数组
    uint32_t *pixels = (uint32_t *)malloc(width *height *sizeof(uint32_t));
    //清空像素数组
    memset(pixels, 0, width*height*sizeof(uint32_t));
    
    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    
    CGContextRef context =CGBitmapContextCreate(pixels, width, height, 8, width*sizeof(uint32_t), colorSpace, kCGBitmapByteOrder32Little | kCGImageAlphaPremultipliedLast);
    CGContextDrawImage(context, CGRectMake(0, 0, width, height), [image CGImage]);
    CGColorSpaceRelease(colorSpace);
    
    //像素将画在这个数组
    uint32_t *gray = (uint32_t *)malloc(width *height *sizeof(uint32_t));
    //清空像素数组
    memset(gray, 0, width*height*sizeof(uint32_t));
    
    [MxImageUtils bitmapToGray:pixels gray:gray width:width height:height];
    
    [MxImageUtils formatGrayToFloydDithering:gray width:width height:height threshold:threshold];
    
    [MxImageUtils grayToBinary:gray binary:pixels width:width height:height threshold:threshold];
    
    free(gray);
    
    NSData *data72 = [MxImageUtils formatBinary69ToData72ByCol:pixels width:width height:height];
    
    free(pixels);
    
    NSString *dataPath = [MxFileManager saveDataToDataCacheFile:data72];
    
    NSString *imagePath = [MxImageUtils imageSimulationWithSave:image threshold:threshold clearBackground:NO dithering:YES compress:NO topBeyondDistance:0 bottomBeyondDistance:0 isZoomTo552:YES initialErrors:NULL lastRowErrors:NULL];
    
    LogoData *logoData = [[LogoData alloc] initLogoData:dataPath dataLength:data72.length imagePath:imagePath];
    
    return logoData;
}


+(void)mergeLogoImageToData:(LogoImage *)logoImage threshold:(int)threshold onStart:(void (^)(void))onStart onComplete:(void (^)(LogoData *logoData))onComplete error:(void (^)(void))onError {
    
    __weak typeof(self) weakSelf = self;
    if (!logoImage) {
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
        
        LogoData *logoData = [weakSelf mergeLogoImageToData:logoImage threshold:threshold];
        if (!logoData) {
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if(onError){
                    onError();
                }
            });
            return;
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            if(onComplete){
                onComplete(logoData);
            }
        });
        
    });
}

+ (LogoData *)mergeLogoImageToData:(LogoImage *)logoImage threshold:(int)threshold {
    
    if (!logoImage||!logoImage.imagePath) {
        return nil;
    }
    
    UIImage *image = [MxFileManager imageFromFilePath:logoImage.imagePath];
    
    if (!image) {
        return nil;
    }
    
    int width = image.size.width;
    int height = image.size.height;
    
    RBQLog3(@" ***** 取图 bitmap width:%d; height:%d",width,height);
    
    if (width != 2000 || height != 552){
        image = [self processImage:image];
        
        width = image.size.width;
        height = image.size.height;
    }
    
    //像素将画在这个数组
    uint32_t *pixels = (uint32_t *)malloc(width *height *sizeof(uint32_t));
    //清空像素数组
    memset(pixels, 0, width*height*sizeof(uint32_t));
    
    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    
    CGContextRef context =CGBitmapContextCreate(pixels, width, height, 8, width*sizeof(uint32_t), colorSpace, kCGBitmapByteOrder32Little | kCGImageAlphaPremultipliedLast);
    CGContextDrawImage(context, CGRectMake(0, 0, width, height), [image CGImage]);
    CGColorSpaceRelease(colorSpace);
    
    uint32_t *binary = (uint32_t *)malloc(width * height * sizeof(uint32_t));
    //清空像素数组
    memset(binary, 0, width * height * sizeof(uint32_t));
    
    [MxImageUtils mergeBitmapToGrayFloydDitheringBinary:pixels binary:binary width:width height:height threshold:threshold dithering:YES compress:NO initialErrors:NULL lastRowErrors:NULL];
    
    free(pixels);
    
    NSData *data72 = [MxImageUtils formatBinary69ToData72ByCol:binary width:width height:height];
    
    NSString *dataPath = [MxFileManager saveDataToDataCacheFile:data72];
    
    NSString *imagePath = [MxImageUtils mergeImageSimulationWithSave:image threshold:threshold clearBackground:NO dithering:YES compress:NO topBeyondDistance:0 bottomBeyondDistance:0 isZoomTo552:YES initialErrors:NULL lastRowErrors:NULL];
    
    LogoData *logoData = [[LogoData alloc] initLogoData:dataPath dataLength:data72.length imagePath:imagePath];
    
    return logoData;
}



+ (UIImage *)processImage:(UIImage *)inputImage {
    
    int targetWidth = 2000;
    int targetHeight = 552;
    
    // 创建一个目标尺寸的白色背景
    UIGraphicsBeginImageContextWithOptions(CGSizeMake(targetWidth, targetHeight), YES, 0.0);
    CGContextRef context = UIGraphicsGetCurrentContext();
    CGContextSetFillColorWithColor(context, [UIColor whiteColor].CGColor);
    CGContextFillRect(context, CGRectMake(0, 0, targetWidth, targetHeight));
    
    int inputWidth = inputImage.size.width;
    int inputHeight = inputImage.size.height;
    
    float scale;
    int scaledWidth;
    int scaledHeight;
    UIImage *scaledImage;
    
    if (inputWidth <= targetWidth && inputHeight <= targetHeight) {
        // 图片比目标尺寸小，居中显示
        scaledImage = inputImage;
        scaledWidth = inputWidth;
        scaledHeight = inputHeight;
    } else {
        // 图片比目标尺寸大，进行缩放
        float widthRatio = (float)targetWidth / inputWidth;
        float heightRatio = (float)targetHeight / inputHeight;
        scale = MIN(widthRatio, heightRatio); // 保持纵横比缩放
        scaledWidth = round(inputWidth * scale);
        scaledHeight = round(inputHeight * scale);
        
        // 创建缩放后的图片
        UIGraphicsBeginImageContextWithOptions(CGSizeMake(scaledWidth, scaledHeight), NO, 0.0);
        [inputImage drawInRect:CGRectMake(0, 0, scaledWidth, scaledHeight)];
        scaledImage = UIGraphicsGetImageFromCurrentImageContext();
        UIGraphicsEndImageContext();
    }
    
    // 计算居中的位置
    int left = (targetWidth - scaledWidth) / 2;
    int top = (targetHeight - scaledHeight) / 2;
    
    // 将缩放后的图片绘制到白色背景的中心位置
    [scaledImage drawInRect:CGRectMake(left, top, scaledWidth, scaledHeight)];
    
    UIImage *outputImage = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    
    return outputImage;
}

@end
