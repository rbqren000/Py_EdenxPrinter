//
//  MultiRowImage.h
//  BelonPrinter
//
//  Created by rbq on 2021/7/5.
//  Copyright © 2021 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "RowImage.h"
#import "RowLayoutDirection.h"

NS_ASSUME_NONNULL_BEGIN

@interface MultiRowImage : NSObject

@property (nonatomic, strong) NSMutableArray<RowImage *> *rowImages;
//thumb缩略图路径
@property (nonatomic, strong) NSString *thumbPath;
/**切图排布方向**/
@property (nonatomic, assign) RowLayoutDirection rowLayoutDirection;
/**rowImages中的图片是否为一张图片裁切而来，如果为连续一张图裁切而来，
 则会进行裁切图衔接位置处理，以尽可能的减少计算过程中抖动算法引起的缝隙问题
 **/
@property (nonatomic, assign) BOOL isCroppedImageSet;

// 禁用 init 方法
- (instancetype)init NS_UNAVAILABLE;

- (instancetype)initMultiRowImage:(NSMutableArray<RowImage *> *)rowImages;
- (instancetype)initMultiRowImage:(NSMutableArray<RowImage *> *)rowImages thumbPath:(nullable NSString *)thumbPath;
- (instancetype)initMultiRowImage:(NSMutableArray<RowImage *> *)rowImages rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection;
- (instancetype)initMultiRowImage:(NSMutableArray<RowImage *> *)rowImages isCroppedImageSet:(BOOL)isCroppedImageSet;
- (instancetype)initMultiRowImage:(NSMutableArray<RowImage *> *)rowImages rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection isCroppedImageSet:(BOOL)isCroppedImageSet;
- (instancetype)initMultiRowImage:(NSMutableArray<RowImage *> *)rowImages thumbPath:(nullable NSString *)thumbPath rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection isCroppedImageSet:(BOOL)isCroppedImageSet;

@end

NS_ASSUME_NONNULL_END
