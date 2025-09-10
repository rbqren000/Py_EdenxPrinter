//
//  TCPClient.h
//
//  Created by rbq on 2021/9/16.
//  Copyright © 2021 rbq. All rights reserved.
//


#import <UIKit/UIKit.h>

@class TCPClient;

@protocol TCPClientDelegate <NSObject>

@optional
/**
 * Callback of received message
 * Call on the specified thread, when you set the receive queue
 */
- (void)client:(TCPClient *)client didReadData:(NSData *)data;

- (void)client:(TCPClient *)client didReadData:(NSData *)data tag:(long)tag;
/**
 * Callback of did connected
 * Call on the specified thread, when you set the receive queue
*/
- (void)client:(TCPClient *)client didConnect:(NSString *)host port:(uint16_t)port;
/**
 * Callback of disconnected
 * Call on the specified thread, when you set the receive queue
*/
- (void)clientDidDisconnect:(TCPClient *)client;
/**
 * add by rbq
 *已经尝试完所有的重连次数后失败的聚合事件(相当于clientDidDisconnect最大次数后才返回该事件)
 */
- (void)clientDidFailToReconnect:(TCPClient *)client;
/**
 * Callback of send heart data
 * Call on the specified thread, when you set the receive queue
*/
- (void)client:(TCPClient *)client didSendHeartData:(NSData *)data;

@end

@interface TCPClient : NSObject

// The delegate of the callback informations
@property (nonatomic, weak) id<TCPClientDelegate> delegate;

// The time interval of sending heart data. Default is 10s
@property (nonatomic, assign) NSTimeInterval heartTimeInterval;

// How often do I reconnect?
// Only disconnect when the network is not good.
// If I disconnect manually, I will not reconnect
//
// The time interval of reconnect. Default is 10s
@property (nonatomic, assign) NSTimeInterval reconnectTimeInterval;

// The time interval of connenting. Default is 5s
@property (nonatomic, assign) NSTimeInterval connectTimeInterval;

// The count of reconnect. Default is 10
@property (nonatomic, assign) NSInteger reconnectCount;

// Print log or not
@property (nonatomic, assign) BOOL isDebug;

// Heartbeat packet data. Keep the tcp unbroken.
@property (nonatomic, strong) NSData *heartData;

// The host of socket, just readonly and thread safe
@property (nonatomic, copy, readonly) NSString *socketHost;

// The post of socket, just readonly and thread safe
@property (nonatomic, assign, readonly) uint16_t socketPort;

/**
 * Appoint the receive queue and initialization
 * If queue is nil, Default is dispatch_get_main_queue
 */
- (instancetype)initWithReceiveQueue:(dispatch_queue_t)queue;

/**
 * Connects to the given host and port.
 */
- (void)connectHost:(NSString *)host port:(uint16_t)port;

/**
 * Disconnects immediately (synchronously). Any pending reads or writes are dropped.
 */
- (void)disConnect;

/**add by rbq completion则表示断开函数disConnectWithCompletion中block内断开先关的代码执行完毕**/
- (void)disConnectWithCompletion:(void (^)(void))completion;

/**
 * Send message data and return whether send success.
 * Return 'NO' when data is nil or current socket is not connected (connecting or disconnected)
 */
- (BOOL)sendData:(NSData *)data;

- (BOOL)sendData:(NSData *)data timeout:(NSTimeInterval)timeout;

- (BOOL)sendData:(NSData *)data timeout:(NSTimeInterval)timeout tag:(long)tag;

/**
 * Returns whether the socket is connected.
 */
- (BOOL)isConnected;

/**
 * Returns whether the socket is disconnected.
 */
- (BOOL)isDisconnected;

@end
