//
//  CorrectCropView.h
//  OpenCVDemo
//
//  Created by rbq on 2021/5/27.
//  Copyright © 2021 lihuaguang. All rights reserved.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

@class CorrectCropView;

//定义代理事件
@protocol CropPointsChangeDelegate<NSObject>

//@optional下的方法可选择实现   //@required 下的方法必须实现  [方法默认都是@required的]
@optional
-(void)onCropPointsChange:(CorrectCropView *)cropView points:(NSArray<NSString *> *)points;

@end

@interface CorrectCropView : UIView

typedef void(^OnCropPointsChange)(CorrectCropView *cropView,NSArray<NSString *> *points);
@property (nonatomic, copy) OnCropPointsChange onCropPointsChange;

//以代理的模式响应事件
@property (nonatomic,weak)IBOutlet id<CropPointsChangeDelegate> delegate;

@property (nonatomic, assign) float imageMargin;
@property (nonatomic, strong) UIImage *originImage;
@property (nonatomic, strong) NSMutableArray<NSString *> *cropPoints;

- (void)setOriginImage:(UIImage *)originImage withPoints:(NSMutableArray<NSString *> *)points ;
-(UIImage *)crop;

@end

NS_ASSUME_NONNULL_END
