//
//  CommandCallback.m
//  Inksi
//
//  Created by rbq on 2024/6/13.
//

#import "CommandCallback.h"

@implementation CommandCallback

- (instancetype)initCommandCallback:(OnCommandSuccess)onSuccess onError:(OnCommandError)onError onTimeout:(OnCommandTimeout)onTimeout
{
    self = [super init];
    if (self) {
        self.onSuccess = onSuccess;
        self.onError = onError;
        self.onTimeout = onTimeout;
    }
    return self;
}

- (instancetype)initCommandCallback:(id<CommandCallbackDelegate>)commandCallbackDelegate{
    self = [super init];
    if (self) {
        self.commandCallbackDelegate = commandCallbackDelegate;
    }
    return self;
}

- (instancetype)initCommandCallback:(id<CommandCallbackDelegate>)commandCallbackDelegate onSuccess:(OnCommandSuccess)onSuccess onError:(OnCommandError)onError onTimeout:(OnCommandTimeout)onTimeout{
    self = [super init];
    if (self) {
        self.onSuccess = onSuccess;
        self.onError = onError;
        self.onTimeout = onTimeout;
        self.commandCallbackDelegate = commandCallbackDelegate;
    }
    return self;
}

@end
