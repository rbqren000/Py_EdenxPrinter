//
//  CommandContext.m
//  Inksi
//
//  Created by rbq on 2024/6/13.
//

#import "CommandContext.h"

@implementation CommandContext

- (instancetype)initCommandContext:(Command *)command commandCallback:(CommandCallback *)commandCallback
{
    self = [super init];
    if (self) {
        self.command = command;
        self.commandCallback = commandCallback;
    }
    return self;
}

@end
