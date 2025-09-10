//
//  RBQFileManager.h
//  BelonPrinter
//
//  Created by rbq on 2020/9/23.
//  Copyright © 2020 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "RBQFileManager.h"
#import "StickerGroupsTemplate.h"
#import "BaseStickerView.h"
#import "TextStickerView.h"
#import "AutoHeightTextStickerView.h"
#import "ImageStickerView.h"
#import "BarCodeStickerView.h"
#import "QRCodeStickerView.h"
#import "OriginalImageStickerView.h"
#import "BaseStickerView.h"
#import "StickerGroupView.h"
#import "Docs.h"

NS_ASSUME_NONNULL_BEGIN

#define TemplateTypeStickerGroup 0
#define TemplateTypeDocument 1

// 使用枚举定义可能的文件类型
typedef NS_ENUM(NSInteger, FileType) {
    FileTypeUnknown,
    FileTypeJPEG,
    FileTypePNG,
    FileTypePDF,
    FileTypeGIF,
    FileTypeBMP,
    FileTypeTIFF,
    FileTypeZIP,
    FileTypeRAR,
    FileTypeMP3,
    FileTypeMP4,
    FileTypeDOCX,
    FileTypeXLSX,
    FileTypeDOC,
    FileTypeXLS,
    FileTypePPT
};

typedef NS_ENUM(NSInteger, ImageReadError) {
    ImageReadErrorCannotOpenFile,
    ImageReadErrorFileTooShort,
    ImageReadErrorUnsupportedFormat
};

@interface MxFileManager : NSObject

