//
//  WifiOatManager.m
//  iOSBKUDPCamera
//
//  Created by rbq on 2021/12/1.
//  Copyright © 2021 belon. All rights reserved.
//

#import "HttpOtaServer.h"
#import "RBQLog.h"
#import "RBQDefine.h"
#import "XBSTimer.h"
#import "ConnectManager.h"

static HttpOtaServer *share=nil;

@interface HttpOtaServer()<TCPClientDelegate,HTTPServerDelegate,DeviceConnectionDelegate>
//服务器最多启动次数
@property (nonatomic,assign)int maxNum;
@property (nonatomic,assign)int num;
@property (nonatomic,strong)GCDObjectTimer *tryNumberTimer;
@property (nonatomic,strong)TCPClient *client;
@property (nonatomic,strong)HTTPServer *httpService;
@property (nonatomic,strong)NSString *documentPath;
@property (nonatomic,strong)Device *device;

@end

@implementation HttpOtaServer

- (GCDObjectTimer *)tryNumberTimer{
    if(!_tryNumberTimer){
        _tryNumberTimer = [[GCDObjectTimer alloc] init];
    }
    return _tryNumberTimer;
}

- (instancetype)init
{
    self = [super init];
    if (self) {
        self.delegates = [NSHashTable weakObjectsHashTable];
    }
    return self;
}

+(HttpOtaServer *)share
{
    static dispatch_once_t disOnce;
    dispatch_once(&disOnce, ^{
        share=[[HttpOtaServer alloc] init];
    });
    return share;
}

+(id)allocWithZone:(struct _NSZone *)zone
{
    static dispatch_once_t disOnce;
    dispatch_once(&disOnce, ^{
        share = [super allocWithZone:zone];
    });
    return share;
}
// 为了严谨，也要重写copyWithZone 和 mutableCopyWithZone
-(id)copyWithZone:(NSZone *)zone
{
    return share;
}
-(id)mutableCopyWithZone:(NSZone *)zone
{
    return share;
}

- (void)registerOtaServerDelegate:(id<OtaServerDelegate>)delegate {
    @synchronized(self.delegates) {
        [self.delegates addObject:delegate];
    }
}

- (void)unregisterOtaServerDelegate:(id<OtaServerDelegate>)delegate {
    @synchronized(self.delegates) {
        [self.delegates removeObject:delegate];
    }
}

- (void)notifyotaHttpServerWillStart {
    for (id<OtaServerDelegate> delegate in self.delegates) {
        if ([delegate respondsToSelector:@selector(otaHttpServerWillStart)]) {
            [delegate otaHttpServerWillStart];
        }
    }
}

- (void)notifyOtaHttpServerDidStartFail:(NSError *)error {
    for (id<OtaServerDelegate> delegate in self.delegates) {
        if ([delegate respondsToSelector:@selector(otaHttpServerDidStartFail:)]) {
            [delegate otaHttpServerDidStartFail:error];
        }
    }
}

- (void)notifyOtaHttpServerDidStartSuccess {
    for (id<OtaServerDelegate> delegate in self.delegates) {
        if ([delegate respondsToSelector:@selector(otaHttpServerDidStartSuccess)]) {
            [delegate otaHttpServerDidStartSuccess];
        }
    }
}

- (void)notifyOtaClientConnectWillStart {
    for (id<OtaServerDelegate> delegate in self.delegates) {
        if ([delegate respondsToSelector:@selector(otaClientConnectWillStart)]) {
            [delegate otaClientConnectWillStart];
        }
    }
}

- (void)notifyOtaClientConnectDidFail:(NSError *)error {
    for (id<OtaServerDelegate> delegate in self.delegates) {
        if ([delegate respondsToSelector:@selector(otaClientConnectDidFail:)]) {
            [delegate otaClientConnectDidFail:error];
        }
    }
}

- (void)notifyOtaClientConnectDidSuccess {
    for (id<OtaServerDelegate> delegate in self.delegates) {
        if ([delegate respondsToSelector:@selector(otaClientConnectDidSuccess)]) {
            [delegate otaClientConnectDidSuccess];
        }
    }
}

- (void)notifyOtaServerReadFirmwareVersionSuccess:(NSString *)version {
    for (id<OtaServerDelegate> delegate in self.delegates) {
        if ([delegate respondsToSelector:@selector(otaServerReadFirmwareVersionSuccess:)]) {
            [delegate otaServerReadFirmwareVersionSuccess:version];
        }
    }
}

