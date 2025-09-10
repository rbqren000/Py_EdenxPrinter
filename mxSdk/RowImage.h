//
//  SingleRowImage.h
//  BelonPrinter
//
//  Created by rbq on 2021/7/5.
//  Copyright © 2021 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

@interface RowImage : NSObject
/**行图的路径*/
@property (nonatomic, strong) NSString *imagePath;

//顶部和底部保留的超出长宽部分，用于抖动算法的时候消除不同行拼接时的缝隙
@property (nonatomic, assign) int topBeyondDistance;
@property (nonatomic, assign) int bottomBeyondDistance;

- (instancetype)init NS_UNAVAILABLE;
- (instancetype)initRowImage:(NSString *)imagePath;
- (instancetype)initRowImage:(NSString *)imagePath topBeyondDistance:(int)topBeyondDistance bottomBeyondDistance:(int)bottomBeyondDistance;

@end

NS_ASSUME_NONNULL_END
