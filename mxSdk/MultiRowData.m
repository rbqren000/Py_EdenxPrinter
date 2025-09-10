//
//  MultiRowImageData.m
//  BelonPrinter
//
//  Created by rbq on 2021/7/5.
//  Copyright © 2021 rbq. All rights reserved.
//

#import "MultiRowData.h"

@implementation MultiRowData

- (instancetype)initMultiRowData:(NSMutableArray<RowData*> *)rowDataArr imagePaths:(nullable NSMutableArray<NSString *> *)imagePaths thumbPath:(nullable NSString *)thumbPath compress:(BOOL)compress rowLayoutDirection:(RowLayoutDirection)rowLayoutDirection
{
    self = [super init];
    if (self) {
        self.rowDataArr = rowDataArr;
        self.imagePaths = imagePaths;
        self.thumbPath = thumbPath;
        self.compress = compress;
        self.rowLayoutDirection = rowLayoutDirection;
    }
    return self;
}

-(NSUInteger)totalDataLength {
    NSInteger totalDataLength = 0;
    if (!_rowDataArr) {
        return totalDataLength;
    }
    for (RowData *singleRowImageData in _rowDataArr){
        totalDataLength = totalDataLength + singleRowImageData.dataLength;
    }
    return totalDataLength;
}

-(NSUInteger)totalPacketCount:(NSUInteger)usefulDataLen{

    NSUInteger totalPacketCount = 0;
    if (!_rowDataArr) {
        return totalPacketCount;
    }
   for (RowData *singleRowImageData in _rowDataArr){
       totalPacketCount = totalPacketCount + [singleRowImageData totalPacketCount:usefulDataLen];
   }
   return totalPacketCount;
}

-(BOOL)hasData{
   return [self totalDataLength] > 0;
}

-(NSUInteger)totalRowCount{
    if (!_rowDataArr) {
        return 0;
    }
   return _rowDataArr.count;
}

-(RowData *)rowDataWithRowIndex:(NSUInteger)rowIndex{
   if (!_rowDataArr||rowIndex<0||rowIndex>=_rowDataArr.count){
       return nil;
   }
   return _rowDataArr[rowIndex];
}

-(int)compressValue{
    
    return self.compress?1:0;
}

@end
