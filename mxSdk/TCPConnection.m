//
//  TCPConnection.m
//  Inksi
//
//  Created by rbq on 2024/11/1.
//

#import "TCPConnection.h"
#import "TCPClient.h"

@interface TCPConnection()

#pragma mark 设备连接相关属性
@property (nonatomic, strong) TCPClient *client;

@end

@implementation TCPConnection

- (instancetype)initWithHost:(NSString *)host port:(uint16_t)port {
    self = [super init];
    if (self) {
        
    }
    return self;
}

- (void)connect {
    NSLog(@"Starting TCP connection...");
}

- (void)disConnect {
    NSLog(@"Stopping TCP connection...");
}

- (void)sendData:(NSData *)data {
    NSLog(@"Sending data over TCP...");
    // 实现发送数据逻辑
}

- (void)receiveData:(NSData *)data {
    NSLog(@"Receiving data over TCP...");
    // 实现接收数据逻辑
}

- (void)startListeningUdp {
    NSLog(@"Starting UDP listening...");
    // 实现监听逻辑
}

- (void)stopListeningUdp {
    NSLog(@"Stopping UDP listening...");
    // 实现停止监听逻辑
}

@end
