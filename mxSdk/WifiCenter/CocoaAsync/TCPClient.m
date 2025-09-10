//
//  TCPClient.h
//
//  Created by rbq on 2021/9/16.
//  Copyright © 2021 rbq. All rights reserved.
//

#import "TCPClient.h"
#import <netinet/in.h>
#import "GCDAsyncSocket.h"
#import <SystemConfiguration/SystemConfiguration.h>
#import "RBQLog.h"

typedef void (^DDNetworkReachabilityStatusBlock)(BOOL reachable);

static void DDNetworkReachilityCallBack(SCNetworkReachabilityRef target, SCNetworkReachabilityFlags flags, void *info) {
    DDNetworkReachabilityStatusBlock block = ((__bridge DDNetworkReachabilityStatusBlock)info);
    if (block) {
        block(((flags & kSCNetworkReachabilityFlagsReachable) != 0));
    }
}

static const void *DDNetworkReachabilityRetainCallback(const void *info) {
    return Block_copy(info);
}

static void DDNetworkReachabilityReleaseCallback(const void *info) {
    if (info) {
        Block_release(info);
    }
}

@interface TCPClient () <GCDAsyncSocketDelegate>

@property (nonatomic, assign) SCNetworkReachabilityRef ref;


@property (nonatomic) GCDAsyncSocket *socket;
@property (nonatomic) dispatch_queue_t socketQueue;
@property (nonatomic) dispatch_queue_t receiveQueue;

// Edit in socket queue
@property (nonatomic, strong) NSData *heart;
@property (nonatomic, assign) NSInteger reconnectFlag;
@property (nonatomic, assign) BOOL needReconnect;
@property (nonatomic, assign) BOOL networkReachable;

@property (nonatomic, copy) NSString *host;
@property (nonatomic, assign) UInt16 port;


@end

static NSTimeInterval DDSocketReadWriteTimeout = -1;
static NSInteger DDSocketTag = 0;

@implementation TCPClient {
    void *IsOnSocketQueueOrTargetQueueKey;
    dispatch_source_t _heartTimer;
    dispatch_source_t _reconnectTimer;
}

- (void)dealloc {
    SCNetworkReachabilitySetDispatchQueue(self.ref, NULL);
    CFRelease(self.ref);
}

- (instancetype)init {
    return [self initWithReceiveQueue:nil];
}

- (instancetype)initWithReceiveQueue:(dispatch_queue_t)queue {
    self = [super init];
    if (self) {
        self.socketQueue = dispatch_queue_create("com.rbq.socket", DISPATCH_QUEUE_SERIAL);
        self.receiveQueue = queue ? queue : dispatch_get_main_queue();
        
        NSAssert(self.receiveQueue != dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_LOW, 0),
                 @"The given receiveQueue parameter must not be a concurrent queue.");
        NSAssert(self.receiveQueue != dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_HIGH, 0),
                 @"The given receiveQueue parameter must not be a concurrent queue.");
        NSAssert(self.receiveQueue != dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0),
                 @"The given receiveQueue parameter must not be a concurrent queue.");
        
        self.socket = [[GCDAsyncSocket alloc] initWithDelegate:self delegateQueue:self.receiveQueue socketQueue:self.socketQueue];
        self.socket.IPv4Enabled = YES;
        self.socket.IPv6Enabled = YES;
        self.socket.IPv4PreferredOverIPv6 = NO;
        
//        self.buffer = [NSMutableData data];
//        self.buffer.length = 0;
        
        IsOnSocketQueueOrTargetQueueKey = &IsOnSocketQueueOrTargetQueueKey;
        void *nonNullUnusedPointer = (__bridge void *)self;
        dispatch_queue_set_specific(self.socketQueue, IsOnSocketQueueOrTargetQueueKey, nonNullUnusedPointer, NULL);
        
        self.heartTimeInterval = 10;
        self.reconnectTimeInterval = 10;
        self.reconnectCount = 10;
        self.reconnectFlag = 0;
        self.connectTimeInterval = 5;
        self.isDebug = NO;
        self.needReconnect = YES;
        
        // Network reachability
        struct sockaddr_in addr;
        bzero(&addr, sizeof(addr));
        addr.sin_len = sizeof(addr);
        addr.sin_family = AF_INET;
        self.ref = SCNetworkReachabilityCreateWithAddress(kCFAllocatorDefault, (const struct sockaddr *)&addr);
        SCNetworkReachabilityFlags flags;
        SCNetworkReachabilityGetFlags(self.ref, &flags);
        self.networkReachable = ((flags & kSCNetworkReachabilityFlagsReachable) != 0);
    }
    return self;
}

