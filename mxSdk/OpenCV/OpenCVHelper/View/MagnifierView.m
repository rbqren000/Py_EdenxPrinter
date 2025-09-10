//
//  MagnifierView.m
//  BelonPrinter
//
//  Created by rbq on 2021/5/26.
//  Copyright © 2021 rbq. All rights reserved.
//

#import "MagnifierView.h"

@interface MagnifierView ()

@property (nonatomic, assign) CGPoint renderPoint;
@property (nonatomic, strong) UIView *renderView;

@end

@implementation MagnifierView

- (instancetype)initWithCoder:(NSCoder *)coder
{
    self = [super initWithCoder:coder];
    if (self) {
        [self setUp];
    }
    return self;
}

- (instancetype)initWithFrame:(CGRect)frame {
    self = [super initWithFrame:frame];
    if (self) {
        [self setUp];
    }
    return self;
}

-(void)setUp{
    
    self.layer.masksToBounds = YES;
    self.layer.borderWidth = 2;
    self.layer.cornerRadius = MagnifierSize / 2;
    self.layer.borderColor = [[UIColor lightGrayColor] CGColor];
    self.layer.delegate = self;
    //保证和屏幕读取像素的比例一致
    self.layer.contentsScale = [[UIScreen mainScreen] scale];
}

- (void)drawLayer:(CALayer *)layer inContext:(CGContextRef)ctx {
    //提前位移半个长宽的坑
    CGContextTranslateCTM(ctx, self.frame.size.width * 0.5, self.frame.size.height * 0.5);
    CGContextScaleCTM(ctx, 1.5, 1.5);
    //再次位移后就可以把触摸点移至self.center的位置
    CGContextTranslateCTM(ctx, -1 * self.renderPoint.x, -1 * self.renderPoint.y);
    CGContextSetInterpolationQuality(ctx, kCGInterpolationHigh);
    [self.renderView.layer renderInContext:ctx];
}

- (void)updateRenderPoint:(CGPoint)renderPoint renderView:(UIView *)renderView {
    self.renderPoint = renderPoint;
    self.renderView = renderView;
    [self.layer setNeedsDisplay];
}

@end
