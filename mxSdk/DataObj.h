//
//  DataObj.h
//  Inksi
//
//  Created by rbq on 2024/7/3.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

@interface DataObj : NSObject

@property (nonatomic, assign) int index;//指令号  一版为随机数
@property (nonatomic, strong) NSData *data;
@property (nonatomic, assign) int tag;

- (instancetype)initDataObj:(NSData *)data;

- (instancetype)initDataObj:(NSData *)data withTag:(int)tag;

- (instancetype)initDataObj:(NSData *)data index:(int)index withTag:(int)tag;

@end

NS_ASSUME_NONNULL_END
