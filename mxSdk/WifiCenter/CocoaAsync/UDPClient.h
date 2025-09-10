//
//  UDPClient.h
//  BelonPrinter
//
//  Created by rbq on 2021/9/24.
//  Copyright © 2021 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "CocoaAsyncSocket.h"

NS_ASSUME_NONNULL_BEGIN

@protocol UDPClientSocketDelegate <NSObject>

- (void)clientSocketDidReceiveMessage:(NSString *)message;

@end

@interface UDPClient : NSObject <GCDAsyncUdpSocketDelegate>

@property (nonatomic, weak)id <UDPClientSocketDelegate>delegate;

- (void)sendMessage:(NSString *)ip port:(uint16_t)port message:(NSString *)message;
-(void)releaseClient;

@end

NS_ASSUME_NONNULL_END