/**存储图片到缓存目录，会主动清理*/
+(NSString *)saveImageToCache:(UIImage *)image;
+(void)asynSaveImageToCache:(UIImage *)image completion:(void (^)(NSString *filePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

/*** 获取本地图片*/
+(UIImage *)imageFromFilePath:(NSString *)filePath;
+(void)asynImageFromFilePath:(NSString *)filePath completion:(void (^)(UIImage *image))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

/*** 获取本地图片，是否镜像*/
+(UIImage *)imageFromFilePath:(NSString *)filePath flipHorizontally:(BOOL)flipHorizontally;
+(void)asynImageFromFilePath:(NSString *)filePath flipHorizontally:(BOOL)flipHorizontally completion:(void (^)(UIImage *image))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

+(NSData *)imageDataFromFilePath:(NSString *)filePath;
+(void)asynImageDataFromFilePath:(NSString *)filePath completion:(void (^)(NSData *imageData))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

/**根据文件存储的路径名称，获取图片的倍图倍率**/
+(int)imageScaleAtPath:(NSString *)filePath;

/**将json写入目录*/
+(NSString *)saveJsonToJsonFile:(NSString *)json;
+(void)asynSaveJsonToJsonFile:(NSString *)json completion:(void (^)(NSString *filePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

/**读取本地json*/
+(NSString *)jsonFromJsonFile:(NSString *)filePath;
+(void)asynJsonFromJsonFile:(NSString *)filePath completion:(void (^)(NSString *json))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

/**用于存储打印数据*/
+(NSString *)saveDataToDataCacheFile:(NSData *)data;
+(void)asynSaveDataToDataCacheFile:(NSData *)data completion:(void (^)(NSString *filePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

/**根据路径获取打印数据*/
+(NSData *)dataFromPath:(NSString *)filePath;
+(void)asynDataFromPath:(NSString *)filePath completion:(void (^)(NSData *data))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

+(NSString *)baseFontSavedFilePath;
+ (NSMutableArray<CustomTypeface *> *)loadCustomTypefaceFromFontSavedFilePath;

+(NSString *)baseDocsSavedFilePath;
+(NSMutableArray<Docs *> *)loadDocsFromDocsSavedFile;

+(NSString *)baseDocsCacheFilePath;

+(NSString *)savePdfToDocsCacheFile:(NSMutableData *)pdfData;
+(void)asynSavePdfToDocsCacheFile:(NSMutableData *)pdfData completion:(void (^)(NSString *filePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

+(NSString *)savePdfToDocsCacheFile:(NSMutableData *)pdfData pdfFileName:(NSString *)pdfFileName;
+(void)asynSavePdfToDocsCacheFile:(NSMutableData *)pdfData pdfFileName:(NSString *)pdfFileName completion:(void (^)(NSString *filePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

+(NSString *)saveImageToDocsFilePath:(UIImage *)image;
+(void)saveImageToDocsFilePath:(UIImage *)image completion:(void (^)(NSString *filePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

+(NSString *)saveImageToDocsFilePath:(UIImage *)image imageName:(NSString *)baseimageName;
+(void)asynSaveImageToDocsFilePath:(UIImage *)image imageName:(NSString *)baseimageName completion:(void (^)(NSString *filePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

/**带Mx的方法为存储到本地模版当中的相关方法，其中key会被创建为一个文件夹，则保存的图片、pdf等都保存在该文件夹下，返回则返回保存的图片或者pdf的文件名**/
/**根据key返回zip模版保存的文件夹的绝对路径**/
+(NSString *)absoluteMxCacheFilePath:(NSString *)mxKey;
+(void)asynAbsoluteMxCacheFilePath:(NSString *)mxKey completion:(void (^)(NSString *mxCacheFilePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

/**根据模版的mxKey创建zip路径**/
+(NSString *)createZipAbsoluteMxCacheFilePath:(NSString *)mxKey;
+(void)asynCreateZipAbsoluteMxCacheFilePath:(NSString *)mxKey completion:(void (^)(NSString *mxCacheFilePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

/**创建一个mxKey的文件夹用于放解压文件**/
+(NSString *)createUnZipAbsoluteMxCacheFilePath:(NSString *)mxKey;
+(void)asynCreateUnZipAbsoluteMxCacheFilePath:(NSString *)mxKey completion:(void (^)(NSString *mxCacheFilePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock;
    
/**根据key返回zip模版中json文件的绝对路径**/
+(NSString *)mainJsonAbsoluteFilePath:(NSString *)mxKey;
+(void)asynmainJsonAbsoluteFilePath:(NSString *)mxKey completion:(void (^)(NSString *filePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

/**通过zip模版中json的文件名，返回zip模版中文件的绝对路径**/
+(NSString *)mainJsonInnerPathToAbsolutePath:(NSString *)mxKey fileName:(NSString *)fileName;
+(void)asynMainJsonInnerPathToAbsolutePath:(NSString *)mxKey fileName:(NSString *)fileName completion:(void (^)(NSString *filePath))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

+(NSString *)saveImageToMxCacheFile:(NSString *)mxKey image:(UIImage *)image;
+(void)asynSaveImageToMxCacheFile:(NSString *)mxKey image:(UIImage *)image completion:(void (^)(NSString *imageName))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

+(NSString *)savePDFToMxCacheFile:(NSString *)mxKey pdfFileName:(NSString *)pdfFileName pdfData:(NSMutableData *)pdfData;
+(NSString *)saveJsonToMxCacheFile:(NSString *)mxKey json:(NSString *)json;
+(NSString *)copyToMxCacheFile:(NSString *)mxKey filePath:(NSString *)filePath;
+(void)readMxFileFormMxKey:(NSString *)mxKey onComplete:(void (^)(StickerGroupsTemplate *_Nullable documentStickerGroupTemplate,StickerGroupTemplate  * _Nullable stickerGroupTemplate,NSString *version))onComplete error:(void (^)(void))onError;
+(void)readMxFileFormFilePath:(NSString *)mxFilePath onComplete:(void (^)(StickerGroupsTemplate *_Nullable documentStickerGroupTemplate,StickerGroupTemplate  * _Nullable stickerGroupTemplate))onComplete error:(void (^)(void))onError;
+(NSString *)createJsonByMxStickerGroupTemplate:(StickerGroupTemplate *)stickerGroupTemplate version:(NSString *)version;
+(NSString *)createJsonByMxDocumentStickerGroupTemplate:(StickerGroupsTemplate *)documentStickerGroupTemplate version:(NSString *)version;

+(StickerGroupsTemplate *)createMxDocumentStickerGroupTemplate:(NSString *)fileName
                             group:(StickerGroupsTemplate *)documentStickerGroupTemplate
                              flag:(int)flag
                           version:(NSString *)version
                             mxKey:(NSString *)mxKey;
+(void)asynCreateMxDocumentStickerGroupTemplate:(NSString *)fileName
                             group:(StickerGroupsTemplate *)documentStickerGroupTemplate
                              flag:(int)flag
                           version:(NSString *)version
                             mxKey:(NSString *)mxKey
                        completion:(void (^)(StickerGroupsTemplate *))completionBlock
                             erroe:(void (^)(NSError *error))erroeBlock;



+(StickerGroupTemplate *)createMxStickerGroupTemplate:(NSString *)fileName
                             group:(StickerGroupTemplate *)stickerGroupTemplate
                              flag:(int)flag
                           version:(NSString *)version
                             mxKey:(NSString *)mxKey;
+(void)asynCreateMxStickerGroupTemplate:(NSString *)fileName
                             group:(StickerGroupTemplate *)stickerGroupTemplate
                              flag:(int)flag
                           version:(NSString *)version
                             mxKey:(NSString *)mxKey
                        completion:(void (^)(StickerGroupTemplate *))completionBlock
                                  erroe:(void (^)(NSError *error))erroeBlock;

/**压缩文件**/
+(BOOL)zipFile:(NSString *)zipFilePath form:(NSString *)sourceFilePath;
+(void)asynZipFile:(NSString *)zipFilePath form:(NSString *)sourceFilePath completion:(void (^)(void))completionBlock erroe:(void (^)(NSError *error))erroeBlock;
/**解压文件**/
+(BOOL)unzipFile:(NSString *)zipFilePath to:(NSString *)desFilePath;
+(void)asynUnzipFile:(NSString *)zipFilePath to:(NSString *)desFilePath completion:(void (^)(void))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

/**拷贝文件*/
+(BOOL)copy:(NSString *)sourceFilePath to:(NSString *)desFilePath isDeleteSrc:(BOOL)isDeleteSrc;
+(void)asynCopy:(NSString *)sourceFilePath to:(NSString *)destFilePath isDeleteSrc:(BOOL)isDeleteSrc completion:(void (^)(void))completionBlock erroe:(void (^)(NSError *error))erroeBlock;

// ota
+(NSArray *)searchOtaFileArray;
+(void)asynSearchOtaFileArray:(void (^)(NSArray *otaFiles))completionBlock;

/*** 根据路径删除文件*/
+(BOOL)deleteFileWithPath:(NSString *)filePath;

+(void)clearAllImageInImageCacheFile;
+(void)clearAllJsonInJsonCacheFile;
+(void)clearAllDataInDataCacheFile;
+(void)clearAllFileInMxCacheFile;
+(void)clearAllFileInDocsCacheFile;
+(void)clearAllCacheFile;

+(NSString *)createStringByData;
+(NSString *)createStringByDataFromMsec;
+(NSString *)create42StringByLetterAndNumber;

//+ (BOOL)isWordOrPdfFileAtPath:(NSString *)filePath;
//+ (BOOL)isWordFileAtPath:(NSString *)filePath;
//+ (BOOL)isPDFFileAtPath:(NSString *)filePath;
//+ (NSString *)fileDisplayNameWithPath:(NSString *)filePath;
//+ (NSString *)fileNameWithPath:(NSString *)filePath;

+(FileType)fileTypeFromFilePathByFileHandle:(NSString *)filePath;
//+(FileType)fileTypeFromFilePathByInputStream:(NSString *)filePath;

+ (NSDictionary *)fileAttributesForItemAtPath:(NSString *)filePath error:(NSError **)error;
+ (NSDictionary *)imageAttributesForItemFilePath:(NSString *)filePath error:(NSError **)error;

+ (NSDictionary *)imageAttributesFromFilePathByFileHandle:(NSString *)filePath error:(NSError **)error;
+ (NSDictionary *)imageAttributesFromFilePathByInputStream:(NSString *)filePath error:(NSError **)error;

+ (UIImage *)thumbnailForImageAtPath:(NSString *)imagePath withMaxPixelSize:(CGFloat)maxPixelSize;

+ (UIImage *)cropImageAtPath:(NSString *)imagePath withRect:(CGRect)cropRect;
+ (NSArray<UIImage *> *)cropImagesAtPath:(NSString *)imagePath withRectValues:(NSArray<NSValue *> *)cropRects;
+ (NSArray<UIImage *> *)cropImagesAtPath:(NSString *)imagePath withRectStrings:(NSArray<NSString *> *)cropRectStrings;

+ (NSString *)cropAndSaveImageAtPath:(NSString *)imagePath withRect:(CGRect)cropRect;
+ (NSArray<NSString *> *)cropAndSaveImagesAtPath:(NSString *)imagePath withRectValues:(NSArray<NSValue *> *)cropRects;
+ (NSArray<NSString *> *)cropAndSaveImagesAtPath:(NSString *)imagePath withRectStrings:(NSArray<NSString *> *)cropRectStrings;

@end

NS_ASSUME_NONNULL_END