#pragma mark - Network Monitoring

- (void)_startMonitoring {
    [self _stopMonitoring];
    
    __weak __typeof(self)wself = self;
    void (^block)(BOOL reachable) = ^(BOOL reachable) {
        __strong __typeof(wself)sself = wself;
        if (reachable) {
            sself.networkReachable = YES;
            // Reconnect
            if ([sself isDisconnected] && [self _checkNeedReconnectTimer]) {
                [sself _connect];
                [sself _resetConnect];
                [sself _startReconnectTimer];
            }
        } else {
            sself.networkReachable = NO;
        }
    };
    SCNetworkReachabilityContext context = { 0, (__bridge void *)block, DDNetworkReachabilityRetainCallback, DDNetworkReachabilityReleaseCallback, NULL };
    SCNetworkReachabilitySetCallback(self.ref, DDNetworkReachilityCallBack, &context);
    SCNetworkReachabilitySetDispatchQueue(self.ref, self.socketQueue);
}

- (void)_stopMonitoring {
    SCNetworkReachabilitySetDispatchQueue(self.ref, NULL);
}

#pragma mark - Send Heart

- (void)_sendHeart {
    BOOL success = [self sendData:self.heart];
    if (success) {
//        NSString *heart = [[NSString alloc] initWithData:self.heart encoding:NSUTF8StringEncoding];
//        RBQLog3(@"成功发送心跳包:%@ host: %@ port: %d send heart", heart, self.host, self.port);
        if (self.isDebug) {
            RBQLog3(@"成功发送心跳包:%@ -- <%p> host: %@ port: %d send heart", NSStringFromClass([self class]), self, self.host, self.port);
        }
        // Send heart
        NSData *copyData = [self.heart copy];
        dispatch_async(self.receiveQueue, ^{
            if (self.delegate && [self.delegate respondsToSelector:@selector(client:didSendHeartData:)]) {
                [self.delegate client:self didSendHeartData:copyData];
            }
        });
    }
}

- (void)_startHeartTimer {
    [self _stopHeartTimer];
    
    if (self.heartTimeInterval > 0) {
        // Thread start timer needs to be specified
        // No matter which thread the current method is executed in, the call of timer will call back in the specified thread
        dispatch_source_t timer = dispatch_source_create(DISPATCH_SOURCE_TYPE_TIMER, 0, 0, self.socketQueue);
        dispatch_source_set_timer(timer, dispatch_time(DISPATCH_TIME_NOW, self.heartTimeInterval * NSEC_PER_SEC), self.heartTimeInterval * NSEC_PER_SEC, self.heartTimeInterval * NSEC_PER_SEC);
        dispatch_source_set_event_handler(timer, ^{
            [self _sendHeart];
        });
        dispatch_resume(timer);
        _heartTimer = timer;
    }
}

- (void)_stopHeartTimer {
    if (_heartTimer) {
        dispatch_source_cancel(_heartTimer);
        _heartTimer = nil;
    }
}

#pragma mark - Reconnect Actions

- (void)_resetConnect {
    _reconnectFlag = 0;
}

- (void)_resetConnectState:(BOOL)state {
    RBQLog3(@"--【TCPClient】---①---_resetConnectState: %@ --", state ? @"YES" : @"NO");
    _needReconnect = state;
    RBQLog3(@"--【TCPClient】---②---_resetConnectState: %@ --", _needReconnect ? @"YES" : @"NO");
}

- (BOOL)_checkNeedReconnectTimer {
    return (_needReconnect && _reconnectTimer == nil);
}

- (void)_reconnect {
    if (!self.networkReachable) {
        return;
    }
    if (self.reconnectCount >= 0 && _reconnectFlag >= self.reconnectCount) {
        return;
    }
    _reconnectFlag ++;
    
    if (self.isDebug) {
        RBQLog3(@"%@ -- <%p> host: %@ port: %d reconnect count %ld", NSStringFromClass([self class]), self.socket, self.host, self.port, (long)_reconnectFlag);
    }
    
    [self _connect];
}