- (void)notifyOtaServerReadFirmwareVersionError:(NSError *)error {
    for (id<OtaServerDelegate> delegate in self.delegates) {
        if ([delegate respondsToSelector:@selector(otaServerReadFirmwareVersionError:)]) {
            [delegate otaServerReadFirmwareVersionError:error];
        }
    }
}

- (void)notifyOtaClientNotConnectError:(NSError *)error {
    for (id<OtaServerDelegate> delegate in self.delegates) {
        if ([delegate respondsToSelector:@selector(otaClientNotConnectError:)]) {
            [delegate otaClientNotConnectError:error];
        }
    }
}

- (void)notifyOtaServerDidWritePartialDataOfLength:(GCDAsyncSocket *)sock partialLength:(NSUInteger)partialLength
                                                tag:(long)tag
                                       httpResponse:(NSObject<HTTPResponse> *)httpResponse
                                  totalBytesWritten:(NSUInteger)totalBytesWritten {
    for (id<OtaServerDelegate> delegate in self.delegates) {
        if ([delegate respondsToSelector:@selector(otaServer:didWritePartialDataOfLength:tag:httpResponse:totalBytesWritten:)]) {
            [delegate otaServer:sock didWritePartialDataOfLength:partialLength tag:tag httpResponse:httpResponse totalBytesWritten:totalBytesWritten];
        }
    }
}

- (void)notifyOtaServerNewSocket:(HTTPServer *)server didAcceptNewSocket:(GCDAsyncSocket *)newSocket {
    for (id<OtaServerDelegate> delegate in self.delegates) {
        if ([delegate respondsToSelector:@selector(otaServer:didAcceptNewSocket:)]) {
            [delegate otaServer:server didAcceptNewSocket:newSocket];
        }
    }
}

- (void)notifyOtaServerConnectionDidDie:(HTTPServer *)server httpConnection:(HTTPConnection *)httpConnection {
    for (id<OtaServerDelegate> delegate in self.delegates) {
        if ([delegate respondsToSelector:@selector(otaServerConnectionDidDie:httpConnection:)]) {
            [delegate otaServerConnectionDidDie:server httpConnection:httpConnection];
        }
    }
}

- (BOOL)isRunning{
    if(!self.httpService){
        return NO;
    }
    return [self.httpService isRunning];
}

-(BOOL)isConnected{
    if(!self.device||!self.client){
        return NO;
    }
    return self.client.isConnected;
}

-(BOOL)isConnected:(Device *)device{
    if(!self.device||![self.device isEqual:device]||!self.client){
        return NO;
    }
    return self.client.isConnected;
}

/**
 开启ota服务
 */
- (void)startServerWithSetDocumentPath:(NSString *)documentPath maxNum:(int)maxNum {
    
    NSFileManager *fileManager = [NSFileManager defaultManager];
    
    if (!documentPath || ![fileManager fileExistsAtPath:documentPath]) {
        // documentPath为null，启动失败
        RBQLog3(@"documentPath和device不能为空");
        NSError *error = [NSError errorWithDomain:@"nullError" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"传入ota路径路径为nil或者ota文件不存在"}];
        if (self.otaHttpServerDidStartFailBlock) {
            self.otaHttpServerDidStartFailBlock(error);
        }
        [self notifyOtaHttpServerDidStartFail:error];
        return;
    }
    
    __weak typeof(self) weakSelf = self;
    [self releaseOtaServerWithCompletion:^(BOOL wasAsync) {
        
        if (wasAsync) {
            // 延时启动
            [weakSelf cancelDelayedStartServer];
            NSDictionary *params = @{@"documentPath": documentPath, @"maxNum": @(maxNum)};
            [weakSelf performSelector:@selector(localStartServerWithParams:) withObject:params afterDelay:0.2];
            
        } else {
            // 直接启动
            [weakSelf localStartServerWithSetDocumentPath:documentPath maxNum:maxNum];
        }
    }];
}

- (void)cancelDelayedStartServer {
    [NSObject cancelPreviousPerformRequestsWithTarget:self selector:@selector(localStartServerWithParams:) object:nil];
}

- (void)localStartServerWithParams:(NSDictionary *)params {
    NSString *documentPath = params[@"documentPath"];
    int maxNum = [params[@"maxNum"] intValue];
    [self localStartServerWithSetDocumentPath:documentPath maxNum:maxNum];
}

