//
//  DotView.h  点
//  BelonPrinter
//
//  Created by rbq on 2021/5/26.
//  Copyright © 2021 rbq. All rights reserved.
//
//
#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

typedef NS_ENUM(NSUInteger, DotLocation) {
    DotLocationTopLeft       = 1,
    DotLocationTopRight      = 2,
    DotLocationBottomLeft    = 3,
    DotLocationBottomRight   = 4,
};

@interface DotView : UIView

@property (nonatomic, assign) DotLocation location;
@property (nonatomic, assign) CGPoint point;

@end

NS_ASSUME_NONNULL_END