- (void)_startReconnectTimer {
    [self _stopReconnectTimer];
    
    if (self.reconnectTimeInterval > 0) {
        // Thread start timer needs to be specified
        // No matter which thread the current method is executed in, the call of timer will call back in the specified thread
        dispatch_source_t timer = dispatch_source_create(DISPATCH_SOURCE_TYPE_TIMER, 0, 0, self.socketQueue);
        dispatch_source_set_timer(timer, DISPATCH_TIME_NOW, self.reconnectTimeInterval * NSEC_PER_SEC, 0);
        dispatch_source_set_event_handler(timer, ^{
            [self _reconnect];
        });
        dispatch_resume(timer);
        _reconnectTimer = timer;
    }
}

- (void)_stopReconnectTimer {
    if (_reconnectTimer) {
        dispatch_source_cancel(_reconnectTimer);
        _reconnectTimer = nil;
    }
}

#pragma mark - Socket Connect & Disconnect

- (void)_connect {
    // Cannot connect when the socket is not connected (connecting or connected)
    // Just connect when the socket is disconnected
    // Cancel the after connect actions
    if (![self isDisconnected]) {
        if (self.isDebug) {
            RBQLog3(@"【TCPClient】%@ -- <%p> host: %@ port: %d connect error: already connecting or connected", NSStringFromClass([self class]), self, self.host, self.port);
        }
        return;
    }
    
    if (self.isDebug) {
        RBQLog3(@"【TCPClient】%@ -- <%p> host: %@ port: %d connecting", NSStringFromClass([self class]), self, self.host, self.port);
    }
    
    NSError *error;
    [self.socket connectToHost:self.host onPort:self.port withTimeout:self.connectTimeInterval error:&error];
    if (error) {
        if (self.isDebug) {
            RBQLog3(@"【TCPClient】%@ -- <%p> host: %@ port: %d connect error: %@", NSStringFromClass([self class]), self, self.host, self.port, error);
        }
    }
}

- (void)_disConnect {
    [self.socket disconnect];
}

- (void)_didSendData:(NSData *)data timeout:(NSTimeInterval)timeout tag:(long)tag {
    if (self.socket.isDisconnected) {
        [self _connect];
    }
    [self.socket writeData:data withTimeout:timeout tag:tag];
}

- (void)_didSendData:(NSData *)data {
    [self _didSendData:data timeout:DDSocketReadWriteTimeout tag:DDSocketTag];
}


- (void)_didReceiveData:(NSData *)data tag:(long)tag {
    
    [self _callback:data tag:tag];
}


- (void)_didReadData {
    [self _didReadData:DDSocketTag];
}

- (void)_didReadData:(long)tag{
    [self _didReadData:DDSocketReadWriteTimeout tag:tag];
}

- (void)_didReadData:(NSTimeInterval)timeout tag:(long)tag{
    dispatch_async(self.socketQueue, ^{
        [self.socket readDataWithTimeout:timeout tag:tag];
    });
}

- (void)_callback:(NSData *)data tag:(long)tag{
    
    if (self.delegate && [self.delegate respondsToSelector:@selector(client:didReadData:)]) {
        [self.delegate client:self didReadData:data];
    }
    
    if (self.delegate && [self.delegate respondsToSelector:@selector(client:didReadData:tag:)]) {
        [self.delegate client:self didReadData:data tag:tag];
    }
}

#pragma mark - Public

- (void)connectHost:(NSString *)host port:(uint16_t)port {
    void (^block)(void) = ^(void) {
        self.host = host;
        self.port = port;
        
        [self _resetConnectState:YES]; // Need reconnect
        [self _connect];
        [self _startMonitoring];  // start network monitoring when connect
    };
    if (dispatch_get_specific(IsOnSocketQueueOrTargetQueueKey)) {
        block();
    } else {
        dispatch_async(self.socketQueue, block);
    }
}