-(void)localStartServerWithSetDocumentPath:(NSString *)documentPath maxNum:(int)maxNum{
    
    //创建httpService
    HTTPServer *httpService = [[HTTPServer alloc]init];
    [httpService setType:@"_http.tcp"];
    [httpService setPort:httpServicePort];
    [httpService registerHTTPServerDelegate:self];
    self.httpService = httpService;
    
    TCPClient *client = [[TCPClient alloc] init];
    client.delegate = self;
    client.isDebug = NO;
    client.reconnectCount = 3;
    self.client = client;
    
    self.num = 0;
    self.maxNum = maxNum;
    self.documentPath = documentPath;
    RBQLog3(@"【localStartServerWithSetDocumentPath】setDocumentRoot:%@",documentPath);
    [self.httpService setDocumentRoot:self.documentPath];
    
    if(self.otaHttpServerWillStartBlock){
        self.otaHttpServerWillStartBlock();
    }
    [self notifyotaHttpServerWillStart];
    
    [self tryStartServer];
}

- (void)tryStartServer {
    
    self.num = self.num + 1;
    RBQLog3(@"http服务第:%d次启动", self.num);
    NSError *error;
    
    if ([self.httpService start:&error]) {
        
        [[ConnectManager share] registerDeviceConnectionDelegate:self];
        
        RBQLog3(@"http服务开启成功");
        if(self.otaHttpServerDidStartSuccessBlock){
            self.otaHttpServerDidStartSuccessBlock();
        }
        [self notifyOtaHttpServerDidStartSuccess];
        
    } else {
        RBQLog3(@"http服务开启失败, %@", [error description]);
        [self.tryNumberTimer clearScheduledTimer];
        
        if (self.num <= self.maxNum) { // 启动失败，重新启动
            __weak typeof(self) weakSelf = self;
            [self.tryNumberTimer scheduledGCDTimerWithSartTime:^{
                [weakSelf tryStartServer];
            } startTime:0.2 interval:0 repeats:NO];
        } else { // 启动失败，达到最大次数
            if (self.otaHttpServerDidStartFailBlock) {
                self.otaHttpServerDidStartFailBlock(error);
            }
            [self notifyOtaHttpServerDidStartFail:error];
        }
    }
}

- (void)connect:(Device *)device {
    RBQLog3(@"【OtaServer】--connect--");
    if (!device) {
        NSError *error = [NSError errorWithDomain:@"clientDidFailToReconnect" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"连接设备不能为nil"}];
        [self handleConnectionFailureWithError:error];
        return;
    }
    
    if ([self isDeviceConnected:device]) {
        NSError *error = [NSError errorWithDomain:@"clientDidFailToReconnect" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"当前设备已连接"}];
        [self handleConnectionFailureWithError:error];
        return;
    }
    
    __weak typeof(self) weakSelf = self;
    if ([self.client isConnected]) {
        [self disConnectWithCompletion:^{
            [weakSelf localStartConnectionToDevice:device];
        }];
    } else {
        [self localStartConnectionToDevice:device];
    }
}

- (BOOL)isDeviceConnected:(Device *)device {
    return self.device && [self.device isEqual:device] && [self.client isConnected];
}

- (void)handleConnectionFailureWithError:(NSError *)error {
    if (self.otaClientConnectDidFailBlock) {
        self.otaClientConnectDidFailBlock(error);
    }
    [self notifyOtaClientConnectDidFail:error];
}

- (void)localStartConnectionToDevice:(Device *)device {
    RBQLog3(@"【OtaServer】--localStartConnectionToDevice--");
    self.device = device;
    if (self.otaClientConnectWillStartBlock) {
        self.otaClientConnectWillStartBlock();
    }
    [self notifyOtaClientConnectWillStart];
    [self.client connectHost:device.ip port:clientPort];
}


-(void)disConnectWithCompletion:(nullable void (^)(void))completion{
    RBQLog3(@"【disConnectWithCompletion】--localStartConnectionToDevice--");
    //调用断开
    [self.client disConnectWithCompletion:completion];
}

/**
 读取固件版
 */
