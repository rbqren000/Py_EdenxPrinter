//
//  CorrectCropView.m
//  BelonPrinter
//
//  Created by rbq on 2021/5/26.
//  Copyright © 2021 rbq. All rights reserved.
//

#import "CorrectCropMask.h"
#import "UIColor+Color.h"

#define DotViewSize 20

@interface CorrectCropMask () <UIGestureRecognizerDelegate>

@property (nonatomic, weak) DotView *activeDotView;//手指选中的顶点

@property (nonatomic, copy) NSArray <UIView*> *dotViews;

@end

@implementation CorrectCropMask

@synthesize lineSuccessColor = _lineSuccessColor;
@synthesize cornerFillColor = _cornerFillColor;

- (instancetype)initWithCoder:(NSCoder *)coder
{
    self = [super initWithCoder:coder];
    if (self) {
        [self setUp];
    }
    return self;
}

- (instancetype)initWithFrame:(CGRect)frame
{
    self = [super initWithFrame:frame];
    if (self) {
        [self setUp];
    }
    return self;
}

-(void)setUp{
    
    self.clipsToBounds = NO;
    self.userInteractionEnabled = YES;
    self.contentMode = UIViewContentModeRedraw;
    self.backgroundColor = [[UIColor blackColor] colorWithAlphaComponent:0.5];
    
    UIPanGestureRecognizer *gesturePan = [[UIPanGestureRecognizer alloc] initWithTarget:self action:@selector(panGestureAction:)];
    gesturePan.maximumNumberOfTouches = 1;
    gesturePan.delegate = self;
    [self addGestureRecognizer:gesturePan];
    
    UITapGestureRecognizer *tap = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(tapAction:)];
    [self addGestureRecognizer: tap];
    
    for (UIView *cornerView in self.dotViews) {
        [self addSubview:cornerView];
    }
}

- (void)drawRect:(CGRect)rect {
    
    CGContextRef context = UIGraphicsGetCurrentContext();
    if (context) {
        CGContextSetFillColorWithColor(context, [UIColor clearColor].CGColor);
        self.isQuadEffective = ([self checkForNeighbouringPoints] >= 0);
        if (self.isQuadEffective) {
            CGContextSetStrokeColorWithColor(context, self.lineSuccessColor.CGColor);
        } else {
            CGContextSetStrokeColorWithColor(context, self.lineFailureColor.CGColor);
        }
        
        CGContextSetLineJoin(context, kCGLineJoinRound);
        CGContextSetLineWidth(context, 2.0f);
        
        CGRect boundingRect = CGContextGetClipBoundingBox(context);
        CGContextAddRect(context, boundingRect);
        CGContextFillRect(context, boundingRect);
        
        CGMutablePathRef pathRef = CGPathCreateMutable();
        
        CGPathMoveToPoint(pathRef, NULL, self.bottomLeftView.center.x, self.bottomLeftView.center.y);
        CGPathAddLineToPoint(pathRef, NULL, self.bottomRightView.center.x, self.bottomRightView.center.y);
        CGPathAddLineToPoint(pathRef, NULL, self.topRightView.center.x, self.topRightView.center.y);
        CGPathAddLineToPoint(pathRef, NULL, self.topLeftView.center.x, self.topLeftView.center.y);
        
        CGPathCloseSubpath(pathRef);
        CGContextAddPath(context, pathRef);
        CGContextStrokePath(context);
        
        CGContextSetBlendMode(context, kCGBlendModeClear);
        
        CGContextAddPath(context, pathRef);
        CGContextFillPath(context);
        
        CGContextSetBlendMode(context, kCGBlendModeNormal);
        
        CGPathRelease(pathRef);
    }
}

