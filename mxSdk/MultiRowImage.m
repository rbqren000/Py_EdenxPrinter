//
//  MultiRowImage.m
//  BelonPrinter
//
//  Created by rbq on 2021/7/5.
//  Copyright © 2021 rbq. All rights reserved.
//

#import "MultiRowImage.h"

@implementation MultiRowImage

- (instancetype)initMultiRowImage:(NSMutableArray<RowImage *> *)rowImages
{
    return [self initMultiRowImage:rowImages thumbPath:nil rowLayoutDirection:RowLayoutDirectionVert isCroppedImageSet:NO];
}

- (instancetype)initMultiRowImage:(NSMutableArray<RowImage *> *)rowImages thumbPath:(nullable NSString *)thumbPath
{
    return [self initMultiRowImage:rowImages thumbPath:thumbPath rowLayoutDirection:RowLayoutDirectionVert isCroppedImageSet:NO];
}

- (instancetype)initMultiRowImage:(NSMutableArray<RowImage *> *)rowImages rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection
{
    return [self initMultiRowImage:rowImages thumbPath:nil rowLayoutDirection:rowLayoutDirection isCroppedImageSet:NO];
}

- (instancetype)initMultiRowImage:(NSMutableArray<RowImage *> *)rowImages isCroppedImageSet:(BOOL)isCroppedImageSet
{
    return [self initMultiRowImage:rowImages thumbPath:nil rowLayoutDirection:RowLayoutDirectionVert isCroppedImageSet:isCroppedImageSet];
}

- (instancetype)initMultiRowImage:(NSMutableArray<RowImage *> *)rowImages rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection isCroppedImageSet:(BOOL)isCroppedImageSet
{
    return [self initMultiRowImage:rowImages thumbPath:nil rowLayoutDirection:rowLayoutDirection isCroppedImageSet:isCroppedImageSet];
}

- (instancetype)initMultiRowImage:(NSMutableArray<RowImage *> *)rowImages thumbPath:(nullable NSString *)thumbPath rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection isCroppedImageSet:(BOOL)isCroppedImageSet
{
    self = [super init];
    if (self) {
        _rowImages = rowImages;
        _thumbPath = thumbPath;
        _rowLayoutDirection = rowLayoutDirection;
        _isCroppedImageSet = isCroppedImageSet;
    }
    return self;
}

@end
