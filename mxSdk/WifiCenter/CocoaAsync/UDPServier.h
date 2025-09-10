//
//  UDPServier.h
//  BelonPrinter
//
//  Created by rbq on 2021/9/24.
//  Copyright © 2021 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "CocoaAsyncSocket.h"
#import "WifiRomoteModel.h"

NS_ASSUME_NONNULL_BEGIN

#define LocalServePort 6099

@protocol UDPServerSocketDelegate <NSObject>

- (void)receiveWifiRomoteModel:(WifiRomoteModel *)wifiRomoteModel;

@end

typedef void(^OnReceiveWifiRomoteModel)(WifiRomoteModel *wifiRomoteModel);

@interface UDPServier : NSObject <GCDAsyncUdpSocketDelegate>

@property (nonatomic, weak)id <UDPServerSocketDelegate>delegate;
@property (nonatomic, copy) OnReceiveWifiRomoteModel onReceiveWifiRomoteModel;

-(void)startUdpSocketMonitoring;
-(void)stopUdpSocketMonitoring;
- (void)sendMessage:(NSString *)message;

@end

NS_ASSUME_NONNULL_END
