//
//  MultiRowImageDataFactory.h
//  BelonPrinter
//
//  Created by rbq on 2021/7/5.
//  Copyright © 2021 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "MultiRowData.h"

NS_ASSUME_NONNULL_BEGIN

static const int PrintHeadWidth = 552;
static const NSString *DataSuffix = @".data";

@interface MultiRowDataFactory : NSObject

+(void)bitmap2MultiRowData:(MultiRowImage *)multiRowImage threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress flipHorizontally:(BOOL)flipHorizontally isSimulation:(BOOL)isSimulation thumbToSimulation:(BOOL)thumbToSimulation onStart:(void (^)(void))onStart onComplete:(void (^)(MultiRowData *multiRowData))onComplete error:(void (^)(void))onError;
+(MultiRowData *)bitmap2MultiRowData:(MultiRowImage *)multiRowImage threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress flipHorizontally:(BOOL)flipHorizontally isSimulation:(BOOL)isSimulation thumbToSimulation:(BOOL)thumbToSimulation;

+(void)mergeBitmap2MultiRowData:(MultiRowImage *)multiRowImage threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress flipHorizontally:(BOOL)flipHorizontally isSimulation:(BOOL)isSimulation thumbToSimulation:(BOOL)thumbToSimulation onStart:(void (^)(void))onStart onComplete:(void (^)(MultiRowData *multiRowData))onComplete error:(void (^)(void))onError;
+(MultiRowData *)mergeBitmap2MultiRowData:(MultiRowImage *)multiRowImage threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress flipHorizontally:(BOOL)flipHorizontally isSimulation:(BOOL)isSimulation thumbToSimulation:(BOOL)thumbToSimulation;

+(void)betterMergeBitmap2MultiRowData:(MultiRowImage *)multiRowImage threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress flipHorizontally:(BOOL)flipHorizontally isSimulation:(BOOL)isSimulation thumbToSimulation:(BOOL)thumbToSimulation onStart:(void (^)(void))onStart onComplete:(void (^)(MultiRowData *multiRowData))onComplete error:(void (^)(void))onError;
+(MultiRowData *)betterMergeBitmap2MultiRowData:(MultiRowImage *)multiRowImage threshold:(int)threshold clearBackground:(BOOL)clearBackground dithering:(BOOL)dithering compress:(BOOL)compress flipHorizontally:(BOOL)flipHorizontally isSimulation:(BOOL)isSimulation thumbToSimulation:(BOOL)thumbToSimulation;

@end

NS_ASSUME_NONNULL_END
