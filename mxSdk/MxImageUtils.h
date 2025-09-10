//
//  MxImageUtils.h
//  Inksi
//
//  Created by rbq on 2024/6/22.
//

#import <UIKit/UIKit.h>
#import "MultiRowData.h"

NS_ASSUME_NONNULL_BEGIN

@interface MxImageUtils : NSObject

+(void)bitmapToGray:(uint32_t *)pixels gray:(uint32_t *)gray width:(int)width height:(int)height;

+ (void)formatGrayToFloydDithering:(uint32_t *)gray width:(int)width height:(int)height threshold:(int)threshold;
+ (void)formatGrayToFloydDithering:(uint32_t *)gray width:(int)width height:(int)height threshold:(int)threshold initialErrors:(uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;

+ (void)formatGrayToAtkinsonDithering:(uint32_t *)gray width:(int)width height:(int)height threshold:(int)threshold;
+ (void)formatGrayToBurkesDithering:(uint32_t *)gray width:(int)width height:(int)height threshold:(int)threshold;

+(void)grayToBinary:(uint32_t *)gray binary:(uint32_t *)binary width:(int)width height:(int)height threshold:(int)threshold;

//+(NSData *)formatBinary69ToData72:(uint32_t *)pixels width:(int)width height:(int)height topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance;
+(void)formatBinary69ToData72ByCol:(uint32_t *)binary d72:(uint8_t *)d72 width:(int)width height:(int)height;
+(NSData *)formatBinary69ToData72ByCol:(uint32_t *)binary width:(int)width height:(int)height;

+(void)formatBinary69ToData72ByRow:(uint32_t *)binary d72:(uint8_t *)d72 width:(int)width height:(int)height;
+(NSData *)formatBinary69ToData72ByRow:(uint32_t *)binary width:(int)width height:(int)height;

/*
+(RowData *)createRowData:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;
+(RowData *)createRowData:(nonnull uint32_t *)pixels width:(int)width height:(int)height threshold:(int)threshold dithering:(BOOL)dithering compress:(BOOL)compress initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;
*/

+(void)imageSimulationWithSave:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors onStart:(void (^)(void))onStart onComplete:(void (^)(NSString *simulationPath))onComplete error:(void (^)(void))onError;
+(NSString *)imageSimulationWithSave:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;
+(void)imageSimulationWithSave:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors onStart:(void (^)(void))onStart onComplete:(void (^)(NSString *simulationPath))onComplete error:(void (^)(void))onError;
+(NSString *)imageSimulationWithSave:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;
+(NSString *)imageSimulationWithSave:(uint32_t *)pixels width:(CGFloat)width height:(CGFloat)height threshold:(int)threshold dithering:(BOOL)dithering compress:(BOOL)compress  rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;
+(void)imageSimulation:(UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors onStart:(void (^)(void))onStart onComplete:(void (^)(UIImage *simulationImage))onComplete error:(void (^)(void))onError;
+(UIImage *)imageSimulation:(UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;
+(void)imageSimulation:(UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors onStart:(void (^)(void))onStart onComplete:(void (^)(UIImage *simulationImage))onComplete error:(void (^)(void))onError;
+(UIImage *)imageSimulation:(UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;
+(UIImage *)imageSimulation:(uint32_t *)pixels width:(CGFloat)width height:(CGFloat)height threshold:(int)threshold dithering:(BOOL)dithering compress:(BOOL)compress rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;

+(NSString *)imageSimulationByBinarySave:(uint32_t *)binary width:(CGFloat)width height:(CGFloat)height compress:(BOOL)compress rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection;
+(UIImage *)imageSimulationByBinary:(uint32_t *)binary width:(CGFloat)width height:(CGFloat)height compress:(BOOL)compress rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection;

+(void)mergeBitmapToGrayFloydDitheringBinary:(nonnull uint32_t *)pixels binary:(nonnull uint32_t *)binary width:(int)width height:(int)height threshold:(int)threshold dithering:(BOOL)dithering compress:(BOOL)compress initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;
/*
+(RowData *)mergeCreateRowData:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;
+(RowData *)mergeCreateRowData:(nonnull uint32_t *)pixels width:(int)width height:(int)height threshold:(int)threshold dithering:(BOOL)dithering compress:(BOOL)compress initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;
*/
+(void)mergeImageSimulationWithSave:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors onStart:(void (^)(void))onStart onComplete:(void (^)(NSString *simulationPath))onComplete error:(void (^)(void))onError;
+(NSString *)mergeImageSimulationWithSave:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;
+(void)mergeImageSimulationWithSave:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors onStart:(void (^)(void))onStart onComplete:(void (^)(NSString *simulationPath))onComplete error:(void (^)(void))onError;
+(NSString *)mergeImageSimulationWithSave:(nonnull UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;
+(NSString *)mergeImageSimulationWithSave:(uint32_t *)pixels width:(CGFloat)width height:(CGFloat)height threshold:(int)threshold dithering:(BOOL)dithering compress:(BOOL)compress  rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;
+(void)mergeImageSimulation:(UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors onStart:(void (^)(void))onStart onComplete:(void (^)(UIImage *simulationImage))onComplete error:(void (^)(void))onError;
+(UIImage *)mergeImageSimulation:(UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;
+(void)mergeImageSimulation:(UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors onStart:(void (^)(void))onStart onComplete:(void (^)(UIImage *simulationImage))onComplete error:(void (^)(void))onError;
+(UIImage *)mergeImageSimulation:(UIImage *)image threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance isZoomTo552:(BOOL)isZoomTo552 rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;
+(UIImage *)mergeImageSimulation:(uint32_t *)pixels width:(CGFloat)width height:(CGFloat)height threshold:(int)threshold dithering:(BOOL)dithering compress:(BOOL)compress rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;


+(void)betterMergeBitmapToData72:(nonnull uint32_t *)pixels binary:(nonnull uint32_t *)binary d72:(nonnull uint8_t *)d72 width:(int)width height:(int)height threshold:(int)threshold dithering:(BOOL)dithering compress:(BOOL)compress initialErrors:(nullable uint32_t *)initialErrors lastRowErrors:(uint32_t *_Nullable*_Nullable)lastRowErrors;

+ (UIImage *)rotatedImageWithGraphicsByRadians:(UIImage *)image radians:(CGFloat)radians;

@end

NS_ASSUME_NONNULL_END
