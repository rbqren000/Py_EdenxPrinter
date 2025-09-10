//
//  CorrectCropView.h  剪切View
//  BelonPrinter
//
//  Created by rbq on 2021/5/26.
//  Copyright © 2021 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "DotView.h"

NS_ASSUME_NONNULL_BEGIN

@class CorrectCropMask;

@protocol CropOverlayMaskDelegate <NSObject>

@optional
- (void)cropOverlayMask:(CorrectCropMask *)cropOverlayMask didMoveToPoint:(CGPoint)point location:(DotLocation)location state:(UIGestureRecognizerState)state;

@end

@interface CorrectCropMask : UIView

@property (nonatomic, weak) id<CropOverlayMaskDelegate> delegate;

@property (nonatomic, strong, readwrite) DotView *topLeftView;
@property (nonatomic, strong, readwrite) DotView *topRightView;
@property (nonatomic, strong, readwrite) DotView *bottomLeftView;
@property (nonatomic, strong, readwrite) DotView *bottomRightView;

@property (nonatomic, strong) UIColor *cornerFillColor;

@property (nonatomic, strong) UIColor *lineSuccessColor;

@property (nonatomic, strong) UIColor *lineFailureColor;

// 有效矩形区域
@property (nonatomic, assign) BOOL isQuadEffective;

- (void)updatePointValueByDotLocation:(CGPoint)point location:(DotLocation)location;

- (CGPoint)pointValueWithDotLocation:(DotLocation)location;

@end

NS_ASSUME_NONNULL_END