-(void)readWifiFirmwareVersion {
    if(!self.client||![self.client isConnected]){
        //客户端没连接，无法读取，返回错误
        NSError *error = [NSError errorWithDomain:@"ClientNotConnectError" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"设备未连接错误"}];
        if(self.otaClientNotConnectErrorBlock){
            self.otaClientNotConnectErrorBlock(error);
        }
        [self notifyOtaClientNotConnectError:error];
        return;
    }
    RBQLog3(@"发送获取Wifi固件版本的指令");
    uint8_t cmdVer[4] = {0xAA,0x38,0x00,0x99};
    NSData *data = [NSData dataWithBytes:cmdVer length:4];
    [self.client sendData:data timeout:1000];
}

/**
 开始ota
 */
-(void)startOta:(NSString *)reqURL{
    
    if(!self.client||![self.client isConnected]){
        //返回设备未连接错误
        NSError *error = [NSError errorWithDomain:@"ClientNotConnectError" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"设备未连接错误"}];
        if(self.otaClientNotConnectErrorBlock){
            self.otaClientNotConnectErrorBlock(error);
        }
        [self notifyOtaClientNotConnectError:error];
        return;
    }
    
    // 构建 JSON 字符串
    NSString *jsonStr = [NSString stringWithFormat:@"{\"url\":\"%@\",\"port\":%d,\"timeout\":%d}", reqURL, httpServicePort, 1000];
    NSLog(@"开始ota:%@", jsonStr);

    // 将 JSON 字符串转换为 NSData
    NSData *jsonData = [jsonStr dataUsingEncoding:NSUTF8StringEncoding];
    NSUInteger jsonLen = jsonData.length;

    // 创建一个可变的 NSData 来构建最终的命令数据
    NSMutableData *commandData = [NSMutableData dataWithCapacity:jsonLen + 4];

    // 添加数据头、命令位和 JSON 数据长度
    uint8_t header[] = {0xAA, 0x39, (uint8_t)jsonLen};
    [commandData appendBytes:header length:sizeof(header)];

    // 添加实际的 JSON 数据
    [commandData appendData:jsonData];

    // 添加数据尾部
    uint8_t footer = 0x99;
    [commandData appendBytes:&footer length:1];

    NSLog(@"commandData:%@",[self convertDataToHexStr:commandData]);
    
    [self.client sendData:commandData timeout:1000];
    
}

-(NSString *)convertDataToHexStr:(NSData *)data{
    
    if (!data || [data length] == 0) {
        return @"";
    }
    NSMutableString *string = [[NSMutableString alloc] initWithCapacity:[data length]];
    [data enumerateByteRangesUsingBlock:^(const void *bytes, NSRange byteRange, BOOL *stop) {
        unsigned char *dataBytes = (unsigned char*)bytes;
        for (NSInteger i = 0; i < byteRange.length; i++) {
            NSString *hexStr = [NSString stringWithFormat:@"%02x", (dataBytes[i]) & 0xff];
            [string appendString:hexStr];
        }
    }];
    return string;
}

/**
 释放ota服务
 */
- (void)releaseOtaServerWithCompletion:(nullable void (^)(BOOL wasAsync))completion {
    
    [[ConnectManager share] unregisterDeviceConnectionDelegate:self];
    
    [self cancelDelayedStartServer];
    [self.tryNumberTimer clearScheduledTimer];
    
    dispatch_group_t group = dispatch_group_create();
    BOOL hasPendingOperations = NO;
    
    if (self.client) {
        if (self.client.isConnected) {
            hasPendingOperations = YES;
            dispatch_group_enter(group);
            [self.client disConnectWithCompletion:^{
                dispatch_group_leave(group);
            }];
        }
        self.client = nil;
    }

    if (self.httpService) {
        if (self.httpService.isRunning) {
            hasPendingOperations = YES;
            dispatch_group_enter(group);
            [self.httpService stopWithCompletion:^{
                dispatch_group_leave(group);
            }];
        }
        //经过测试发现，这里还不能将httpService置nil，因为httpService内链接释放没那么快，会造成里边释放的时候造成异常
//        self.httpService = nil;
    }

    if (hasPendingOperations) {
        dispatch_group_notify(group, dispatch_get_main_queue(), ^{
            if (completion) {
                completion(YES); // 异步执行
            }
        });
    } else {
        if (completion) {
            completion(NO); // 直接执行
        }
    }
}

- (void)httpServer:(HTTPServer *)server didAcceptNewSocket:(GCDAsyncSocket *)newSocket{
    //wifi芯片连接httpservice
    if (self.otaServerDidAcceptNewSocketBlock) {
        self.otaServerDidAcceptNewSocketBlock(server, newSocket);
    }
    [self notifyOtaServerNewSocket:server didAcceptNewSocket:newSocket];
}