- (void)disConnect {
    
    BOOL currentConnectState = [self isConnected];
    
    RBQLog3(@"--【TCPClient】[disConnect]---先同步执行需要立即生效的操作-- currentConnectState:%@",currentConnectState?@"YES":@"NO");
    
    [self _stopReconnectTimer];
    [self _stopMonitoring];  // stop network monitoring when disconnect
    [self _resetConnectState:NO];
    
    void (^block)(void) = ^(void) {
        
        [self _disConnect];
        
        RBQLog3(@"--【TCPClient】--[disConnect]--block--执行完成");
        
        if (!currentConnectState) {
            
            if (self.delegate && [self.delegate respondsToSelector:@selector(clientDidDisconnect:)]) {
                [self.delegate clientDidDisconnect:self];
            }
            
            if (self.delegate && [self.delegate respondsToSelector:@selector(clientDidFailToReconnect:)]) {
                [self.delegate clientDidFailToReconnect:self];
            }
        }
    };
    if (dispatch_get_specific(IsOnSocketQueueOrTargetQueueKey)) {
        RBQLog3(@"--【TCPClient】--将在->当前队列调用--[disConnect]--");
        block();
    } else {
        RBQLog3(@"--【TCPClient】--将在->异步队列调用--[disConnect]--");
        dispatch_sync(self.socketQueue, block);
    }
}

- (void)disConnectWithCompletion:(void (^)(void))completion {
    
    BOOL currentConnectState = [self isConnected];
    
    RBQLog3(@"--【TCPClient】[disConnect]---先同步执行需要立即生效的操作-- currentConnectState:%@",currentConnectState?@"YES":@"NO");
    
    [self _stopReconnectTimer];
    [self _stopMonitoring];  // stop network monitoring when disconnect
    [self _resetConnectState:NO];
    
    void (^block)(void) = ^(void) {
        
        [self _disConnect];

        // 调用回调块，表示 block 执行完成
        RBQLog3(@"--【TCPClient】--[disConnectWithCompletion]--block--执行完成");
        
        if (!currentConnectState) {
            
            if (self.delegate && [self.delegate respondsToSelector:@selector(clientDidDisconnect:)]) {
                [self.delegate clientDidDisconnect:self];
            }
            
            if (self.delegate && [self.delegate respondsToSelector:@selector(clientDidFailToReconnect:)]) {
                [self.delegate clientDidFailToReconnect:self];
            }
        }
        
        if (completion) {
            completion();
        }
    };
    if (dispatch_get_specific(IsOnSocketQueueOrTargetQueueKey)) {
        RBQLog3(@"--【TCPClient】--将在->当前队列调用--[disConnectWithCompletion]--");
        block();
    } else {
        RBQLog3(@"--【TCPClient】--将在->异步队列调用--[disConnectWithCompletion]--");
        dispatch_async(self.socketQueue, block);
    }
}

- (void)setHeartData:(NSData *)heartData {
    NSData *copyData = [heartData copy];
    void (^block)(void) = ^(void) {
        if ([self.heart isEqualToData:copyData]) return;
        self.heart = copyData;
        
        if (copyData) {
            [self _sendHeart];
        }
    };
    if (dispatch_get_specific(IsOnSocketQueueOrTargetQueueKey)) {
        block();
    } else {
        dispatch_async(self.socketQueue, block);
    }
}

- (BOOL)sendData:(NSData *)data {
    return [self sendData:data timeout:DDSocketReadWriteTimeout tag:DDSocketTag];
}

- (BOOL)sendData:(NSData *)data timeout:(NSTimeInterval)timeout{
    return [self sendData:data timeout:timeout tag:DDSocketTag];
}

- (BOOL)sendData:(NSData *)data timeout:(NSTimeInterval)timeout tag:(long)tag{
    if (!data || ![self isConnected]) {
        return NO;
    }
    
    void (^block)(void) = ^(void) {
        
        [self _didSendData:data timeout:timeout tag:tag];
    };
    if (dispatch_get_specific(IsOnSocketQueueOrTargetQueueKey)) {
        block();
    } else {
        dispatch_async(self.socketQueue, block);
    }
    return YES;
}

- (BOOL)isConnected {
    return [self.socket isConnected]; // GCDAsyncSocket did the action in socket queue
}

- (BOOL)isDisconnected {
    return [self.socket isDisconnected];
}

- (NSString *)socketHost {
    __block NSString *host = nil;
    void (^block)(void) = ^(void) {
        host = [self.host copy];
    };
    if (dispatch_get_specific(IsOnSocketQueueOrTargetQueueKey)) {
        block();
    } else {
        dispatch_sync(self.socketQueue, ^{
            block();
        });
    }
    return host;
}

