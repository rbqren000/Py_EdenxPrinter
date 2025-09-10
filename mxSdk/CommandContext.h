//
//  CommandContext.h
//  Inksi
//
//  Created by rbq on 2024/6/13.
//

#import <UIKit/UIKit.h>
#import "Command.h"
#import "CommandCallback.h"

NS_ASSUME_NONNULL_BEGIN

@interface CommandContext : NSObject

@property (nonatomic, strong) Command *command;
@property (nonatomic, strong) CommandCallback *commandCallback;

- (instancetype)initCommandContext:(Command *)command commandCallback:(CommandCallback *)commandCallback;

@end

NS_ASSUME_NONNULL_END