- (void)httpServer:(GCDAsyncSocket *)sock didWritePartialDataOfLength:(NSUInteger)partialLength tag:(long)tag httpResponse:(NSObject<HTTPResponse> *)httpResponse totalBytesWritten:(NSUInteger)totalBytesWritten{
    // wifi芯片下载httpservice的配置的ota文件
    if(self.otaServerDidWritePartialDataBlock){
        self.otaServerDidWritePartialDataBlock(sock, partialLength, tag, httpResponse, totalBytesWritten);
    }
    [self notifyOtaServerDidWritePartialDataOfLength:sock partialLength:partialLength tag:tag httpResponse:httpResponse totalBytesWritten:totalBytesWritten];
}

- (void)httpServerConnectionDidDie:(HTTPServer *)server httpConnection:(HTTPConnection *)httpConnection{
    // wifi 芯片断开和httpservice连接
    if (self.otaServerConnectionDidDieBlock) {
        self.otaServerConnectionDidDieBlock(server, httpConnection);
    }
    [self notifyOtaServerConnectionDidDie:server httpConnection:httpConnection];
}

#pragma mark client代理方法

- (void)client:(TCPClient *)client didConnect:(NSString *)host port:(uint16_t)port{
    
    RBQLog3(@" -- ota -- socket 已连接");
    if(self.otaClientConnectDidSuccessBlock){
        self.otaClientConnectDidSuccessBlock();
    }
    [self notifyOtaClientConnectDidSuccess];
}

- (void)clientDidDisconnect:(TCPClient *)client{
    
    RBQLog3(@" -- 【clientDidDisconnect】 ota -- socket 已断开");
    /*
    RBQLog3(@" -- 【clientDidDisconnect】 ota -- socket 已断开");
    if (_onDisConnectOta) {
        self.onDisConnectOta();
    }
     */
}

- (void)clientDidFailToReconnect:(TCPClient *)client{
    
    RBQLog3(@" -- 【clientDidFailToReconnect】 ota -- socket 连接失败");
    NSError *error = [NSError errorWithDomain:@"clientDidFailToReconnect" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"客户端尝试连接超过最大次数仍然失败"}];
    [self handleConnectionFailureWithError:error];
}

- (void)client:(TCPClient *)client didReadData:(NSData *)data{
    
    NSString *jsonStr  =[[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
    NSLog(@"jsonStr:%@",jsonStr);
    if (!jsonStr) {
        return;
    }
    if (![jsonStr hasPrefix:@"{"]&&[jsonStr hasSuffix:@"}"]) {
        return;
    }
    
    NSError *error = nil;
    // 业务逻辑
    NSData *jsonData = [jsonStr dataUsingEncoding:NSUTF8StringEncoding];
    NSDictionary *dic =  [NSJSONSerialization JSONObjectWithData:jsonData options:NSJSONReadingMutableContainers error:&error];
    if(error){
        if (self.otaServerReadFirmwareVersionErrorBlock) {
            self.otaServerReadFirmwareVersionErrorBlock(error);
        }
        [self notifyOtaServerReadFirmwareVersionError:error];
        return;
    }
    NSString *version = [dic objectForKey:@"version"];
    if(!version){
        NSError *error = [NSError errorWithDomain:@"ReadFirmwareVersionError" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"读取数据不包含version字段"}];
        if (self.otaServerReadFirmwareVersionErrorBlock) {
            self.otaServerReadFirmwareVersionErrorBlock(error);
        }
        [self notifyOtaServerReadFirmwareVersionError:error];
        return;
    }
    self.device.wifiVersion = version;
    NSLog(@"version:%@",version);
    
    if (self.otaServerReadFirmwareVersionSuccessBlock) {
        self.otaServerReadFirmwareVersionSuccessBlock(version);
    }
    [self notifyOtaServerReadFirmwareVersionSuccess:version];
}

- (void)onDeviceConnectStart{
    
}

- (void)onDeviceConnectFail{
    
}

- (void)onDeviceConnectSucceed{
    
}

- (void)onDeviceDisconnect{
    if (![self isConnected]) {
        return;
    }
    [self disConnectWithCompletion:^{
        RBQLog3(@"断开OtaService的 tcp 连接 ");
    }];
}

@end
