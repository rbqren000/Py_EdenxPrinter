//
//  DataObjContext.m
//  Inksi
//
//  Created by rbq on 2024/7/3.
//

#import "DataObjContext.h"

@implementation DataObjContext

- (instancetype)initDataObjContext:(DataObj *)dataObj dataObjCallback:(DataObjCallback *)dataObjCallback
{
    self = [super init];
    if (self) {
        self.dataObj = dataObj;
        self.dataObjCallback = dataObjCallback;
    }
    return self;
}

@end
