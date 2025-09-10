//
//  UDPClient.m
//  BelonPrinter
//
//  Created by rbq on 2021/9/24.
//  Copyright © 2021 rbq. All rights reserved.
//

#import "UDPClient.h"
#import "RBQLog.h"

#define LocalClientPort 36000
#define Tag 200

@interface UDPClient()

@property (nonatomic, strong)GCDAsyncUdpSocket *udpSocket;
@property (nonatomic, strong)NSString *currentSendingMessage;

@property (nonatomic, strong)NSString *serveIP;
@property (nonatomic, assign)uint16_t servePort;

@property (nonatomic, assign)BOOL isSending;
@property (nonatomic, strong)NSMutableArray *messageQueue;
@property (nonatomic,assign)NSInteger times;
@property (nonatomic,assign)NSInteger resendTimes;

@end

@implementation UDPClient

- (instancetype)init
{
    self = [super init];
    if (self) {
        [self setUp];
    }
    return self;
}

-(void)setUp{
 
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    self.udpSocket = [[GCDAsyncUdpSocket alloc]initWithDelegate:self delegateQueue:queue];
    
    NSError *error;
    [self.udpSocket bindToPort:LocalClientPort error:&error];
    if (error) {
        NSLog(@"客户端绑定失败");
    }
    [self.udpSocket beginReceiving:nil];
}

- (void)udpSocket:(GCDAsyncUdpSocket *)sock didConnectToAddress:(NSData *)address{
    
    /*
    NSString *ip = [GCDAsyncUdpSocket hostFromAddress:address];
    uint16_t port = [GCDAsyncUdpSocket portFromAddress:address];
    
    self.serveIP = ip;
    self.servePort = port;
    */
}

- (void)udpSocket:(GCDAsyncUdpSocket *)sock didNotConnect:(NSError *)error{
    
}

// 发送消息失败回调
-(void)udpSocket:(GCDAsyncUdpSocket *)sock didNotSendDataWithTag:(long)tag dueToError:(NSError *)error {
    
    self.resendTimes ++;
    if (self.resendTimes > 4) {
        [self.messageQueue removeObject:self.currentSendingMessage];
        self.currentSendingMessage = nil;
        self.isSending = NO;
    }else{
        [self localSendMessage:self.serveIP port:self.servePort message:self.currentSendingMessage];
    }
}

- (void)udpSocket:(GCDAsyncUdpSocket *)sock didSendDataWithTag:(long)tag{
    RBQLog3(@"sock: %@  客户端发送成功!   message:%@",sock,self.currentSendingMessage);
    [self.messageQueue removeObject:self.currentSendingMessage];
    self.isSending = NO;
    self.currentSendingMessage = nil;
}

- (void)udpSocketDidClose:(GCDAsyncUdpSocket *)sock withError:(NSError *)error{
    RBQLog3(@"sock: %@  断开连接  %@",sock,[error description]);
}

// 收到消息回调
-(void)udpSocket:(GCDAsyncUdpSocket *)sock didReceiveData:(NSData *)data fromAddress:(NSData *)address withFilterContext:(id)filterContext {
    
//    NSString *ip = [GCDAsyncUdpSocket hostFromAddress:address];
//    uint16_t port = [GCDAsyncUdpSocket portFromAddress:address];
    /*
    self.serveIP = ip;
    self.servePort = port;
    */
    NSString *messgae = [[NSString alloc]initWithData:data encoding:NSUTF8StringEncoding];
    
    self.times ++;
    NSLog(@"times:%ld",self.times);
    
//    RBQLog3(@"sock: %@  接收到消息：ip:%@  port:%d  message:%@",sock,ip,port,messgae);
    
    dispatch_sync(dispatch_get_main_queue(), ^{
        if ([self.delegate respondsToSelector:@selector(clientSocketDidReceiveMessage:)]) {
            [self.delegate clientSocketDidReceiveMessage:messgae];
        }
    });
}

- (void)sendMessage:(NSString *)ip port:(uint16_t)port message:(NSString *)message {
    self.serveIP = ip;
    self.servePort = port;
    [self.messageQueue addObject:message];
    if (!self.isSending){
        [self localSendMessage:ip port:port message:message];
    }
}

-(void)localSendMessage:(NSString *)ip port:(uint16_t)port message:(NSString *)message{
    self.currentSendingMessage = message;
    self.isSending = YES;
    self.resendTimes = 0;
    NSData *data = [message dataUsingEncoding:NSUTF8StringEncoding];
    //对方的host 和 port
    [self.udpSocket sendData:data
                  toHost:ip
                    port:port
             withTimeout:-1
                     tag:Tag];
}
/*
-(void)localSendData:(NSString *)ip port:(uint16_t)port data:(NSData *)data{
    //对方的host 和 port
    [self.udpSocket sendData:data
                  toHost:ip
                    port:port
             withTimeout:-1
                     tag:Tag];
}
*/

- (void)setIsSending:(BOOL)isSending{
    _isSending = isSending;
    if (!isSending && self.messageQueue.count) {
        [self localSendMessage:self.serveIP port:self.servePort message:[self.messageQueue firstObject]];
    }
}

- (NSMutableArray *)messageQueue{
    if (!_messageQueue) {
        _messageQueue = [[NSMutableArray alloc]init];
    }return _messageQueue;
}

-(void)releaseClient{
    if (self.udpSocket&&!self.udpSocket.isClosed) {
        [self.udpSocket close];
        self.udpSocket = nil;
    }
}

@end
