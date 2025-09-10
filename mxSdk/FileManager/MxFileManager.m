//
//  RBQFileManager.m
//  BelonPrinter
//
//  Created by rbq on 2020/9/23.
//  Copyright © 2020 rbq. All rights reserved.
//

#import "MxFileManager.h"
#import "RBQLog.h"
#import "NSString+String.h"
#import "UIImage+Rotate.h"
#import "UIImage+Image.h"
#import "MXCode.h"
#import "DocsUtils.h"
#import "FontUtils.h"
#import "FilesUtils.h"
#import "UIFont+FontLoader.h"
#import <SSZipArchive/SSZipArchive.h>
#import <ImageIO/ImageIO.h>
#import "RBQFileManager.h"

#define imageCacheFile @".imageCacheFile"
#define imageSqliteFile @".imageSqliteFile"
#define JsonCacheFile @".JsonCacheFile"
#define dataCacheFile @".dataCacheFile"
#define docsCacheFile @".docsCacheFile"
#define docsSavedFile @".docsSavedFile"
//所有模版将要保存的总的路径位置 它下边还有一个文件夹，每个模版一个文件夹
#define mxCacheFiles @".mxCacheFiles"
//用来保存用户字体的位置
#define fontSavedFiles @".fontSavedFiles"
//模版保存的文件名称
#define mx_main_json_name @"mx_main_json.txt"

@implementation MxFileManager

+(NSString *)baseImageCacheFilePath {
    NSFileManager *fileManager = [NSFileManager defaultManager];
    //把图片存储在沙盒中，首先获取沙盒路径
    NSArray *paths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
    NSString *documentsDirectory=[paths objectAtIndex:0];//Documents目录
    //在Documents下面创建一个Image的文件夹的路径
    NSString *basePath=[NSString stringWithFormat:@"%@/%@",documentsDirectory,imageCacheFile];
    
    //没有这个文件夹的话就创建这个文件夹
    if(![fileManager fileExistsAtPath:basePath]){
        
        BOOL success = [fileManager createDirectoryAtPath:basePath withIntermediateDirectories:YES attributes:nil error:nil];
        RBQLog3(@"已创建%@ 文件夹",imageCacheFile);
        if(success){
            return basePath;
        }
        return nil;
    }
    return basePath;
}

/**
 *图片存储到本地Document目录下，ImageName是图片的唯一标识符
 */
+(NSString *)saveImageToCache:(UIImage *)image{
    
    NSString *basePath = [self baseImageCacheFilePath];
    if (!basePath||!image) {
        return nil;
    }
    
    RBQLog3(@" 【saveImageToCache】 width:%f; height:%f; scale:%f; imageOrientation:%ld",image.size.width,image.size.height,image.scale,image.imageOrientation);
    
    image = [image fixOrientationUpWithScale];
    
    NSData *imageData = UIImagePNGRepresentation(image);
    
    NSString *baseimageName = [self create42StringByLetterAndNumber];
    NSString *imageName;
    if (image.scale>1) {
         imageName = [NSString stringWithFormat:@"%@@x%d%@",baseimageName,(int)image.scale,@".png"];
    }else{
        imageName = [NSString stringWithFormat:@"%@%@",baseimageName,@".png"];
    }
    //把数据以.png的形式存储在沙盒中，路径为可变路径
    NSString *filePath = [NSString stringWithFormat:@"%@/%@",basePath,imageName];
    /**如果已存在该文件，则删除*/
    [self deleteFileWithPath:filePath];
    
    BOOL isSaved = [imageData writeToFile:filePath atomically:YES];
    if (isSaved) {
        RBQLog3(@"存储成功");
        return filePath;
    }else{
        RBQLog3(@"存储失败");
    }
    return nil;
}

