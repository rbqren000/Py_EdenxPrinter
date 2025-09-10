//
//  SingleRowImage.m
//  BelonPrinter
//
//  Created by rbq on 2021/7/5.
//  Copyright © 2021 rbq. All rights reserved.
//

#import "RowImage.h"

@implementation RowImage

- (instancetype)initRowImage:(NSString *)imagePath
{
    self = [super init];
    if (self) {
        _imagePath = imagePath;
        _topBeyondDistance = 0;
        _bottomBeyondDistance = 0;
    }
    return self;
}

- (instancetype)initRowImage:(NSString *)imagePath topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance
{
    self = [super init];
    if (self) {
        _imagePath = imagePath;
        _topBeyondDistance = topBeyondDistance;
        _bottomBeyondDistance = bottomBeyondDistance;
    }
    return self;
}

@end
