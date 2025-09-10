//
//  CropOverlayView.m
//  OpenCVDemo
//
//  Created by rbq on 2021/5/27.
//  Copyright © 2021 lihuaguang. All rights reserved.
//

#import "CorrectCropView.h"
#import "UIImageView+SHMContentRect.h"
#import "Scanner.h"
#import "Cropper.h"
#import "CorrectCropMask.h"
#import "MagnifierView.h"
#import "DotView.h"
#import "CropperProcessor.h"
#import "RBQLog.h"

static CGFloat kWDOpenCVEditingImageMargin = 30.0;

@interface CorrectCropView()<CropOverlayMaskDelegate>


@property (nonatomic, strong) UIImageView *imageView;//图片
@property (nonatomic, strong) CorrectCropMask *cropOverlayMask;//图片
@property (strong, nonatomic) MagnifierView *magnifierView;//放大镜

@end

@implementation CorrectCropView

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
    
    _imageMargin = kWDOpenCVEditingImageMargin;
    
    self.imageView = [[UIImageView alloc] init];
    self.imageView.contentMode = UIViewContentModeScaleAspectFit;
    [self addSubview:_imageView];
    
    self.cropOverlayMask = [[CorrectCropMask alloc] init];
    [self addSubview:_cropOverlayMask];
    self.cropOverlayMask.delegate = self;
    
    self.magnifierView = [[MagnifierView alloc] initWithFrame:CGRectMake(0, 0, MagnifierSize, MagnifierSize)];
    self.magnifierView.backgroundColor = [UIColor blueColor];
    [self addSubview:_magnifierView];
    self.magnifierView.hidden = YES;
    
}

- (void)layoutSubviews{
    [super layoutSubviews];
    
    CGRect imageFrame = CGRectZero;
    imageFrame.origin.x = _imageMargin;
    imageFrame.origin.y = _imageMargin;
    imageFrame.size.width = CGRectGetWidth(self.frame) - _imageMargin * 2;
    imageFrame.size.height = CGRectGetHeight(self.frame) - imageFrame.origin.y - _imageMargin;
    
    self.imageView.frame = imageFrame;
    
    if (_originImage) {
        
        CGRect imageFrame = self.imageView.frame;
        CGRect cropFrame = [self.imageView shm_contentFrame];
        cropFrame.origin.x += imageFrame.origin.x;
        cropFrame.origin.y += imageFrame.origin.y;
        self.cropOverlayMask.frame = cropFrame;
    }
}

- (void)setOriginImage:(UIImage *)originImage{
    
    if (!originImage) {
        return;
    }
    _originImage = originImage;
    _imageView.image = _originImage;
//    [self setCropPoints:[[OCRProcessor nativeScanWithNSStringPoint:originImage] mutableCopy]];
    self.cropPoints = [[CropperProcessor nativeScanWithNSStringPoint:originImage] mutableCopy];
}

- (void)setOriginImage:(UIImage *)originImage withPoints:(NSMutableArray<NSString *> *)points {
    
    if (!originImage) {
        return;
    }
    _originImage = originImage;
    _imageView.image = _originImage;
    if ([self checkPoints:points]) {
        self.cropPoints = points;
    }else{
        self.cropPoints = [[CropperProcessor nativeScanWithNSStringPoint:originImage] mutableCopy];
    }
}

-(void)setCropPoints:(NSMutableArray<NSString *> *)cropPoints{
    if (!_originImage) {
        return;
    }
    if (![self checkPoints:cropPoints]) {
        RBQLog3(@" checkPoints 0");
        _cropPoints = [self getFullImgCropPoints];
    } else {
        RBQLog3(@" checkPoints 1");
        _cropPoints = cropPoints;
    }
    
    [self.cropOverlayMask updatePointValueByDotLocation:[self viewPoint:CGPointFromString(cropPoints[0])] location:DotLocationTopLeft];

    [self.cropOverlayMask updatePointValueByDotLocation:[self viewPoint:CGPointFromString(cropPoints[1])] location:DotLocationTopRight];

    [self.cropOverlayMask updatePointValueByDotLocation:[self viewPoint:CGPointFromString(cropPoints[2])] location:DotLocationBottomRight];

    [self.cropOverlayMask updatePointValueByDotLocation:[self viewPoint:CGPointFromString(cropPoints[3])] location:DotLocationBottomLeft];
    
    [self setNeedsLayout];
    [self layoutIfNeeded];
    
    [self.cropOverlayMask setNeedsLayout];
    [self.cropOverlayMask layoutIfNeeded];
    
    if (self.delegate && [self.delegate respondsToSelector:@selector(onCropPointsChange:points:)]) {
        [self.delegate onCropPointsChange:self points:_cropPoints];
    }
    
    if (self.onCropPointsChange) {
        self.onCropPointsChange(self, _cropPoints);
    }
}

