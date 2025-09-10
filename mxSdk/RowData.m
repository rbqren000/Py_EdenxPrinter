//
//  SingleRowImageData.m
//  BelonPrinter
//
//  Created by rbq on 2021/7/5.
//  Copyright © 2021 rbq. All rights reserved.
//

#import "RowData.h"
#import "RBQLog.h"
#import "MxFileManager.h"

@implementation RowData

-(NSUInteger)totalPacketCount:(NSUInteger)usefulDataLen{
    if (_dataLength%usefulDataLen ==0) {
         return _dataLength/usefulDataLen;
    }else{
        return _dataLength/usefulDataLen + 1;
    }
}
-(NSData *)data{
    if (!_rowDataPath) {
        return nil;
    }
    RBQLog3(@"获取的数据的文件路径为:%@",_rowDataPath);
    return [MxFileManager dataFromPath:_rowDataPath];
}

@end
