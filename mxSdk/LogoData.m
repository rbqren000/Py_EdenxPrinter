//
//  LogoData.m
//  Inksi
//
//  Created by rbq on 2024/6/21.
//

#import "LogoData.h"
#import "MxFileManager.h"

@implementation LogoData

- (instancetype)initLogoData:(NSString *)dataPath dataLength:(NSUInteger)dataLength imagePath:(NSString *)imagePath
{
    self = [super init];
    if (self) {
        _dataPath = dataPath;
        _dataLength = dataLength;
        _imagePath = imagePath;
    }
    return self;
}

-(NSUInteger)totalPacketCount:(NSUInteger)usefulDataLen{
    if (_dataLength%usefulDataLen ==0) {
         return _dataLength/usefulDataLen;
    }else{
        return _dataLength/usefulDataLen + 1;
    }
}
-(NSData *)data{
    if (!self.dataPath) {
        return nil;
    }
    RBQLog3(@"获取的数据的文件路径为:%@",self.dataPath);
    return [MxFileManager dataFromPath:self.dataPath];
}

@end
