//
//  MagnifierView.h 放大镜
//  BelonPrinter
//
//  Created by rbq on 2021/5/26.
//  Copyright © 2021 rbq. All rights reserved.
//
#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

static const CGFloat MagnifierSize = 100.0f;

@interface MagnifierView : UIView

- (void)updateRenderPoint:(CGPoint)renderPoint renderView:(UIView *)renderView;

@end

NS_ASSUME_NONNULL_END
