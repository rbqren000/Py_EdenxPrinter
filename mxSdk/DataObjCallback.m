//
//  DataObjCallback.m
//  Inksi
//
//  Created by rbq on 2024/7/3.
//

#import "DataObjCallback.h"

@implementation DataObjCallback

- (instancetype)initDataObjCallback:(OnDataObjWriteSuccess)onSuccess onError:(OnDataObjWriteError)onError onTimeout:(OnDataObjWriteTimeout)onTimeout{
    self = [super init];
    if (self) {
        self.onSuccess = onSuccess;
        self.onError = onError;
        self.onTimeout = onTimeout;
    }
    return self;
}

- (instancetype)initDataObjCallback:(id<DataObjCallbackDelegate>)dataObjCallbackDelegate{
    self = [super init];
    if (self) {
        self.dataObjCallbackDelegate = dataObjCallbackDelegate;
    }
    return self;
}

- (instancetype)initDataObjCallback:(id<DataObjCallbackDelegate>)dataObjCallbackDelegate onSuccess:(OnDataObjWriteSuccess)onSuccess onError:(OnDataObjWriteError)onError onTimeout:(OnDataObjWriteTimeout)onTimeout{
    self = [super init];
    if (self) {
        self.dataObjCallbackDelegate = dataObjCallbackDelegate;
        self.onSuccess = onSuccess;
        self.onError = onError;
        self.onTimeout = onTimeout;
    }
    return self;
}

@end
