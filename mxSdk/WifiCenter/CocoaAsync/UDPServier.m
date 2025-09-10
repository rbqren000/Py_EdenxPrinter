//
//  UDPServier.m
//  BelonPrinter
//
//  Created by rbq on 2021/9/24.
//  Copyright © 2021 rbq. All rights reserved.
//

#import "UDPServier.h"
#import "RBQLog.h"
#import "XBSTimer.h"

#define Tag 200

@interface UDPServier()

@property (nonatomic, strong)GCDAsyncUdpSocket *udpSocket;
@property (nonatomic, strong)NSString *currentSendingMessage;
@property (nonatomic, strong)NSString *clientIP;
@property (nonatomic, assign)uint16_t clientPort;
@property (nonatomic, assign)BOOL isSending;
@property (nonatomic, strong)NSMutableArray<NSString *> *messageQueue;
@property (nonatomic,assign)NSInteger times;
@property (nonatomic,assign)NSInteger resendTimes;

@property (nonatomic, strong) GCDObjectTimer *listenerTimer;
@property (nonatomic, strong) GCDObjectTimer *receivingTimer;

@property (nonatomic, assign) BOOL isStart;

@end

@implementation UDPServier

- (GCDObjectTimer *)listenerTimer {
    if (!_listenerTimer) {
        _listenerTimer = [[GCDObjectTimer alloc] init];
    }
    return _listenerTimer;
}

- (GCDObjectTimer *)receivingTimer {
    if (!_receivingTimer) {
        _receivingTimer = [[GCDObjectTimer alloc] init];
    }
    return _receivingTimer;
}

-(void)startUdpSocketMonitoring{
        
    if(self.isStart){
        return;
    }
    self.isStart = YES;
    [self releaseUdpSocket];
    RBQLog3(@"【startUdpSocketMonitoring】");
    __weak typeof(self) weakSelf = self;
    [self.listenerTimer scheduledGCDTimerWithSartTime:^{
        [weakSelf localStartUdpSocketMonitoring];
    } startTime:0.5 interval:0 repeats:NO];
}

-(void)localStartUdpSocketMonitoring{
    
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    GCDAsyncUdpSocket *udpSocket = [[GCDAsyncUdpSocket alloc]initWithDelegate:self delegateQueue:queue];
    self.udpSocket = udpSocket;
    self.isSending = NO;
    // 关联端口,监听端口
    NSError * error;
    [udpSocket bindToPort:LocalServePort error:&error];
    //开始接收消息
    [self beginReceiving:udpSocket];
}

-(void)beginReceiving:(GCDAsyncUdpSocket *)socket{
    
    __weak typeof(self) weakSelf = self;
    [self.receivingTimer scheduledGCDTimerWithSartTime:^{
        [weakSelf localBeginReceiving:socket];
    } startTime:0.2 interval:0 repeats:NO];
}

-(void)localAgainUdpSocketMonitoring{
    
    [self releaseUdpSocket];
    RBQLog3(@"【localAgainUdpSocketMonitoring】");
    __weak typeof(self) weakSelf = self;
    [self.listenerTimer scheduledGCDTimerWithSartTime:^{
        [weakSelf localStartUdpSocketMonitoring];
    } startTime:2 interval:0 repeats:NO];
}

-(void)localBeginReceiving:(GCDAsyncUdpSocket *)socket{
    
    NSError * error;
    // 接受一次消息（启动一个等待接受，且只接收一次）
//    [udpSocket receiveOnce:&error];
    //开始接收消息，会一直监听并接收
    [socket beginReceiving:&error];
    if(error){
        RBQLog3(@" [UDPServier] 监听udp广播失败 error.description:%@",error.description);
        [self localAgainUdpSocketMonitoring];
    }else{
        RBQLog3(@" [UDPServier] 开始监听udp广播");
    }
}

-(void)stopUdpSocketMonitoring{
    if(!self.isStart){
        return;
    }
    self.isStart = NO;
    RBQLog3(@"【stopUdpSocketMonitoring】");
    [self.listenerTimer clearScheduledTimer];
    [self.receivingTimer clearScheduledTimer];
    [self releaseUdpSocket];
}

-(void)releaseUdpSocket{
    if (self.udpSocket) {
        [self.udpSocket close];
        if(self.udpSocket.isClosed){
            RBQLog3(@"套接字已关闭")
        }
        self.udpSocket = nil;
    }
}

- (void)udpSocket:(GCDAsyncUdpSocket *)sock didConnectToAddress:(NSData *)address{
    
    /*
    NSString *ip = [GCDAsyncUdpSocket hostFromAddress:address];
    uint16_t port = [GCDAsyncUdpSocket portFromAddress:address];
    
    self.clientIP = ip;
    self.clientPort = port;
    NSLog(@"didConnectToAddress：ip:%@  port:%d",ip,port);
    */
}

