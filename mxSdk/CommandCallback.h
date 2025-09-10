//
//  CommandCallback.h
//  Inksi
//
//  Created by rbq on 2024/6/13.
//

#import <UIKit/UIKit.h>
#import "Command.h"

NS_ASSUME_NONNULL_BEGIN

@protocol CommandCallbackDelegate<NSObject>

//@optional下的方法可选择实现   //@required 下的方法必须实现  [方法默认都是@required的]
@optional
-(void)onCommandSuccess:(Command *)command obj:(NSObject *)obj;

@optional
-(void)onCommandError:(Command *)command errorMsg:(NSString *)errorMsg;

@optional
-(void)OnCommandTimeout:(Command *)command errorMsg:(NSString *)errorMsg;

@end

typedef void(^OnCommandSuccess)(Command *command, NSObject *obj);
typedef void(^OnCommandError)(Command *command, NSString *errorMsg);
typedef void(^OnCommandTimeout)(Command *command, BOOL delayEfficacy);

@interface CommandCallback : NSObject

@property (nonatomic, copy) OnCommandSuccess onSuccess;
@property (nonatomic, copy) OnCommandError onError;
@property (nonatomic, copy) OnCommandTimeout onTimeout;

@property (nonatomic,weak) id<CommandCallbackDelegate> commandCallbackDelegate;

- (instancetype)initCommandCallback:(OnCommandSuccess)onSuccess onError:(OnCommandError)onError onTimeout:(OnCommandTimeout)onTimeout;

- (instancetype)initCommandCallback:(id<CommandCallbackDelegate>)commandCallbackDelegate;

- (instancetype)initCommandCallback:(id<CommandCallbackDelegate>)commandCallbackDelegate onSuccess:(OnCommandSuccess)onSuccess onError:(OnCommandError)onError onTimeout:(OnCommandTimeout)onTimeout;

@end

NS_ASSUME_NONNULL_END