- (double)checkForNeighbouringPoints {
    CGPoint p1;
    CGPoint p2;
    CGPoint p3;
    for (DotView *cornerView in self.dotViews) {
        switch (cornerView.location) {
            case DotLocationTopLeft:{
                p1 = self.topLeftView.point;
                p2 = self.topRightView.point;
                p3 = self.bottomLeftView.point;
                break;
            }
            case DotLocationTopRight:{
                p1 = self.topRightView.point;
                p2 = self.bottomRightView.point;
                p3 = self.topLeftView.point;
                break;
            }
            case DotLocationBottomRight:{
                p1 = self.bottomRightView.point;
                p2 = self.bottomLeftView.point;
                p3 = self.topRightView.point;
                break;
            }
            case DotLocationBottomLeft:{
                p1 = self.bottomLeftView.point;
                p2 = self.topLeftView.point;
                p3 = self.bottomRightView.point;
                break;
            }
            default:{
                break;
            }
        }
        
        CGPoint ab = CGPointMake (p2.x - p1.x, p2.y - p1.y);
        CGPoint cb = CGPointMake( p2.x - p3.x, p2.y - p3.y);
        float dot = (ab.x * cb.x + ab.y * cb.y); // dot product
        float cross = (ab.x * cb.y - ab.y * cb.x); // cross product
        float alpha = atan2(cross, dot);
        
        if ((-1*(float) floor(alpha * 180. / 3.14 + 0.5)) < 0) {
            return -1*(float) floor(alpha * 180. / 3.14 + 0.5);
        }
    }
    return 0;
}

#pragma mark - UIGestureRecognizerDelegate

- (BOOL)gestureRecognizer:(UIGestureRecognizer *)gestureRecognizer shouldReceiveTouch:(UITouch *)touch {
    CGPoint location = [touch locationInView:self];
    for (DotView *cornerView in self.dotViews) {
        CGPoint covertPoint = [self convertPoint:location toView:cornerView];
        CGRect bounds = cornerView.bounds;
        //由于手动调节时，比较难以触摸到DotView的范围内，这里将其bounds扩大化
        CGRect extendBounds = CGRectMake(bounds.origin.x-30, bounds.origin.y-30, bounds.size.width+60, bounds.size.height+60);
        if (CGRectContainsPoint(extendBounds, covertPoint)) {
            self.activeDotView = cornerView;
            self.activeDotView.hidden = YES;
            break;
        }
    }
    return YES;
}


- (void)tapAction:(id)sender{
    
    CGPoint location = [sender locationInView:self];
    for (DotView *dotView in self.dotViews) {
        CGPoint covertPoint = [self convertPoint:location toView:dotView];
        CGRect bounds = dotView.bounds;
        //由于手动调节时，比较难以触摸到DotView的范围内，这里将其bounds扩大化
        CGRect extendBounds = CGRectMake(bounds.origin.x-30, bounds.origin.y-30, bounds.size.width+60, bounds.size.height+60);
        if (CGRectContainsPoint(extendBounds, covertPoint)) {
            self.activeDotView.hidden = NO;
            self.activeDotView = nil;
            break;
        }
    }
}

- (void)panGestureAction:(UIPanGestureRecognizer *)sender {
    CGPoint point = [sender locationInView:self];
    if (sender.state == UIGestureRecognizerStateEnded || sender.state == UIGestureRecognizerStateCancelled) {
        self.activeDotView.hidden = NO;
        self.activeDotView = nil;
    }

    CGFloat newX = point.x;
    CGFloat newY = point.y;

    if (newX < self.bounds.origin.x) {
        newX = self.bounds.origin.x;
    } else if (newX > self.frame.size.width) {
        newX = self.frame.size.width;
    }
    if (newY < self.bounds.origin.y) {
        newY = self.bounds.origin.y;
    } else if (newY > self.frame.size.height) {
        newY = self.frame.size.height;
    }
    point = CGPointMake(newX, newY);
    self.activeDotView.point = point;
    [self setNeedsDisplay];
    if ([self.delegate respondsToSelector:@selector(cropOverlayMask:didMoveToPoint:location:state:)]) {
        [self.delegate cropOverlayMask:self didMoveToPoint:point location:self.activeDotView.location state:sender.state];
    }
}

#pragma mark - Public