- (uint16_t)socketPort {
    __block uint16_t port = 0;
    void (^block)(void) = ^(void) {
        port = self.port;
    };
    if (dispatch_get_specific(IsOnSocketQueueOrTargetQueueKey)) {
        block();
    } else {
        dispatch_sync(self.socketQueue, ^{
            block();
        });
    }
    return port;
}

- (NSData *)heartData {
    __block NSData *copyData = nil;
    void (^block)(void) = ^(void) {
        copyData = self.heart;
    };
    if (dispatch_get_specific(IsOnSocketQueueOrTargetQueueKey)) {
        block();
    } else {
        dispatch_sync(self.socketQueue, block);
    }
    return copyData;
}

#pragma mark - GCDAsyncSocketDelegate
// All delegate methods run in receiveQueue

- (void)socket:(GCDAsyncSocket *)sock didConnectToHost:(NSString *)host port:(uint16_t)port {
    if (self.isDebug) {
        RBQLog3(@"【TCPClient】%@ -- <%p> host: %@ port: %d connect successed", NSStringFromClass([self class]), self, self.socketHost, self.socketPort);
    }
    // Reset default value
//    self.buffer.length = 0;
    
    if (self.delegate && [self.delegate respondsToSelector:@selector(client:didConnect:port:)]) {
        [self.delegate client:self didConnect:host port:port];
    }
    
    dispatch_async(self.socketQueue, ^{
        [self _startHeartTimer];
        [self _stopReconnectTimer];
    });
}

- (void)socketDidDisconnect:(GCDAsyncSocket *)sock withError:(NSError *)err {
    if (self.isDebug) {
        RBQLog3(@"【TCPClient】%@ -- <%p> host: %@ port: %d disConnect error: %@", NSStringFromClass([self class]), self, self.socketHost, self.socketPort, err);
    }
    RBQLog3(@"【TCPClient】clientDidDisconnect");
    if (self.delegate && [self.delegate respondsToSelector:@selector(clientDidDisconnect:)]) {
        [self.delegate clientDidDisconnect:self];
    }
    NSString *needReconnectStr = _needReconnect ? @"YES" : @"NO";
    RBQLog3(@"【TCPClient】当前-->_reconnectFlag:%ld; needReconnectStr:%@",_reconnectFlag,needReconnectStr);
    if(_needReconnect){
        //需要重连，则需要达到最大值才发送聚合事件
        if (self.reconnectCount >= 0 && _reconnectFlag >= self.reconnectCount) {
            RBQLog3(@"【TCPClient】尝试重连次数已最大，仍失败");
            if (self.delegate && [self.delegate respondsToSelector:@selector(clientDidFailToReconnect:)]) {
                [self.delegate clientDidFailToReconnect:self];
            }
        }else{
            //启用重连
            RBQLog3(@"【TCPClient】启动重连-->_reconnectFlag:%ld",_reconnectFlag);
            dispatch_async(self.socketQueue, ^{
                
                [self _stopHeartTimer];
                
                if ([self _checkNeedReconnectTimer]) {
                    [self _resetConnect];
                    [self _startReconnectTimer];
                }
            });
        }
    }else{
        //不需要重连的情况下，直接发出聚合事件
        RBQLog3(@"【TCPClient】不需要重连的情况下，直接发出聚合事件");
        if (self.delegate && [self.delegate respondsToSelector:@selector(clientDidFailToReconnect:)]) {
            [self.delegate clientDidFailToReconnect:self];
        }
    }
    
}

- (void)socket:(GCDAsyncSocket *)sock didWriteDataWithTag:(long)tag {
    if (self.isDebug) {
        RBQLog3(@"【TCPClient】%@ -- <%p> host: %@ port: %d did write", NSStringFromClass([self class]), self, self.socketHost, self.socketPort);
    }
    [self _didReadData:tag];
}

- (void)socket:(GCDAsyncSocket *)sock didReadData:(NSData *)data withTag:(long)tag {
    if (self.isDebug) {
        RBQLog3(@"【TCPClient】%@ -- <%p> host: %@ port: %d did receive data", NSStringFromClass([self class]), self, self.socketHost, self.socketPort);
    }
    if (self.heart&&[self.heartData isEqualToData:data]) {
        return;
    }
    [self _didReceiveData:data tag:tag];
    [self _didReadData:tag];
}

@end
