//
//  WifiOatManager.h
//  iOSBKUDPCamera
//
//  Created by rbq on 2021/12/1.
//  Copyright © 2021 belon. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <ifaddrs.h>
#import <arpa/inet.h>
#import "TCPClient.h"
#import "HTTPServer.h"
#import "Device.h"

NS_ASSUME_NONNULL_BEGIN

#define clientPort 35001
#define httpServicePort 8000

@protocol OtaServerDelegate <NSObject>

@optional
//服务启动和client连接的相关事件
- (void)otaHttpServerWillStart;//服务将要启动
- (void)otaHttpServerDidStartFail:(NSError *)error;//服务启动失败
- (void)otaHttpServerDidStartSuccess;//ota服务启动成功

- (void)otaClientConnectWillStart;
- (void)otaClientConnectDidFail:(NSError *)error;
- (void)otaClientConnectDidSuccess;//客户端连接成功

- (void)otaServerReadFirmwareVersionSuccess:(NSString *)version;
- (void)otaServerReadFirmwareVersionError:(NSError *)error;

/**设备未连接错误**/
- (void)otaClientNotConnectError:(NSError *)error;

// ota时，WiFi芯片下载固件相关的代理事件
- (void)otaServer:(HTTPServer *)server didAcceptNewSocket:(GCDAsyncSocket *)newSocket;
- (void)otaServer:(GCDAsyncSocket *)socket didWritePartialDataOfLength:(NSUInteger)partialLength tag:(long)tag httpResponse:(NSObject<HTTPResponse> *)httpResponse totalBytesWritten:(NSUInteger)totalBytesWritten;
- (void)otaServerConnectionDidDie:(HTTPServer *)server httpConnection:(HTTPConnection *)httpConnection;

@end

@interface HttpOtaServer : NSObject

@property (nonatomic, strong) NSHashTable<id<OtaServerDelegate>> *delegates;

- (void)registerOtaServerDelegate:(id<OtaServerDelegate>)delegate;
- (void)unregisterOtaServerDelegate:(id<OtaServerDelegate>)delegate;

//服务启动和client连接的相关事件
// 服务启动和 client 连接的相关事件
typedef void(^OtaHttpServerWillStartBlock)(void);
typedef void(^OtaHttpServerDidStartFailBlock)(NSError *error);
typedef void(^OtaHttpServerDidStartSuccessBlock)(void);

typedef void(^OtaClientConnectWillStartBlock)(void);
typedef void(^OtaClientConnectDidFailBlock)(NSError *error);
typedef void(^OtaClientConnectDidSuccessBlock)(void);

typedef void(^OtaServerReadFirmwareVersionSuccessBlock)(NSString *version);
typedef void(^OtaServerReadFirmwareVersionErrorBlock)(NSError *error);

typedef void(^OtaClientNotConnectErrorBlock)(NSError *error);

// OTA 时，WiFi 芯片下载固件相关的事件
typedef void(^OtaServerDidAcceptNewSocketBlock)(HTTPServer *server, GCDAsyncSocket *newSocket);
typedef void(^OtaServerDidWritePartialDataBlock)(GCDAsyncSocket *socket, NSUInteger partialLength, long tag, NSObject<HTTPResponse> *httpResponse, NSUInteger totalBytesWritten);
typedef void(^OtaServerConnectionDidDieBlock)(HTTPServer *server, HTTPConnection *httpConnection);


@property (nonatomic, copy) OtaHttpServerWillStartBlock otaHttpServerWillStartBlock;
@property (nonatomic, copy) OtaHttpServerDidStartFailBlock otaHttpServerDidStartFailBlock;
@property (nonatomic, copy) OtaHttpServerDidStartSuccessBlock otaHttpServerDidStartSuccessBlock;

@property (nonatomic, copy) OtaClientConnectWillStartBlock otaClientConnectWillStartBlock;
@property (nonatomic, copy) OtaClientConnectDidFailBlock otaClientConnectDidFailBlock;
@property (nonatomic, copy) OtaClientConnectDidSuccessBlock otaClientConnectDidSuccessBlock;

@property (nonatomic, copy) OtaClientNotConnectErrorBlock otaClientNotConnectErrorBlock;

@property (nonatomic, copy) OtaServerReadFirmwareVersionSuccessBlock otaServerReadFirmwareVersionSuccessBlock;
@property (nonatomic, copy) OtaServerReadFirmwareVersionErrorBlock otaServerReadFirmwareVersionErrorBlock;

@property (nonatomic, copy) OtaServerDidAcceptNewSocketBlock otaServerDidAcceptNewSocketBlock;
@property (nonatomic, copy) OtaServerDidWritePartialDataBlock otaServerDidWritePartialDataBlock;
@property (nonatomic, copy) OtaServerConnectionDidDieBlock otaServerConnectionDidDieBlock;

+(HttpOtaServer *)share;

@property (nonatomic, assign, readonly) BOOL isRunning;
@property (nonatomic, assign, readonly) BOOL isConnected;

/**
 开启ota服务
 */
-(void)startServerWithSetDocumentPath:(NSString *)documentPath maxNum:(int)maxNum;
/**连接ota设备**/
-(void)connect:(Device *)device;
-(BOOL)isConnected:(Device *)device;
/**断开ota设备**/
-(void)disConnectWithCompletion:(nullable void (^)(void))completion;

/**
 开始ota
 */
-(void)startOta:(NSString *)reqURL;

/**
 读取固件版本
 */
-(void)readWifiFirmwareVersion;

/**
 释放ota服务，如果需要执行释放，且释放成功则返回true，如果无需释放则返回false
 */
- (void)releaseOtaServerWithCompletion:(nullable void (^)(BOOL wasAsync))completion;

@end

NS_ASSUME_NONNULL_END