+(void)asynSaveImageToCache:(UIImage *)image completion:(void (^)(NSString *filePath))completionBlock
                      erroe:(void (^)(NSError *error))erroeBlock{
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSString *filePath = [weakSelf saveImageToCache:image];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(filePath){
                
                if(completionBlock){
                    completionBlock(filePath);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"SaveErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"保存失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}

#pragma mark 根据路径获取本地图片
+(UIImage *)imageFromFilePath:(NSString *)filePath{
    
    NSFileManager *fileManager = [NSFileManager defaultManager];
    @autoreleasepool {
        UIImage *image;
        if ([fileManager fileExistsAtPath:filePath]) {
            NSError *error;
            NSData *imageData = [NSData dataWithContentsOfFile:filePath options:0 error:&error];
            if (error) {
                NSLog(@"Error loading image data: %@", error);
                return nil;
            }
//            NSNumber *fileSize = [RBQFileManager sizeOfFileAtPath:filePath error:&error];
//            RBQLog3(@"imageData:%fMB;fileSize:%@",imageData.length/1024.0f/1024.0f,fileSize);
            int scale = [self imageScaleAtPath:filePath];
            image = [UIImage imageWithData:imageData scale:scale];
            image = [image fixOrientationUpWithScale];
        }
        return image;
    }
}

+(void)asynImageFromFilePath:(NSString *)filePath completion:(void (^)(UIImage *image))completionBlock erroe:(void (^)(NSError *error))erroeBlock{
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        UIImage *image = [weakSelf imageFromFilePath:filePath];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(image){
                
                if(completionBlock){
                    completionBlock(image);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"GetErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"读取图片失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}

+(UIImage *)imageFromFilePath:(NSString *)filePath flipHorizontally:(BOOL)flipHorizontally{
    @autoreleasepool {
        UIImage *image = [self imageFromFilePath:filePath];
        if(!image){
            return nil;
        }
        if (flipHorizontally) {
            image = [image horizontalFlip];
        }
        RBQLog3(@" 【imageFromFilePath】 width:%f; height:%f; scale:%f; imageOrientation:%ld",image.size.width,image.size.height,image.scale,image.imageOrientation);
        return image;
    }
}


+(void)asynImageFromFilePath:(NSString *)filePath flipHorizontally:(BOOL)flipHorizontally completion:(void (^)(UIImage *image))completionBlock erroe:(void (^)(NSError *error))erroeBlock{
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        UIImage *image = [weakSelf imageFromFilePath:filePath flipHorizontally:flipHorizontally];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(image){
                
                if(completionBlock){
                    completionBlock(image);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"GetErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"读取图片失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}


/**
*第二个方法：获取本地图片
*/
+(NSData *)imageDataFromFilePath:(NSString *)filePath{

    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSData *imageData;
    //如果存在存储图片的文件，则根据路径取出图片
    if ([fileManager fileExistsAtPath:filePath]) {
        imageData = [NSData dataWithContentsOfFile:filePath];
    }
    return imageData;
}

+(void)asynImageDataFromFilePath:(NSString *)filePath completion:(void (^)(NSData *imageData))completionBlock erroe:(void (^)(NSError *error))erroeBlock{

    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSData *imageData = [weakSelf imageDataFromFilePath:filePath];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(imageData){
                
                if(completionBlock){
                    completionBlock(imageData);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"GetErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"读取图片失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}


+(int)imageScaleAtPath:(NSString *)filePath {
    NSString *scaleStr = [NSString selcteStringWithSelect:filePath Satrt:@"@x" selecteEnd:@"."];
    int scale = [scaleStr intValue];
    return scale < 1 ? 1 : scale;
}

+(NSString *)baseJsonCacheFilePath{
    NSFileManager *fileManage = [NSFileManager defaultManager];
    //把图片存储在沙盒中，首先获取沙盒路径
    NSArray *paths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
    NSString *documentsDirectory=[paths objectAtIndex:0];
    //Documents目录
    //在Documents下面创建一个Image的文件夹的路径
    NSString *basePath=[NSString stringWithFormat:@"%@/%@",documentsDirectory,JsonCacheFile];
   
    //没有这个文件夹的话就创建这个文件夹
    if(![fileManage fileExistsAtPath:basePath]){
        
        BOOL success = [fileManage createDirectoryAtPath:basePath withIntermediateDirectories:YES attributes:nil error:nil];
        RBQLog3(@"已创建%@ 文件夹",JsonCacheFile);
        if(success){
            return basePath;
        }
        return nil;
    }
    return basePath;
}

+(NSString *)saveJsonToJsonFile:(NSString *)json{
    //把图片存储在沙盒中，首先获取沙盒路径
    NSString *basePath = [self baseJsonCacheFilePath];
    if (!basePath||!json||json.length==0) {
        return nil;
    }
    NSString *baseFileName = [self create42StringByLetterAndNumber];
    NSString *fileName = [NSString stringWithFormat:@"%@%@",baseFileName,@".mx"];
    //把数据以.png的形式存储在沙盒中，路径为可变路径
    NSString *filePath = [NSString stringWithFormat:@"%@/%@",basePath,fileName];
    //        RBQLog3(@" --> 删除已存在的");
    [self deleteFileWithPath:filePath];
    NSError *error;
    BOOL isSuccess = [json writeToFile:filePath atomically:YES encoding:NSUTF8StringEncoding error:&error];

    /*读取文件*/
//        NSString *string = [NSString stringWithContentsOfFile:filePath encoding:NSUTF8StringEncoding error:&error];
    if (isSuccess) {
        RBQLog3(@"存储成功");
        return filePath;
    }
    RBQLog3(@"存储失败");
    return filePath;
}

+(void)asynSaveJsonToJsonFile:(NSString *)json completion:(void (^)(NSString *filePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock{
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSString *filePath = [weakSelf saveJsonToJsonFile:json];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(filePath){
                
                if(completionBlock){
                    completionBlock(filePath);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"SaveJsonErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"json保存失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}


+(NSString *)jsonFromJsonFile:(NSString *)filePath{
    
    if (filePath&&filePath.length>0) {
        
        NSFileManager *fileManage = [NSFileManager defaultManager];

        //没有这个文件夹的话就创建这个文件夹
        if([fileManage fileExistsAtPath:filePath]){
            
            NSError *error;
            NSString *json = [NSString stringWithContentsOfFile:filePath encoding:NSUTF8StringEncoding error:&error];
            if (error) {
                return nil;
            }
            return json;
        }
    }
    return nil;
    
}

+(void)asynJsonFromJsonFile:(NSString *)filePath completion:(void (^)(NSString *json))completionBlock erroe:(void (^)(NSError *error))erroeBlock{
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSString *json = [weakSelf jsonFromJsonFile:filePath];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(json){
                
                if(completionBlock){
                    completionBlock(json);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"SaveJsonErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"读取json失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}


+(NSString *)baseDataCacheFilePath {
    NSFileManager *fileManager = [NSFileManager defaultManager];
    //把图片存储在沙盒中，首先获取沙盒路径
    NSArray *paths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
    NSString *documentsDirectory=[paths objectAtIndex:0];//Documents目录
    //在Documents下面创建一个Image的文件夹的路径
    NSString *basePath=[NSString stringWithFormat:@"%@/%@",documentsDirectory,dataCacheFile];
    
    //没有这个文件夹的话就创建这个文件夹
    if(![fileManager fileExistsAtPath:basePath]){
        
        BOOL success = [fileManager createDirectoryAtPath:basePath withIntermediateDirectories:YES attributes:nil error:nil];
        RBQLog3(@"已创建%@ 文件夹",dataCacheFile);
        if(success){
            return basePath;
        }
        return nil;
    }
    return basePath;
}

+(NSString *)saveDataToDataCacheFile:(NSData *)data{
    //把图片存储在沙盒中，首先获取沙盒路径
    NSString *basePath = [self baseDataCacheFilePath];
    if (!basePath||!data) {
        return nil;
    }
    //把数据以.data的形式存储在沙盒中，路径为可变路径
    NSString *filePath = [NSString stringWithFormat:@"%@/%@%@", basePath, [self create42StringByLetterAndNumber], @".data"];
    
    [self deleteFileWithPath:filePath];
    
    BOOL isSaved = [data writeToFile:filePath atomically:YES];
    if (isSaved) {
        RBQLog3(@"存储成功");
        return filePath;
    }else{
        RBQLog3(@"存储失败");
        return nil;
    }
}

+(void)asynSaveDataToDataCacheFile:(NSData *)data completion:(void (^)(NSString *filePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock{
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSString *filePath = [weakSelf saveDataToDataCacheFile:data];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(filePath){
                
                if(completionBlock){
                    completionBlock(filePath);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"SaveDataErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"保存data失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}


+(NSData *)dataFromPath:(NSString *)filePath{
    
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSData *data;
    //如果存在存储图片的文件，则根据路径取出图片
    if ([fileManager fileExistsAtPath:filePath]) {
        data = [NSData dataWithContentsOfFile:filePath];
    }
    return data;
}

+(void)asynDataFromPath:(NSString *)filePath completion:(void (^)(NSData *data))completionBlock erroe:(void (^)(NSError *error))erroeBlock{
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSData *data = [weakSelf dataFromPath:filePath];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(data){
                
                if(completionBlock){
                    completionBlock(data);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"SaveDataErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"保存data失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}

+(NSString *)baseFontSavedFilePath{
    NSFileManager *fileManage = [NSFileManager defaultManager];
    //把图片存储在沙盒中，首先获取沙盒路径
    NSArray *paths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
    NSString *documentsDirectory=[paths objectAtIndex:0];
    //Documents目录
    //在Documents下面创建一个Image的文件夹的路径
    NSString *basePath=[NSString stringWithFormat:@"%@/%@",documentsDirectory,fontSavedFiles];
   
    //没有这个文件夹的话就创建这个文件夹
    if(![fileManage fileExistsAtPath:basePath]){
        
        BOOL success = [fileManage createDirectoryAtPath:basePath withIntermediateDirectories:YES attributes:nil error:nil];
        RBQLog3(@"已创建%@ 文件夹",docsSavedFile);
        if(success){
            return basePath;
        }
        return nil;
    }
    return basePath;
}

// 加载用户自定义字体
+ (NSMutableArray<CustomTypeface *> *)loadCustomTypefaceFromFontSavedFilePath{
    
    NSMutableArray<CustomTypeface *> *customTypefaces = [[NSMutableArray<CustomTypeface *> alloc] init];
    
    NSString *basePath = [self baseFontSavedFilePath];
    if (!basePath) {
        return customTypefaces;
    }
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSDirectoryEnumerator *enumerator = [fileManager enumeratorAtPath:basePath];
    for (NSString *fileName in enumerator) {
      // 拼接完整的文件路径
      NSString *filePath = [basePath stringByAppendingPathComponent:fileName];
        if([FontUtils isFontFileAtPath:filePath]){
            // 创建一个CustomTypeface对象并添加到数组中
            UIFont *font = [UIFont fontWithTTFFilePath:filePath size:16];
            if(!font){
                continue;
            }
            // 获取字体的属性和文件的属性
            NSError *error = nil;
            NSDictionary *fontAtt = [FontUtils getFontAttributesFromPath:filePath];
            NSDictionary *fileAtt = [FilesUtils getFileAttributesAtPath:filePath error:&error];
            if (error) {
                // 如果有错误，打印错误信息
                RBQLog3(@"获取文件属性失败：%@", error.localizedDescription);
                continue;
            }
            // 创建一个CustomTypeface对象并添加到数组中
            CustomTypeface *customTypeface = [UIFont createCustomTypefaceWithFilePath:font filePath:filePath fontAttributes:fontAtt fileAttributes:fileAtt];
            [customTypefaces addObject:customTypeface];
        }
    }
    return customTypefaces;
}

+(NSString *)baseDocsSavedFilePath{
    NSFileManager *fileManage = [NSFileManager defaultManager];
    //把图片存储在沙盒中，首先获取沙盒路径
    NSArray *paths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
    NSString *documentsDirectory=[paths objectAtIndex:0];
    //Documents目录
    //在Documents下面创建一个Image的文件夹的路径
    NSString *basePath=[NSString stringWithFormat:@"%@/%@",documentsDirectory,docsSavedFile];
   
    //没有这个文件夹的话就创建这个文件夹
    if(![fileManage fileExistsAtPath:basePath]){
        
        BOOL success = [fileManage createDirectoryAtPath:basePath withIntermediateDirectories:YES attributes:nil error:nil];
        RBQLog3(@"已创建%@ 文件夹",docsSavedFile);
        if(success){
            return basePath;
        }
        return nil;
    }
    return basePath;
}

+(NSMutableArray<Docs *> *)loadDocsFromDocsSavedFile{
    
    NSMutableArray<Docs *> *docsArr = [NSMutableArray array];
    
    NSString *basePath = [self baseDocsSavedFilePath];
    if (!basePath) {
        return docsArr;
    }
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSDirectoryEnumerator *enumerator = [fileManager enumeratorAtPath:basePath];
    for (NSString *fileName in enumerator) {
      // 拼接完整的文件路径
      NSString *filePath = [basePath stringByAppendingPathComponent:fileName];
        if([DocsUtils isWordOrPdfFileAtPath:filePath]){
            // 创建一个CustomTypeface对象并添加到数组中
            NSString *name = [DocsUtils fileNameWithPath:filePath];
            Docs *docs = [[Docs alloc] initDocs:name docsPath:filePath];
            [docsArr addObject:docs];
        }
    }
    return docsArr;
}

+(NSString *)baseDocsCacheFilePath{
    NSFileManager *fileManage = [NSFileManager defaultManager];
    //把图片存储在沙盒中，首先获取沙盒路径
    NSArray *paths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
    NSString *docsDirectory = [paths objectAtIndex:0];
    //Documents目录
    //在Documents下面创建一个Image的文件夹的路径
    NSString *basePath = [NSString stringWithFormat:@"%@/%@",docsDirectory,docsCacheFile];
   
    //没有这个文件夹的话就创建这个文件夹
    if(![fileManage fileExistsAtPath:basePath]){
        
        BOOL success = [fileManage createDirectoryAtPath:basePath withIntermediateDirectories:YES attributes:nil error:nil];
        RBQLog3(@"已创建%@ 文件夹",docsCacheFile);
        if(success){
            return basePath;
        }
        return nil;
    }
    return basePath;
}

+(NSString *)savePdfToDocsCacheFile:(NSMutableData *)pdfData{
    //把图片存储在沙盒中，首先获取沙盒路径
    NSString *basePath = [self baseDocsCacheFilePath];
    if (!basePath||!pdfData) {
        return nil;
    }
    //把数据以.data的形式存储在沙盒中，路径为可变路径
    NSString *baseFileName = [MxFileManager create42StringByLetterAndNumber];
    NSString *pdfFileName = [NSString stringWithFormat:@"%@%@",baseFileName,@".pdf"];
    //pdf文件存储路径
    NSString *filePath = [NSString stringWithFormat:@"%@/%@",basePath,pdfFileName];
    
    [self deleteFileWithPath:filePath];
    
    BOOL isSaved = [pdfData writeToFile:filePath atomically:YES];
    if (isSaved) {
        RBQLog3(@"存储成功");
        return filePath;
    }else{
        RBQLog3(@"存储失败");
        return nil;
    }
}

+(NSString *)asynSavePdfToDocsCacheFile:(NSMutableData *)pdfData{
    //把图片存储在沙盒中，首先获取沙盒路径
    NSString *basePath = [self baseDocsCacheFilePath];
    if (!basePath||!pdfData) {
        return nil;
    }
    //把数据以.data的形式存储在沙盒中，路径为可变路径
    NSString *baseFileName = [MxFileManager create42StringByLetterAndNumber];
    NSString *pdfFileName = [NSString stringWithFormat:@"%@%@",baseFileName,@".pdf"];
    //pdf文件存储路径
    NSString *filePath = [NSString stringWithFormat:@"%@/%@",basePath,pdfFileName];
    
    [self deleteFileWithPath:filePath];
    
    BOOL isSaved = [pdfData writeToFile:filePath atomically:YES];
    if (isSaved) {
        RBQLog3(@"存储成功");
        return filePath;
    }else{
        RBQLog3(@"存储失败");
        return nil;
    }
}


+(void)asynSavePdfToDocsCacheFile:(NSMutableData *)pdfData completion:(void (^)(NSString *filePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock{
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSString *filePath = [weakSelf savePdfToDocsCacheFile:pdfData];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(filePath){
                
                if(completionBlock){
                    completionBlock(filePath);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"SavePDFErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"保存PDF失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}

+(NSString *)savePdfToDocsCacheFile:(NSMutableData *)pdfData pdfFileName:(NSString *)pdfFileName{
    //把图片存储在沙盒中，首先获取沙盒路径
    NSString *basePath = [self baseDocsCacheFilePath];
    if (!basePath||!pdfData) {
        return nil;
    }
    //pdf文件存储路径
    NSString *filePath = [NSString stringWithFormat:@"%@/%@",basePath,pdfFileName];
    
    [self deleteFileWithPath:filePath];
    
    BOOL isSaved = [pdfData writeToFile:filePath atomically:YES];
    if (isSaved) {
        RBQLog3(@"存储成功");
        return filePath;
    }else{
        RBQLog3(@"存储失败");
        return nil;
    }
}

+(void)asynSavePdfToDocsCacheFile:(NSMutableData *)pdfData pdfFileName:(NSString *)pdfFileName completion:(void (^)(NSString *filePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock{
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSString *filePath = [weakSelf savePdfToDocsCacheFile:pdfData pdfFileName:pdfFileName];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(filePath){
                
                if(completionBlock){
                    completionBlock(filePath);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"SavePDFErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"保存PDF失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}


+(NSString *)saveImageToDocsFilePath:(UIImage *)image {
    //把图片存储在沙盒中，首先获取沙盒路径
    NSString *basePath = [self baseDocsCacheFilePath];
    if (!basePath||!image) {
        return nil;
    }
    image = [image fixOrientationUpWithScale];
    
    NSData *imageData = UIImagePNGRepresentation(image);
    
    NSString *baseimageName = [self create42StringByLetterAndNumber];
    NSString *imageName;
    if (image.scale>1) {
         imageName = [NSString stringWithFormat:@"%@@x%d%@",baseimageName,(int)image.scale,@".png"];
    }else{
        imageName = [NSString stringWithFormat:@"%@%@",baseimageName,@".png"];
    }
    //把数据以.png的形式存储在沙盒中，路径为可变路径
    NSString *filePath = [NSString stringWithFormat:@"%@/%@",basePath,imageName];
    /**如果已存在该文件，则删除*/
    [self deleteFileWithPath:filePath];
    
    BOOL isSaved = [imageData writeToFile:filePath atomically:YES];
    if (isSaved) {
        RBQLog3(@"存储成功");
        return filePath;
    }
    if (!isSaved) {
        RBQLog3(@"存储失败");
    }
    return nil;
}


+(void)saveImageToDocsFilePath:(UIImage *)image completion:(void (^)(NSString *filePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock{
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSString *filePath = [weakSelf saveImageToDocsFilePath:image];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(filePath){
                
                if(completionBlock){
                    completionBlock(filePath);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"SaveImageErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"保存图片失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}


+(NSString *)saveImageToDocsFilePath:(UIImage *)image imageName:(NSString *)baseimageName{
    //把图片存储在沙盒中，首先获取沙盒路径
    NSString *basePath = [self baseDocsCacheFilePath];
    if (!basePath||!image) {
        return nil;
    }
    image = [image fixOrientationUpWithScale];
    NSString *imageName;
    if (image.scale>1) {
         imageName = [NSString stringWithFormat:@"%@@x%d%@",baseimageName,(int)image.scale,@".png"];
    }else{
        imageName = [NSString stringWithFormat:@"%@%@",baseimageName,@".png"];
    }
    
    NSData *imageData = UIImagePNGRepresentation(image);
    
    //把数据以.png的形式存储在沙盒中，路径为可变路径
    NSString *filePath = [NSString stringWithFormat:@"%@/%@",basePath,imageName];
    /**如果已存在该文件，则删除*/
    [self deleteFileWithPath:filePath];
    
    BOOL isSaved = [imageData writeToFile:filePath atomically:YES];
    if (isSaved) {
        RBQLog3(@"存储成功");
        return filePath;
    }
    if (!isSaved) {
        RBQLog3(@"存储失败");
    }
    return nil;
}


+(void)asynSaveImageToDocsFilePath:(UIImage *)image imageName:(NSString *)baseimageName completion:(void (^)(NSString *filePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock{
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSString *filePath = [weakSelf saveImageToDocsFilePath:image imageName:baseimageName];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(filePath){
                
                if(completionBlock){
                    completionBlock(filePath);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"SaveImageErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"保存图片失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}


+(NSString *)baseMxCacheFilePath {
    NSFileManager *fileManager = [NSFileManager defaultManager];
    //把图片存储在沙盒中，首先获取沙盒路径
    NSArray *paths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
    NSString *documentsDirectory=[paths objectAtIndex:0];//Documents目录
    //在Documents下面创建一个Image的文件夹的路径
    NSString *basePath = [NSString stringWithFormat:@"%@/%@",documentsDirectory,mxCacheFiles];
    
    //没有这个文件夹的话就创建这个文件夹
    if(![fileManager fileExistsAtPath:basePath]){
        
        BOOL success = [fileManager createDirectoryAtPath:basePath withIntermediateDirectories:YES attributes:nil error:nil];
        RBQLog3(@"已创建%@ 文件夹",dataCacheFile);
        if(success){
            return basePath;
        }
        return nil;
    }
    return basePath;
}

+(NSString *)absoluteMxCacheFilePath:(NSString *)mxKey {
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSString *basePath = [self baseMxCacheFilePath];
    if (!basePath) {
        return nil;
    }
    NSString *mxCacheFilePath = [NSString stringWithFormat:@"%@/%@",basePath,mxKey];
    if (![fileManager fileExistsAtPath:mxCacheFilePath]) {
        return nil;
    }
    return mxCacheFilePath;
}

+(void)asynAbsoluteMxCacheFilePath:(NSString *)mxKey completion:(void (^)(NSString *mxCacheFilePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock{
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSString *mxCacheFilePath = [weakSelf absoluteMxCacheFilePath:mxKey];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(mxCacheFilePath){
                
                if(completionBlock){
                    completionBlock(mxCacheFilePath);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"CreateFileErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"创建文件夹失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}

/**根据mxkey创建要压缩的文件夹将要保存的zip的路径**/
+(NSString *)createZipAbsoluteMxCacheFilePath:(NSString *)mxKey {
    NSString *basePath = [self baseMxCacheFilePath];
    if (!basePath) {
        return nil;
    }
    NSString *mxCacheFilePath = [NSString stringWithFormat:@"%@/%@.zip",basePath,mxKey];
    return mxCacheFilePath;
}

+(void)asynCreateZipAbsoluteMxCacheFilePath:(NSString *)mxKey completion:(void (^)(NSString *mxCacheFilePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock{
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSString *mxCacheFilePath = [weakSelf createZipAbsoluteMxCacheFilePath:mxKey];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(mxCacheFilePath){
                
                if(completionBlock){
                    completionBlock(mxCacheFilePath);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"CreateFileErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"创建文件夹失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}

+(NSString *)createUnZipAbsoluteMxCacheFilePath:(NSString *)mxKey {
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSString *basePath = [self baseMxCacheFilePath];
    if (!basePath) {
        return nil;
    }
    NSString *mxCacheFilePath = [NSString stringWithFormat:@"%@/%@",basePath,mxKey];
    if([fileManager fileExistsAtPath:mxCacheFilePath]){
        [self deleteFileWithPath:mxCacheFilePath];
    }
    BOOL success = [fileManager createDirectoryAtPath:mxCacheFilePath withIntermediateDirectories:YES attributes:nil error:nil];
    RBQLog3(@"已创建%@ 文件夹",mxCacheFilePath);
    if(success){
        return mxCacheFilePath;
    }
    return nil;
}


+(void)asynCreateUnZipAbsoluteMxCacheFilePath:(NSString *)mxKey completion:(void (^)(NSString *mxCacheFilePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock {
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSString *mxCacheFilePath = [weakSelf createUnZipAbsoluteMxCacheFilePath:mxKey];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(mxCacheFilePath){
                
                if(completionBlock){
                    completionBlock(mxCacheFilePath);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"CreateFileErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"创建文件夹失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}


+(NSString *)mainJsonAbsoluteFilePath:(NSString *)mxKey {
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSString *basePath = [self baseMxCacheFilePath];
    if (!basePath) {
        return nil;
    }
    NSString *mxCacheFilePath = [NSString stringWithFormat:@"%@/%@",basePath,mxKey];
    if (![fileManager fileExistsAtPath:mxCacheFilePath]) {
        return nil;
    }
    NSString *filePath = [NSString stringWithFormat:@"%@/%@",mxCacheFilePath,mx_main_json_name];
    if (![fileManager fileExistsAtPath:filePath]) {
        return nil;
    }
    return filePath;
}

+(void)asynmainJsonAbsoluteFilePath:(NSString *)mxKey completion:(void (^)(NSString *filePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock {
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSString *filePath = [weakSelf mainJsonAbsoluteFilePath:mxKey];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(filePath){
                
                if(completionBlock){
                    completionBlock(filePath);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"CreateFileErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"创建文件夹失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}

+(NSString *)mainJsonInnerPathToAbsolutePath:(NSString *)mxKey fileName:(NSString *)fileName {
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSString *basePath = [self baseMxCacheFilePath];
    if (!basePath) {
        return nil;
    }
    NSString *mxCacheFilePath = [NSString stringWithFormat:@"%@/%@",basePath,mxKey];
    if (![fileManager fileExistsAtPath:mxCacheFilePath]) {
        return nil;
    }
    NSString *filePath = [NSString stringWithFormat:@"%@/%@",mxCacheFilePath,fileName];
    if (![fileManager fileExistsAtPath:filePath]) {
        return nil;
    }
    return filePath;
}

+(void)asynMainJsonInnerPathToAbsolutePath:(NSString *)mxKey fileName:(NSString *)fileName completion:(void (^)(NSString *filePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock {
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSString *filePath = [weakSelf mainJsonInnerPathToAbsolutePath:mxKey fileName:fileName];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(filePath){
                
                if(completionBlock){
                    completionBlock(filePath);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"CreateFileErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"创建文件夹失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}


+(NSString *)saveImageToMxCacheFile:(NSString *)mxKey image:(UIImage *)image{
    NSFileManager *fileManager = [NSFileManager defaultManager];
    //把图片存储在沙盒中，首先获取沙盒路径
    NSString *basePath = [self baseMxCacheFilePath];
    if (!basePath) {
        return nil;
    }
    //把数据以.data的形式存储在沙盒中，路径为可变路径
    NSString *mxCacheFilePath = [NSString stringWithFormat:@"%@/%@",basePath,mxKey];
    BOOL isSuccess = [fileManager createDirectoryAtPath:mxCacheFilePath withIntermediateDirectories:YES attributes:nil error:nil];
    if(!isSuccess){
        RBQLog3(@"创建模版缓存文件夹%@失败",mxCacheFilePath);
        return nil;
    }
    NSString *baseimageName = [self create42StringByLetterAndNumber];
    NSString *imageName;
    if (image.scale>1) {
         imageName = [NSString stringWithFormat:@"%@@x%d%@",baseimageName,(int)image.scale,@".png"];
    }else{
        imageName = [NSString stringWithFormat:@"%@%@",baseimageName,@".png"];
    }
    //把数据以.png的形式存储在沙盒中，路径为可变路径
    NSString *filePath = [NSString stringWithFormat:@"%@/%@",mxCacheFilePath,imageName];
    /**如果已存在该文件，则删除*/
    [self deleteFileWithPath:filePath];
    
    image = [image fixOrientationUpWithScale];
    NSData *imageData = UIImagePNGRepresentation(image);
    
    isSuccess = [imageData writeToFile:filePath atomically:YES];
    if (isSuccess) {
        RBQLog3(@"存储成功");
        return imageName;
    }
    RBQLog3(@"存储失败");
    return nil;
}


+(void)asynSaveImageToMxCacheFile:(NSString *)mxKey image:(UIImage *)image completion:(void (^)(NSString *imageName))completionBlock erroe:(void (^)(NSError *error))erroeBlock{
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSString *imageName = [weakSelf saveImageToMxCacheFile:mxKey image:image];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(imageName){
                
                if(completionBlock){
                    completionBlock(imageName);
                }
                
            }else{
                
                if(erroeBlock){
                    NSError *error = [NSError errorWithDomain:@"CreateFileErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"创建文件夹失败"}];
                    erroeBlock(error);
                }
            }
        });
    });
    
}


+(NSString *)savePDFToMxCacheFile:(NSString *)mxKey pdfFileName:(NSString *)pdfFileName pdfData:(NSMutableData *)pdfData {
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSString *basePath = [self baseMxCacheFilePath];
    if (!basePath) {
        return nil;
    }
    //把数据以.data的形式存储在沙盒中，路径为可变路径
    NSString *mxCacheFilePath = [NSString stringWithFormat:@"%@/%@",basePath,mxKey];
    BOOL isSuccess = [fileManager createDirectoryAtPath:mxCacheFilePath withIntermediateDirectories:YES attributes:nil error:nil];
    if(!isSuccess){
        RBQLog3(@"创建模版缓存文件夹%@失败",mxCacheFilePath);
        return nil;
    }
    
    NSString *filePath = [NSString stringWithFormat:@"%@/%@",mxCacheFilePath,pdfFileName];
    //        RBQLog3(@" --> 删除已存在的");
    [self deleteFileWithPath:filePath];
    
    isSuccess = [pdfData writeToFile:filePath atomically:YES];
    if (isSuccess) {
        RBQLog3(@"存储成功");
        return pdfFileName;
    }
    RBQLog3(@"存储失败");
    return nil;
}

+(NSString *)saveJsonToMxCacheFile:(NSString *)mxKey json:(NSString *)json {
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSString *basePath = [self baseMxCacheFilePath];
    if (!basePath) {
        return nil;
    }
    //把数据以.data的形式存储在沙盒中，路径为可变路径
    NSString *mxCacheFilePath = [NSString stringWithFormat:@"%@/%@",basePath,mxKey];
    BOOL isSuccess = [fileManager createDirectoryAtPath:mxCacheFilePath withIntermediateDirectories:YES attributes:nil error:nil];
    if(!isSuccess){
        RBQLog3(@"创建模版缓存文件夹%@失败",mxCacheFilePath);
        return nil;
    }
    
    //把数据以.png的形式存储在沙盒中，路径为可变路径
    NSString *filePath = [NSString stringWithFormat:@"%@/%@",mxCacheFilePath,mx_main_json_name];
    //        RBQLog3(@" --> 删除已存在的");
    [self deleteFileWithPath:filePath];
    NSError *error;
    isSuccess = [json writeToFile:filePath atomically:YES encoding:NSUTF8StringEncoding error:&error];
    if (isSuccess) {
        RBQLog3(@"存储成功");
        return filePath;
    }
    RBQLog3(@"存储失败");
    return nil;
}


+(NSString *)copyToMxCacheFile:(NSString *)mxKey filePath:(NSString *)filePath{
    NSFileManager *fileManager = [NSFileManager defaultManager];
    //把图片存储在沙盒中，首先获取沙盒路径
    NSString *basePath = [self baseMxCacheFilePath];
    if (!basePath) {
        return nil;
    }
    //把数据以.data的形式存储在沙盒中，路径为可变路径
    NSString *mxCacheFilePath = [NSString stringWithFormat:@"%@/%@",basePath,mxKey];
    BOOL isSuccess = [fileManager createDirectoryAtPath:mxCacheFilePath withIntermediateDirectories:YES attributes:nil error:nil];
    if(!isSuccess){
        RBQLog3(@"创建模版缓存文件夹%@失败",mxCacheFilePath);
        return nil;
    }
    NSString *fileName = filePath.lastPathComponent;
    NSString *mxFilePath = [NSString stringWithFormat:@"%@/%@",mxCacheFilePath,fileName];
    NSString *mxFileName = mxFilePath.lastPathComponent;
    isSuccess = [self copy:filePath to:mxFilePath isDeleteSrc:NO];
    if (isSuccess) {
        RBQLog3(@"存储成功:filePath:%@;fileName:%@;mxFilePath:%@;mxFileName:%@",filePath,fileName,mxFilePath,mxFileName);
        return mxFileName;
    }
    RBQLog3(@"存储失败");
    return nil;
}

+(NSString *)createJsonByMxStickerGroupTemplate:(StickerGroupTemplate *)stickerGroupTemplate version:(NSString *)version{
    
    NSDictionary *group = [stickerGroupTemplate mj_keyValues];
    // type 该属性，在version 3及以上的版本才具有该属性，主要用来区分保存的是文档还是普通的模版
    NSDictionary *data = @{@"version":version,@"type":@(TemplateTypeStickerGroup), @"data":group};
    // 序列化 JSON 数据
    NSError *error = nil;
    NSData *jsonData = [NSJSONSerialization dataWithJSONObject:data options:NSJSONWritingPrettyPrinted error:&error];
    if (error) {
        return nil;
    }
    NSString *jsonString = [[NSString alloc] initWithData:jsonData encoding:NSUTF8StringEncoding];
    return jsonString;
}

+(NSString *)createJsonByMxDocumentStickerGroupTemplate:(StickerGroupsTemplate *)documentStickerGroupTemplate version:(NSString *)version {
    
    NSDictionary *group = [documentStickerGroupTemplate mj_keyValues];
    // type 该属性，在version 3及以上的版本才具有该属性，主要用来区分保存的是文档还是普通的模版
    NSDictionary *data = @{@"version":version,@"type":@(TemplateTypeDocument), @"data":group};
    // 序列化 JSON 数据
    NSError *error = nil;
    NSData *jsonData = [NSJSONSerialization dataWithJSONObject:data options:NSJSONWritingPrettyPrinted error:&error];
    if (error) {
        return nil;
    }
    NSString *jsonString = [[NSString alloc] initWithData:jsonData encoding:NSUTF8StringEncoding];
    return jsonString;
}

+(void)readMxFileFormMxKey:(NSString *)mxKey onComplete:(void (^)(StickerGroupsTemplate *_Nullable documentStickerGroupTemplate,StickerGroupTemplate  * _Nullable stickerGroupTemplate,NSString *version))onComplete error:(void (^)(void))onError{
    
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSString *basePath = [self baseMxCacheFilePath];
    if (!basePath) {
        if(onError){
            onError();
        }
        return;
    }
    NSString *mxCacheFilePath = [NSString stringWithFormat:@"%@/%@",basePath,mxKey];
    if (![fileManager fileExistsAtPath:mxCacheFilePath]) {
        if(onError){
            onError();
        }
        return;
    }
    //遍历文件夹
    [self enumerateFilesInDirectory:mxCacheFilePath];
    
//    NSString *filePath = [NSString stringWithFormat:@"%@/%@",mxCacheFilePath,mx_main_json_name];
    //查找文件夹内的mx_main_json.txt文件
    NSString *filePath = [self findFileNamed:mx_main_json_name inDirectory:mxCacheFilePath];
    
    if (!filePath) {
        RBQLog3(@"【readMxFileFormMxKey】未查找到mx_main_json.txt文件 ~ filePath: %@", filePath);
        if(onError){
            onError();
        }
        return;
    }
    
    RBQLog3(@"【readMxFileFormMxKey】文件路径: %@", filePath);
    NSString *mainJsonDirectoryPath = [filePath stringByDeletingLastPathComponent];
    
    NSError *error;
    NSString *jsonString = [NSString stringWithContentsOfFile:filePath encoding:NSUTF8StringEncoding error:&error];
    if (error) {
        RBQLog3(@"【readMxFileFormMxKey】文件读取错误 ~ filePath: %@", filePath);
        if (onError) {
            onError();
        }
        return;
    }
    RBQLog3(@"【readMxFileFormMxKey】jsonString:%@",jsonString);
    NSData *jsonData = [jsonString dataUsingEncoding:NSUTF8StringEncoding];
    NSDictionary *jsonDict = [NSJSONSerialization JSONObjectWithData:jsonData options:NSJSONReadingMutableContainers error:&error];
    if (error) {
        if (onError) {
            onError();
        }
        return;
    }
    if(![jsonDict objectForKey:@"version"]){
        if (onError) {
            onError();
        }
        return;
    }
    NSString *version = jsonDict[@"version"];
    
    RBQLog3(@"当前模版的版本为:%@",version);
    
    NSArray<NSString *> *versionArr = [version componentsSeparatedByString:@"."];
    int version_0 = 1;
    if (versionArr.count>0) {
        version_0 = [versionArr.firstObject intValue];
    }
    //不包含type则
    if(![jsonDict objectForKey:@"type"]){
        if (onError) {
            onError();
        }
        return;
    }
    int type = [jsonDict[@"type"] intValue];
    if (type == TemplateTypeDocument) {
        //文档模式
        StickerGroupsTemplate *documentStickerGroupTemplate = [StickerGroupsTemplate mj_objectWithKeyValues:jsonDict[@"data"]];
        NSString *documentName = documentStickerGroupTemplate.documentName;
        if(documentName){
            NSString *documentPath = [NSString stringWithFormat:@"%@/%@",mainJsonDirectoryPath,documentName];
            RBQLog3(@"--->documentPath:%@",documentPath);
            documentStickerGroupTemplate.documentPath = documentPath;
        }
        NSMutableArray<StickerGroupTemplate *> *stickerGroupTemplates = documentStickerGroupTemplate.groups;
        if(stickerGroupTemplates){
            for (StickerGroupTemplate *stickerGroupTemplate in stickerGroupTemplates) {
                NSString *documentName = stickerGroupTemplate.documentName;
                if(documentName){
                    NSString *documentPath = [NSString stringWithFormat:@"%@/%@",mainJsonDirectoryPath,documentName];
                    RBQLog3(@"--->documentPath2:%@",documentPath);
                    stickerGroupTemplate.documentPath = documentPath;
                }
                NSMutableArray<StickerTemplate *> *stickerTemplates = stickerGroupTemplate.stickers;
                if(stickerTemplates){
                    for (StickerTemplate *stickerTemplate in stickerTemplates) {
                        NSString *fileName = stickerTemplate.fileName;
                        if(fileName){
                          NSString *localPath = [NSString stringWithFormat:@"%@/%@",mainJsonDirectoryPath,fileName];
                            RBQLog3(@"--->localPath:%@",localPath);
                            stickerTemplate.localPath = localPath;
                        }
                    }
                }
            }
        }
        if (onComplete) {
            onComplete(documentStickerGroupTemplate,nil,version);
        }
        return;
    }
    //普通单StickerGroupTemplate
    StickerGroupTemplate *stickerGroupTemplate = [StickerGroupTemplate mj_objectWithKeyValues:jsonDict[@"data"]];
    NSString *documentName = stickerGroupTemplate.documentName;
    if(documentName){
        NSString *documentPath = [NSString stringWithFormat:@"%@/%@",mainJsonDirectoryPath,documentName];
        RBQLog3(@"--->documentPath:%@",documentPath);
        stickerGroupTemplate.documentPath = documentPath;
    }
    NSMutableArray<StickerTemplate *> *stickerTemplates = stickerGroupTemplate.stickers;
    for (StickerTemplate *stickerTemplate in stickerTemplates) {
        NSString *fileName = stickerTemplate.fileName;
        if(fileName){
            NSString *localPath = [NSString stringWithFormat:@"%@/%@",mainJsonDirectoryPath,fileName];
            RBQLog3(@"--->localPath:%@",localPath);
            stickerTemplate.localPath = localPath;
        }
    }
    if (onComplete) {
        onComplete(nil,stickerGroupTemplate,version);
    }
}

+(void)readMxFileFormFilePath:(NSString *)mxKeyFilePath onComplete:(void (^)(StickerGroupsTemplate *_Nullable documentStickerGroupTemplate,StickerGroupTemplate  * _Nullable stickerGroupTemplate))onComplete error:(void (^)(void))onError{
    
    RBQLog3(@"文件路径:%@", mxKeyFilePath);
    NSFileManager *fileManager = [NSFileManager defaultManager];
    if (![fileManager fileExistsAtPath:mxKeyFilePath]) {
        if(onError){
            onError();
        }
        return;
    }
//    NSString *filePath = [NSString stringWithFormat:@"%@/%@",mxKeyFilePath,mx_main_json_name];
    NSString *filePath = [self findFileNamed:mx_main_json_name inDirectory:mxKeyFilePath];
    
    if (!filePath) {
        RBQLog3(@"【readMxFileFormMxKey】未查找到mx_main_json.txt文件 ~ filePath: %@", filePath);
        if(onError){
            onError();
        }
        return;
    }
    
    RBQLog3(@"【readMxFileFormMxKey】文件路径: %@", filePath);
    NSString *mainJsonDirectoryPath = [filePath stringByDeletingLastPathComponent];
    
    NSError *error;
    NSString *jsonString = [NSString stringWithContentsOfFile:filePath encoding:NSUTF8StringEncoding error:&error];
    if (error) {
        if (onError) {
            onError();
        }
        return;
    }
    
    NSData *jsonData = [jsonString dataUsingEncoding:NSUTF8StringEncoding];
    NSDictionary *jsonDict = [NSJSONSerialization JSONObjectWithData:jsonData options:NSJSONReadingMutableContainers error:&error];
    if (error) {
        if (onError) {
            onError();
        }
        return;
    }
    if(![jsonDict objectForKey:@"version"]){
        if (onError) {
            onError();
        }
        return;
    }
    NSString *version = jsonDict[@"version"];
    
    RBQLog3(@"当前模版的版本为:%@",version);
    
    NSArray<NSString *> *versionArr = [version componentsSeparatedByString:@"."];
    int version_0 = 1;
    if (versionArr.count>0) {
        version_0 = [versionArr.firstObject intValue];
    }
    //不包含type则
    if(![jsonDict objectForKey:@"type"]){
        if (onError) {
            onError();
        }
        return;
    }
    int type = [jsonDict[@"type"] intValue];
    if (type == TemplateTypeDocument) {
        //文档模式
        StickerGroupsTemplate *documentStickerGroupTemplate = [StickerGroupsTemplate mj_objectWithKeyValues:jsonDict[@"data"]];
        NSString *documentName = documentStickerGroupTemplate.documentName;
        //这里需要把文档或者图片的真实的路径转化出来赋值给localPath
        if(documentName){
            documentStickerGroupTemplate.documentPath = [NSString stringWithFormat:@"%@/%@",mainJsonDirectoryPath,documentName];
        }
        NSMutableArray<StickerGroupTemplate *> *stickerGroupTemplates = documentStickerGroupTemplate.groups;
        for (StickerGroupTemplate *stickerGroupTemplate in stickerGroupTemplates) {
            NSString *documentName = stickerGroupTemplate.documentName;
            if(documentName){
                stickerGroupTemplate.documentPath = [NSString stringWithFormat:@"%@/%@",mainJsonDirectoryPath,documentName];
            }
            NSMutableArray<StickerTemplate *> *stickerTemplates = stickerGroupTemplate.stickers;
            for (StickerTemplate *stickerTemplate in stickerTemplates) {
                NSString *fileName = stickerTemplate.fileName;
                if(fileName){
                    stickerTemplate.localPath = [NSString stringWithFormat:@"%@/%@",mainJsonDirectoryPath,fileName];
                }
            }
        }
        if (onComplete) {
            onComplete(documentStickerGroupTemplate,nil);
        }
        return;
    }
    //普通单StickerGroupTemplate
    StickerGroupTemplate *stickerGroupTemplate = [StickerGroupTemplate mj_objectWithKeyValues:jsonDict[@"data"]];
    NSMutableArray<StickerTemplate *> *stickerTemplates = stickerGroupTemplate.stickers;
    for (StickerTemplate *stickerTemplate in stickerTemplates) {
        NSString *fileName = stickerTemplate.fileName;
        if(fileName){
            stickerTemplate.localPath = [NSString stringWithFormat:@"%@/%@",mainJsonDirectoryPath,fileName];
        }
    }
    if (onComplete) {
        onComplete(nil,stickerGroupTemplate);
    }
    
}


+(StickerGroupsTemplate *)createMxDocumentStickerGroupTemplate:(NSString *)fileName
                             group:(StickerGroupsTemplate *)documentStickerGroupTemplate
                              flag:(int)flag
                           version:(NSString *)version
                             mxKey:(NSString *)mxKey{
    RBQLog3(@"【createMxDocumentStickerGroupTemplate】documentPath:%@;flag:%d",documentStickerGroupTemplate.documentPath,flag)
    
    NSString *documentName;
    if(flag == StickerGroupTemplateFromDocument && documentStickerGroupTemplate.documentPath){
        documentName = [self copyToMxCacheFile:mxKey filePath:documentStickerGroupTemplate.documentPath];
    }
    StickerGroupsTemplate *mxDocumentStickerGroupTemplate = [[StickerGroupsTemplate alloc] init];
    NSMutableArray<StickerGroupTemplate *> *mxGroups = [[NSMutableArray<StickerGroupTemplate *> alloc] init];
    for (StickerGroupTemplate *stickerGroupTemplate in documentStickerGroupTemplate.groups) {
        StickerGroupTemplate *mxStickerGroupTemplate = [self createMxStickerGroupTemplate:fileName group:stickerGroupTemplate flag:flag version:version mxKey:mxKey];
        [mxGroups addObject:mxStickerGroupTemplate];
    }
    mxDocumentStickerGroupTemplate.groups = mxGroups;
    mxDocumentStickerGroupTemplate.fileName = fileName;
    mxDocumentStickerGroupTemplate.documentName = documentName;
    return mxDocumentStickerGroupTemplate;
}

+(void)asynCreateMxDocumentStickerGroupTemplate:(NSString *)fileName
                             group:(StickerGroupsTemplate *)documentStickerGroupTemplate
                              flag:(int)flag
                           version:(NSString *)version
                             mxKey:(NSString *)mxKey
                        completion:(void (^)(StickerGroupsTemplate *))completionBlock
                             erroe:(void (^)(NSError *error))erroeBlock{
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        StickerGroupsTemplate *mxDocumentStickerGroupTemplate = [weakSelf createMxDocumentStickerGroupTemplate:fileName group:documentStickerGroupTemplate flag:flag version:version mxKey:mxKey];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(completionBlock){
                completionBlock(mxDocumentStickerGroupTemplate);
            }
        });
        
    });
    
    
}

+(StickerGroupTemplate *)createMxStickerGroupTemplate:(NSString *)fileName
                             group:(StickerGroupTemplate *)stickerGroupTemplate
                              flag:(int)flag
                           version:(NSString *)version
                             mxKey:(NSString *)mxKey{
    
    NSString *documentName;
    if(flag == StickerGroupTemplateFromDocument && stickerGroupTemplate.documentPath){
        documentName = [self copyToMxCacheFile:mxKey filePath:stickerGroupTemplate.documentPath];
    }
    
    NSMutableArray<StickerTemplate *> *stickers = [self createMxStickerTemplates:stickerGroupTemplate.stickers version:version mxKey:mxKey];
    
    StickerGroupTemplate *mxStickerGroupTemplate = [[StickerGroupTemplate alloc] init];
    mxStickerGroupTemplate.fileName = stickerGroupTemplate.fileName;
    mxStickerGroupTemplate.row = stickerGroupTemplate.row;
    mxStickerGroupTemplate.stickers = stickers;
    mxStickerGroupTemplate.flag = flag;
    mxStickerGroupTemplate.documentName = documentName;
    return mxStickerGroupTemplate;
}


+(void)asynCreateMxStickerGroupTemplate:(NSString *)fileName
                             group:(StickerGroupTemplate *)stickerGroupTemplate
                              flag:(int)flag
                           version:(NSString *)version
                             mxKey:(NSString *)mxKey
                        completion:(void (^)(StickerGroupTemplate *))completionBlock
                             erroe:(void (^)(NSError *error))erroeBlock{
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        
        StickerGroupTemplate *mxStickerGroupTemplate = [weakSelf createMxStickerGroupTemplate:fileName group:stickerGroupTemplate flag:flag version:version mxKey:mxKey];
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(completionBlock){
                completionBlock(mxStickerGroupTemplate);
            }
        });
        
    });
    
}


+(NSMutableArray<StickerTemplate *> *)createMxStickerTemplates:(NSMutableArray<StickerTemplate *> *)stickerTemplates version:(NSString *)version mxKey:(NSString *)mxKey{
    
    RBQLog3(@"保存到本地stickerViews");
    NSMutableArray<StickerTemplate *> *mxStickerTemplates = [[NSMutableArray<StickerTemplate *> alloc] init];

    for (StickerTemplate *stickerTemplate in stickerTemplates) {
        StickerTemplate *mxStickerTemplate = [self createMxStickerTemplate:stickerTemplate version:version mxKey:mxKey];
        if (mxStickerTemplate) {
            [mxStickerTemplates addObject:mxStickerTemplate];
        }
    }
    return mxStickerTemplates;
}

+(void)asynCreateMxStickerTemplates:(NSMutableArray<StickerTemplate *> *)stickerTemplates version:(NSString *)version mxKey:(NSString *)mxKey completion:(void (^)(NSMutableArray<StickerTemplate *> *mxStickerTemplates))completionBlock erroe:(void (^)(NSError *error))erroeBlock{
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSMutableArray<StickerTemplate *> *mxStickerTemplates = [weakSelf createMxStickerTemplates:stickerTemplates version:version mxKey:mxKey];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(completionBlock){
                completionBlock(mxStickerTemplates);
            }
        });
    });
    
}


/**该方法通过页面内StickerTemplate建模版过程，遇到图片会将图片复制到mxKey文件夹，但是对下面几个存文本的没啥用，只是为了形成一系列的方法，暂时放着**/
+(StickerTemplate *)createMxStickerTemplate:(StickerTemplate *)stickerTemplate version:(NSString *)version mxKey:(NSString *)mxKey{
    
    if (stickerTemplate.type == ImageStickerType || stickerTemplate.type == OriginalImageStickerType) {
        
        NSString *fileName = [self copyToMxCacheFile:mxKey filePath:stickerTemplate.localPath];
        StickerTemplate *mxStickerTemplate = [[StickerTemplate alloc] init];
        mxStickerTemplate.type = stickerTemplate.type;
        mxStickerTemplate.fileName = fileName;
        mxStickerTemplate.isLock = stickerTemplate.isLock;
        mxStickerTemplate.width = stickerTemplate.width;
        mxStickerTemplate.height = stickerTemplate.height;
        mxStickerTemplate.centerX = stickerTemplate.centerX;
        mxStickerTemplate.centerY = stickerTemplate.centerY;
        mxStickerTemplate.rotate = stickerTemplate.rotate;
        
        return mxStickerTemplate;
        
    }else if(stickerTemplate.type == AutoHeightTextStickerType ){
        
        StickerTemplate *mxStickerTemplate = [[StickerTemplate alloc] init];
        mxStickerTemplate.type = stickerTemplate.type;
        mxStickerTemplate.isLock = stickerTemplate.isLock;
        mxStickerTemplate.width = stickerTemplate.width;
        mxStickerTemplate.height = stickerTemplate.height;
        mxStickerTemplate.centerX = stickerTemplate.centerX;
        mxStickerTemplate.centerY = stickerTemplate.centerY;
        mxStickerTemplate.rotate = stickerTemplate.rotate;
        mxStickerTemplate.text = stickerTemplate.text;
        mxStickerTemplate.textSize = stickerTemplate.textSize;
        mxStickerTemplate.align = stickerTemplate.align;
        mxStickerTemplate.bold = stickerTemplate.bold;
        mxStickerTemplate.italic = stickerTemplate.italic;
        mxStickerTemplate.underline = stickerTemplate.underline;
        mxStickerTemplate.font = stickerTemplate.font;
        
        return mxStickerTemplate;
        
    }else if(stickerTemplate.type == BarCodeStickerType){
    
        StickerTemplate *mxStickerTemplate = [[StickerTemplate alloc] init];
        mxStickerTemplate.type = stickerTemplate.type;
        mxStickerTemplate.isLock = stickerTemplate.isLock;
        mxStickerTemplate.width = stickerTemplate.width;
        mxStickerTemplate.height = stickerTemplate.height;
        mxStickerTemplate.centerX = stickerTemplate.centerX;
        mxStickerTemplate.centerY = stickerTemplate.centerY;
        mxStickerTemplate.rotate = stickerTemplate.rotate;
        mxStickerTemplate.text = stickerTemplate.text;
        mxStickerTemplate.textSize = stickerTemplate.textSize;
        mxStickerTemplate.align = stickerTemplate.align;
        mxStickerTemplate.bold = stickerTemplate.bold;
        mxStickerTemplate.italic = stickerTemplate.italic;
        mxStickerTemplate.underline = stickerTemplate.underline;
        mxStickerTemplate.font = stickerTemplate.font;
        mxStickerTemplate.textPosition = stickerTemplate.textPosition;
        mxStickerTemplate.codeFormat = stickerTemplate.codeFormat;
        mxStickerTemplate.entryModel = stickerTemplate.entryModel;
        mxStickerTemplate.changeValue = stickerTemplate.changeValue;
        
        return mxStickerTemplate;
        
    }else if(stickerTemplate.type == QRCodeStickerType){
        
        StickerTemplate *mxStickerTemplate = [[StickerTemplate alloc] init];
        mxStickerTemplate.type = stickerTemplate.type;
        mxStickerTemplate.isLock = stickerTemplate.isLock;
        mxStickerTemplate.width = stickerTemplate.width;
        mxStickerTemplate.height = stickerTemplate.height;
        mxStickerTemplate.centerX = stickerTemplate.centerX;
        mxStickerTemplate.centerY = stickerTemplate.centerY;
        mxStickerTemplate.rotate = stickerTemplate.rotate;
        mxStickerTemplate.text = stickerTemplate.text;
        mxStickerTemplate.textSize = stickerTemplate.textSize;
        mxStickerTemplate.align = stickerTemplate.align;
        mxStickerTemplate.bold = stickerTemplate.bold;
        mxStickerTemplate.italic = stickerTemplate.italic;
        mxStickerTemplate.underline = stickerTemplate.underline;
        mxStickerTemplate.font = stickerTemplate.font;
        mxStickerTemplate.codeFormat = stickerTemplate.codeFormat;
        
        return mxStickerTemplate;
    }
    
    return nil;
}

+(void)asynCreateMxStickerTemplate:(StickerTemplate *)stickerTemplate version:(NSString *)version mxKey:(NSString *)mxKey completion:(void (^)(StickerTemplate *stickerTemplate))completionBlock erroe:(void (^)(NSError *error))erroeBlock {
    
    typeof(self) __weak weakSelf = self;
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        StickerTemplate *mxStickerTemplate = [weakSelf createMxStickerTemplate:stickerTemplate version:version mxKey:mxKey];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(stickerTemplate){
                
                if(completionBlock){
                    completionBlock(mxStickerTemplate);
                }
                
            }else{
             
                NSError *error = [NSError errorWithDomain:@"ZipErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"创建sticker模版失败"}];
                if(erroeBlock){
                    erroeBlock(error);
                }
                
            }
        });
    });
}

+(BOOL)zipFile:(NSString *)zipFilePath form:(NSString *)sourceFilePath{
    RBQLog3(@"【zipFile】zipFilePath:%@; sourceFilePath:%@",zipFilePath,sourceFilePath);
    [self deleteFileWithPath:zipFilePath];
    BOOL sucess = [SSZipArchive createZipFileAtPath:zipFilePath withContentsOfDirectory:sourceFilePath];
    return sucess;
}

+(void)asynZipFile:(NSString *)zipFilePath form:(NSString *)sourceFilePath completion:(void (^)(void))completionBlock erroe:(void (^)(NSError *error))erroeBlock{
    
    RBQLog3(@"【zipFile】zipFilePath:%@; sourceFilePath:%@",zipFilePath,sourceFilePath);
    [self deleteFileWithPath:zipFilePath];
    
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        BOOL success = [SSZipArchive createZipFileAtPath:zipFilePath withContentsOfDirectory:sourceFilePath];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            if (success) {
                NSLog(@"~~压缩~~%@-->%@ 成功",sourceFilePath,zipFilePath);
                if(completionBlock){
                    completionBlock();
                }
            } else {
                NSLog(@"~~压缩~~%@-->%@ 失败",sourceFilePath,zipFilePath);
                NSError *error = [NSError errorWithDomain:@"ZipErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"压缩失败"}];
                if(erroeBlock){
                    erroeBlock(error);
                }
            }
        });
    });
}

+(BOOL)unzipFile:(NSString *)zipFilePath to:(NSString *)desFilePath{
    RBQLog3(@"【unzipFile】zipFilePath:%@; desFilePath:%@",zipFilePath,desFilePath);
    [self deleteFileWithPath:desFilePath];
    BOOL success = [SSZipArchive unzipFileAtPath:zipFilePath toDestination:desFilePath];
    return success;
}

+(void)asynUnzipFile:(NSString *)zipFilePath to:(NSString *)desFilePath completion:(void (^)(void))completionBlock erroe:(void (^)(NSError *error))erroeBlock{
    
    RBQLog3(@"【unzipFile】zipFilePath:%@; desFilePath:%@",zipFilePath,desFilePath);
    [self deleteFileWithPath:desFilePath];
    
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        BOOL success = [SSZipArchive unzipFileAtPath:zipFilePath toDestination:desFilePath];
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            if (success) {
                NSLog(@"~~解压~~%@-->%@ 成功",zipFilePath,desFilePath);
                if(completionBlock){
                    completionBlock();
                }
            } else {
                NSLog(@"~~解压~~%@-->%@ 失败",zipFilePath,desFilePath);
                NSError *error = [NSError errorWithDomain:@"ZipErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"解压失败"}];
                if(erroeBlock){
                    erroeBlock(error);
                }
            }
        });
    });
}

+(BOOL)copy:(NSString *)sourceFilePath to:(NSString *)desFilePath isDeleteSrc:(BOOL)isDeleteSrc {
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSError *error = nil;
    // 检查目标路径文件是否存在，如果存在则尝试删除
    if ([fileManager fileExistsAtPath:desFilePath]) {
        if (![fileManager removeItemAtPath:desFilePath error:&error]) {
            NSLog(@"无法移除旧文件。错误: %@", error);
            return NO;
        }
    }
    // 尝试复制文件
    BOOL success = [fileManager copyItemAtPath:sourceFilePath toPath:desFilePath error:&error];
    if (success) {
        NSLog(@"~~复制~~%@-->%@ 成功",sourceFilePath,desFilePath);
        // 如果复制成功且需要删除源文件
        if (isDeleteSrc) {
            if (![fileManager removeItemAtPath:sourceFilePath error:&error]) {
                NSLog(@"复制成功但删除源文件失败。错误: %@", error);
            } else {
                NSLog(@"~~删除源文件~~%@ 成功", sourceFilePath);
            }
        }
    } else {
        NSLog(@"~~复制~~%@-->%@ 失败",sourceFilePath,desFilePath);
    }
    return success;
}

+(void)asynCopy:(NSString *)sourceFilePath to:(NSString *)desFilePath isDeleteSrc:(BOOL)isDeleteSrc completion:(void (^)(void))completionBlock erroe:(void (^)(NSError *error))erroeBlock {
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSError *error = nil;
    // 检查目标路径文件是否存在，如果存在则尝试删除
    if ([fileManager fileExistsAtPath:desFilePath]) {
        if (![fileManager removeItemAtPath:desFilePath error:&error]) {
            NSLog(@"无法移除旧文件。错误: %@", error);
            NSError *error = [NSError errorWithDomain:@"CopyErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"无法移除旧文件"}];
            if(erroeBlock){
                dispatch_async(dispatch_get_main_queue(), ^{
                    erroeBlock(error);
                });
            }
            return;
        }
    }
    // 尝试复制文件
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        NSError *error = nil;
        BOOL success = [fileManager copyItemAtPath:sourceFilePath toPath:desFilePath error:&error];
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            if (success) {
                NSLog(@"~~复制~~%@; --到-->%@ 成功",sourceFilePath,desFilePath);
                // 如果复制成功且需要删除源文件
                if (isDeleteSrc) {
                    NSError *deleteError = nil;
                    if (![fileManager removeItemAtPath:sourceFilePath error:&deleteError]) {
                        NSLog(@"复制成功但删除源文件失败。错误: %@", deleteError);
                    } else {
                        NSLog(@"~~删除源文件~~%@ 成功", sourceFilePath);
                    }
                }
                if(completionBlock){
                    completionBlock();
                }
            } else {
                NSLog(@"~~复制~~%@; --到-->%@ 失败",sourceFilePath,desFilePath);
                NSError *error = [NSError errorWithDomain:@"CopyErrorDomain" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"复制失败"}];
                if(erroeBlock){
                    erroeBlock(error);
                }
            }
        });
    });
}

+(NSArray *)searchOtaFileArray {
    NSArray<NSString *> *files = [RBQFileManager listFilesInDocumentDirectoryByDeep:NO];
    NSPredicate *predicate = [NSPredicate predicateWithFormat:@"self ENDSWITH '.rbl'"];
    NSArray<NSString *> *otaFiles = [files filteredArrayUsingPredicate:predicate];
    // 如果需要日志记录，可以在这里添加
    for (NSString *file in otaFiles) {
        NSLog(@"找到OTA文件: %@", file);
    }
    return otaFiles;
}

+(void)asynSearchOtaFileArray:(void (^)(NSArray *otaFiles))completionBlock{
    
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(queue, ^{
        
        NSArray<NSString *> *files = [RBQFileManager listFilesInDocumentDirectoryByDeep:NO];
        NSPredicate *predicate = [NSPredicate predicateWithFormat:@"self ENDSWITH '.rbl'"];
        NSArray<NSString *> *otaFiles = [files filteredArrayUsingPredicate:predicate];
        // 如果需要日志记录，可以在这里添加
        for (NSString *file in otaFiles) {
            NSLog(@"找到OTA文件: %@", file);
        }
        
        // 在主线程回调
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(completionBlock){
                completionBlock(otaFiles);
            }
        });
    });
    
}

+(BOOL)deleteFileWithPath:(NSString *)filePath {
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSError *error;
    BOOL isRemove = [fileManager fileExistsAtPath:filePath];
    if (isRemove) {
        isRemove = [fileManager removeItemAtPath:filePath error:&error];
        if (!isRemove || error) {
            // 处理错误
            NSLog(@"删除文件出错: %@", error.localizedDescription);
        } else {
            NSLog(@"删除成功");
        }
    } else {
        NSLog(@"该文件不存在，无需删除");
    }
    return isRemove;
}

+(void)clearAllImageInImageCacheFile {
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        NSString *documentsDirectory = [NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES) firstObject];
        NSString *filePath = [documentsDirectory stringByAppendingPathComponent:imageCacheFile];
        NSFileManager *fileManager = [NSFileManager defaultManager];
        NSError *error;
        NSArray *contents = [fileManager contentsOfDirectoryAtPath:filePath error:&error];
        if (error) {
            // 处理错误
            NSLog(@"Error getting contents of directory: %@", error.localizedDescription);
            return;
        }
        for (NSString *filename in contents) {
            NSString *fullPath = [filePath stringByAppendingPathComponent:filename];
            BOOL success = [fileManager removeItemAtPath:fullPath error:&error];
            if (!success || error) {
                // 处理错误
                NSLog(@"Error removing file %@: %@", filename, error.localizedDescription);
            } else {
                NSLog(@"成功删除缓存文件:%@", filename);
            }
        }
    });
}


+(void)clearAllJsonInJsonCacheFile {
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        NSString *documentsDirectory = [NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES) firstObject];
        NSString *filePath = [documentsDirectory stringByAppendingPathComponent:JsonCacheFile];
        NSFileManager *fileManager = [NSFileManager defaultManager];
        NSError *error;
        NSArray *contents = [fileManager contentsOfDirectoryAtPath:filePath error:&error];
        if (error) {
            // 处理错误
            NSLog(@"获取目录内容错误: %@", error.localizedDescription);
            return;
        }
        for (NSString *filename in contents) {
            NSString *fullPath = [filePath stringByAppendingPathComponent:filename];
            BOOL success = [fileManager removeItemAtPath:fullPath error:&error];
            if (!success || error) {
                // 处理错误
                NSLog(@"删除文件%@出错: %@", filename, error.localizedDescription);
            } else {
                NSLog(@"成功删除缓存的数据:%@", filename);
            }
        }
    });
}


+(void)clearAllDataInDataCacheFile {
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        NSString *documentsDirectory = [NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES) firstObject];
        NSString *filePath = [documentsDirectory stringByAppendingPathComponent:dataCacheFile];
        NSFileManager *fileManager = [NSFileManager defaultManager];
        NSError *error;
        NSArray *contents = [fileManager contentsOfDirectoryAtPath:filePath error:&error];
        if (error) {
            // 处理错误
            NSLog(@"获取目录内容错误: %@", error.localizedDescription);
            return;
        }
        for (NSString *filename in contents) {
            NSString *fullPath = [filePath stringByAppendingPathComponent:filename];
            BOOL success = [fileManager removeItemAtPath:fullPath error:&error];
            if (!success || error) {
                // 处理错误
                NSLog(@"删除文件%@出错: %@", filename, error.localizedDescription);
            } else {
                NSLog(@"成功删除缓存的数据:%@", filename);
            }
        }
    });
}


+(void)clearAllFileInMxCacheFile {
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        NSString *documentsDirectory = [NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES) firstObject];
        NSString *filePath = [documentsDirectory stringByAppendingPathComponent:mxCacheFiles];
        NSFileManager *fileManager = [NSFileManager defaultManager];
        NSError *error;
        NSArray *contents = [fileManager contentsOfDirectoryAtPath:filePath error:&error];
        if (error) {
            // 处理错误
            NSLog(@"获取目录内容错误: %@", error.localizedDescription);
            return;
        }
        for (NSString *filename in contents) {
            NSString *fullPath = [filePath stringByAppendingPathComponent:filename];
            BOOL success = [fileManager removeItemAtPath:fullPath error:&error];
            if (!success || error) {
                // 处理错误
                NSLog(@"删除文件%@出错: %@", filename, error.localizedDescription);
            } else {
                NSLog(@"成功删除缓存的数据:%@", filename);
            }
        }
    });
}

+(void)clearAllFileInDocsCacheFile {
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        NSString *documentsDirectory = [NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES) firstObject];
        NSString *filePath = [documentsDirectory stringByAppendingPathComponent:docsCacheFile];
        NSFileManager *fileManager = [NSFileManager defaultManager];
        NSError *error;
        NSArray *contents = [fileManager contentsOfDirectoryAtPath:filePath error:&error];
        if (error) {
            // 处理错误
            NSLog(@"获取目录内容错误: %@", error.localizedDescription);
            return;
        }
        for (NSString *filename in contents) {
            NSString *fullPath = [filePath stringByAppendingPathComponent:filename];
            BOOL success = [fileManager removeItemAtPath:fullPath error:&error];
            if (!success || error) {
                // 处理错误
                NSLog(@"删除文件%@出错: %@", filename, error.localizedDescription);
            } else {
                NSLog(@"成功删除缓存的数据:%@", filename);
            }
        }
    });
}


+(void)clearAllCacheFile{
    
    [self clearAllImageInImageCacheFile];
    [self clearAllJsonInJsonCacheFile];
    [self clearAllDataInDataCacheFile];
    [self clearAllFileInMxCacheFile];
    [self clearAllFileInDocsCacheFile];
}

+(NSString *)createStringByData{
    
    NSDateFormatter *formatter = [[NSDateFormatter alloc] init];
    [formatter setDateStyle: NSDateFormatterMediumStyle];
    [formatter setTimeStyle: NSDateFormatterShortStyle];
    [formatter setDateFormat: @"YYYY_MM_dd_HH_mm_ss"];

    NSTimeZone *timeZone = [NSTimeZone timeZoneWithName: @"Asia/Shanghai"];
    [formatter setTimeZone: timeZone];
    NSDate *datenow = [NSDate date];
    NSString *timeString = [formatter stringFromDate:datenow];
    return timeString;
}

+(NSString *)createStringByDataFromMsec{
    
    NSDateFormatter *formatter = [[NSDateFormatter alloc] init];
    [formatter setDateStyle: NSDateFormatterMediumStyle];
    [formatter setTimeStyle: NSDateFormatterShortStyle];
    [formatter setDateFormat: @"YYYY-MM-dd-HH-mm-ss-SSS"];

    NSTimeZone *timeZone = [NSTimeZone timeZoneWithName: @"Asia/Shanghai"];
    [formatter setTimeZone: timeZone];
    NSDate *datenow = [NSDate date];
    NSString *timeString = [formatter stringFromDate:datenow];
    return timeString;
}

+ (NSString *)create42StringByLetterAndNumber {
    NSString *strAll = @"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    NSMutableString *result = [NSMutableString stringWithCapacity:42];
    for (int i = 0; i < 42; i++) {
        // 生成一个安全的随机数
        uint32_t randomNum;
        int err = SecRandomCopyBytes(kSecRandomDefault, sizeof(randomNum), (uint8_t*)&randomNum);
        if (err != errSecSuccess) {
            // 处理错误情况
            RBQLog3(@"无法生成安全随机数: %d", err);
            return [self create42StringByLetterAndNumber1];
        }
        // 使用随机数作为索引
        u_int32_t index = randomNum % (u_int32_t)strAll.length;
        unichar tempStr = [strAll characterAtIndex:index];
        [result appendFormat:@"%c", tempStr];
    }
    return result;
}

/**使用26个字母作为文件名*/
+(NSString *)create42StringByLetterAndNumber1 {
    NSString *strAll = @"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    NSMutableString *result = [NSMutableString stringWithCapacity:42];
    for (int i = 0; i < 42; i++) {
        // 获取随机数
        u_int32_t index = arc4random_uniform((u_int32_t)strAll.length);
        unichar tempStr = [strAll characterAtIndex:index];
        [result appendFormat:@"%c", tempStr];
    }
    return result;
}

+ (void)enumerateFilesInDirectory:(NSString *)directoryPath {
    // 检查传入的 directoryPath 是否为 nil
    if (directoryPath == nil) {
        RBQLog3(@"【enumerateFilesInDirectory】Error: directoryPath cannot be nil.");
        return;
    }
    
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSDirectoryEnumerator *enumerator = [fileManager enumeratorAtPath:directoryPath];
    
    NSString *file;
    while ((file = [enumerator nextObject]) != nil) {
        NSString *fullPath = [directoryPath stringByAppendingPathComponent:file];
        BOOL isDirectory;
        if ([fileManager fileExistsAtPath:fullPath isDirectory:&isDirectory]) {
            if (isDirectory) {
                RBQLog3(@"【enumerateFilesInDirectory】Directory: %@", fullPath);
                // 如果你想进一步遍历子目录，可以递归调用这个方法
                [self enumerateFilesInDirectory:fullPath];
            } else {
                RBQLog3(@"【enumerateFilesInDirectory】File: %@", fullPath);
            }
        }
    }
}


+ (NSString *)findFileNamed:(NSString *)fileName inDirectory:(NSString *)directoryPath {
    if (!directoryPath) {
        // 如果传入的目录路径为 nil，返回错误信息
        RBQLog3(@"【findFileNamed】传入的 directoryPath为 nil");
        return nil;
    }
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSDirectoryEnumerator *enumerator = [fileManager enumeratorAtPath:directoryPath];
    
    NSString *file;
    while ((file = [enumerator nextObject]) != nil) {
        NSString *fullPath = [directoryPath stringByAppendingPathComponent:file];
        BOOL isDirectory;
        // 检查这是一个文件还是目录
        [fileManager fileExistsAtPath:fullPath isDirectory:&isDirectory];
        if (isDirectory) {
            // 如果是目录，递归调用
            NSString *foundPath = [self findFileNamed:fileName inDirectory:fullPath];
            if (foundPath) return foundPath; // 如果在子目录中找到了文件，返回路径
        } else if ([[file lastPathComponent] isEqualToString:fileName]) {
            // 如果找到了文件，返回路径
            return fullPath;
        }
    }
    // 如果没有找到文件，返回 nil
    return nil;
}


+ (BOOL)isWordOrPdfFileAtPath:(NSString *)filePath {
    FileType fileType = [self fileTypeFromFilePathByFileHandle:filePath];
    return fileType == FileTypeDOC || fileType == FileTypeDOCX || fileType == FileTypePDF;
}
+ (BOOL)isWordFileAtPath:(NSString *)filePath {
    // 如果文件路径不为空，且文件名以.doc或.docx结尾，就返回真，否则返回假
    FileType fileType = [self fileTypeFromFilePathByFileHandle:filePath];
    return fileType == FileTypeDOC || fileType == FileTypeDOCX;
}

+ (BOOL)isPDFFileAtPath:(NSString *)filePath {
    FileType fileType = [self fileTypeFromFilePathByFileHandle:filePath];
    return fileType == FileTypePDF;
}

+ (NSString *)fileDisplayNameWithPath:(NSString *)filePath {
    return [[NSFileManager defaultManager] displayNameAtPath:filePath];
}

+ (NSString *)fileNameWithPath:(NSString *)filePath {
    return [filePath lastPathComponent];
}


// 分块读取文件头信息来判断文件类型
+(FileType)fileTypeFromFilePathByFileHandle:(NSString *)filePath {
    
    NSFileHandle *fileHandle = [NSFileHandle fileHandleForReadingAtPath:filePath];
    if (!fileHandle) {
        NSLog(@"无法打开文件");
        return FileTypeUnknown;
    }
    
    NSData *data = [fileHandle readDataOfLength:11]; // 读取足够的字节来检查大部分文件类型
    [fileHandle closeFile]; // 立即关闭文件句柄
    
    if (data.length < 11) {
        NSLog(@"读取文件头失败");
        return FileTypeUnknown;
    }
    
    uint8_t buffer[11];
    [data getBytes:buffer length:sizeof(buffer)];
    
    // 检查JPEG文件头
    if (buffer[0] == 0xFF && buffer[1] == 0xD8 && buffer[2] == 0xFF) {
        return FileTypeJPEG;
    }
    // 检查PNG文件头
    if (buffer[0] == 0x89 && buffer[1] == 'P' && buffer[2] == 'N' && buffer[3] == 'G' &&
        buffer[4] == 0x0D && buffer[5] == 0x0A && buffer[6] == 0x1A && buffer[7] == 0x0A) {
        return FileTypePNG;
    }
    // 检查PDF文件头
    if (buffer[0] == '%' && buffer[1] == 'P' && buffer[2] == 'D' && buffer[3] == 'F' &&
        buffer[4] == '-') {
        return FileTypePDF;
    }
    // 检查GIF文件头（GIF87a/GIF89a）
    if (buffer[0] == 'G' && buffer[1] == 'I' && buffer[2] == 'F' &&
        (buffer[3] == '8' && (buffer[4] == '7' || buffer[4] == '9') && buffer[5] == 'a')) {
        return FileTypeGIF;
    }
    // 检查BMP文件头（BM）
    if (buffer[0] == 'B' && buffer[1] == 'M') {
        return FileTypeBMP;
    }
    // 检查TIFF文件头（II*或MM*）
    if ((buffer[0] == 'I' && buffer[1] == 'I' && buffer[2] == '*') ||
        (buffer[0] == 'M' && buffer[1] == 'M' && buffer[2] == '*')) {
        return FileTypeTIFF;
    }
    // 检查ZIP文件头（PK\x03\x04）
    if (buffer[0] == 'P' && buffer[1] == 'K' && buffer[2] == 0x03 && buffer[3] == 0x04) {
        return FileTypeZIP;
    }
    // 检查RAR文件头（Rar!）
    if (buffer[0] == 'R' && buffer[1] == 'a' && buffer[2] == 'r' && buffer[3] == '!') {
        return FileTypeRAR;
    }
    // 检查MP3文件头（ID3或者FFFx）
    if ((buffer[0] == 'I' && buffer[1] == 'D' && buffer[2] == '3') ||
        (buffer[0] == 0xFF && (buffer[1] & 0xE0) == 0xE0)) {
        return FileTypeMP3;
    }
    // 检查MP4文件头（ftyp）
    if (buffer[0] == 'f' && buffer[1] == 't' && buffer[2] == 'y' && buffer[3] == 'p') {
        return FileTypeMP4;
    }
    // 检查DOCX文件头（50 4B 03 04）
    if (buffer[0] == 0x50 && buffer[1] == 0x4B && buffer[2] == 0x03 && buffer[3] == 0x04) {
        return FileTypeDOCX;
    }
    // 检查XLSX文件头（50 4B 03 04）
    if (buffer[0] == 0x50 && buffer[1] == 0x4B && buffer[2] == 0x03 && buffer[3] == 0x04) {
        return FileTypeXLSX;
    }
    // 检查Microsoft Office文件头（D0 CF 11 E0）
    if (buffer[0] == 0xD0 && buffer[1] == 0xCF && buffer[2] == 0x11 && buffer[3] == 0xE0) {
        fileHandle = [NSFileHandle fileHandleForReadingAtPath:filePath];
        [fileHandle seekToFileOffset:512]; // 移动到Microsoft Office文件类型标识的位置
        NSData *officeData = [fileHandle readDataOfLength:19];
        [fileHandle closeFile];
        
        if (officeData.length < 19) {
            NSLog(@"读取Microsoft Office文件头失败");
            return FileTypeUnknown;
        }
        
        uint8_t officeBuffer[19];
        [officeData getBytes:officeBuffer length:sizeof(officeBuffer)];
        
        // 检查Word文档（Word.Document.）
        if (officeBuffer[0] == 'W' && officeBuffer[1] == 'o' && officeBuffer[2] == 'r' && officeBuffer[3] == 'd' &&
            officeBuffer[4] == '.' && officeBuffer[5] == 'D' && officeBuffer[6] == 'o' && officeBuffer[7] == 'c' &&
            officeBuffer[8] == 'u' && officeBuffer[9] == 'm' && officeBuffer[10] == 'e' && officeBuffer[11] == 'n' &&
            officeBuffer[12] == 't' && officeBuffer[13] == '.') {
            return FileTypeDOC;
        }
        // 检查Excel文档（Workbook）
        if (officeBuffer[0] == 'W' && officeBuffer[1] == 'o' && officeBuffer[2] == 'r' && officeBuffer[3] == 'k' &&
            officeBuffer[4] == 'b' && officeBuffer[5] == 'o' && officeBuffer[6] == 'o' && officeBuffer[7] == 'k') {
            return FileTypeXLS;
        }
        // 检查PowerPoint文档（PowerPoint Document）
        if (officeBuffer[0] == 'P' && officeBuffer[1] == 'o' && officeBuffer[2] == 'w' && officeBuffer[3] == 'e' &&
            officeBuffer[4] == 'r' && officeBuffer[5] == 'P' && officeBuffer[6] == 'o' && officeBuffer[7] == 'i' &&
            officeBuffer[8] == 'n' && officeBuffer[9] == 't' && officeBuffer[10] == ' ' && officeBuffer[11] == 'D' &&
            officeBuffer[12] == 'o' && officeBuffer[13] == 'c' && officeBuffer[14] == 'u' && officeBuffer[15] == 'm' &&
            officeBuffer[16] == 'e' && officeBuffer[17] == 'n' && officeBuffer[18] == 't') {
            return FileTypePPT;
        }
    }
    
    return FileTypeUnknown;
}

+(FileType)fileTypeFromFilePathByInputStream:(NSString *)filePath {
    
    NSInputStream *inputStream = [[NSInputStream alloc] initWithFileAtPath:filePath];
    [inputStream open];
    
    if ([inputStream streamStatus] == NSStreamStatusError) {
        NSLog(@"无法打开文件");
        [inputStream close];
        return FileTypeUnknown;
    }
    
    uint8_t buffer[11];
    NSInteger bytesRead = [inputStream read:buffer maxLength:sizeof(buffer)];
    
    if (bytesRead < sizeof(buffer)) {
        NSLog(@"读取文件头失败");
        [inputStream close];
        return FileTypeUnknown;
    }
    
    // 检查JPEG文件头
    if (buffer[0] == 0xFF && buffer[1] == 0xD8 && buffer[2] == 0xFF) {
        [inputStream close];
        return FileTypeJPEG;
    }
    // 检查PNG文件头
    else if (buffer[0] == 0x89 && buffer[1] == 'P' && buffer[2] == 'N' && buffer[3] == 'G' &&
        buffer[4] == 0x0D && buffer[5] == 0x0A && buffer[6] == 0x1A && buffer[7] == 0x0A) {
        [inputStream close];
        return FileTypePNG;
    }
    // 检查PDF文件头
    else if (buffer[0] == '%' && buffer[1] == 'P' && buffer[2] == 'D' && buffer[3] == 'F' &&
        buffer[4] == '-') {
        [inputStream close];
        return FileTypePDF;
    }
    // 检查GIF文件头（GIF87a/GIF89a）
    else if (buffer[0] == 'G' && buffer[1] == 'I' && buffer[2] == 'F' &&
        (buffer[3] == '8' && (buffer[4] == '7' || buffer[4] == '9') && buffer[5] == 'a')) {
        [inputStream close];
        return FileTypeGIF;
    }
    // 检查BMP文件头（BM）
    else if (buffer[0] == 'B' && buffer[1] == 'M') {
        [inputStream close];
        return FileTypeBMP;
    }
    // 检查TIFF文件头（II*或MM*）
    else if ((buffer[0] == 'I' && buffer[1] == 'I' && buffer[2] == '*') ||
        (buffer[0] == 'M' && buffer[1] == 'M' && buffer[2] == '*')) {
        [inputStream close];
        return FileTypeTIFF;
    }
    // 检查ZIP文件头（PK\x03\x04）
    else if (buffer[0] == 'P' && buffer[1] == 'K' && buffer[2] == 0x03 && buffer[3] == 0x04) {
        [inputStream close];
        return FileTypeZIP;
    }
    // 检查RAR文件头（Rar!）
    else if (buffer[0] == 'R' && buffer[1] == 'a' && buffer[2] == 'r' && buffer[3] == '!') {
        [inputStream close];
        return FileTypeRAR;
    }
    // 检查MP3文件头（ID3或者FFFx）
    else if ((buffer[0] == 'I' && buffer[1] == 'D' && buffer[2] == '3') ||
        (buffer[0] == 0xFF && (buffer[1] & 0xE0) == 0xE0)) {
        [inputStream close];
        return FileTypeMP3;
    }
    // 检查MP4文件头（ftyp）
    else if (buffer[0] == 'f' && buffer[1] == 't' && buffer[2] == 'y' && buffer[3] == 'p') {
        [inputStream close];
        return FileTypeMP4;
    }
    // 检查DOCX文件头（50 4B 03 04）
    else if (buffer[0] == 0x50 && buffer[1] == 0x4B && buffer[2] == 0x03 && buffer[3] == 0x04) {
        [inputStream close];
        return FileTypeDOCX;
    }
    // 检查XLSX文件头（50 4B 03 04）
    else if (buffer[0] == 0x50 && buffer[1] == 0x4B && buffer[2] == 0x03 && buffer[3] == 0x04) {
        [inputStream close];
        return FileTypeXLSX;
    }
    // 检查Microsoft Office文件头（D0 CF 11 E0）
    else if (buffer[0] == 0xD0 && buffer[1] == 0xCF && buffer[2] == 0x11 && buffer[3] == 0xE0) {
        // 为了检查Microsoft Office文件类型，需要读取更多的字节
        uint8_t officeBuffer[19];
        NSInteger officeBytesRead = [inputStream read:officeBuffer maxLength:sizeof(officeBuffer)];
        
        if (officeBytesRead < sizeof(officeBuffer)) {
            NSLog(@"读取Microsoft Office文件头失败");
            [inputStream close];
            return FileTypeUnknown;
        }
        
        // 检查Word文档（Word.Document.）
        if (officeBuffer[0] == 'W' && officeBuffer[1] == 'o' && officeBuffer[2] == 'r' && officeBuffer[3] == 'd' &&
            officeBuffer[4] == '.' && officeBuffer[5] == 'D' && officeBuffer[6] == 'o' && officeBuffer[7] == 'c' &&
            officeBuffer[8] == 'u' && officeBuffer[9] == 'm' && officeBuffer[10] == 'e' && officeBuffer[11] == 'n' &&
            officeBuffer[12] == 't' && officeBuffer[13] == '.') {
            [inputStream close];
            return FileTypeDOC;
        }
        // 检查Excel文档（Workbook）
        else if (officeBuffer[0] == 'W' && officeBuffer[1] == 'o' && officeBuffer[2] == 'r' && officeBuffer[3] == 'k' &&
            officeBuffer[4] == 'b' && officeBuffer[5] == 'o' && officeBuffer[6] == 'o' && officeBuffer[7] == 'k') {
            [inputStream close];
            return FileTypeXLS;
        }
        // 检查PowerPoint文档（PowerPoint Document）
        else if (officeBuffer[0] == 'P' && officeBuffer[1] == 'o' && officeBuffer[2] == 'w' && officeBuffer[3] == 'e' &&
            officeBuffer[4] == 'r' && officeBuffer[5] == 'P' && officeBuffer[6] == 'o' && officeBuffer[7] == 'i' &&
            officeBuffer[8] == 'n' && officeBuffer[9] == 't' && officeBuffer[10] == ' ' && officeBuffer[11] == 'D' &&
            officeBuffer[12] == 'o' && officeBuffer[13] == 'c' && officeBuffer[14] == 'u' && officeBuffer[15] == 'm' &&
            officeBuffer[16] == 'e' && officeBuffer[17] == 'n' && officeBuffer[18] == 't') {
            [inputStream close];
            return FileTypePPT;
        }
        else {
            [inputStream close];
            return FileTypeUnknown;
        }
    }
    
    [inputStream close];
    return FileTypeUnknown;
}

+ (BOOL)isImageFileAtPathBySuffix:(NSString *)filePath {
    NSString *fileExtension = [filePath pathExtension];
    NSArray *imageExtensions = @[@"jpg", @"jpeg", @"png", @"gif", @"bmp", @"tiff", @"tif"];
    return [imageExtensions containsObject:fileExtension];
}

+ (BOOL)isPDFFileAtPathBySuffix:(NSString *)filePath {
    NSString *fileExtension = [filePath pathExtension];
    return [fileExtension isEqualToString:@"pdf"];
}

+ (NSDictionary *)fileAttributesForItemAtPath:(NSString *)filePath error:(NSError **)error {
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSDictionary *attributes = [fileManager attributesOfItemAtPath:filePath error:error];
    if (attributes == nil) {
        // 处理错误
        RBQLog3(@"无法获取文件属性: %@", *error);
    }
    return attributes;
}

+ (NSDictionary *)imageAttributesForItemFilePath:(NSString *)filePath error:(NSError **)error {
    NSURL *imageURL = [NSURL fileURLWithPath:filePath];
    CGImageSourceRef imageSource = CGImageSourceCreateWithURL((__bridge CFURLRef)imageURL, NULL);
    if (imageSource == NULL) {
        // 处理错误
        *error = [NSError errorWithDomain:@"ImageProcessingErrorDomain" code:1001 userInfo:@{NSLocalizedDescriptionKey: @"无法获取图像属性，可能是文件不存在或不是有效的图像文件。"}];
        return nil;
    }
    CFDictionaryRef imageProperties = CGImageSourceCopyPropertiesAtIndex(imageSource, 0, NULL);
    NSDictionary *propertiesDict = nil;
    if (imageProperties) {
        propertiesDict = (__bridge_transfer NSDictionary *)imageProperties;
    }
    CFRelease(imageSource);
    return propertiesDict;
}

+ (NSDictionary *)imageAttributesFromFilePathByFileHandle:(NSString *)filePath error:(NSError **)error {
    
    NSFileHandle *fileHandle = [NSFileHandle fileHandleForReadingAtPath:filePath];
    if (!fileHandle) {
        if (error) {
            *error = [NSError errorWithDomain:@"ImageReadErrorDomain" code:ImageReadErrorCannotOpenFile userInfo:nil];
        }
        return nil;
    }
    
    NSData *headerData = [fileHandle readDataOfLength:24];
    if ([headerData length] < 24) {
        if (error) {
            *error = [NSError errorWithDomain:@"ImageReadErrorDomain" code:ImageReadErrorFileTooShort userInfo:nil];
        }
        [fileHandle closeFile];
        return nil;
    }
    
    const uint8_t *buffer = [headerData bytes];
    NSMutableDictionary *imageInfo = [NSMutableDictionary dictionary];
    
    // 检查 JPEG
    if (buffer[0] == 0xFF && buffer[1] == 0xD8) {
        int width = (buffer[7] << 8) + buffer[8];
        int height = (buffer[9] << 8) + buffer[10];
        [imageInfo setObject:@(width) forKey:@"Width"];
        [imageInfo setObject:@(height) forKey:@"Height"];
        [imageInfo setObject:@(FileTypeJPEG) forKey:@"FileType"];
    }
    // 检查 PNG
    else if (buffer[0] == 0x89 && buffer[1] == 'P' && buffer[2] == 'N' && buffer[3] == 'G') {
        int width = (buffer[16] << 8) + buffer[17];
        int height = (buffer[18] << 8) + buffer[19];
        [imageInfo setObject:@(width) forKey:@"Width"];
        [imageInfo setObject:@(height) forKey:@"Height"];
        [imageInfo setObject:@(FileTypePNG) forKey:@"FileType"];
    }
    // 检查 GIF
    else if (buffer[0] == 'G' && buffer[1] == 'I' && buffer[2] == 'F') {
        int width = buffer[6] + (buffer[7] << 8);
        int height = buffer[8] + (buffer[9] << 8);
        [imageInfo setObject:@(width) forKey:@"Width"];
        [imageInfo setObject:@(height) forKey:@"Height"];
        [imageInfo setObject:@(FileTypeGIF) forKey:@"FileType"];
    }
    // 检查 BMP
    else if (buffer[0] == 'B' && buffer[1] == 'M') {
        // 读取 BMP 需要的额外字节
        [fileHandle seekToFileOffset:18]; // 移动到 BMP 宽度和高度信息的起始位置
        NSData *bmpData = [fileHandle readDataOfLength:8];
        if ([bmpData length] < 8) {
            if (error) {
                *error = [NSError errorWithDomain:@"ImageReadErrorDomain" code:ImageReadErrorFileTooShort userInfo:nil];
            }
            [fileHandle closeFile];
            return nil;
        }
        const uint8_t *bmpBuffer = [bmpData bytes];
        int width = bmpBuffer[0] + (bmpBuffer[1] << 8) + (bmpBuffer[2] << 16) + (bmpBuffer[3] << 24);
        int height = bmpBuffer[4] + (bmpBuffer[5] << 8) + (bmpBuffer[6] << 16) + (bmpBuffer[7] << 24);
        [imageInfo setObject:@(width) forKey:@"Width"];
        [imageInfo setObject:@(height) forKey:@"Height"];
        [imageInfo setObject:@(FileTypeBMP) forKey:@"FileType"];
    }
    else {
        if (error) {
            *error = [NSError errorWithDomain:@"ImageReadErrorDomain" code:ImageReadErrorUnsupportedFormat userInfo:nil];
        }
        [fileHandle closeFile];
        return nil;
    }
    
    [fileHandle closeFile];
    return imageInfo;
}

/**
 获取图片属性，按照数据流的方式来实现
 */
+ (NSDictionary *)imageAttributesFromFilePathByInputStream:(NSString *)filePath error:(NSError **)error {
    
    NSInputStream *inputStream = [[NSInputStream alloc] initWithFileAtPath:filePath];
    [inputStream open];
    
    uint8_t buffer[24];
    NSInteger bytesRead = [inputStream read:buffer maxLength:24];
    
    if (bytesRead < 24) {
        if (error) {
            *error = [NSError errorWithDomain:@"ImageReadErrorDomain" code:ImageReadErrorFileTooShort userInfo:nil];
        }
        [inputStream close];
        return nil;
    }
    
    NSMutableDictionary *imageInfo = [NSMutableDictionary dictionary];
    
    // 检查 JPEG
    if (buffer[0] == 0xFF && buffer[1] == 0xD8) {
        int width = (buffer[7] << 8) + buffer[8];
        int height = (buffer[9] << 8) + buffer[10];
        [imageInfo setObject:@(width) forKey:@"Width"];
        [imageInfo setObject:@(height) forKey:@"Height"];
        [imageInfo setObject:@(FileTypeJPEG) forKey:@"FileType"];
    }
    // 检查 PNG
    else if (buffer[0] == 0x89 && buffer[1] == 'P' && buffer[2] == 'N' && buffer[3] == 'G') {
        int width = (buffer[16] << 8) + buffer[17];
        int height = (buffer[18] << 8) + buffer[19];
        [imageInfo setObject:@(width) forKey:@"Width"];
        [imageInfo setObject:@(height) forKey:@"Height"];
        [imageInfo setObject:@(FileTypePNG) forKey:@"FileType"];
    }
    // 检查 GIF
    else if (buffer[0] == 'G' && buffer[1] == 'I' && buffer[2] == 'F') {
        int width = buffer[6] + (buffer[7] << 8);
        int height = buffer[8] + (buffer[9] << 8);
        [imageInfo setObject:@(width) forKey:@"Width"];
        [imageInfo setObject:@(height) forKey:@"Height"];
        [imageInfo setObject:@(FileTypeGIF) forKey:@"FileType"];
    }
    // 检查 BMP
    else if (buffer[0] == 'B' && buffer[1] == 'M') {
        // 读取 BMP 需要的额外字节
        uint8_t bmpBuffer[26];
        bytesRead = [inputStream read:bmpBuffer maxLength:26];
        if (bytesRead < 26) {
            if (error) {
                *error = [NSError errorWithDomain:@"ImageReadErrorDomain" code:ImageReadErrorFileTooShort userInfo:nil];
            }
            [inputStream close];
            return nil;
        }
        int width = bmpBuffer[18] + (bmpBuffer[19] << 8) + (bmpBuffer[20] << 16) + (bmpBuffer[21] << 24);
        int height = bmpBuffer[22] + (bmpBuffer[23] << 8) + (bmpBuffer[24] << 16) + (bmpBuffer[25] << 24);
        [imageInfo setObject:@(width) forKey:@"Width"];
        [imageInfo setObject:@(height) forKey:@"Height"];
        [imageInfo setObject:@(FileTypeBMP) forKey:@"FileType"];
    }
    else {
        if (error) {
            *error = [NSError errorWithDomain:@"ImageReadErrorDomain" code:ImageReadErrorUnsupportedFormat userInfo:nil];
        }
        [inputStream close];
        return nil;
    }
    
    [inputStream close];
    return imageInfo;
}

+ (UIImage *)thumbnailForImageAtPath:(NSString *)imagePath withMaxPixelSize:(CGFloat)maxPixelSize {
    // 创建图片来源
    NSURL *imageURL = [NSURL fileURLWithPath:imagePath];
    CGImageSourceRef imageSource = CGImageSourceCreateWithURL((CFURLRef)imageURL, NULL);
    
    if (imageSource == NULL) {
        NSLog(@"Failed to create image source for path: %@", imagePath);
        return nil;
    }
    
    // 定义缩略图选项
    NSDictionary *options = @{(NSString *)kCGImageSourceCreateThumbnailFromImageAlways: @YES,
                              (NSString *)kCGImageSourceThumbnailMaxPixelSize: @(maxPixelSize),
                              (NSString *)kCGImageSourceCreateThumbnailWithTransform: @YES};
    // 创建缩略图
    CGImageRef thumbnailImageRef = CGImageSourceCreateThumbnailAtIndex(imageSource, 0, (CFDictionaryRef)options);
    CFRelease(imageSource); // 释放图像源对象
    
    if (thumbnailImageRef == NULL) {
        NSLog(@"Failed to create thumbnail for path: %@", imagePath);
        return nil;
    }
    
    // 转换为UIImage
    UIImage *thumbnail = [UIImage imageWithCGImage:thumbnailImageRef];
    CGImageRelease(thumbnailImageRef); // 释放CGImage对象
    
    return thumbnail;
}

+ (UIImage *)cropImageAtPath:(NSString *)imagePath withRect:(CGRect)cropRect {
    return [self cropImagesAtPath:imagePath withRectValues:@[[NSValue valueWithCGRect:cropRect]]].firstObject;
}

+ (NSArray<UIImage *> *)cropImagesAtPath:(NSString *)imagePath withRectValues:(NSArray<NSValue *> *)cropRects {
    return [self processImagesAtPath:imagePath withRectValues:cropRects save:NO];
}

+ (NSArray<UIImage *> *)cropImagesAtPath:(NSString *)imagePath withRectStrings:(NSArray<NSString *> *)cropRectStrings {
    return [self processImagesAtPath:imagePath withRectStrings:cropRectStrings save:NO];
}

+ (NSString *)cropAndSaveImageAtPath:(NSString *)imagePath withRect:(CGRect)cropRect {
    return [self cropAndSaveImagesAtPath:imagePath withRectValues:@[[NSValue valueWithCGRect:cropRect]]].firstObject;
}

+ (NSArray<NSString *> *)cropAndSaveImagesAtPath:(NSString *)imagePath withRectValues:(NSArray<NSValue *> *)cropRects {
    return [self processImagesAtPath:imagePath withRectValues:cropRects save:YES];
}

+ (NSArray<NSString *> *)cropAndSaveImagesAtPath:(NSString *)imagePath withRectStrings:(NSArray<NSString *> *)cropRectStrings {
    return [self processImagesAtPath:imagePath withRectStrings:cropRectStrings save:YES];
}

+ (id)processImagesAtPath:(NSString *)imagePath withRectValues:(NSArray<NSValue *> *)cropRects save:(BOOL)save {
    
    CGFloat scale = [self imageScaleAtPath:imagePath];
    
    NSURL *imageURL = [NSURL fileURLWithPath:imagePath];
    CGImageSourceRef imageSource = CGImageSourceCreateWithURL((CFURLRef)imageURL, NULL);
    
    if (imageSource == NULL) {
        RBQLog3(@"Failed to create image source for path: %@", imagePath);
        return nil;
    }
    
    NSDictionary *properties = (NSDictionary *)CFBridgingRelease(CGImageSourceCopyPropertiesAtIndex(imageSource, 0, NULL));
    CGFloat imageWidth = [properties[(NSString *)kCGImagePropertyPixelWidth] floatValue];
    CGFloat imageHeight = [properties[(NSString *)kCGImagePropertyPixelHeight] floatValue];
    
    CGImageRef imageRef = CGImageSourceCreateImageAtIndex(imageSource, 0, NULL);
    CFRelease(imageSource);
    
    if (imageRef == NULL) {
        RBQLog3(@"Failed to create full image for path: %@", imagePath);
        return nil;
    }
    
    NSMutableArray *results = [NSMutableArray array];
    
    for (NSInteger i=0;i<cropRects.count;i++) {
        
        @autoreleasepool {
            
            NSValue *rectValue = cropRects[i];
            
            CGRect cropRect = [rectValue CGRectValue];
            CGRect scaledCropRect = CGRectMake(cropRect.origin.x * scale, cropRect.origin.y * scale, cropRect.size.width * scale, cropRect.size.height * scale);
            
            scaledCropRect = CGRectIntersection(scaledCropRect, CGRectMake(0, 0, imageWidth * scale, imageHeight * scale));
            
            CGImageRef croppedImageRef = CGImageCreateWithImageInRect(imageRef, scaledCropRect);
            
            if (croppedImageRef != NULL) {
                UIImage *croppedImage = [UIImage imageWithCGImage:croppedImageRef scale:scale orientation:UIImageOrientationUp];
                
                RBQLog3(@"【processImagesAtPath】i:%ld;scale:%f;imageSize:%@;cropRect:%@;croppedImageSize:%@; scaledCropRect:%@;",i,scale,NSStringFromCGSize(CGSizeMake(imageWidth, imageHeight)),NSStringFromCGRect(cropRect),NSStringFromCGSize(croppedImage.size),NSStringFromCGRect(scaledCropRect));
                
                // 由于裁切图片边界的限制，这里还需要检查图片的高度是否和目标高度一致，如果不一致，则生成该高度的图片
                if(croppedImage.size.height != cropRect.size.height){
                    RBQLog3(@"【processImagesAtPath】判定为竖向纸张");
                    croppedImage = [UIImage scaleToSize:croppedImage targetSize:cropRect.size alignment:ImageAlignmentTopCenter backgroundColor:UIColor.whiteColor];
                }else if(croppedImage.size.width != cropRect.size.width){
                    RBQLog3(@"【processImagesAtPath】判定为横向纸张");
                    croppedImage = [UIImage scaleToSize:croppedImage targetSize:cropRect.size alignment:ImageAlignmentMiddleLeft backgroundColor:UIColor.whiteColor];
                }
                if (save) {
                    NSString *croppedImagePath = [self saveImageToCache:croppedImage];
                    [results addObject:croppedImagePath];
                } else {
                    [results addObject:croppedImage];
                }
                CGImageRelease(croppedImageRef);
            } else {
                RBQLog3(@"Failed to crop image for rect: %@", NSStringFromCGRect(cropRect));
            }
            
        }
        
    }
    
    CGImageRelease(imageRef);
    
    return [results copy];
}

+ (NSArray *)processImagesAtPath:(NSString *)imagePath withRectStrings:(NSArray<NSString *> *)cropRectStrings save:(BOOL)save {
    NSMutableArray<NSValue *> *rectValues = [NSMutableArray arrayWithCapacity:cropRectStrings.count];
    for (NSString *rectString in cropRectStrings) {
        [rectValues addObject:[NSValue valueWithCGRect:CGRectFromString(rectString)]];
    }
    return [self processImagesAtPath:imagePath withRectValues:rectValues save:save];
}


@end

