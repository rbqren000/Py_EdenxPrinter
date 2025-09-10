//
//  MultiRowImageData.h
//  BelonPrinter
//
//  Created by rbq on 2021/7/5.
//  Copyright © 2021 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "MultiRowImage.h"
#import "RowData.h"

NS_ASSUME_NONNULL_BEGIN

@interface MultiRowData : NSObject

@property (nonatomic, strong) NSMutableArray<RowData*> *rowDataArr;
//预览图的地址，这里每一拼包含一个预览图
@property (nonatomic, strong, nullable) NSMutableArray<NSString *> *imagePaths;

@property (nonatomic, strong, nonnull) NSString *thumbPath;
//默认为压缩数据
@property (nonatomic, assign) BOOL compress;
/**切图排布方向**/
@property (nonatomic, assign) RowLayoutDirection rowLayoutDirection;

- (instancetype)initMultiRowData:(NSMutableArray<RowData*> *)rowDataArr imagePaths:(nullable NSMutableArray<NSString *> *)imagePaths thumbPath:(nullable NSString *)thumbPath compress:(BOOL)compress rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection;

-(NSUInteger)totalDataLength;
-(NSUInteger)totalPacketCount:(NSUInteger)usefulDataLen;
-(BOOL)hasData;
-(NSUInteger)totalRowCount;
-(RowData *)rowDataWithRowIndex:(NSUInteger)rowIndex;
-(int)compressValue;

@end

NS_ASSUME_NONNULL_END
