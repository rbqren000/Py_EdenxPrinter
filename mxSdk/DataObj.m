//
//  DataObj.m
//  Inksi
//
//  Created by rbq on 2024/7/3.
//

#import "DataObj.h"

@implementation DataObj

- (instancetype)initDataObj:(NSData *)data{
    self = [super init];
    if (self) {
        self.index = -1;
        self.data = data;
        self.tag = -1;
    }
    return self;
}

- (instancetype)initDataObj:(NSData *)data withTag:(int)tag{
    self = [super init];
    if (self) {
        self.index = -1;
        self.data = data;
        self.tag = tag;
    }
    return self;
}

- (instancetype)initDataObj:(NSData *)data index:(int)index withTag:(int)tag{
    self = [super init];
    if (self) {
        self.index = index;
        self.data = data;
        self.tag = tag;
    }
    return self;
}

@end