- (void)udpSocket:(GCDAsyncUdpSocket *)sock didReceiveData:(NSData *)data fromAddress:(NSData *)address withFilterContext:(id)filterContext{
    
    @synchronized(self){
        
//        NSString *ip = [GCDAsyncUdpSocket hostFromAddress:address];
//        uint16_t port = [GCDAsyncUdpSocket portFromAddress:address];
        
        NSError *error;
        NSString *message = [[NSString alloc]initWithData:data encoding:NSUTF8StringEncoding];
        NSData *jsonData = [message dataUsingEncoding:NSUTF8StringEncoding];
        NSDictionary *dic =  [NSJSONSerialization JSONObjectWithData:jsonData options:NSJSONReadingMutableContainers error:&error];
//        RBQLog3(@"【didReceiveData】dic:%@",dic);
        if(error){
            return;
        }
        
        if (![dic.allKeys containsObject:@"NAME"]
            ||![dic.allKeys containsObject:@"IP"]
            ||![dic.allKeys containsObject:@"POAT"]
            ||![dic.allKeys containsObject:@"MAC"]) {
            return;
        }
        
        NSString *name = [dic objectForKey:@"NAME"];
        NSString *ip = [dic objectForKey:@"IP"];
        uint16_t port = [[dic objectForKey:@"POAT"] unsignedIntValue];
        NSString *mac = [dic objectForKey:@"MAC"];
        NSString *model = [dic objectForKey:@"MODEL"];
        
        self.clientIP = ip;
        self.clientPort = port;
        
        self.times ++;
//        RBQLog3(@"times:%ld",self.times);
        
        WifiRomoteModel *romoteModel = [[WifiRomoteModel alloc] initWifiRomoteModel:name ip:ip port:port mac:mac model:model];
//        RBQLog3(@" [UDPServier] 接收到消息:ip:%@  port:%d  message:%@",ip,port,message);
        dispatch_sync(dispatch_get_main_queue(), ^{
            if ([self.delegate respondsToSelector:@selector(receiveWifiRomoteModel:)]) {
                [self.delegate receiveWifiRomoteModel:romoteModel];
            }
            if (self.onReceiveWifiRomoteModel) {
                self.onReceiveWifiRomoteModel(romoteModel);
            }
        });
        
        /*
        [self sendAnswerDataToHost:ip port:port message:@"***************************************************"];
        
        // 再次启动接收等待
        [self.udpSocket receiveOnce:nil];
         */
    }
}

- (void)udpSocket:(GCDAsyncUdpSocket *)sock didSendDataWithTag:(long)tag{
    RBQLog3(@"[UDPServier] 服务端发送成功!   message:%@",self.currentSendingMessage);
    [self.messageQueue removeObject:self.currentSendingMessage];
    self.isSending = NO;
    self.currentSendingMessage = nil;
    
}

- (void)udpSocket:(GCDAsyncUdpSocket *)sock didNotSendDataWithTag:(long)tag dueToError:(NSError *)error{
    RBQLog3(@"s[UDPServier] %@  服务端发送失败 %@",sock,[error description]);
    self.resendTimes ++;
    if (self.resendTimes > 4) {
        [self.messageQueue removeObject:self.currentSendingMessage];
        self.currentSendingMessage = nil;
        self.isSending = NO;
    }else{
        [self localSendMessage:self.clientIP port:self.clientPort message:self.currentSendingMessage];
    }
}

- (void)udpSocketDidClose:(GCDAsyncUdpSocket *)sock withError:(NSError *)error{
    if(error){
        RBQLog3(@"[UDPServier] udpSocketDidClose error:%@",error.description);
    }else{
        RBQLog3(@"[UDPServier] udpSocketDidClose");
    }
}

- (void)sendMessage:(NSString *)message{
    [self.messageQueue addObject:message];
    if (!self.isSending){
        [self localSendMessage:self.clientIP port:self.clientPort message:message];
    }
}

-(void)localSendMessage:(NSString *)ip port:(uint16_t)port message:(NSString *)message{
    self.currentSendingMessage = message;
    self.isSending = YES;
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
    self.currentSendingMessage = message;
    self.isSending = YES;
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
        [self localSendMessage:self.clientIP port:self.clientPort message:[self.messageQueue firstObject]];
    }
}

- (NSMutableArray *)messageQueue{
    if (!_messageQueue) {
        _messageQueue = [[NSMutableArray<NSString *> alloc]init];
    }return _messageQueue;
}

@end