- (void)updatePointValueByDotLocation:(CGPoint)point location:(DotLocation)location {
    switch (location) {
        case DotLocationTopLeft: {
            self.topLeftView.point = point;
            [self setNeedsDisplay];
            break;
        }
        case DotLocationTopRight: {
            self.topRightView.point = point;
            [self setNeedsDisplay];
            break;
        }
        case DotLocationBottomLeft: {
            self.bottomLeftView.point = point;
            [self setNeedsDisplay];
            break;
        }
        case DotLocationBottomRight: {
            self.bottomRightView.point = point;
            [self setNeedsDisplay];
            break;
        }
        default: {
            break;
        }
    }
}

- (CGPoint)pointValueWithDotLocation:(DotLocation)location {
    switch (location) {
        case DotLocationTopLeft: {
            return self.topLeftView.point;
        }
        case DotLocationTopRight: {
            return self.topRightView.point;
        }
        case DotLocationBottomLeft: {
            return self.bottomLeftView.point;
        }
        case DotLocationBottomRight: {
            return self.bottomRightView.point;
        }
        default: {
            return self.center;;
        }
    }
}

#pragma mark - Setters

- (void)setlineSuccessColor:(UIColor *)lineSuccessColor {
    _lineSuccessColor = lineSuccessColor;
    self.topLeftView.layer.borderColor = lineSuccessColor.CGColor;
    self.topRightView.layer.borderColor = lineSuccessColor.CGColor;
    self.bottomLeftView.layer.borderColor = lineSuccessColor.CGColor;
    self.bottomRightView.layer.borderColor = lineSuccessColor.CGColor;
    [self setNeedsDisplay];
}

- (void)setCornerFillColor:(UIColor *)cornerFillColor {
    _cornerFillColor = cornerFillColor;
    self.topLeftView.layer.backgroundColor = cornerFillColor.CGColor;
    self.topRightView.layer.backgroundColor = cornerFillColor.CGColor;
    self.bottomLeftView.layer.backgroundColor = cornerFillColor.CGColor;
    self.bottomRightView.layer.backgroundColor = cornerFillColor.CGColor;
    [self setNeedsDisplay];
}

#pragma mark - Getters

- (DotView *)topLeftView {
    if (!_topLeftView) {
        _topLeftView = [self cornerView];
        _topLeftView.location = DotLocationTopLeft;
    }
    return _topLeftView;
}

- (DotView *)topRightView {
    if (!_topRightView) {
        _topRightView = [self cornerView];
        _topRightView.location = DotLocationTopRight;
    }
    return _topRightView;
}

- (DotView *)bottomLeftView {
    if (!_bottomLeftView) {
        _bottomLeftView = [self cornerView];
        _bottomLeftView.location = DotLocationBottomLeft;
    }
    return _bottomLeftView;
}

- (DotView *)bottomRightView {
    if (!_bottomRightView) {
        _bottomRightView = [self cornerView];
        _bottomRightView.location = DotLocationBottomRight;
    }
    return _bottomRightView;
}

- (DotView *)cornerView {
    DotView *cornerView = [[DotView alloc] init];
    cornerView.frame = CGRectMake(0, 0, DotViewSize, DotViewSize);
    cornerView.layer.backgroundColor = self.cornerFillColor.CGColor;
    cornerView.layer.cornerRadius = DotViewSize/2;
    cornerView.layer.borderWidth = 1.0;
    cornerView.layer.borderColor = self.lineSuccessColor.CGColor;
    cornerView.layer.masksToBounds = YES;
    return cornerView;
}

- (NSArray<UIView *> *)dotViews {
    if (!_dotViews) {
        _dotViews = @[self.topLeftView, self.topRightView, self.bottomRightView, self.bottomLeftView];
    }
    return _dotViews;
}

- (UIColor *)cornerFillColor {
    if (!_cornerFillColor) {
        _cornerFillColor = [UIColor whiteColor];
    }
    return _cornerFillColor;
}

- (UIColor *)lineSuccessColor {
    if (!_lineSuccessColor) {
        _lineSuccessColor = [UIColor colorWithHexString:@"#2EA7E0"];
    }
    return _lineSuccessColor;
}

- (UIColor *)lineFailureColor {
    if (!_lineFailureColor) {
        _lineFailureColor = [UIColor redColor];
    }
    return _lineFailureColor;
}

@end