- (void)updatePointByDotLocation:(CGPoint)point location:(DotLocation)location {
    if (!_cropPoints||_cropPoints.count<4) {
        return;
    }
    switch (location) {
        case DotLocationTopLeft: {
            _cropPoints[0] = NSStringFromCGPoint(point);
            break;
        }
        case DotLocationTopRight: {
            _cropPoints[1] = NSStringFromCGPoint(point);
            break;
        }
        case DotLocationBottomLeft: {
            _cropPoints[3] = NSStringFromCGPoint(point);
            break;
        }
        case DotLocationBottomRight: {
            _cropPoints[2] = NSStringFromCGPoint(point);
            break;
        }
        default: {
            break;
        }
    }
    
    if (self.delegate && [self.delegate respondsToSelector:@selector(onCropPointsChange:points:)]) {
        [self.delegate onCropPointsChange:self points:_cropPoints];
    }
    
    if (self.onCropPointsChange) {
        self.onCropPointsChange(self, _cropPoints);
    }
}

- (void)setImageMargin:(float)imageMargin{
    
    if (imageMargin<0) {
        return;
    }
    _imageMargin = imageMargin;
    
    [self setNeedsLayout];
    [self layoutIfNeeded];
}

-(BOOL)checkPoints:(NSArray<NSString *> *) points {
    
    return points && points.count == 4
            && points[0] && points[1] && points[2] && points[3];
}

-(NSMutableArray<NSString *> *)getFullImgCropPoints {
    //最常用，不可少nil
    NSMutableArray<NSString *> *points = [NSMutableArray<NSString *> arrayWithObjects:NSStringFromCGPoint(CGPointMake(0,0)),NSStringFromCGPoint(CGPointMake(0,0)),NSStringFromCGPoint(CGPointMake(0,0)),NSStringFromCGPoint(CGPointMake(0,0)), nil];
    if (_originImage) {
        int width = _originImage.size.width;
        int height = _originImage.size.height;
        points[0] = NSStringFromCGPoint(CGPointMake(0,0));
        points[1] = NSStringFromCGPoint(CGPointMake(width,0));
        points[2] = NSStringFromCGPoint(CGPointMake(width,height));
        points[3] = NSStringFromCGPoint(CGPointMake(0,height));
    }
    return points;
}

/**
 * 裁剪
 * @return 裁剪后的图片
 */
-(UIImage *)crop{
    
    return [self crop:_cropPoints];
}

/**
 * 使用自定义选区裁剪
 * @param points 大小为4
 * @return 裁剪后的图片
 */
-(UIImage *)crop:(NSArray<NSString *> *)points {
    if (![self checkPoints:points]) {
        return NULL;
    }
    UIImage *bmp = [CropperProcessor cropWithImageWithNSStringPoint:self.originImage area:points];
    if (bmp) {
        return bmp;
    }
    return _originImage;
}


-(CGFloat)viewPointX:(CGPoint)point{
    CGFloat scale = [self.imageView shm_contentScale];
    return point.x * scale;
}

-(CGFloat)viewPointY:(CGPoint)point{
    CGFloat scale = [self.imageView shm_contentScale];
    return point.y * scale;
}

-(CGPoint)viewPoint:(CGPoint)point{
    CGFloat scale = [self.imageView shm_contentScale];
//    RBQLog3(@"缩放比例 scale:%f",scale);
    return CGPointMake(point.x * scale, point.y * scale);
}


-(CGFloat)pointToViewX:(CGPoint)point{
    CGFloat scale = [self.imageView shm_contentScale];
    return point.x / scale;
}

-(CGFloat)pointToViewY:(CGPoint)point{
    CGFloat scale = [self.imageView shm_contentScale];
    return point.y / scale;
}

-(CGPoint)pointToView:(CGPoint)point{
    CGFloat scale = [self.imageView shm_contentScale];
//    RBQLog3(@"缩放比例 scale:%f",scale);
    return CGPointMake(point.x / scale, point.y / scale);
}

#pragma mark - CropOverlayMaskDelegate

- (void)cropOverlayMask:(CorrectCropMask *)cropOverlayMask didMoveToPoint:(CGPoint)point location:(DotLocation)location state:(UIGestureRecognizerState)state{
    
    if (state == UIGestureRecognizerStateBegan) {
        self.magnifierView.hidden = NO;
    } else if (state == UIGestureRecognizerStateEnded || state == UIGestureRecognizerStateCancelled) {
        self.magnifierView.hidden = YES;
    }
    
    CGPoint imagePoint = [self pointToView:point];
    [self updatePointByDotLocation:imagePoint location:location];
    
    CGPoint renderPoint = [cropOverlayMask convertPoint:point toView:self];
    
    [self.magnifierView updateRenderPoint:renderPoint renderView:self];
    
    CGPoint magnifierCenter = [cropOverlayMask convertPoint:point toView:self.magnifierView.superview];
    magnifierCenter.y -= self.magnifierView.frame.size.height;
    self.magnifierView.center = magnifierCenter;
    
}

@end
