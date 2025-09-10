//
//  ConnectManager.m
//  BelonPrinter
//
//  Created by rbq on 2021/9/23.
//  Copyright © 2021 rbq. All rights reserved.
//

#import "ConnectManager.h"
#import "CRC16.h"
#import "RBQLog.h"
#import "OpCode.h"
#import "TransportProtocol.h"
#import "TCPClient.h"
#import "UDPServier.h"
#import "MxFileManager.h"
#import "XBSTimer.h"
#import "NSString+String.h"
#import "MxUtils.h"
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <arpa/inet.h>
#import <SystemConfiguration/CaptiveNetwork.h>
#import <NetworkExtension/NetworkExtension.h>
#import <CoreLocation/CoreLocation.h>

//指令服务
#define Service_UUID @"0000fff0-0000-1000-8000-00805f9b34fb"
//[可读][通知]
#define Notify_UUID @"0000fff1-0000-1000-8000-00805f9b34fb"
//[写无应答]
#define Write_UUID @"0000fff2-0000-1000-8000-00805f9b34fb"

//服务
#define DNW_Service_UUID @"0000ffff-0000-1000-8000-00805f9b34fb"
#define DNW_Write_UUID @"0000ff01-0000-1000-8000-00805f9b34fb"
#define DNW_Indicate_UUID @"0000ff02-0000-1000-8000-00805f9b34fb"
#define DNW_Notify_UUID @"0000ff03-0000-1000-8000-00805f9b34fb"

static ConnectManager *share=nil;

static int commandSequence = 1;//指令序列号，以下会自动计算增加
static NSTimeInterval const commandInterval = 0.6;
static const int maxLoseHeartTimes = 4;

static const int retrySendDataTime = 3;

@interface ConnectManager()<TCPClientDelegate,CommandCallbackDelegate,DataObjCallbackDelegate>

#pragma mark 指令超时
@property (nonatomic, strong) GCDObjectTimer *commandQueueTimer;
@property (nonatomic, strong) NSMutableArray<CommandContext *> *commandQueue;
@property (nonatomic, assign) NSTimeInterval lastSendCommandTime;
@property (nonatomic, strong) GCDObjectTimer *checkCommandQueueCompleteTimer;

#pragma mark 设备连接相关属性
@property (nonatomic, strong) BabyBluetooth *baby;
@property (nonatomic, strong) TCPClient *client;
//扫描超时设置
@property (nonatomic, strong) GCDObjectTimer *scanTimeoutTimer;
@property (nonatomic, strong) GCDObjectTimer *apDeviceDiscoverTimer;

#pragma mark 指令接收及发送等
@property (nonatomic, assign) int sequenceNumber;
@property (nonatomic, assign) BOOL receivingJson;
@property (nonatomic, strong) NSString *stringBuilder;
@property (nonatomic, assign) int N_Index;
@property (nonatomic, assign) int heartLoseTimes;
@property (nonatomic, strong) GCDObjectTimer *heartMonitorTimer;

//用于延时等待重新尝试发送数据指令
@property (nonatomic, strong) GCDObjectTimer *waitResponseTimer;

#pragma mark 配网相关属性
/**监听配网的广播*/
@property (nonatomic, strong) UDPServier *distributionNetworkUdpServer;
/**配网的账号*/
@property (nonatomic, strong) NSString *ssid;
/**配网的密码*/
@property (nonatomic, strong) NSString *password;
/**配网是否成功标志位*/
@property (nonatomic, assign) BOOL sendedNetworkConfigurationSuccess;
/**配网超时*/
@property (nonatomic, strong) GCDObjectTimer *networkConfigurationTimeoutTimer;
/**更新配网进度的时间间隔*/
@property (nonatomic, assign) NSTimeInterval networkConfigurationTimeInterval;
/**超时时间**/
@property (nonatomic, assign) NSTimeInterval scanTimeout;
/**配网进度*/
@property (nonatomic, assign) CGFloat networkConfigurationProgress;

#pragma mark WiFi设备扫描相关属性
@property (nonatomic, strong) UDPServier *discoverUdpServer;

@property (nonatomic, assign) DataSendType dataSendType;

@property (nonatomic, strong, readonly) NSLock *lock;
@property (nonatomic, strong, readonly) NSLock *receiveLock;

@property (nonatomic, strong) NSMutableArray<BasePacket *> *packets;

@property (nonatomic, assign) BOOL isSendingData;

@property (nonatomic, strong) CommandCallback *commandCallback;
@property (nonatomic, strong) DataObjCallback *dataObjCallback;

@end

@implementation ConnectManager

- (NSMutableArray<CommandContext *> *)commandQueue{
    if(!_commandQueue){
        _commandQueue = [[NSMutableArray<CommandContext *> alloc] init];
    }
    return _commandQueue;
}

- (GCDObjectTimer *)commandQueueTimer {
    if (!_commandQueueTimer) {
        _commandQueueTimer = [[GCDObjectTimer alloc] init];
    }
    return _commandQueueTimer;
}

- (GCDObjectTimer *)checkCommandQueueCompleteTimer {
    if (!_checkCommandQueueCompleteTimer) {
        _checkCommandQueueCompleteTimer = [[GCDObjectTimer alloc] init];
    }
    return _checkCommandQueueCompleteTimer;
}

- (GCDObjectTimer *)scanTimeoutTimer {
    if (!_scanTimeoutTimer) {
        _scanTimeoutTimer = [[GCDObjectTimer alloc] init];
    }
    return _scanTimeoutTimer;
}

- (GCDObjectTimer *)apDeviceDiscoverTimer {
    if (!_apDeviceDiscoverTimer) {
        _apDeviceDiscoverTimer = [[GCDObjectTimer alloc] init];
    }
    return _apDeviceDiscoverTimer;
}

- (GCDObjectTimer *)heartMonitorTimer {
    if (!_heartMonitorTimer) {
        _heartMonitorTimer = [[GCDObjectTimer alloc] init];
    }
    return _heartMonitorTimer;
}

- (GCDObjectTimer *)waitResponseTimer{
    if (!_waitResponseTimer) {
        _waitResponseTimer = [[GCDObjectTimer alloc] init];
    }
    return _waitResponseTimer;
}

- (GCDObjectTimer *)networkConfigurationTimeoutTimer {
    if (!_networkConfigurationTimeoutTimer) {
        _networkConfigurationTimeoutTimer = [[GCDObjectTimer alloc] init];
    }
    return _networkConfigurationTimeoutTimer;
}

- (CommandCallback *)commandCallback{
    if(!_commandCallback){
        _commandCallback = [[CommandCallback alloc] initCommandCallback:self];
    }
    return _commandCallback;
}

- (DataObjCallback *)dataObjCallback{
    if(!_dataObjCallback){
        _dataObjCallback = [[DataObjCallback alloc] initDataObjCallback:self];
    }
    return _dataObjCallback;
}

- (NSMutableArray<id<CentralManagerDelegate>> *)centralManagerdelegates{
    if(!_centralManagerdelegates){
        _centralManagerdelegates = [NSMutableArray array];
    }
    return _centralManagerdelegates;
}

- (void)registerCentralManagerDelegate:(id<CentralManagerDelegate>)delegate {
    if (![self.centralManagerdelegates containsObject:delegate]) {
        [self.centralManagerdelegates addObject:delegate];
    }
}

- (void)unregisterCentralManagerDelegate:(id<CentralManagerDelegate>)delegate {
    [self.centralManagerdelegates removeObject:delegate];
}

- (void)notifyCentralManagerDidUpdateState:(CBCentralManager *)central {
    for (id<CentralManagerDelegate> delegate in self.centralManagerdelegates) {
        if ([delegate respondsToSelector:@selector(onCentralManagerDidUpdateState:)]) {
            [delegate onCentralManagerDidUpdateState:central];
        }
    }
}


- (NSMutableArray<id<DeviceDiscoveryDelegate>> *)deviceDiscoveryDelegates {
    if (!_deviceDiscoveryDelegates) {
        _deviceDiscoveryDelegates = [NSMutableArray array];
    }
    return _deviceDiscoveryDelegates;
}

- (void)registerDeviceDiscoveryDelegate:(id<DeviceDiscoveryDelegate>)delegate {
    if (![self.deviceDiscoveryDelegates containsObject:delegate]) {
        [self.deviceDiscoveryDelegates addObject:delegate];
    }
}

- (void)unregisterDeviceDiscoveryDelegate:(id<DeviceDiscoveryDelegate>)delegate {
    [self.deviceDiscoveryDelegates removeObject:delegate];
}

- (void)notifyDeviceStartDiscover {
    for (id<DeviceDiscoveryDelegate> delegate in self.deviceDiscoveryDelegates) {
        if ([delegate respondsToSelector:@selector(onDeviceStartDiscover)]) {
            [delegate onDeviceStartDiscover];
        }
    }
}

- (void)notifyDeviceDiscover:(Device *)device {
    for (id<DeviceDiscoveryDelegate> delegate in self.deviceDiscoveryDelegates) {
        if ([delegate respondsToSelector:@selector(onDeviceDiscoverDevice:)]) {
            [delegate onDeviceDiscoverDevice:device];
        }
    }
}

- (void)notifyDeviceStopDiscover {
    for (id<DeviceDiscoveryDelegate> delegate in self.deviceDiscoveryDelegates) {
        if ([delegate respondsToSelector:@selector(onDeviceStopDiscover)]) {
            [delegate onDeviceStopDiscover];
        }
    }
}


- (NSMutableArray<id<ConnModelDiscoveryDelegate>> *)connModelDiscoveryDelegates {
    if (!_connModelDiscoveryDelegates) {
        _connModelDiscoveryDelegates = [NSMutableArray array];
    }
    return _connModelDiscoveryDelegates;
}

- (void)registerConnModelDiscoveryDelegate:(id<ConnModelDiscoveryDelegate>)delegate {
    if (![self.connModelDiscoveryDelegates containsObject:delegate]) {
        [self.connModelDiscoveryDelegates addObject:delegate];
    }
}

- (void)unregisterConnModelDiscoveryDelegate:(id<ConnModelDiscoveryDelegate>)delegate {
    [self.connModelDiscoveryDelegates removeObject:delegate];
}

- (void)notifyConnModelStartDiscover {
    for (id<ConnModelDiscoveryDelegate> delegate in self.connModelDiscoveryDelegates) {
        if ([delegate respondsToSelector:@selector(onConnModelStartDiscover)]) {
            [delegate onConnModelStartDiscover];
        }
    }
}

- (void)notifyConnModelDiscover:(ConnModel *)model {
    for (id<ConnModelDiscoveryDelegate> delegate in self.connModelDiscoveryDelegates) {
        if ([delegate respondsToSelector:@selector(onConnModelDiscover:)]) {
            [delegate onConnModelDiscover:model];
        }
    }
}

- (void)notifyConnModelStopDiscover {
    for (id<ConnModelDiscoveryDelegate> delegate in self.connModelDiscoveryDelegates) {
        if ([delegate respondsToSelector:@selector(onConnModelStopDiscover)]) {
            [delegate onConnModelStopDiscover];
        }
    }
}


- (NSMutableArray<id<DeviceConnectionDelegate>> *)deviceConnectionDelegates {
    if (!_deviceConnectionDelegates) {
        _deviceConnectionDelegates = [NSMutableArray array];
    }
    return _deviceConnectionDelegates;
}

- (void)registerDeviceConnectionDelegate:(id<DeviceConnectionDelegate>)delegate {
    if (![self.deviceConnectionDelegates containsObject:delegate]) {
        [self.deviceConnectionDelegates addObject:delegate];
    }
}

- (void)unregisterDeviceConnectionDelegate:(id<DeviceConnectionDelegate>)delegate {
    [self.deviceConnectionDelegates removeObject:delegate];
}

- (void)notifyDeviceConnectStart {
    for (id<DeviceConnectionDelegate> delegate in self.deviceConnectionDelegates) {
        if ([delegate respondsToSelector:@selector(onDeviceConnectStart)]) {
            [delegate onDeviceConnectStart];
        }
    }
}

- (void)notifyDeviceConnectSucceed {
    for (id<DeviceConnectionDelegate> delegate in self.deviceConnectionDelegates) {
        if ([delegate respondsToSelector:@selector(onDeviceConnectSucceed)]) {
            [delegate onDeviceConnectSucceed];
        }
    }
}

- (void)notifyDeviceDisconnect {
    for (id<DeviceConnectionDelegate> delegate in self.deviceConnectionDelegates) {
        if ([delegate respondsToSelector:@selector(onDeviceDisconnect)]) {
            [delegate onDeviceDisconnect];
        }
    }
}

- (void)notifyDeviceConnectFail {
    for (id<DeviceConnectionDelegate> delegate in self.deviceConnectionDelegates) {
        if ([delegate respondsToSelector:@selector(onDeviceConnectFail)]) {
            [delegate onDeviceConnectFail];
        }
    }
}


- (NSMutableArray<id<DataProgressDelegate>> *)dataProgressDelegates {
    if (!_dataProgressDelegates) {
        _dataProgressDelegates = [NSMutableArray array];
    }
    return _dataProgressDelegates;
}

- (void)registerDataProgressDelegate:(id<DataProgressDelegate>)delegate {
    if (![self.dataProgressDelegates containsObject:delegate]) {
        [self.dataProgressDelegates addObject:delegate];
    }
}

- (void)unregisterDataProgressDelegate:(id<DataProgressDelegate>)delegate {
    [self.dataProgressDelegates removeObject:delegate];
}

- (void)notifyDataProgressStart:(CGFloat)size progress:(CGFloat)progress progressPrecision:(NSInteger)progressPrecision startTime:(NSTimeInterval)startTime {
    for (id<DataProgressDelegate> delegate in self.dataProgressDelegates) {
        if ([delegate respondsToSelector:@selector(onDataProgressStart:progress:progressPrecision:startTime:)]) {
            [delegate onDataProgressStart:size progress:progress progressPrecision:progressPrecision startTime:startTime];
        }
    }
}

- (void)notifyDataProgress:(CGFloat)size progress:(CGFloat)progress progressPrecision:(NSInteger)progressPrecision startTime:(NSTimeInterval)startTime currentTime:(NSTimeInterval)currentTime {
    for (id<DataProgressDelegate> delegate in self.dataProgressDelegates) {
        if ([delegate respondsToSelector:@selector(onDataProgress:progress:progressPrecision:startTime:currentTime:)]) {
            [delegate onDataProgress:size progress:progress progressPrecision:progressPrecision startTime:startTime currentTime:currentTime];
        }
    }
}

- (void)notifyDataProgressFinish:(CGFloat)size progress:(CGFloat)progress progressPrecision:(NSInteger)progressPrecision startTime:(NSTimeInterval)startTime currentTime:(NSTimeInterval)currentTime {
    for (id<DataProgressDelegate> delegate in self.dataProgressDelegates) {
        if ([delegate respondsToSelector:@selector(onDataProgressFinish:progress:progressPrecision:startTime:currentTime:)]) {
            [delegate onDataProgressFinish:size progress:progress progressPrecision:progressPrecision startTime:startTime currentTime:currentTime];
        }
    }
}

- (void)notifyDataProgressError:(NSError *)error {
    for (id<DataProgressDelegate> delegate in self.dataProgressDelegates) {
        if ([delegate respondsToSelector:@selector(onDataProgressError:)]) {
            [delegate onDataProgressError:error];
        }
    }
}


- (NSMutableArray<id<DeviceReadMsgDelegate>> *)deviceReadMsgDelegates {
    if (!_deviceReadMsgDelegates) {
        _deviceReadMsgDelegates = [NSMutableArray array];
    }
    return _deviceReadMsgDelegates;
}

- (void)registerDeviceReadMsgDelegate:(id<DeviceReadMsgDelegate>)delegate {
    if (![self.deviceReadMsgDelegates containsObject:delegate]) {
        [self.deviceReadMsgDelegates addObject:delegate];
    }
}

- (void)unregisterDeviceReadMsgDelegate:(id<DeviceReadMsgDelegate>)delegate {
    [self.deviceReadMsgDelegates removeObject:delegate];
}

- (void)notifyReadBatteryForDevice:(Device *)device batteryLevel:(int)batteryLevel {
    for (id<DeviceReadMsgDelegate> delegate in self.deviceReadMsgDelegates) {
        if ([delegate respondsToSelector:@selector(onReadBatteryForDevice:batteryLevel:)]) {
            [delegate onReadBatteryForDevice:device batteryLevel:batteryLevel];
        }
    }
}

- (void)notifyReadParameterForDevice:(Device *)device headValue:(int)headValue lPix:(int)lPix pPix:(int)pPix distance:(int)distance {
    for (id<DeviceReadMsgDelegate> delegate in self.deviceReadMsgDelegates) {
        if ([delegate respondsToSelector:@selector(onReadParameterForDevice:headValue:lPix:pPix:distance:)]) {
            [delegate onReadParameterForDevice:device headValue:headValue lPix:lPix pPix:pPix distance:distance];
        }
    }
}

- (void)notifyReadCirculationRepeatForDevice:(Device *)device circulationTime:(int)circulationTime repeatTime:(int)repeatTime {
    for (id<DeviceReadMsgDelegate> delegate in self.deviceReadMsgDelegates) {
        if ([delegate respondsToSelector:@selector(onReadCirculationRepeatForDevice:circulationTime:repeatTime:)]) {
            [delegate onReadCirculationRepeatForDevice:device circulationTime:circulationTime repeatTime:repeatTime];
        }
    }
}

- (void)notifyReadDirectionForDevice:(Device *)device direction:(int)direction printHeadDirection:(int)printHeadDirection {
    for (id<DeviceReadMsgDelegate> delegate in self.deviceReadMsgDelegates) {
        if ([delegate respondsToSelector:@selector(onReadDirectionForDevice:direction:printHeadDirection:)]) {
            [delegate onReadDirectionForDevice:device direction:direction printHeadDirection:printHeadDirection];
        }
    }
}

- (void)notifyReadDeviceInfoForDevice:(Device *)device deviceId:(NSString *)deviceId name:(NSString *)name mcuVersion:(NSString *)mcuVersion date:(NSString *)date {
    for (id<DeviceReadMsgDelegate> delegate in self.deviceReadMsgDelegates) {
        if ([delegate respondsToSelector:@selector(onReadDeviceInfoForDevice:deviceId:name:mcuVersion:date:)]) {
            [delegate onReadDeviceInfoForDevice:device deviceId:deviceId name:name mcuVersion:mcuVersion date:date];
        }
    }
}

- (void)notifyReadPrinterHeadTemperatureForDevice:(Device *)device index:(int)index tempGet:(int)tempGet tempSet:(int)tempSet {
    for (id<DeviceReadMsgDelegate> delegate in self.deviceReadMsgDelegates) {
        if ([delegate respondsToSelector:@selector(onReadPrinterHeadTemperatureForDevice:index:tempGet:tempSet:)]) {
            [delegate onReadPrinterHeadTemperatureForDevice:device index:index tempGet:tempGet tempSet:tempSet];
        }
    }
}

- (void)notifyReadSilentStateForDevice:(Device *)device silentState:(BOOL)silentState{
    for (id<DeviceReadMsgDelegate> delegate in self.deviceReadMsgDelegates) {
        if ([delegate respondsToSelector:@selector(onReadSilentStateForDevice:silentState:)]) {
            [delegate onReadSilentStateForDevice:device silentState:silentState];
        }
    }
}

- (void)notifyReadAutoPowerOffStateForDevice:(Device *)device autoPowerOff:(BOOL)autoPowerOff{
    for (id<DeviceReadMsgDelegate> delegate in self.deviceReadMsgDelegates) {
        if ([delegate respondsToSelector:@selector(onReadAutoPowerOffStateForDevice:autoPowerOff:)]) {
            [delegate onReadAutoPowerOffStateForDevice:device autoPowerOff:autoPowerOff];
        }
    }
}


- (NSMutableArray<id<PrintDelegate>> *)printDelegates {
    if (!_printDelegates) {
        _printDelegates = [NSMutableArray array];
    }
    return _printDelegates;
}

- (void)registerPrintDelegate:(id<PrintDelegate>)delegate {
    if (![self.printDelegates containsObject:delegate]) {
        [self.printDelegates addObject:delegate];
    }
}

- (void)unregisterPrintDelegate:(id<PrintDelegate>)delegate {
    [self.printDelegates removeObject:delegate];
}

- (void)notifyPrintStart:(Device *)device beginIndex:(int)beginIndex endIndex:(int)endIndex currentIndex:(int)currentIndex {
    for (id<PrintDelegate> delegate in self.printDelegates) {
        if ([delegate respondsToSelector:@selector(onPrintStartForDevice:beginIndex:endIndex:currentIndex:)]) {
            [delegate onPrintStartForDevice:device beginIndex:beginIndex endIndex:endIndex currentIndex:currentIndex];
        }
    }
}

- (void)notifyPrintComplete:(Device *)device beginIndex:(int)beginIndex endIndex:(int)endIndex currentIndex:(int)currentIndex {
    for (id<PrintDelegate> delegate in self.printDelegates) {
        if ([delegate respondsToSelector:@selector(onPrintCompleteForDevice:beginIndex:endIndex:currentIndex:)]) {
            [delegate onPrintCompleteForDevice:device beginIndex:beginIndex endIndex:endIndex currentIndex:currentIndex];
        }
    }
}


- (NSMutableArray<id<DistNetDeviceDiscoveryDelegate>> *)distNetDeviceDelegates {
    if (!_distNetDeviceDelegates) {
        _distNetDeviceDelegates = [NSMutableArray array];
    }
    return _distNetDeviceDelegates;
}

- (void)registerDistNetDeviceDiscoveryDelegate:(id<DistNetDeviceDiscoveryDelegate>)delegate {
    if (![self.distNetDeviceDelegates containsObject:delegate]) {
        [self.distNetDeviceDelegates addObject:delegate];
    }
}

- (void)unregisterDistNetDeviceDiscoveryDelegate:(id<DistNetDeviceDiscoveryDelegate>)delegate {
    [self.distNetDeviceDelegates removeObject:delegate];
}

- (void)notifyDistNetDeviceDiscoverStart {
    for (id<DistNetDeviceDiscoveryDelegate> delegate in self.distNetDeviceDelegates) {
        if ([delegate respondsToSelector:@selector(onDistNetDeviceDiscoverStart)]) {
            [delegate onDistNetDeviceDiscoverStart];
        }
    }
}

- (void)notifyDistNetDeviceDiscover:(DistNetDevice *)device {
    for (id<DistNetDeviceDiscoveryDelegate> delegate in self.distNetDeviceDelegates) {
        if ([delegate respondsToSelector:@selector(onDistNetDeviceDiscover:)]) {
            [delegate onDistNetDeviceDiscover:device];
        }
    }
}

- (void)notifyDistNetDeviceDiscoverCancel {
    for (id<DistNetDeviceDiscoveryDelegate> delegate in self.distNetDeviceDelegates) {
        if ([delegate respondsToSelector:@selector(onDistNetDeviceDiscoverCancel)]) {
            [delegate onDistNetDeviceDiscoverCancel];
        }
    }
}


- (NSMutableArray<id<DistributionNetworkDelegate>> *)networkDelegates {
    if (!_networkDelegates) {
        _networkDelegates = [NSMutableArray array];
    }
    return _networkDelegates;
}

- (void)registerNetworkDelegate:(id<DistributionNetworkDelegate>)delegate {
    if (![self.networkDelegates containsObject:delegate]) {
        [self.networkDelegates addObject:delegate];
    }
}

- (void)unregisterNetworkDelegate:(id<DistributionNetworkDelegate>)delegate {
    [self.networkDelegates removeObject:delegate];
}

- (void)notifyDistributionNetworkStart {
    for (id<DistributionNetworkDelegate> delegate in self.networkDelegates) {
        if ([delegate respondsToSelector:@selector(onDistributionNetworkStart)]) {
            [delegate onDistributionNetworkStart];
        }
    }
}

- (void)notifyDistributionNetworkSucceed:(Device *)device {
    for (id<DistributionNetworkDelegate> delegate in self.networkDelegates) {
        if ([delegate respondsToSelector:@selector(onDistributionNetworkSucceed:)]) {
            [delegate onDistributionNetworkSucceed:device];
        }
    }
}

- (void)notifyDistributionNetworkProgress:(CGFloat)progress {
    for (id<DistributionNetworkDelegate> delegate in self.networkDelegates) {
        if ([delegate respondsToSelector:@selector(onDistributionNetworkProgress:)]) {
            [delegate onDistributionNetworkProgress:progress];
        }
    }
}

- (void)notifyDistributionNetworkFail {
    for (id<DistributionNetworkDelegate> delegate in self.networkDelegates) {
        if ([delegate respondsToSelector:@selector(onDistributionNetworkFail)]) {
            [delegate onDistributionNetworkFail];
        }
    }
}

- (void)notifyDistributionNetworkTimeOut {
    for (id<DistributionNetworkDelegate> delegate in self.networkDelegates) {
        if ([delegate respondsToSelector:@selector(onDistributionNetworkTimeOut)]) {
            [delegate onDistributionNetworkTimeOut];
        }
    }
}


- (NSMutableArray<id<CommandWriteDelegate>> *)commandWriteDelegates {
    if (!_commandWriteDelegates) {
        _commandWriteDelegates = [NSMutableArray array];
    }
    return _commandWriteDelegates;
}

- (void)registerCommandWriteDelegate:(id<CommandWriteDelegate>)delegate {
    if (![self.commandWriteDelegates containsObject:delegate]) {
        [self.commandWriteDelegates addObject:delegate];
    }
}

- (void)unregisterCommandWriteDelegate:(id<CommandWriteDelegate>)delegate {
    [self.commandWriteDelegates removeObject:delegate];
}

- (void)notifyWriteCommandSuccess:(Command *)command withObject:(NSObject *)object {
    for (id<CommandWriteDelegate> delegate in self.commandWriteDelegates) {
        if ([delegate respondsToSelector:@selector(onWriteCommandSuccess:withObject:)]) {
            [delegate onWriteCommandSuccess:command withObject:object];
        }
    }
}

- (void)notifyWriteCommandError:(Command *)command withErrorMsg:(NSString *)errorMsg {
    for (id<CommandWriteDelegate> delegate in self.commandWriteDelegates) {
        if ([delegate respondsToSelector:@selector(onWriteCommandError:withErrorMsg:)]) {
            [delegate onWriteCommandError:command withErrorMsg:errorMsg];
        }
    }
}


- (NSMutableArray<id<DataWriteDelegate>> *)dataWriteDelegates {
    if (!_dataWriteDelegates) {
        _dataWriteDelegates = [NSMutableArray array];
    }
    return _dataWriteDelegates;
}

- (void)registerDataWriteDelegate:(id<DataWriteDelegate>)delegate {
    if (![self.dataWriteDelegates containsObject:delegate]) {
        [self.dataWriteDelegates addObject:delegate];
    }
}

- (void)unregisterDataWriteDelegate:(id<DataWriteDelegate>)delegate {
    [self.dataWriteDelegates removeObject:delegate];
}

- (void)notifyDataWriteSuccess:(DataObj *)dataObj withObject:(NSObject *)object {
    for (id<DataWriteDelegate> delegate in self.dataWriteDelegates) {
        if ([delegate respondsToSelector:@selector(onDataWriteSuccess:withObject:)]) {
            [delegate onDataWriteSuccess:dataObj withObject:object];
        }
    }
}

- (void)notifyDataWriteError:(DataObj *)dataObj withErrorMsg:(NSString *)errorMsg {
    for (id<DataWriteDelegate> delegate in self.dataWriteDelegates) {
        if ([delegate respondsToSelector:@selector(onDataWriteError:withErrorMsg:)]) {
            [delegate onDataWriteError:dataObj withErrorMsg:errorMsg];
        }
    }
}


- (NSMutableArray<BasePacket *> *)packets{
    if(!_packets){
        _packets = [[NSMutableArray<BasePacket *> alloc] initWithObjects:self.multiRowDataPacket,self.logoDataPacket,self.otaDataPacket, nil];
    }
    return _packets;
}

- (MultiRowDataPacket *)multiRowDataPacket{
    if(!_multiRowDataPacket){
        _multiRowDataPacket = [[MultiRowDataPacket alloc] init];
    }
    return _multiRowDataPacket;
}

- (LogoDataPacket *)logoDataPacket{
    if(!_logoDataPacket){
        _logoDataPacket = [[LogoDataPacket alloc] init];
    }
    return _logoDataPacket;
}

- (OtaDataPacket *)otaDataPacket{
    if(!_otaDataPacket){
        _otaDataPacket = [[OtaDataPacket alloc] init];
    }
    return _otaDataPacket;
}

-(void)startPacket:(BasePacket*)packet{
    for (BasePacket *_packet in self.packets){
        if (packet != _packet){
            _packet.start = NO;
        }
    }
    packet.start = YES;
}

-(void)cancelAllPacketStart{
    for (BasePacket *packet in self.packets){
        packet.start = NO;
    }
}

-(BOOL)hasPacketStart{
    BOOL isStart = NO;
    for (BasePacket *packet in self.packets){
        if (packet.start){
            isStart = YES;
            break;
        }
    }
    return isStart;
}

- (instancetype)init
{
    self = [super init];
    if (self) {
         [self config];
    }
    return self;
}

+(ConnectManager *)share
{

    static dispatch_once_t disOnce;
    dispatch_once(&disOnce, ^{

        share=[[ConnectManager alloc] init];
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

#pragma mark - peripheral <外设>相关方法<开始>位置

//********************************************************
//                作为外设相关的方法 begin
//********************************************************

-(void)config{
    
    //初始化锁对象
    _lock = [[NSLock alloc] init];
    _receiveLock = [[NSLock alloc] init];
    //实例化baby
    self.baby = [BabyBluetooth shareBabyBluetooth];
    [self babyCenterDelegate];
    
    self.isSendingData = NO;

    TCPClient *client = [[TCPClient alloc] init];
    client.delegate = self;
    client.isDebug = NO;
    client.reconnectCount = 3;
    self.client = client;
    
    _scanType = ScanTypeIdle;
    
    self.N_Index = 0;
    //默认为一次连续发送完毕
    self.dataSendType = DataSendOnceContinuous;
    
    self.distributionNetworkUdpServer = [[UDPServier alloc] init];
    [self distributionNetworkUdpServerDelegate];

    self.discoverUdpServer = [[UDPServier alloc] init];
    [self discoverUdpServerDelegate];
}

- (BOOL)isScanTypeIdle{
    return self.scanType == ScanTypeIdle;
}
- (BOOL)isScanTypeBle{
    return self.scanType == ScanTypeBle;
}
- (BOOL)isScanTypeDNW{
    return self.scanType == ScanTypeDNW;
}
- (BOOL)isScanTypeConnModel{
    return self.scanType == ScanTypeConnModel;
}

- (BOOL)isConnectTypeIdle{
    return self.connectType == ConnectTypeIdle;
}
- (BOOL)isConnectTypeBle{
    return self.connectType == ConnectTypeBle;
}
- (BOOL)isConnectTypeNetWork{
    return self.connectType == ConnectTypeNetWork;
}
- (BOOL)isConnectTypeDNW{
    return self.connectType == ConnectTypeDNW;
}
// udp监听类型判断
- (BOOL)isUdpMonitorTypeIdle{
    return self.udpMonitorType == UdpMonitorTypeIdle;
}
- (BOOL)isUdpMonitorTypeWifi{
    return self.udpMonitorType == UdpMonitorTypeWifi;
}
- (BOOL)isUdpMonitorTypeDNW{
    return self.udpMonitorType == UdpMonitorTypeDNW;
}

/**
 *只扫描设备
 */
-(void)discoverBleDevice:(NSTimeInterval)scanTimeout{
    @synchronized (self.lock) {
        if(!self.isScanTypeIdle){
            RBQLog3(@"【discoverBleDevice】current scanType ->:%ld; isEnable:%@",self.scanType,self.isEnable?@"YES":@"NO");
            return;
        }
        [self localDiscoverPeripherals:ScanTypeBle scanTimeout:scanTimeout];
    }
}

/**
停止扫描
 */
- (void)cancelDiscoverBleDevice{
    @synchronized (self.lock) {
        if(!self.isScanTypeBle){
            RBQLog3(@"【cancelDiscoverBleDevice】current scanType ->:%ld; isEnable:%@",self.scanType,self.isEnable?@"YES":@"NO");
            return;
        }
        [self localCancelDiscoverPeripherals];
    }
}

/**
 *只扫描设备连接支持类型对象
 */
-(void)discoverConnModel:(NSTimeInterval)scanTimeout{
    @synchronized (self.lock) {
        if(!self.isScanTypeIdle){
            RBQLog3(@"【discoverConnModel】current scanType ->:%ld; isEnable:%@",self.scanType,self.isEnable?@"YES":@"NO");
            return;
        }
        [self localDiscoverPeripherals:ScanTypeConnModel scanTimeout:scanTimeout];
    }
}

/**
停止扫描
 */
- (void)cancelDiscoverConnModel{
    @synchronized (self.lock) {
        if(!self.isScanTypeConnModel){
            RBQLog3(@"【cancelDiscoverConnModel】current scanType ->:%ld; isEnable:%@",self.scanType,self.isEnable?@"YES":@"NO");
            return;
        }
        [self localCancelDiscoverPeripherals];
    }
}

-(void)localDiscoverPeripherals:(ScanType)bleScanType scanTimeout:(NSTimeInterval)scanTimeout{
    
    [self.scanTimeoutTimer clearScheduledTimer];
    
    _scanType = bleScanType;
    _scanTimeout = scanTimeout;
    //停止之前的连接
//    [baby cancelAllPeripheralsConnection];
    
    //扫描选项->CBCentralManagerScanOptionAllowDuplicatesKey:忽略同一个Peripheral端的多个发现事件被聚合成一个发现事件
    NSDictionary *scanForPeripheralsWithOptions = @{CBCentralManagerScanOptionAllowDuplicatesKey:@NO};
    //连接设备->
    [self.baby setBabyOptionsWithScanForPeripheralsWithOptions:scanForPeripheralsWithOptions connectPeripheralWithOptions:nil scanForPeripheralsWithServices:nil discoverWithServices:nil discoverWithCharacteristics:nil];
    self.baby.scanForPeripherals().begin();
    
    if (scanTimeout>0) {
        __weak typeof(self)  weakSelf = self;
        [self.scanTimeoutTimer scheduledGCDTimerWithSartTime:^{
            [weakSelf localScanTimeOut];
        } startTime:scanTimeout interval:0 repeats:NO];
    }
}

-(void)localCancelDiscoverPeripherals{
    
    [self.scanTimeoutTimer clearScheduledTimer];
    [self.baby cancelScan];
    self.scanTimeout = -1;
}

//执行连接超时的方法
-(void)localScanTimeOut{
    [self.scanTimeoutTimer clearScheduledTimer];
    [self.baby cancelScan];
}

- (BOOL)isConnected {
    @synchronized (self.lock) {
        if (!self.device) {
            return NO;
        }
        return self.device.isConnected;
    }
}

- (BOOL)isConnected:(Device *)device {
    @synchronized (self.lock) {
        if (!device) {
            return NO;
        }
        return device.isConnected;
    }
}

- (BOOL)isBleConnType{
    @synchronized (self.lock) {
        if (!self.device
            ||!self.device.peripheral) {
            return NO;
        }
        return self.device.isBleConnType;
    }
}

- (BOOL)isApConnType{
    @synchronized (self.lock) {
        if (!self.device) {
            return NO;
        }
        return self.device.isApConnType;
    }
}

- (BOOL)isWifiConnType{
    @synchronized (self.lock) {
        if(!self.device){
            return NO;
        }
        return self.device.isWifiConnType;
    }
}

- (BOOL)isApOrWifiConnType{
    @synchronized (self.lock) {
        if(!self.device){
            return NO;
        }
        return self.device.isApOrWifiConnType;
    }
}

- (BOOL)isEnable{
    @synchronized (self.lock) {
        if (@available(iOS 10.0, *)) {
            return [self.baby centralManager].state==CBManagerStatePoweredOn;
        } else {
    #pragma clang diagnostic push
    #pragma clang diagnostic ignored "-Wdeprecated-declarations"
            return [self.baby centralManager].state==CBCentralManagerStatePoweredOn;
    #pragma clang diagnostic pop
        }
    }
}

- (BOOL)isDiscoveringBleDevice{
    @synchronized (self.lock) {
        return [self.baby isScanning];
    }
}

- (void)connect:(Device *)device {
    
    @synchronized (self.lock) {
        
        if (!device) {
            return;
        }
        
        if (self.device
            &&self.device.isConnected) {
            return;
        }
        _device = device;
        if (self.isBleConnType) {
            _connectType = ConnectTypeBle;
            RBQLog3(@"【ConnectManager】连接 ble device; connectType:%ld",self.connectType)
            CBPeripheral *peripheral = self.device.peripheral;
            self.baby.having(peripheral).connectToPeripherals().discoverServices().discoverCharacteristics().readValueForCharacteristic().discoverDescriptorsForCharacteristic().readValueForDescriptors().begin();
            return;
        }
        if (self.isApOrWifiConnType) {
            _connectType = ConnectTypeNetWork;
            RBQLog3(@"【ConnectManager】连接 netWork device;connectType:%ld",self.connectType)
            __weak typeof(self)  weakSelf = self;
            dispatch_async(dispatch_get_main_queue(), ^{
                if (weakSelf.onDeviceConnectStart) {
                    weakSelf.onDeviceConnectStart();
                }
                [weakSelf notifyDeviceConnectStart];
            });
            [self.client connectHost:self.device.ip port:self.device.port];
        }
        
    }
}

- (void)disConnect {
    
    @synchronized (self.lock) {
        
        if (!self.device) {
            return;
        }
        if (self.isBleConnType) {
            CBPeripheral *peripheral = self.device.peripheral;
            [self.baby cancelPeripheralConnection:peripheral];
            return;
        }
        if (self.isApOrWifiConnType) {
            [self stopMonitorHeartData];
            [self.client disConnectWithCompletion:^{
                
                RBQLog3(@"【ConnectManager】---disConnectWithCompletion---");
                // 主要是不给执行断开的事件，所以这里主动调用了
//                weakSelf.device.isConnected = NO;
//                strongSelf->_connectType = ConnectTypeIdle;
//                [weakSelf stopMonitorHeartData];
//                [weakSelf clearCommandQueue];
//                dispatch_async(dispatch_get_main_queue(), ^{
//                    [weakSelf notifyDeviceDisconnect];
//                });
            }];
        }
        
    }
}

- (Device *)connectedDevice{
    @synchronized (self.lock) {
        if (!self.device||!self.device.isConnected) {
            return nil;
        }
        return self.device;
    }
}

#pragma mark 配网相关代码

/**搜索配网设备*/
-(void)discoverDistNetDevice:(NSTimeInterval)scanTimeout{
    @synchronized (self.lock) {
        if(!self.isScanTypeIdle){
            RBQLog3(@"【discoverDistNetDevice】current scanType ->:%ld; isEnable:%@",self.scanType,self.isEnable?@"YES":@"NO");
            return;
        }
        [self localDiscoverPeripherals:ScanTypeDNW scanTimeout:scanTimeout];
    }
}
/**取消配网设备搜索*/
-(void)cancelDiscoverDistNetDevice{
    @synchronized (self.lock) {
        if(!self.isScanTypeDNW){
            RBQLog3(@"【cancelDiscoverDistNetDevice】current scanType ->:%ld; isEnable:%@",self.scanType,self.isEnable?@"YES":@"NO");
            return;
        }
        [self localCancelDiscoverPeripherals];
    }
}
/**启动配网*/
- (void)distributionNetwork:(DistNetDevice *)distNetDevice ssid:(NSString *)ssid pw:(NSString *)password timeout:(NSTimeInterval)timeoutValue{
    @synchronized (self.lock) {
        if (!self.isUdpMonitorTypeIdle) {
            RBQLog3(@"【distributionNetwork】current udpMonitorType ->:%ld",self.udpMonitorType);
            return;
        }
        if (!distNetDevice||!distNetDevice.peripheral) {
            if (self.onDistributionNetworkFail) {
                self.onDistributionNetworkFail();
            }
            [self notifyDistributionNetworkFail];
            return;
        }
        /**配网的时候断开之前的链接*/
        if (self.isConnected) {
            [self disConnect];
        }
        _connectType = ConnectTypeDNW;
        self.sendedNetworkConfigurationSuccess = NO;
        self.networkConfigurationProgress = 0;
        if (self.onDistributionNetworkStart) {
            self.onDistributionNetworkStart();
        }
        [self notifyDistributionNetworkStart];
        self.ssid = ssid;
        self.password = password;
        _disNetDevice = distNetDevice;
        RBQLog3(@"开始配网，配网设备的mac:%@",distNetDevice.mac);
        self.networkConfigurationTimeInterval = timeoutValue/100.0f;
        __weak typeof(self)  weakSelf = self;
        [self.networkConfigurationTimeoutTimer scheduledGCDTimerWithSartTime:^{
            [weakSelf updateDistributionNetworkProgress];
        } startTime:0 interval:self.networkConfigurationTimeInterval repeats:YES];
        
        self.baby.having(distNetDevice.peripheral).connectToPeripherals().discoverServices().discoverCharacteristics().begin();
    }
}

-(void)updateDistributionNetworkProgress{
    
    __weak typeof(self)  weakSelf = self;
    __strong __typeof(weakSelf) strongSelf = weakSelf;
    
    self.networkConfigurationProgress = self.networkConfigurationProgress + 1;
    if (self.networkConfigurationProgress>=100.0f) {
        self.networkConfigurationProgress = 100.0f;
        //配网超时
        [self.networkConfigurationTimeoutTimer clearScheduledTimer];
        [self.distributionNetworkUdpServer stopUdpSocketMonitoring];
        [self cancelDiscoverDistNetDevice];
        CGFloat progress = self.networkConfigurationProgress/100.0;
        if (self.onDistributionNetworkProgress) {
            self.onDistributionNetworkProgress(progress);
        }
        [self notifyDistributionNetworkProgress:progress];
        dispatch_after(dispatch_time(DISPATCH_TIME_NOW, 0.3), dispatch_get_main_queue(), ^{
            
            // udp监听置空闲
            strongSelf->_udpMonitorType = UdpMonitorTypeIdle;
            
            [weakSelf.networkConfigurationTimeoutTimer clearScheduledTimer];
            if (weakSelf.onDistributionNetworkTimeOut) {
                weakSelf.onDistributionNetworkTimeOut();
            }
            [weakSelf notifyDistributionNetworkTimeOut];
        });
        
    }else{
        
        CGFloat progress = self.networkConfigurationProgress/100.0;
        dispatch_async(dispatch_get_main_queue(), ^{
            if (weakSelf.onDistributionNetworkProgress) {
                weakSelf.onDistributionNetworkProgress(progress);
            }
            [weakSelf notifyDistributionNetworkProgress:progress];
        });
    }
}

-(void)discoverWifiDevice:(NSTimeInterval)scanTimeout{
    @synchronized (self.lock) {
        if(!self.isUdpMonitorTypeIdle){
            RBQLog3(@"【discoverWifiDevice】current udpMonitorType ->:%ld",self.udpMonitorType);
            return;
        }
        _udpMonitorType = UdpMonitorTypeWifi;
        RBQLog3(@"【discoverWifiDevice】scanTimeout:%f",scanTimeout);
        __weak typeof(self) weakSelf = self;
        dispatch_async(dispatch_get_main_queue(), ^{
            if (weakSelf.onDeviceStartDiscover) {
                weakSelf.onDeviceStartDiscover();
            }
            [weakSelf notifyDeviceStartDiscover];
        });
        [self.distributionNetworkUdpServer stopUdpSocketMonitoring];
        [self.discoverUdpServer startUdpSocketMonitoring];
        
        [self.scanTimeoutTimer clearScheduledTimer];
        if (scanTimeout>0) {
            __weak typeof(self)  weakSelf = self;
            [self.scanTimeoutTimer scheduledGCDTimerWithSartTime:^{
                [weakSelf cancelDiscoverWifiDevice];
            } startTime:scanTimeout interval:0 repeats:NO];
        }
    }
}

-(void)cancelDiscoverWifiDevice{
    @synchronized (self.lock) {
        if(!self.isUdpMonitorTypeWifi){
            return;
        }
        RBQLog3(@"【cancelDiscoverWifiDevice】");
        _udpMonitorType = UdpMonitorTypeIdle;
        [self.scanTimeoutTimer clearScheduledTimer];
        [self.discoverUdpServer stopUdpSocketMonitoring];
        __weak typeof(self) weakSelf = self;
        dispatch_async(dispatch_get_main_queue(), ^{
            if (weakSelf.onDeviceStopDiscover) {
                weakSelf.onDeviceStopDiscover();
            }
            [weakSelf notifyDeviceStopDiscover];
        });
    }
}

-(void)distributionNetworkUdpServerDelegate{
    
    __weak typeof(self)  weakSelf = self;
    __strong __typeof(weakSelf) strongSelf = weakSelf;
    self.distributionNetworkUdpServer.onReceiveWifiRomoteModel = ^(WifiRomoteModel * _Nonnull wifiRomoteModel) {
      
        @try {
            
            RBQLog3(@"~配网监听到【wifi设备】name:%@;ip:%@;port:%d;mac:%@ ~",wifiRomoteModel.name,wifiRomoteModel.ip,wifiRomoteModel.port,wifiRomoteModel.mac);
            
            if(!weakSelf.isUdpMonitorTypeDNW
               &&weakSelf.disNetDevice
               &&![weakSelf.disNetDevice.mac isEqualToString:wifiRomoteModel.mac]){
                return;
            }
            
            strongSelf->_udpMonitorType = UdpMonitorTypeIdle;
            
            //这里的支持类型以及别名都采用配网对象disNetDevice的
            Device *device = [[Device alloc] initDeviceWithWifi:wifiRomoteModel.name ip:wifiRomoteModel.ip mac:wifiRomoteModel.mac port:wifiRomoteModel.port peripheral:weakSelf.disNetDevice.peripheral localName:weakSelf.disNetDevice.localName connTypes:weakSelf.disNetDevice.connTypes firmwareConfigs:weakSelf.disNetDevice.firmwareConfigs aliases:weakSelf.disNetDevice.aliases];
            
            RBQLog3(@" 🎉 配网成功 -->【设备】name:%@;ip:%@;port:%d;mac:%@🎉 将udpMonitorType置为空闲",wifiRomoteModel.name,wifiRomoteModel.ip,wifiRomoteModel.port,wifiRomoteModel.mac);
            
            /**配网成功*/
            if (!weakSelf.sendedNetworkConfigurationSuccess) {
                [weakSelf.networkConfigurationTimeoutTimer clearScheduledTimer];
                weakSelf.sendedNetworkConfigurationSuccess = YES;
                [weakSelf.distributionNetworkUdpServer stopUdpSocketMonitoring];
                /**延迟结束事件*/
                dispatch_after(dispatch_time(DISPATCH_TIME_NOW, 1), dispatch_get_main_queue(), ^{
                    
                    if (weakSelf.onDistributionNetworkSucceed) {
                        weakSelf.onDistributionNetworkSucceed(device);
                    }
                    [weakSelf notifyDistributionNetworkSucceed:device];
                });
            }
            
        } @catch (NSException *exception) {
            RBQLog3(@"异常名称: %@; 异常原因: %@; 用户信息: %@; 调用栈: %@", exception.name,exception.reason,exception.userInfo,exception.callStackSymbols);
        } @finally {
            
        }
        
    };
    
}

-(void)discoverUdpServerDelegate{
    
    __weak typeof(self)  weakSelf = self;
    self.discoverUdpServer.onReceiveWifiRomoteModel = ^(WifiRomoteModel * _Nonnull wifiRomoteModel) {
      
        @try {
            
            NSUInteger connTypes = 0;
            NSString *aliases = nil;
            NSDictionary *firmwareConfigs;
            // B为inksi-01中间的一个过渡版本
            if(wifiRomoteModel.model&&[wifiRomoteModel.model isEqualToString:@"B"]){
                //过渡版本，所以这里connTypes没有去调用专门统一的方法
                connTypes = ConnTypeBLE|ConnTypeAP|ConnTypeWiFi;
                firmwareConfigs = [weakSelf inksi01FirmwareConfigs];
                aliases = wifiRomoteModel.mac && wifiRomoteModel.mac.length>4 ? [wifiRomoteModel.mac substringFromIndex:wifiRomoteModel.mac.length - 4] : @"";
            }else if (wifiRomoteModel.model&&[wifiRomoteModel.model isEqualToString:@"BX20"]){
                // inksi-01的最终版本 BX20 代表机器型号，这里的 firmwareConfigs，对于连接方式这里既然监听到了广播，毫无疑问，这个时候是wifi
                connTypes = ConnTypeBLE|ConnTypeWiFi;
                firmwareConfigs = [weakSelf inksi01FirmwareConfigs];
            }
            if(!firmwareConfigs){
                firmwareConfigs = @{};
            }
            Device *device = [[Device alloc] initDeviceWithWifi:wifiRomoteModel.name ip:wifiRomoteModel.ip mac:wifiRomoteModel.mac port:wifiRomoteModel.port peripheral:nil localName:nil connTypes:connTypes firmwareConfigs:firmwareConfigs aliases:aliases];
            RBQLog3(@" ~ 扫描发现 -->【wifi设备】wifiRomoteModel->%@",wifiRomoteModel.description);
            dispatch_async(dispatch_get_main_queue(), ^{
                if (weakSelf.onDeviceDiscovered) {
                    weakSelf.onDeviceDiscovered(device);
                }
                [weakSelf notifyDeviceDiscover:device];
            });
            
        } @catch (NSException *exception) {
            
        } @finally {
            
        }
        
    };
}

-(void)discoverApDevice:(NSTimeInterval)scanTimeout {
    @synchronized (self.lock) {
        [self.scanTimeoutTimer clearScheduledTimer];
        [self localDiscoverApDevice];
        if (scanTimeout>0) {
            __weak typeof(self) weakSelf = self;
            [self.scanTimeoutTimer scheduledGCDTimerWithSartTime:^{
                [weakSelf cancelDiscoverApDevice];
            } startTime:scanTimeout interval:0 repeats:NO];
        }
    }
}

-(void)localDiscoverApDevice{
    @synchronized (self.lock) {
        __weak typeof(self)  weakSelf = self;
        [self.apDeviceDiscoverTimer scheduledGCDTimerWithSartTime:^{
            [weakSelf fetchSSID];
        } startTime:0 interval:1.0f repeats:YES];
    }
}

-(void)cancelDiscoverApDevice {
    @synchronized (self.lock) {
        [self.apDeviceDiscoverTimer clearScheduledTimer];
        [self.scanTimeoutTimer clearScheduledTimer];
    }
}

- (void)fetchSSID {
    __weak typeof(self)  weakSelf = self;
    [self getSSID:^(NSString * _Nonnull ssid) {
        if([MxUtils isPrinterAp:ssid]){
            Device *device = [[Device alloc] initDeviceWithAp:ssid mac:nil peripheral:nil localName:nil connTypes:0 firmwareConfigs:@{} aliases:nil];
            dispatch_async(dispatch_get_main_queue(), ^{
                if (weakSelf.onDeviceDiscovered) {
                    weakSelf.onDeviceDiscovered(device);
                }
                [weakSelf notifyDeviceDiscover:device];
            });
        }
    }];
}

/**获取SSID*/
- (void)getSSID:(void(^)(NSString *ssid))resultBlock {
    if (@available(iOS 14.0, *)) {
        [NEHotspotNetwork fetchCurrentWithCompletionHandler:^(NEHotspotNetwork * _Nullable currentNetwork) {
            NSString *ssid = currentNetwork.SSID ?: @"";
            if (resultBlock) {
                dispatch_async(dispatch_get_main_queue(), ^{
                    resultBlock(ssid);
                });
            }
        }];
    } else {
        NSArray *interfaceNames = CFBridgingRelease(CNCopySupportedInterfaces());
        NSDictionary *info = nil;
        for (NSString *interfaceName in interfaceNames) {
            info = CFBridgingRelease(CNCopyCurrentNetworkInfo((__bridge CFStringRef)interfaceName));
            if (info[@"SSID"]) {
                break;
            }
        }
        NSString *ssid = info[@"SSID"] ?: @"";
        if (resultBlock) {
            dispatch_async(dispatch_get_main_queue(), ^{
                resultBlock(ssid);
            });
        }
    }
}

-(void)syncingData{
    /**自动去同步部分打印机信息*/
    @synchronized (self.lock) {
        
        _isSyncingData = YES;
        
        uint8_t params1[1] = {0};
        [self innerSendCommand:params1 lenght:0 opcode:opcode_readSoftwareInfo delayTime:0.5f tag:200];
        
        uint8_t params2[1] = {0};
        [self innerSendCommand:params2 lenght:0 opcode:opcode_readPrinterParameters delayTime:0.6f tag:200];
        
        uint8_t params3[1] = {0};
        [self innerSendCommand:params3 lenght:0 opcode:opcode_readPrinterCirculationAndRepeatTime delayTime:0.7f tag:200];
        
        uint8_t param4[1] = {0};
        [self innerSendCommand:param4 lenght:0 opcode:opcode_readSilentState delayTime:0.8 tag:200];
        
        uint8_t param5[1] = {0};
        [self innerSendCommand:param5 lenght:0 opcode:opcode_readAutoPowerOffState delayTime:0.8 tag:200];
        
        uint8_t param6[1] = {0};
        [self innerSendCommand:param6 lenght:0 opcode:opcode_readBattery delayTime:0.8 tag:300];
        
        _isSyncingData = NO;
    }
}

#pragma mark - center <中心设备>相关方法<开始>位置
//蓝牙网关初始化和委托方法设置
- (void)babyCenterDelegate{
    
//    __weak typeof(self.baby) weakBaby = self.baby;
    __block BabyBluetooth *blockBaby = self.baby;
    __weak typeof(self)  weakSelf = self;
    __strong __typeof(weakSelf) strongSelf = weakSelf;
    
    [self.baby setBlockOnCentralManagerDidUpdateState:^(CBCentralManager *central) {
        if(weakSelf.scanType != ScanTypeIdle){
            [weakSelf localDiscoverPeripherals:weakSelf.scanType scanTimeout:weakSelf.scanTimeout];
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            if (weakSelf.onCentralManagerDidUpdateState) {
                weakSelf.onCentralManagerDidUpdateState(central);
            }
            [weakSelf notifyCentralManagerDidUpdateState:central];
        });
    }];
    
    [self.baby setBlockOnScanBlock:^(CBCentralManager *centralManager) {
        
        dispatch_async(dispatch_get_main_queue(), ^{
            
            if(weakSelf.isScanTypeBle){
                
                if (weakSelf.onDeviceStartDiscover) {
                    weakSelf.onDeviceStartDiscover();
                }
                [weakSelf notifyDeviceStartDiscover];
                
            }else if (weakSelf.isScanTypeDNW) {
                
                if (weakSelf.onDistNetDeviceDiscoverStart) {
                    weakSelf.onDistNetDeviceDiscoverStart();
                }
                [weakSelf notifyDistNetDeviceDiscoverStart];
                
            }else if(weakSelf.isScanTypeConnModel){
                
                if (weakSelf.onConnModelStartDiscover) {
                    weakSelf.onConnModelStartDiscover();
                }
                [weakSelf notifyConnModelStartDiscover];
                
            }
            
        });
        
    }];
    
    [self.baby setBlockOnCancelScanBlock:^(CBCentralManager *centralManager) {
        
        if(weakSelf.isScanTypeBle){
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if (weakSelf.onDeviceStopDiscover) {
                    weakSelf.onDeviceStopDiscover();
                }
                [weakSelf notifyDeviceStopDiscover];
            });
            
        }else if(weakSelf.isScanTypeDNW){
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if (weakSelf.onDistNetDeviceDiscoverCancel) {
                    weakSelf.onDistNetDeviceDiscoverCancel();
                }
                [weakSelf notifyDistNetDeviceDiscoverCancel];
            });
            
        }else if(weakSelf.isScanTypeConnModel){
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if (weakSelf.onConnModelStopDiscover) {
                    weakSelf.onConnModelStopDiscover();
                }
                [weakSelf notifyConnModelStopDiscover];
            });
        }
        
        strongSelf->_scanType = ScanTypeIdle;
        
    }];
    
    //设置扫描到设备的委托
    [self.baby setBlockOnDiscoverToPeripherals:^(CBCentralManager *central, CBPeripheral *peripheral, NSDictionary *advertisementData, NSNumber *RSSI) {
        
        //--------------------------------打印广播数据----------------------------------
        /*
        NSString *name = peripheral.name;
        if([NSString isBlankString:name]){
            return;
        }
        RBQLog3(@" ---------------- 搜索到带名字的设备 name:%@ -----------------------",name)
        NSArray *keys = [advertisementData allKeys];
        NSData *dataAmb, *dataObj;

        for (int i = 0; i < [keys count]; ++i) {

            id key = [keys objectAtIndex: i];
            NSString *keyName = (NSString *) key;
            NSObject *value = [advertisementData objectForKey: key];

            if ([value isKindOfClass: [NSArray class]]) {

                printf("(一) key: %s\n", [keyName cStringUsingEncoding: NSUTF8StringEncoding]);

                NSArray *values = (NSArray *) value;

                for (int j = 0; j < [values count]; ++j) {

                    if ([[values objectAtIndex: j] isKindOfClass: [CBUUID class]]) {

                        CBUUID *uuid = [values objectAtIndex: j];
                        NSData *data = uuid.data;

                        if (j == 0) {
                            dataObj = uuid.data;
                        } else {
                            dataAmb = uuid.data;
                        }
                        printf("uuid(%d):", j);

                        UInt8 *bytes = (UInt8 *)[data bytes];

                        UInt8 *byte1 = malloc(sizeof(UInt8)*data.length);
                        memset(byte1, 0, sizeof(UInt8)*1);
                        //进行倒序
                        for (int i = 0; i < data.length; i++)
                        {
                            byte1[i] = bytes[data.length - 1 - i];
                        }

                        for (int j = 0; j < data.length; ++j)
                            printf(" %02X", ((UInt8 *) byte1)[j]);

                        free(byte1);

                        for (int j = 0; j < data.length; ++j)
                            printf(" %02X", ((UInt8 *) data.bytes)[j]);

                        printf("\n");

                    } else {

                        const char *valueString = [[value description] cStringUsingEncoding: NSUTF8StringEncoding];
                        printf("value(%d): %s\n", j, valueString);
                    }
                }

            }else{

                const char *valueString = [[value description] cStringUsingEncoding: NSUTF8StringEncoding];
                printf(" (二) key: %s, value: %s\n", [keyName cStringUsingEncoding: NSUTF8StringEncoding], valueString);
            }
        }
         */
        //--------------------------以上为打印广播数据-------------------------
        
        //发现设备
        if(weakSelf.isScanTypeBle){
            /**普通的连接模式*/
            NSString *localName = [advertisementData objectForKey:CBAdvertisementDataLocalNameKey];
            NSString *name = peripheral.name;
            
            if (![weakSelf isMxPrinter:name localName:localName]) {
                return;
            }
            
            NSData *data = [advertisementData valueForKey:CBAdvertisementDataManufacturerDataKey];
            
            // 没有0xff类型的数据，则为02机型，如果data长度为7个，则为06机型，ble仅仅用作配网
            if(!data){
                
                RBQLog3(@"发现MX-02机型【Device】identifier:%@",peripheral.identifier.UUIDString);
                
                Device *device = [[Device alloc] initDeviceWithPeripheral:peripheral localName:localName mac:nil connTypes:[weakSelf mx02ConnTypes] firmwareConfigs:[weakSelf mx02FirmwareConfigs] aliases:MX_02];
                
                dispatch_async(dispatch_get_main_queue(), ^{
                    if (weakSelf.onDeviceDiscovered) {
                        weakSelf.onDeviceDiscovered(device);
                    }
                    [weakSelf notifyDeviceDiscover:device];
                });
                return;
            }
            // 新一代机型，则长度会大于7个
            if (data.length == 7) {
                
                NSString *hex_str = [NSString convertDataToHexStr:data];
                NSString *string = [NSString stringWithUTF8String:[data bytes]];
                
                NSData *macData = [data subdataWithRange:NSMakeRange(0, 6)];
                NSString *mac_str = [NSString convertDataToHexStr:macData];
                
                NSData *last_4_macData = [data subdataWithRange:NSMakeRange(4, 2)];
                NSString *last_4_mac_str = [NSString convertDataToHexStr:last_4_macData];
                
                NSData *stateData = [data subdataWithRange:NSMakeRange(6, 1)];
                uint8_t *stateByte = (UInt8 *)[stateData bytes];
                int state = stateByte[0];
                
                NSString *aliases = [NSString stringWithFormat:@"%@_%@",MX_06,last_4_mac_str];
                
                RBQLog3(@"发现MX-06机型【Device】 identifier:%@; name:%@; localName:%@; kCBAdvDataManufacturerData ->hex_str:%@; string:%@;mac_str:%@;配网状态state->:%d;aliases:%@",peripheral.identifier.UUIDString,name,localName,hex_str,string,mac_str,state,aliases);
                
                Device *device = [[Device alloc] initDeviceWithPeripheral:peripheral localName:localName mac:mac_str connTypes:[weakSelf mx06ConnTypes] firmwareConfigs:[weakSelf mx06FirmwareConfigs] aliases:MX_06];
                
                dispatch_async(dispatch_get_main_queue(), ^{
                    if (weakSelf.onDeviceDiscovered) {
                        weakSelf.onDeviceDiscovered(device);
                    }
                    [weakSelf notifyDeviceDiscover:device];
                });
                return;
            }
            if (data.length >= 12) {
                
                NSString *hex_str = [NSString convertDataToHexStr:data];
                NSInteger length = data.length;
                NSString *string = [NSString stringWithUTF8String:[data bytes]];
                
                NSData *macData = [data subdataWithRange:NSMakeRange(0, 6)];
                NSString *mac_str = [NSString convertDataToHexStr:macData];
                
                NSData *last_4_macData = [data subdataWithRange:NSMakeRange(4, 2)];
                NSString *last_4_mac_str = [NSString convertDataToHexStr:last_4_macData];
                
                NSData *stateData = [data subdataWithRange:NSMakeRange(6, 1)];
                uint8_t *stateByte = (UInt8 *)[stateData bytes];
                int state = stateByte[0];
                
                NSData *device_model_data = [data subdataWithRange:NSMakeRange(7, 4)];
                NSString *device_model_data_str = [[NSString alloc] initWithData:device_model_data encoding:NSUTF8StringEncoding];
                
                NSData *apWifiData = [data subdataWithRange:NSMakeRange(11, 1)];
                uint8_t *apWifiByte = (UInt8 *)[apWifiData bytes];
                int apWifi = apWifiByte[0];

                switch (apWifi) {
                    case 1:
                        apWifi = ConnTypeAP;
                        break;
                    case 2:
                        apWifi = ConnTypeWiFi;
                        break;
                    default:
                        apWifi = ConnTypeAP | ConnTypeWiFi;
                        break;
                }
                
                NSString *aliases = [NSString stringWithFormat:@"%@_%@",INKSI_01,last_4_mac_str];
                
                RBQLog3(@"发现inksi-01机型【Device】identifier:%@; name:%@; localName:%@; kCBAdvDataManufacturerData ->hex_str:%@; string:%@; length:%ld; device_model_data_str:%@;mac_str:%@;配网状态->state:%d;aliases:%@;apWifi:%d",peripheral.identifier.UUIDString,name,localName,hex_str,string,length,device_model_data_str,mac_str,state,aliases,apWifi);
                
                Device *device = [[Device alloc] initDeviceWithPeripheral:peripheral localName:localName mac:mac_str connTypes:[weakSelf inksi01ConnTypes:apWifi] firmwareConfigs:[weakSelf inksi01FirmwareConfigs] aliases:INKSI_01];
                
                dispatch_async(dispatch_get_main_queue(), ^{
                    if (weakSelf.onDeviceDiscovered) {
                        weakSelf.onDeviceDiscovered(device);
                    }
                    [weakSelf notifyDeviceDiscover:device];
                });
                
            }
            
        }else if(weakSelf.isScanTypeConnModel){
            
            /**普通的连接模式*/
            NSString *localName = [advertisementData objectForKey:CBAdvertisementDataLocalNameKey];
            NSString *name = peripheral.name;
            
            if (![weakSelf isMxPrinter:name localName:localName]) {
                return;
            }
            
//                NSData *data = [advertisementData valueForKey:@"kCBAdvDataManufacturerData"];
            NSData *data = [advertisementData valueForKey:CBAdvertisementDataManufacturerDataKey];
            
            // 没有0xff类型的数据，则为02机型，如果data长度为7个，则为06机型，ble仅仅用作配网
            if(!data){
                RBQLog3(@"发现MX-02机型【ConnModel】identifier:%@",peripheral.identifier.UUIDString);
                ConnModel *model = [[ConnModel alloc] initConnModel:peripheral localName:localName connTypes:[weakSelf mx02ConnTypes] firmwareConfigs:[weakSelf mx02FirmwareConfigs] mac:nil aliases:MX_02];
                
                dispatch_async(dispatch_get_main_queue(), ^{
                    if(weakSelf.onConnModelDiscovered){
                        weakSelf.onConnModelDiscovered(model);
                    }
                    [weakSelf notifyConnModelDiscover:model];
                });
                return;
            }
            // 新一代机型，则长度会大于7个
            if (data.length == 7) {
                
                NSString *hex_str = [NSString convertDataToHexStr:data];
//                NSString *string = [NSString stringWithUTF8String:[data bytes]];
                NSData *macData = [data subdataWithRange:NSMakeRange(0, 6)];
                NSString *mac_str = [NSString convertDataToHexStr:macData];
                
                NSData *last_4_macData = [data subdataWithRange:NSMakeRange(4, 2)];
                NSString *last_4_mac_str = [NSString convertDataToHexStr:last_4_macData];
                
                NSData *stateData = [data subdataWithRange:NSMakeRange(6, 1)];
                uint8_t *stateByte = (UInt8 *)[stateData bytes];
                int state = stateByte[0];
                
                NSString *aliases = [NSString stringWithFormat:@"%@_%@",MX_06,last_4_mac_str];
                
                RBQLog3(@"发现MX-06机型【ConnModel】identifier:%@; name:%@; localName:%@; 0xff数据 ->hex_str:%@;mac_str:%@;配网状态state->:%d;aliases:%@",peripheral.identifier.UUIDString,name,localName,hex_str,mac_str,state,aliases);
                
                ConnModel *model = [[ConnModel alloc] initConnModel:peripheral localName:localName connTypes:[weakSelf mx06ConnTypes] firmwareConfigs:[weakSelf mx06FirmwareConfigs] mac:mac_str aliases:aliases state:state];
                
                dispatch_async(dispatch_get_main_queue(), ^{
                    if(weakSelf.onConnModelDiscovered){
                        weakSelf.onConnModelDiscovered(model);
                    }
                    [weakSelf notifyConnModelDiscover:model];
                });
                return;
            }
            if (data.length >= 12) {
                
                NSString *hex_str = [NSString convertDataToHexStr:data];
                NSInteger length = data.length;
                
                NSData *macData = [data subdataWithRange:NSMakeRange(0, 6)];
                NSString *mac_str = [NSString convertDataToHexStr:macData];
                
                NSData *last_4_macData = [data subdataWithRange:NSMakeRange(4, 2)];
                NSString *last_4_mac_str = [NSString convertDataToHexStr:last_4_macData];
                
                NSData *stateData = [data subdataWithRange:NSMakeRange(6, 1)];
                uint8_t *stateByte = (UInt8 *)[stateData bytes];
                int state = stateByte[0];
                
                NSData *device_model_data = [data subdataWithRange:NSMakeRange(7, 4)];
                NSString *device_model_data_str = [[NSString alloc] initWithData:device_model_data encoding:NSUTF8StringEncoding];
                
                NSData *apWifiData = [data subdataWithRange:NSMakeRange(11, 1)];
                uint8_t *apWifiByte = (UInt8 *)[apWifiData bytes];
                int apWifi = apWifiByte[0];

                switch (apWifi) {
                    case 1:
                        apWifi = ConnTypeAP;
                        break;
                    case 2:
                        apWifi = ConnTypeWiFi;
                        break;
                    default:
                        apWifi = ConnTypeAP | ConnTypeWiFi;
                        break;
                }
                
                NSString *aliases = [NSString stringWithFormat:@"%@_%@",INKSI_01,last_4_mac_str];
                
                RBQLog3(@"发现inksi-01机型【ConnModel】identifier:%@; name:%@; localName:%@; 0xff数据 ->hex_str:%@; length:%ld; device_model_data_str:%@;mac_str:%@;配网状态->state:%d;aliases:%@;apWifi:%d",peripheral.identifier.UUIDString,name,localName,hex_str,length,device_model_data_str,mac_str,state,aliases,apWifi);
                // 打印示例 RBQLog: 发现inksi-01机型【ConnModel】 name:Mindtree-HID; localName:INKSI-01_9C40; 0xff数据 ->hex_str:c8478c6c9c40004258323002; length:12; device_model_data_str:BX20;mac_str:c8478c6c9c40;配网状态->state:0;aliases:INKSI-01_9c40
                
                ConnModel *model = [[ConnModel alloc] initConnModel:peripheral localName:localName connTypes:[weakSelf inksi01ConnTypes:apWifi] firmwareConfigs:[weakSelf inksi01FirmwareConfigs] mac:mac_str aliases:aliases state:state];
                
                dispatch_async(dispatch_get_main_queue(), ^{
                    if(weakSelf.onConnModelDiscovered){
                        weakSelf.onConnModelDiscovered(model);
                    }
                    [weakSelf notifyConnModelDiscover:model];
                });
            }
            
        }else if (weakSelf.isScanTypeDNW) {
            
            NSString *localName = [advertisementData objectForKey:CBAdvertisementDataLocalNameKey];
            NSString *name = peripheral.name;
            
            if (![weakSelf isMxPrinter:name localName:localName]) {
                return;
            }
            
            NSData *data = [advertisementData valueForKey:CBAdvertisementDataManufacturerDataKey];
            if (!data||data.length<7) {
                return;
            }
            // 新一代机型，则长度会大于7个
            if (data.length == 7) {
                
                NSString *hex_str = [NSString convertDataToHexStr:data];
                
                NSData *macData = [data subdataWithRange:NSMakeRange(0, 6)];
                NSString *mac_str = [NSString convertDataToHexStr:macData];
                
                NSData *last_4_macData = [data subdataWithRange:NSMakeRange(4, 2)];
                NSString *last_4_mac_str = [NSString convertDataToHexStr:last_4_macData];
                
                NSData *stateData = [data subdataWithRange:NSMakeRange(6, 1)];
                uint8_t *stateByte = (UInt8 *)[stateData bytes];
                int state = stateByte[0];
                
                NSString *aliases = [NSString stringWithFormat:@"%@_%@",MX_06,last_4_mac_str];
                
                RBQLog3(@"发现MX-06机型【DNW】identifier:%@; name:%@; localName:%@; 0xff数据 ->hex_str:%@;mac_str:%@;配网状态state->:%d;aliases:%@",peripheral.identifier.UUIDString,name,localName,hex_str,mac_str,state,aliases);
                
                DistNetDevice *device = [[DistNetDevice alloc] initDistNetDevice:peripheral localName:localName mac:mac_str state:state connTypes:[weakSelf mx06ConnTypes] firmwareConfigs:[weakSelf mx06FirmwareConfigs] aliases:MX_06];

                dispatch_async(dispatch_get_main_queue(), ^{
                    if (weakSelf.onDistNetDeviceDiscover) {
                        weakSelf.onDistNetDeviceDiscover(device);
                    }
                    [weakSelf notifyDistNetDeviceDiscover:device];
                });
                return;
            }
            if (data.length >= 12) {
                
                NSString *hex_str = [NSString convertDataToHexStr:data];
                NSInteger length = data.length;
                
                NSData *macData = [data subdataWithRange:NSMakeRange(0, 6)];
                NSString *mac_str = [NSString convertDataToHexStr:macData];
                
                NSData *last_4_macData = [data subdataWithRange:NSMakeRange(4, 2)];
                NSString *last_4_mac_str = [NSString convertDataToHexStr:last_4_macData];
                
                NSData *stateData = [data subdataWithRange:NSMakeRange(6, 1)];
                uint8_t *stateByte = (UInt8 *)[stateData bytes];
                int state = stateByte[0];
                
                NSData *device_model_data = [data subdataWithRange:NSMakeRange(7, 4)];
                NSString *device_model_data_str = [[NSString alloc] initWithData:device_model_data encoding:NSUTF8StringEncoding];
                
                NSData *apWifiData = [data subdataWithRange:NSMakeRange(11, 1)];
                uint8_t *apWifiByte = (UInt8 *)[apWifiData bytes];
                int apWifi = apWifiByte[0];

                switch (apWifi) {
                    case 1:
                        apWifi = ConnTypeAP;
                        break;
                    case 2:
                        apWifi = ConnTypeWiFi;
                        break;
                    default:
                        apWifi = ConnTypeAP | ConnTypeWiFi;
                        break;
                }
                
                NSString *aliases = [NSString stringWithFormat:@"%@_%@",INKSI_01,last_4_mac_str];
                
                RBQLog3(@"发现inksi-01机型【DNW】identifier:%@; name:%@; localName:%@; 0xff数据 ->hex_str:%@; length:%ld; device_model_data_str:%@;mac_str:%@;配网状态->state:%d;aliases:%@;apWifi:%d",peripheral.identifier.UUIDString,name,localName,hex_str,length,device_model_data_str,mac_str,state,aliases,apWifi);
                
                DistNetDevice *device = [[DistNetDevice alloc] initDistNetDevice:peripheral localName:localName mac:mac_str state:state connTypes:[weakSelf inksi01ConnTypes:apWifi] firmwareConfigs:[weakSelf inksi01FirmwareConfigs] aliases:INKSI_01];

                dispatch_async(dispatch_get_main_queue(), ^{
                    if (weakSelf.onDistNetDeviceDiscover) {
                        weakSelf.onDistNetDeviceDiscover(device);
                    }
                    [weakSelf notifyDistNetDeviceDiscover:device];
                });
            }
            
        }
        
    }];
    //开始连接设备
    [self.baby setBlockOnStartConnectToPeripheral:^(CBPeripheral *peripheral) {
        
        //停止扫描
        [weakSelf.scanTimeoutTimer clearScheduledTimer];
        [blockBaby cancelScan];
        
        if(weakSelf.isConnectTypeBle){
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if (weakSelf.onDeviceConnectStart) {
                    weakSelf.onDeviceConnectStart();
                }
                [weakSelf notifyDeviceConnectStart];
            });
        }else if(weakSelf.isConnectTypeDNW){
            RBQLog3(@"配网开始连接蓝牙，这里没设置事件，所以没事件向外反馈");
        }
    }];
    
    //设置设备连接成功的委托
    [self.baby setBlockOnConnected:^(CBCentralManager *central, CBPeripheral *peripheral) {
        //设置连接成功的block
        RBQLog3(@"设备：%@--连接成功 -> 已经设置让baby框架自动发现ble的服务，这里暂时无需做什么了; connectType:%ld",peripheral.name,weakSelf.connectType);
    }];
    //连接失败
    [self.baby setBlockOnFailToConnect:^(CBCentralManager *central, CBPeripheral *peripheral, NSError *error) {
        RBQLog3(@"设备: %@--连接失败",peripheral.name);
        
        if(weakSelf.isConnectTypeBle){
            
            weakSelf.device.isConnected = NO;
            [weakSelf clearCommandQueue];
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if (weakSelf.onDeviceConnectFail) {
                    weakSelf.onDeviceConnectFail();
                }
                [weakSelf notifyDeviceConnectFail];
            });
            
        }else if(weakSelf.isConnectTypeDNW){
            //配网失败
            [weakSelf.networkConfigurationTimeoutTimer clearScheduledTimer];
            dispatch_async(dispatch_get_main_queue(), ^{
                if (weakSelf.onDistributionNetworkFail) {
                    weakSelf.onDistributionNetworkFail();
                }
                [weakSelf notifyDistributionNetworkFail];
            });
        }
        //将连接置空闲
        strongSelf->_connectType = ConnectTypeIdle;
        
    }];
    //连接断开
    [self.baby setBlockOnDisconnect:^(CBCentralManager *central, CBPeripheral *peripheral, NSError *error) {
        RBQLog3(@"设备: %@--连接断开",peripheral.name);
        
        if(weakSelf.isConnectTypeBle){
            
            weakSelf.device.isConnected = NO;
            [weakSelf clearCommandQueue];
            
            dispatch_async(dispatch_get_main_queue(), ^{
                if (weakSelf.onDeviceDisconnect) {
                    weakSelf.onDeviceDisconnect();
                }
                [weakSelf notifyDeviceDisconnect];
            });
            
            // 将连接状态置为空闲
            strongSelf->_connectType = ConnectTypeIdle;
            
        }else if(weakSelf.isConnectTypeDNW){
            //这里不做什么，监听会在发送完配网密码后，1秒钟开始，且会判断是否断开，如果没断开，会主动断开，这里断开的空闲状态放到开始监听udp前
            RBQLog3(@"配网->ble连接已断开");
        }
        
    }];
    
    //设置发现设备的Services的委托
    [self.baby setBlockOnDiscoverServices:^(CBPeripheral *peripheral, NSError *error) {
        
//        for (CBService *service in peripheral.services) {
//            RBQLog3(@"搜索到服务:%@",service.UUID.UUIDString);
//        }
        
    }];
    //设置发现设service的Characteristics的委托
    [self.baby setBlockOnDiscoverCharacteristics:^(CBPeripheral *peripheral, CBService *service, NSError *error) {
        
        for (CBCharacteristic *characteristic in service.characteristics)
        {
            if(weakSelf.isConnectTypeBle){
                
                if ([service.UUID isEqual:[CBUUID UUIDWithString:Service_UUID]]
                    &&[characteristic.UUID isEqual:[CBUUID UUIDWithString:Notify_UUID]])
                {
                    
                    RBQLog3(@"【setBlockOnDiscoverCharacteristics】BLE连接模式 打开通知 connectType:%ld",weakSelf.connectType)
                    //打开通知
                    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(0.3f * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
                        [peripheral setNotifyValue:YES forCharacteristic:characteristic];
                    });
                }
            }else if(weakSelf.isConnectTypeDNW){/**处于配网工作模式*/
                /**增加配网设备的*/
                if ([service.UUID isEqual:[CBUUID UUIDWithString:DNW_Service_UUID]]
                    &&[characteristic.UUID isEqual:[CBUUID UUIDWithString:DNW_Notify_UUID]]) {
                    
                    RBQLog3(@"【setBlockOnDiscoverCharacteristics】配网模式 打开通知 connectType:%ld",weakSelf.connectType)
                    
                    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(0.3f * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
                        [peripheral setNotifyValue:YES forCharacteristic:characteristic];
                    });
                }
            }
        }
        
    }];
    //订阅状态发生改变时调用
    [self.baby setBlockOnDidUpdateNotificationStateForCharacteristic:^(CBPeripheral *peripheral, CBCharacteristic *characteristic, NSError *error) {
        
        if(weakSelf.isConnectTypeBle){
            
            //普通模式
            if ([characteristic.UUID isEqual:[CBUUID UUIDWithString:Notify_UUID]])
            {
                
                if (characteristic.isNotifying) {
                    
                    weakSelf.device.isConnected = YES;
                    
                    dispatch_async(dispatch_get_main_queue(), ^{
                        if (weakSelf.onDeviceConnectSucceed) {
                            weakSelf.onDeviceConnectSucceed();
                        }
                        [weakSelf notifyDeviceConnectSucceed];
                    });
                    
                    /**自动去同步部分打印机信息*/
                    [weakSelf syncingData];
                    
                }else{
                    
                    [weakSelf.baby cancelPeripheralConnection:peripheral];
                }
            }
            
        }else if (weakSelf.isConnectTypeDNW){//配网模式
            
            /**增加配网设备的*/
            if ([characteristic.UUID isEqual:[CBUUID UUIDWithString:DNW_Notify_UUID]]) {
                
                //发送WiFi名和密码
                if (characteristic.isNotifying) {
                    
                    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(1.0f * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
                        
                        //字典方式转来的json，默认无法设置编码方式，mcu会无法解析
                        NSDictionary *dic = @{@"SSID":weakSelf.ssid,@"PASSWORD":weakSelf.password};
                        NSError *error = nil;
                        NSData *jsonData = [NSJSONSerialization dataWithJSONObject:dic options:NSJSONWritingPrettyPrinted error:&error];
                        NSString *jsonString = [[NSString alloc] initWithData:jsonData encoding:NSUTF8StringEncoding];
                        RBQLog3(@"配网的json:%@",jsonString);
                        
                        NSArray *peripherals = [weakSelf.baby findConnectedPeripherals];
                        [weakSelf writeCharacteristics:peripherals serviceUuid:DNW_Service_UUID characteristicUuid:DNW_Write_UUID value:jsonData];
                        
                        //发送完配网账号和密码后，延时开始监听udp广播 1秒钟后开始扫描设备
                        dispatch_after(dispatch_time(DISPATCH_TIME_NOW, 1), dispatch_get_main_queue(), ^{
                            //如果设备没断开，则直接断开设备
                            for (CBPeripheral *peripheral in peripherals) {
                                if(peripheral.state != CBPeripheralStateConnected){
                                    [weakSelf.baby cancelPeripheralConnection:peripheral];
                                }
                            }
                            //配网后将连接置为空闲
                            strongSelf->_connectType = ConnectTypeIdle;
                            RBQLog3(@"配网->发送完ssid和密码，将connectType置为空闲状态");
                            
                            //开始监听配网设备
                            strongSelf->_udpMonitorType = UdpMonitorTypeDNW;
                            /**开始监听广播*/
                            RBQLog3(@"配网->开始监听udp");
                            [weakSelf.discoverUdpServer stopUdpSocketMonitoring];
                            [weakSelf.distributionNetworkUdpServer startUdpSocketMonitoring];
                            
                        });
                        
                    });
                    
                }else{

                    [weakSelf.baby cancelPeripheralConnection:peripheral];
                }
                
            }
            
        }
        
    }];
    
//设置读取characteristics的委托，也就从设备通过通知给主设备传递数据的通知通道，该委托通过didUpdateValueForCharacteristic方法将数据传递过来的
    [self.baby setBlockOnReadValueForCharacteristic:^(CBPeripheral *peripheral, CBCharacteristic *characteristic, NSError *error) {
        
        if(weakSelf.isConnectTypeBle){
            //普通模式
            if ([characteristic.UUID isEqual:[CBUUID UUIDWithString:Notify_UUID]]) {
                
//                    RBQLog3(@"【setBlockOnReadValueForCharacteristic】BLE连接模式 connectType:%ld",weakSelf.connectType)
            
                NSData *data = characteristic.value;
                if (!data) {
                    return;
                }
                [weakSelf receiving:data];
            }
            
        }else if(weakSelf.isConnectTypeDNW) {
            
            if ([characteristic.UUID isEqual:[CBUUID UUIDWithString:DNW_Notify_UUID]]) {
                
                RBQLog3(@"【setBlockOnReadValueForCharacteristic】配网模式 connectType:%ld",weakSelf.connectType)
                
                NSData *data = characteristic.value;
                if (!data) {
                    return;
                }
                NSString *jsonStr  =[[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
                if (!jsonStr) {
                    return;
                }
                RBQLog3(@"收到配网反馈:%@",jsonStr);
            }
            
        }
        
    }];
    
    //设置发现characteristics的descriptors的委托
    [weakSelf.baby setBlockOnDiscoverDescriptorsForCharacteristic:^(CBPeripheral *peripheral, CBCharacteristic *characteristic, NSError *error) {
//        RBQLog3(@"===characteristic name:%@",characteristic.service.UUID);
//        for (CBDescriptor *d in characteristic.descriptors) {
//            RBQLog3(@"CBDescriptor name is :%@",d.UUID);
//        }
        
    }];
    //设置读取Descriptor的委托
    [weakSelf.baby setBlockOnReadValueForDescriptors:^(CBPeripheral *peripheral, CBDescriptor *descriptor, NSError *error) {
//        RBQLog3(@"Descriptor name:%@ value is:%@",descriptor.characteristic.UUID, descriptor.value);
    }];
    //写Characteristic是否成功block
    [weakSelf.baby setBlockOnDidWriteValueForCharacteristic:^(CBCharacteristic *characteristic, NSError *error) {
        
        if (error) {
            
//            RBQLog3(@"写数据失败");
        }else{
//            RBQLog3(@"写数据成功");
        }
    }];
    
}

// 辅助方法：查找具有指定 UUID 的服务
- (CBService *)findServiceForPeripheral:(CBPeripheral *)peripheral
                             serviceUuid:(NSString *)serviceUuid {
    if (peripheral.state != CBPeripheralStateConnected) {
        RBQLog3(@"设备没连接！");
        return nil;
    }
    
    for (CBService *service in peripheral.services) {
        if ([service.UUID isEqual:[CBUUID UUIDWithString:serviceUuid]]) {
            return service;
        }
    }
    
    RBQLog3(@"未找到服务！");
    return nil;
}

// 辅助方法：在服务中查找特征
- (CBCharacteristic *)findCharacteristicForService:(CBService *)service characteristicUuid:(NSString *)characteristicUuid {
    for (CBCharacteristic *characteristic in service.characteristics) {
        if ([characteristic.UUID isEqual:[CBUUID UUIDWithString:characteristicUuid]]) {
            return characteristic;
        }
    }
    RBQLog3(@"未找到特征！");
    return nil;
}

// 统一的方法，通过服务和特征 UUID 获取特征
- (CBCharacteristic *)characteristicForPeripheral:(CBPeripheral *)peripheral serviceUuid:(NSString *)serviceUuid characteristicUuid:(NSString *)characteristicUuid {
    
    CBService *service = [self findServiceForPeripheral:peripheral serviceUuid:serviceUuid];
    if (!service) return nil;
    return [self findCharacteristicForService:service characteristicUuid:characteristicUuid];
}

// 为多个外设写入值到特征
- (void)writeCharacteristics:(NSArray<CBPeripheral *> *)peripherals serviceUuid:(NSString *)serviceUuid characteristicUuid:(NSString *)characteristicUuid value:(NSData *)value {
    
    for (CBPeripheral *peripheral in peripherals) {
        CBCharacteristic *characteristic = [self characteristicForPeripheral:peripheral serviceUuid:serviceUuid characteristicUuid:characteristicUuid];
        
        if (characteristic) {
            [self writeValue:value toPeripheral:peripheral characteristic:characteristic];
        }
    }
}

// 为单个外设写入值到特征
- (void)writeCharacteristic:(CBPeripheral *)peripheral serviceUuid:(NSString *)serviceUuid characteristicUuid:(NSString *)characteristicUuid value:(NSData *)value {
    
    CBCharacteristic *characteristic = [self characteristicForPeripheral:peripheral serviceUuid:serviceUuid characteristicUuid:characteristicUuid];
    if (characteristic) {
        [self writeValue:value toPeripheral:peripheral characteristic:characteristic];
    }
}

//打印出 characteristic 的权限，可以看到有很多种，这是一个NS_OPTIONS，就是可以同时用于好几个值，常见的有read，write，notify，indicate，知知道这几个基本就够用了，前连个是读写权限，后两个都是通知，两种不同的通知方式。
/*
 typedef NS_OPTIONS(NSUInteger, CBCharacteristicProperties) {
 CBCharacteristicPropertyBroadcast                                                = 0x01,
 CBCharacteristicPropertyRead                                                    = 0x02,
 CBCharacteristicPropertyWriteWithoutResponse                                    = 0x04,
 CBCharacteristicPropertyWrite                                                    = 0x08,
 CBCharacteristicPropertyNotify                                                    = 0x10,
 CBCharacteristicPropertyIndicate                                                = 0x20,
 CBCharacteristicPropertyAuthenticatedSignedWrites                                = 0x40,
 CBCharacteristicPropertyExtendedProperties                                        = 0x80,
 CBCharacteristicPropertyNotifyEncryptionRequired NS_ENUM_AVAILABLE(NA, 6_0)        = 0x100,
 CBCharacteristicPropertyIndicateEncryptionRequired NS_ENUM_AVAILABLE(NA, 6_0)    = 0x200
 };
 */

// 核心方法，处理数据写入
- (void)writeValue:(NSData *)value toPeripheral:(CBPeripheral *)peripheral characteristic:(CBCharacteristic *)characteristic {
    // 确保特征是可写的
    if (!(characteristic.properties & CBCharacteristicPropertyWriteWithoutResponse) &&
        !(characteristic.properties & CBCharacteristicPropertyWrite)) {
        RBQLog3(@"该字段不可写！");
        return;
    }
    
    // 确定可以写入的最大数据大小
    NSUInteger maxDataSize = [peripheral maximumWriteValueLengthForType:CBCharacteristicWriteWithoutResponse] - 3;
//    RBQLog3(@"【writeCharacteristic】maxDataSize:%ld", (unsigned long)maxDataSize);
    // 分块发送数据
    NSUInteger offset = 0;
    while (offset < value.length) {
        NSUInteger chunkSize = MIN(maxDataSize, value.length - offset);
        NSData *chunk = [value subdataWithRange:NSMakeRange(offset, chunkSize)];
        //应答模式写入会较慢
        [peripheral writeValue:chunk forCharacteristic:characteristic type:CBCharacteristicWriteWithResponse];
        //使用非应答模式
//        [peripheral writeValue:chunk forCharacteristic:characteristic type:CBCharacteristicWriteWithoutResponse];
        offset += chunkSize;
        // 可选：延迟写入以防止过载
        [NSThread sleepForTimeInterval:0.02];
    }
//    RBQLog3(@"数据已发送");
}


- (BOOL)isMxPrinter:(nullable NSString *)name localName:(nullable NSString *)localName {

    // 将设备名称和本地名称转为小写进行比较
    NSString *lowercaseLocalName = localName ? [localName lowercaseString] : nil;
    NSString *lowercaseName = name ? [name lowercaseString] : nil;

    // 检查名称中是否包含目标字符串
    BOOL isMatchingName = lowercaseName && [lowercaseName containsString:inksi_mobile_printer];
    BOOL isMatchingLocalName = lowercaseLocalName && [lowercaseLocalName containsString:inksi_mobile_printer];

    return isMatchingName || isMatchingLocalName;
}

//GB2312转换为UTF-8的方法
+ (NSData *)UTF8WithGB2312Data:(NSData *)gb2312Data
{
    NSStringEncoding enc = CFStringConvertEncodingToNSStringEncoding(kCFStringEncodingGB_18030_2000);
    NSString *str = [[NSString alloc] initWithData:gb2312Data encoding:enc];
    NSData *utf8Data = [str dataUsingEncoding:NSUTF8StringEncoding];
    return utf8Data;
}
//UTF-8转换为GB2312的方法
+ (NSData *)GB2312WithUTF8Data:(NSData *)UTF8Data
{
    NSStringEncoding enc = CFStringConvertEncodingToNSStringEncoding(kCFStringEncodingGB_18030_2000);
    NSString *str = [[NSString alloc] initWithData:UTF8Data  encoding:NSUTF8StringEncoding];
    NSData *gb2312Data = [str dataUsingEncoding:enc];
    return gb2312Data;
}

-(NSData *)createCommand:(int)opcode {

    // 各部分长度定义
    const int prefixLen = 1;
    const int packetLenLen = 2;
    const int packetXorLenLen = 2;
    const int packet_ctLen = 4;
    const int opcodeLen = 2;
    const int crcLen = 2;

    // 整个指令包的总长度
    const int byteLen = prefixLen + packetLenLen + packetXorLenLen + packet_ctLen + opcodeLen + crcLen;
    // 包长度，不包括CRC
    const int pack_Len = packet_ctLen + opcodeLen;

    // 分配内存用于存储指令
    uint8_t command[byteLen];
    memset(command, 0, sizeof(command));

    int offset = 0;
    // 前缀
    command[offset++] = 0x17;

    // 包长度
    command[offset++] = pack_Len & 0xFF;
    command[offset++] = (pack_Len >> 8) & 0xFF;

    // 包长度取反
    command[offset++] = (~pack_Len) & 0xFF;
    command[offset++] = ((~pack_Len) >> 8) & 0xFF;

    // 帧序列号，总共4字节
    int pack_ct = [self generateSequenceNumber];
    command[offset++] = pack_ct & 0xFF;
    command[offset++] = (pack_ct >> 8) & 0xFF;
    command[offset++] = (pack_ct >> 16) & 0xFF;
    command[offset++] = (pack_ct >> 24) & 0xFF;

    // 操作码
    command[offset++] = opcode & 0xFF;
    command[offset++] = (opcode >> 8) & 0xFF;

    // 计算CRC
    uint16_t crc = [CRC16 crc16_calc:command dataLength:offset];

    // 将CRC附加到指令末尾
    command[offset++] = (crc >> 8) & 0xFF;
    command[offset++] = crc & 0xFF;

    // 将指令数组转换为NSData对象
    NSData *commandData = [NSData dataWithBytes:command length:byteLen];

    return commandData;
}

-(NSData *)createCommand:(uint8_t *)params length:(int)paramsLen opcode:(int)opcode {

    // 各部分长度定义
    const int prefixLen = 1;
    const int packetLenLen = 2;
    const int packetXorLenLen = 2;
    const int packet_ctLen = 4;
    const int opcodeLen = 2;
    const int crcLen = 2;

    // 整个指令包的总长度
    int byteLen = prefixLen + packetLenLen + packetXorLenLen + packet_ctLen + opcodeLen + paramsLen + crcLen;
    // 包长度，不包括CRC
    int pack_Len = packet_ctLen + opcodeLen + paramsLen;

    // 分配内存用于存储指令
    uint8_t *command = (uint8_t *)malloc(byteLen * sizeof(uint8_t));
    memset(command, 0, byteLen * sizeof(uint8_t));

    int offset = 0;
    // 前缀
    command[offset++] = 0x17;

    // 包长度
    command[offset++] = pack_Len & 0xFF;
    command[offset++] = (pack_Len >> 8) & 0xFF;

    // 包长度取反
    command[offset++] = (~pack_Len) & 0xFF;
    command[offset++] = ((~pack_Len) >> 8) & 0xFF;

    // 帧序列号，总共4字节
    int pack_ct = [self generateSequenceNumber];
    command[offset++] = pack_ct & 0xFF;
    command[offset++] = (pack_ct >> 8) & 0xFF;
    command[offset++] = (pack_ct >> 16) & 0xFF;
    command[offset++] = (pack_ct >> 24) & 0xFF;

    // 操作码
    command[offset++] = opcode & 0xFF;
    command[offset++] = (opcode >> 8) & 0xFF;

    // 参数
    if (paramsLen != 0) {
        memcpy(&command[offset], params, paramsLen);
        offset += paramsLen;
    }

    // 计算CRC
    uint16_t crc = [CRC16 crc16_calc:command dataLength:offset];

    // 将CRC附加到指令末尾
    command[offset++] = (crc >> 8) & 0xFF;
    command[offset++] = crc & 0xFF;

    // 将指令数组转换为NSData对象
    NSData *commandData = [NSData dataWithBytes:command length:byteLen];
    free(command);

    return commandData;
}

-(NSData *)createCommand:(NSData *)paramsData opcode:(int)opcode {

    // 各部分长度定义
    const int prefixLen = 1;
    const int packetLenLen = 2;
    const int packetXorLenLen = 2;
    const int packet_ctLen = 4;
    const int opcodeLen = 2;
    const int crcLen = 2;

    // 参数数据长度
    int paramsLen = (int)[paramsData length];
    uint8_t *params = (uint8_t *)[paramsData bytes];

    // 整个指令包的总长度
    int byteLen = prefixLen + packetLenLen + packetXorLenLen + packet_ctLen + opcodeLen + paramsLen + crcLen;
    // 包长度，不包括CRC
    int pack_Len = packet_ctLen + opcodeLen + paramsLen;

    // 分配内存用于存储指令
    uint8_t *command = (uint8_t *)malloc(byteLen * sizeof(uint8_t));
    memset(command, 0, byteLen * sizeof(uint8_t));

    int offset = 0;
    // 前缀
    command[offset++] = 0x17;

    // 包长度
    command[offset++] = pack_Len & 0xFF;
    command[offset++] = (pack_Len >> 8) & 0xFF;

    // 包长度取反
    command[offset++] = (~pack_Len) & 0xFF;
    command[offset++] = ((~pack_Len) >> 8) & 0xFF;

    // 帧序列号，总共4字节
    int pack_ct = [self generateSequenceNumber];
    command[offset++] = pack_ct & 0xFF;
    command[offset++] = (pack_ct >> 8) & 0xFF;
    command[offset++] = (pack_ct >> 16) & 0xFF;
    command[offset++] = (pack_ct >> 24) & 0xFF;

    // 操作码
    command[offset++] = opcode & 0xFF;
    command[offset++] = (opcode >> 8) & 0xFF;

    // 参数
    if (paramsLen != 0) {
        memcpy(&command[offset], params, paramsLen);
        offset += paramsLen;
    }

    // 计算CRC
    uint16_t crc = [CRC16 crc16_calc:command dataLength:offset];

    // 将CRC附加到指令末尾
    command[offset++] = (crc >> 8) & 0xFF;
    command[offset++] = crc & 0xFF;

    // 将指令数组转换为NSData对象
    NSData *commandData = [NSData dataWithBytes:command length:byteLen];
    free(command);

    return commandData;
}


-(void)sendCommand:(int)opcode{
    
    if (self.isSendingData) {
        return;
    }

    NSData *commandData = [self createCommand:opcode];
    Command *command = [[Command alloc] initCommand:commandData];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)sendCommand:(int)opcode tag:(int)tag{
    
    if (self.isSendingData) {
        return;
    }

    NSData *commandData = [self createCommand:opcode];
    Command *command = [[Command alloc] initCommand:commandData withTag:tag];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)sendCommand:(uint8_t *)params lenght:(int)paramsLen opcode:(int)opcode{
    
    if (self.isSendingData) {
        return;
    }

    NSData *commandData = [self createCommand:params length:paramsLen opcode:opcode];
    Command *command = [[Command alloc] initCommand:commandData];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)sendCommand:(uint8_t *)params lenght:(int)paramsLen opcode:(int)opcode tag:(int)tag{
    
    if (self.isSendingData) {
        return;
    }

    NSData *commandData = [self createCommand:params length:paramsLen opcode:opcode];
    Command *command = [[Command alloc] initCommand:commandData withTag:tag];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)sendCommand:(NSData *)paramsData opcode:(int)opcode{
    
    if (self.isSendingData) {
        return;
    }

    NSData *commandData = [self createCommand:paramsData opcode:opcode];
    Command *command = [[Command alloc] initCommand:commandData];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)sendCommand:(NSData *)paramsData opcode:(int)opcode tag:(int)tag{
    
    if (self.isSendingData) {
        return;
    }

    NSData *commandData = [self createCommand:paramsData opcode:opcode];
    Command *command = [[Command alloc] initCommand:commandData withTag:tag];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)sendCommand:(int)opcode delayTime:(NSTimeInterval)delayTime{
    
    if (self.isSendingData) {
        return;
    }

    NSData *commandData = [self createCommand:opcode];
    Command *command = [[Command alloc] initCommand:commandData delayTime:delayTime];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)sendCommand:(int)opcode delayTime:(NSTimeInterval)delayTime tag:(int)tag{
    
    if (self.isSendingData) {
        return;
    }

    NSData *commandData = [self createCommand:opcode];
    Command *command = [[Command alloc] initCommand:commandData delayTime:delayTime];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)sendCommand:(uint8_t *)params lenght:(int)paramsLen opcode:(int)opcode delayTime:(NSTimeInterval)delayTime{
    
    if (self.isSendingData) {
        return;
    }

    NSData *commandData = [self createCommand:params length:paramsLen opcode:opcode];
    Command *command = [[Command alloc] initCommand:commandData delayTime:delayTime];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)sendCommand:(uint8_t *)params lenght:(int)paramsLen opcode:(int)opcode delayTime:(NSTimeInterval)delayTime tag:(int)tag{
    
    if (self.isSendingData) {
        return;
    }

    NSData *commandData = [self createCommand:params length:paramsLen opcode:opcode];
    Command *command = [[Command alloc] initCommand:commandData delayTime:delayTime withTag:tag];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)sendCommand:(NSData *)paramsData opcode:(int)opcode delayTime:(NSTimeInterval)delayTime{
    
    if (self.isSendingData) {
        return;
    }

    NSData *commandData = [self createCommand:paramsData opcode:opcode];
    Command *command = [[Command alloc] initCommand:commandData delayTime:delayTime];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)sendCommand:(NSData *)paramsData opcode:(int)opcode delayTime:(NSTimeInterval)delayTime tag:(int)tag{
    
    if (self.isSendingData) {
        return;
    }

    NSData *commandData = [self createCommand:paramsData opcode:opcode];
    Command *command = [[Command alloc] initCommand:commandData delayTime:delayTime withTag:tag];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)innerSendCommand:(int)opcode{

    NSData *commandData = [self createCommand:opcode];
    Command *command = [[Command alloc] initCommand:commandData];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)innerSendCommand:(int)opcode tag:(int)tag{

    NSData *commandData = [self createCommand:opcode];
    Command *command = [[Command alloc] initCommand:commandData withTag:tag];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)innerSendCommand:(uint8_t *)params lenght:(int)paramsLen opcode:(int)opcode{

    NSData *commandData = [self createCommand:params length:paramsLen opcode:opcode];
    Command *command = [[Command alloc] initCommand:commandData];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)innerSendCommand:(uint8_t *)params lenght:(int)paramsLen opcode:(int)opcode tag:(int)tag{

    NSData *commandData = [self createCommand:params length:paramsLen opcode:opcode];
    Command *command = [[Command alloc] initCommand:commandData withTag:tag];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)innerSendCommand:(NSData *)paramsData opcode:(int)opcode{

    NSData *commandData = [self createCommand:paramsData opcode:opcode];
    Command *command = [[Command alloc] initCommand:commandData];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)innerSendCommand:(NSData *)paramsData opcode:(int)opcode tag:(int)tag{

    NSData *commandData = [self createCommand:paramsData opcode:opcode];
    Command *command = [[Command alloc] initCommand:commandData withTag:tag];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)innerSendCommand:(int)opcode delayTime:(NSTimeInterval)delayTime{

    NSData *commandData = [self createCommand:opcode];
    Command *command = [[Command alloc] initCommand:commandData delayTime:delayTime];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)innerSendCommand:(int)opcode delayTime:(NSTimeInterval)delayTime tag:(int)tag{

    NSData *commandData = [self createCommand:opcode];
    Command *command = [[Command alloc] initCommand:commandData delayTime:delayTime];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)innerSendCommand:(uint8_t *)params lenght:(int)paramsLen opcode:(int)opcode delayTime:(NSTimeInterval)delayTime{

    NSData *commandData = [self createCommand:params length:paramsLen opcode:opcode];
    Command *command = [[Command alloc] initCommand:commandData delayTime:delayTime];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)innerSendCommand:(uint8_t *)params lenght:(int)paramsLen opcode:(int)opcode delayTime:(NSTimeInterval)delayTime tag:(int)tag{

    NSData *commandData = [self createCommand:params length:paramsLen opcode:opcode];
    Command *command = [[Command alloc] initCommand:commandData delayTime:delayTime withTag:tag];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)innerSendCommand:(NSData *)paramsData opcode:(int)opcode delayTime:(NSTimeInterval)delayTime{

    NSData *commandData = [self createCommand:paramsData opcode:opcode];
    Command *command = [[Command alloc] initCommand:commandData delayTime:delayTime];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)innerSendCommand:(NSData *)paramsData opcode:(int)opcode delayTime:(NSTimeInterval)delayTime tag:(int)tag{

    NSData *commandData = [self createCommand:paramsData opcode:opcode];
    Command *command = [[Command alloc] initCommand:commandData delayTime:delayTime withTag:tag];
    CommandContext *context = [[CommandContext alloc] initCommandContext:command commandCallback:self.commandCallback];
    
    [self localSendCommand:context];
}

-(void)localSendCommand:(CommandContext *)context {
    
    @synchronized(self.lock) {
        
        NSTimeInterval currentTime = [[NSDate date] timeIntervalSince1970];
        NSTimeInterval offsetTime = currentTime - self.lastSendCommandTime;

        if (offsetTime > commandInterval && self.commandQueue.count == 0 && [self isCurrentSendCommandContext:context]) {
            
            RBQLog3(@">>> ① commandQueue中指令为空，且当前指令符合立即发送");

            [self writeCommandContext:context];
            self.lastSendCommandTime = currentTime;
            
        } else {
            
            [self.commandQueue addObject:context];

            NSTimeInterval delayTime = context.command ? context.command.delayTime : -1;
            int tag = context.command ? context.command.tag : -1;
            
            RBQLog3(@">>> ② 添加指令到commandQueue中 count:%ld, 将在%f秒后启动下一次发送数据,delayTime:%f;tag:%d", self.commandQueue.count, commandInterval, delayTime, tag);

            __weak typeof(self) weakSelf = self;
            [self.commandQueueTimer scheduledGCDTimerWithSartTime:^{
                [weakSelf sendQueueCommand];
            } startTime:commandInterval interval:0 repeats:NO];
        }
    }
}


-(void)sendQueueCommand {
    if (self.commandQueue.count == 0) {
        RBQLog3(@">>>> 😊 commandQueue中指令发送完毕 😊 >>>>>");
        return;
    }
//    RBQLog3(@" >>> 发送commandQueue中的指令");
    CommandContext *context = [self findWithRemoveCommandContext];
    [self writeCommandContext:context];

    if (self.commandQueue.count > 0) {
//        RBQLog3(@" >>> 启动下次commandQueue中指令发送");
        __weak typeof(self) weakSelf = self;
        [self.commandQueueTimer scheduledGCDTimerWithSartTime:^{
            [weakSelf sendQueueCommand];
        } startTime:commandInterval interval:0 repeats:NO];
    }
}


-(void)writeDataObjContext:(DataObjContext *)context{
    
    @autoreleasepool {
        
        if(!context || !context.dataObj || !context.dataObj.data){
            return;
        }
        
        DataObj *dataObj = context.dataObj;
        NSData *data = dataObj.data;
        
        [self writeData:data];
        
    }
}

-(void)writeData:(NSData *)data{
    if(!data){
        return;
    }
//    NSString *cmdArr = [self HexStringWithData:data];
    if (self.isBleConnType) {
//        RBQLog3(@" --> BLE 发送数据为:>>>%@",cmdArr);
        NSArray *peripherals = [self.baby findConnectedPeripherals];
        [self writeCharacteristics:peripherals serviceUuid:Service_UUID characteristicUuid:Write_UUID value:data];
        return;
    }

    if (self.isApOrWifiConnType) {
//        RBQLog3(@" --> WIFI 发送数据为:>>>%@",cmdArr);
        [self.client sendData:data];
    }
}

-(void)writeCommandContext:(CommandContext *)context{
    
    @autoreleasepool {
        
        if(!context || !context.command || !context.command.data){
            return;
        }
        
        Command *command = context.command;
        NSData *commandData = command.data;
        
        [self writeCommand:commandData];
        
        //记录上一次发送完指令的时间
        NSTimeInterval currentTime = [[NSDate date] timeIntervalSince1970];
        self.lastSendCommandTime = currentTime;
    }
}

-(void)writeCommand:(NSData *)data{
    if(!data){
        return;
    }
    NSString *cmdArr = [NSString convertDataToHexStr:data withSeparator:@","];
    if (self.isBleConnType) {
        RBQLog3(@" -->{BLE}发送的指令数据为:>>>%@",cmdArr);
        NSArray *peripherals = [self.baby findConnectedPeripherals];
        [self writeCharacteristics:peripherals serviceUuid:Service_UUID characteristicUuid:Write_UUID value:data];
        return;
    }
    
    if (self.isApOrWifiConnType) {
        RBQLog3(@" -->{WIFI}发送的指令数据为:>>>%@",cmdArr);
        [self.client sendData:data];
    }
}

-(BOOL)isCurrentSendCommandContext:(CommandContext *)context{
    if(!context||!context.command||!context.command.data){
        return NO;
    }
    if(context.command.delayTime == -1){
        return YES;
    }
    NSTimeInterval currentTime = [[NSDate date] timeIntervalSince1970];
    NSTimeInterval offset = currentTime - context.command.createTime;
//        if(offset>=command.delayTime&&command.isLossOnTimeout){
    // 目前还没设计合理的丢弃方案，暂时不考虑 isLossOnTimeout 值
    if(offset >= context.command.delayTime){
        return YES;
    }
    return NO;
}

/*
-(CommandContext *)findWithRemoveCommandContext{
    CommandContext *context;
    Command *command;
    for (NSInteger i=0; i<commandQueue.count; i++) {
        context = commandQueue[i];
        if(!context){
            continue;
        }
        command = context.command;
        if(!command){
            continue;
        }
        if(command.delayTime==-1){
            //移除并返回
            [commandQueue removeObject:context];
            return context;
        }
        NSTimeInterval currentTime = [[NSDate date] timeIntervalSince1970];
        NSTimeInterval offset = currentTime - command.createTime;
//        if(offset>=command.delayTime&&command.isLossOnTimeout){
        // 目前还没设计合理的丢弃方案，暂时不考虑 isLossOnTimeout 值
        if(offset>=command.delayTime){
            //移除并返回
            [commandQueue removeObject:context];
            return context;
        }
    }
    return nil;
}
 */

-(CommandContext *)findWithRemoveCommandContext{
    // 使用局部变量存储 foundContext，用于存储找到的需要移除的 CommandContext
    __block CommandContext *foundContext = nil;
    
    // 使用 enumerateObjectsUsingBlock: 遍历 commandQueue，简化代码并提高可读性
    [self.commandQueue enumerateObjectsUsingBlock:^(CommandContext * _Nonnull context, NSUInteger idx, BOOL * _Nonnull stop) {
        Command *command = context.command;
        
        // 如果 command 存在且 delayTime 为 -1，则找到需要移除的 CommandContext
        if (command && command.delayTime == -1) {
            foundContext = context;
            *stop = YES;
        }
        // 如果 command 存在且已超过 delayTime，则找到需要移除的 CommandContext
        else if (command && command.delayTime < [[NSDate date] timeIntervalSince1970] - command.createTime) {
            foundContext = context;
            *stop = YES;
        }
    }];
    
    // 如果找到了需要移除的 CommandContext，将其从 commandQueue 中移除
    if (foundContext) {
        [self.commandQueue removeObject:foundContext];
    }
    // 返回找到的需要移除的 CommandContext
    return foundContext;
}

#pragma mark -- CommandCallbackDelegate --
- (void)onCommandSuccess:(Command *)command obj:(NSObject *)obj{
    
}

- (void)onCommandError:(Command *)command errorMsg:(NSString *)errorMsg{
    
}

- (void)OnCommandTimeout:(Command *)command errorMsg:(NSString *)errorMsg{
    
}

#pragma mark -- DataObjCallbackDelegate --
- (void)onDataObjWriteSuccess:(DataObj *)dataObj obj:(NSObject *)obj{
    
}

- (void)onDataObjWriteError:(DataObj *)dataObj errorMsg:(NSString *)errorMsg{
    
}

- (void)OnDataObjWriteTimeout:(DataObj *)dataObj errorMsg:(NSString *)errorMsg{
    
}

-(void)beginReceivingJson{
    
    self.receivingJson = YES;
}

- (void)endReceivingJson{
    
    self.receivingJson = NO;
}

/*
-(void)receiving:(NSData *)data{
    
    @synchronized(self.receiveLock){
    
        @try {
            
//            RBQLog3(@"【receiving】data:%@",[NSString convertDataToHexStr:data]);
            
            if(![self hasPacketStart]){
                
                NSString *jsonStr  =[[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
                if (!jsonStr) {
                    return;
                }
                if ([jsonStr hasPrefix:@"{"]&&[jsonStr hasSuffix:@"}"]) {

                    //分发json事件
                    [self dispatchJsonEven:jsonStr];
                    return;
                }
                // 容错处理
                if ([jsonStr containsString:@"{"]
                    &&[jsonStr containsString:@"}"]
                    &&(![jsonStr hasPrefix:@"{"]||![jsonStr hasSuffix:@"}"])) {

                    NSRange start = [jsonStr rangeOfString:@"{"];
                    NSRange end = [jsonStr rangeOfString:@"}"];
                    
                    jsonStr = [jsonStr substringWithRange:NSMakeRange(start.location,end.location+1)];
                    
                    [self dispatchJsonEven:jsonStr];
                    return;
                }
                // 容错处理  这里一条json数据分多条返回过来，所以需要对json数据进行组装后进行解析
                if ([jsonStr containsString:@"{"]
                    &&![jsonStr containsString:@"}"]
                    &&![jsonStr hasPrefix:@"{"]) {
                    NSRange start = [jsonStr rangeOfString:@"{"];
                    jsonStr = [jsonStr substringFromIndex:start.location];
                }
                if ([jsonStr hasPrefix:@"{"]) {//json数据开始位置
                    self.stringBuilder = @"";
                    [self beginReceivingJson];
                    self.stringBuilder = jsonStr;
                    return;
                }
                if (self.receivingJson) {
                    
                    // 容错处理
                    if (![jsonStr hasSuffix:@"}"]&&[jsonStr containsString:@"}"]) {
                        
                        NSRange end = [jsonStr rangeOfString:@"}"];
                        jsonStr = [jsonStr substringWithRange:NSMakeRange(0,end.location+1)];
                    }

                    if ([jsonStr hasSuffix:@"}"]){
                        
                        if (!self.stringBuilder) {
                            return;
                        }
                        
                        self.stringBuilder = [self.stringBuilder stringByAppendingString: jsonStr];
                        [self dispatchJsonEven:self.stringBuilder];
                        //设置json数据接收结束标志receivingJsonData
                        [self endReceivingJson];
                        return;
                        
                    }else{

                        if (self.receivingJson){//持续接收json数据
                            if (!self.stringBuilder) {
                                return;
                            }
                            self.stringBuilder = [self.stringBuilder stringByAppendingString: jsonStr];
                        }
                    }
                    return;
                }
                
            }

            [self dispatchNSDataEven:data];
            
        } @catch (NSException *exception) {
            
        } @finally {
            
        }
        
    }
}
 */

-(void)receiving:(NSData *)data {
    
    @synchronized(self.receiveLock) {
        @try {
//             RBQLog3(@"【receiving】data:%@", [NSString convertDataToHexStr:data]);
            if (![self hasPacketStart]) {
                NSString *jsonStr = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
                if (!jsonStr) {
                    return;
                }

                if ([jsonStr hasPrefix:@"{"] && [jsonStr hasSuffix:@"}"]) {
                    [self dispatchJsonEven:jsonStr];
                    return;
                }

                if ([jsonStr containsString:@"{"] && [jsonStr containsString:@"}"]) {
                    NSRange start = [jsonStr rangeOfString:@"{"];
                    NSRange end = [jsonStr rangeOfString:@"}"];
                    jsonStr = [jsonStr substringWithRange:NSMakeRange(start.location, end.location - start.location + 1)];
                    [self dispatchJsonEven:jsonStr];
                    return;
                }

                if ([jsonStr containsString:@"{"] && ![jsonStr containsString:@"}"] && ![jsonStr hasPrefix:@"{"]) {
                    NSRange start = [jsonStr rangeOfString:@"{"];
                    jsonStr = [jsonStr substringFromIndex:start.location];
                }

                if ([jsonStr hasPrefix:@"{"]) {
                    self.stringBuilder = jsonStr;
                    [self beginReceivingJson];
                    return;
                }

                if (self.receivingJson) {
                    if (![jsonStr hasSuffix:@"}"] && [jsonStr containsString:@"}"]) {
                        NSRange end = [jsonStr rangeOfString:@"}"];
                        jsonStr = [jsonStr substringToIndex:end.location + 1];
                    }

                    if ([jsonStr hasSuffix:@"}"]) {
                        if (self.stringBuilder) {
                            self.stringBuilder = [self.stringBuilder stringByAppendingString:jsonStr];
                            [self dispatchJsonEven:self.stringBuilder];
                            [self endReceivingJson];
                        }
                        return;
                    } else if (self.receivingJson) {
                        if (self.stringBuilder) {
                            self.stringBuilder = [self.stringBuilder stringByAppendingString:jsonStr];
                        }
                    }
                    return;
                }
            }
            [self dispatchNSDataEven:data];
        } @catch (NSException *exception) {
            // Handle exception
        } @finally {
            // Finalize code if needed
        }
    }
}


-(void)clearCommandQueue{
    
    @synchronized(self.lock){
        
        [self.commandQueueTimer clearScheduledTimer];
        if (self.commandQueue.count!=0) {
            [self.commandQueue removeAllObjects];
        }
    }
}

-(void)clearHeartMonitorTimer{
    @synchronized (self.lock) {
        [self.heartMonitorTimer clearScheduledTimer];
    }
}

-(void)startMonitorHeartData:(int)start{
    @synchronized (self.lock) {
        [self clearHeartMonitorTimer];
        _heartLoseTimes = 0;
        __weak typeof(self)  weakSelf = self;
        [self.heartMonitorTimer scheduledGCDTimerWithSartTime:^{
            [weakSelf clientConnectTimeout];
        } startTime:start interval:0 repeats:NO];
    }
}

-(void)stopMonitorHeartData{
    @synchronized (self.lock) {
        [self clearHeartMonitorTimer];
        _heartLoseTimes = 0;
    }
}

-(void)clientConnectTimeout{
    _heartLoseTimes = _heartLoseTimes + 1;
    RBQLog3(@"当前丢失heartData次数:%d",_heartLoseTimes);
    if (_heartLoseTimes<maxLoseHeartTimes) {
        __weak typeof(self)  weakSelf = self;
        [self.heartMonitorTimer scheduledGCDTimerWithSartTime:^{
            [weakSelf clientConnectTimeout];
        } startTime:3.0f interval:0 repeats:NO];
        return;
    }
    if (!self.client) {
        return;
    }
    if([self.client isConnected]){
        RBQLog3(@"client socket 还连接着-主动断开打印机连接");
        [self.client disConnectWithCompletion:^{
            
        }];
    }
}

#pragma mark 代理方法
- (void)client:(TCPClient *)client didReadData:(NSData *)data {
    
    //5秒后启动心跳检测
    [self startMonitorHeartData:5.0f];
    
    if (!data) {
        return;
    }
    [self receiving:data];
}

- (void)client:(TCPClient *)client didConnect:(NSString *)host port:(uint16_t)port {

    __weak typeof(self)  weakSelf = self;
    RBQLog3(@"已连接WiFi")
    self.device.isConnected = YES;
    
    dispatch_async(dispatch_get_main_queue(), ^{
        if (weakSelf.onDeviceConnectSucceed) {
            weakSelf.onDeviceConnectSucceed();
        }
        [weakSelf notifyDeviceConnectSucceed];
    });
    
    /**自动去同步部分打印机信息*/
    [weakSelf syncingData];
    //5秒后启动心跳检测
    [weakSelf startMonitorHeartData:5.0f];
    
}

- (void)clientDidDisconnect:(TCPClient *)client {
    
    RBQLog3(@"😱【clientDidDisconnect】WiFi连接断开😱")
    /*
    __weak typeof(self)  weakSelf = self;
    
    RBQLog3(@"😱【clientDidDisconnect】WiFi连接断开😱")
    self.device.isConnected = NO;
    _connectType = ConnectTypeIdle;
    [self stopMonitorHeartData];
    [self clearCommandQueue];
    
    dispatch_async(dispatch_get_main_queue(), ^{
        if (weakSelf.onDeviceDisconnect) {
            weakSelf.onDeviceDisconnect();
        }
        [weakSelf notifyDeviceDisconnect];
    });
     */
}

- (void)clientDidFailToReconnect:(TCPClient *)client{
   
    __weak typeof(self)  weakSelf = self;
    
    RBQLog3(@"😱【clientDidFailToReconnect】WiFi连接断开😱")
    self.device.isConnected = NO;
    _connectType = ConnectTypeIdle;
    [self stopMonitorHeartData];
    [self clearCommandQueue];
    
    dispatch_async(dispatch_get_main_queue(), ^{
        if (weakSelf.onDeviceDisconnect) {
            weakSelf.onDeviceDisconnect();
        }
        [weakSelf notifyDeviceDisconnect];
    });
    
}


-(void)dispatchJsonEven:(NSString *)json{
    
    RBQLog3(@" <-- dispatchJsonEven:%@",json);

    __weak typeof(self)  weakSelf = self;
    __strong __typeof(weakSelf) strongSelf = weakSelf;

    @try
    {
        NSError *error = nil;
        // 业务逻辑
        NSData *jsonData = [json dataUsingEncoding:NSUTF8StringEncoding];
        NSDictionary *dic =  [NSJSONSerialization JSONObjectWithData:jsonData options:NSJSONReadingMutableContainers error:&error];

        int code = [[dic objectForKey:@"code"] intValue];

        if (code==0) {

            int cmd = [[dic objectForKey:@"cmd"] intValue];
            
            switch (cmd) {
                case opcode_readSoftwareInfo:
                {
                    NSString *deviceId = [dic objectForKey:@"id"];
                    NSString *name = [dic objectForKey:@"name"];
                    NSString *mcu_ver = [dic objectForKey:@"mcu_ver"];
                    NSString *date = [dic objectForKey:@"date"];

                    RBQLog3(@" <-- deviceId:%@; name:%@; mcu_ver:%@; date:%@",deviceId,name,mcu_ver,date);

                    self.device.printer_head_id = deviceId;
                    self.device.mcuName = name;
                    self.device.mcuVersion = mcu_ver;
                    self.device.mcu_date = date;

                    dispatch_async(dispatch_get_main_queue(), ^{
                        if (weakSelf.onReadDeviceInfo) {
                            weakSelf.onReadDeviceInfo(strongSelf.device, deviceId, name, mcu_ver, date);
                        }
                        [weakSelf notifyReadDeviceInfoForDevice:strongSelf.device deviceId:deviceId name:name mcuVersion:mcu_ver date:date];
                    });

                    break;
                }
                case opcode_readBattery:
                {
                    int bat = [[dic objectForKey:@"bat"] intValue];//电量
                    self.device.batteryLevel = bat;
                    
                    dispatch_async(dispatch_get_main_queue(), ^{
                        if (weakSelf.onReadBattery) {
                            weakSelf.onReadBattery(strongSelf.device, bat);
                        }
                        [weakSelf notifyReadBatteryForDevice:strongSelf.device batteryLevel:bat];
                    });

                    break;
                }
                case opcode_readPrinterParameters:
                {
                    NSString *msg = [dic objectForKey:@"msg"];

                    if (!msg) {
                        return;
                    }

                    RBQLog3(@" <-- cmd:%d; [msg]:%@",cmd,msg);

                    NSArray<NSString *> *parameters = [msg componentsSeparatedByString:@","];

                    int headValue = [parameters[0] intValue];
                    int l_pix = [parameters[1] intValue];
                    int p_pix = [parameters[2] intValue];
                    int distance = [parameters[3] intValue];

                    self.device.printer_head = headValue;
                    self.device.l_pix = l_pix;
                    self.device.p_pix = p_pix;
                    self.device.distance = distance;

                    dispatch_async(dispatch_get_main_queue(), ^{
                        if (weakSelf.onReadParameter) {
                            weakSelf.onReadParameter(strongSelf.device, headValue, l_pix, p_pix, distance);
                        }
                        [weakSelf notifyReadParameterForDevice:strongSelf.device headValue:headValue lPix:l_pix pPix:p_pix distance:distance];
                    });

                    break;
                }
                case opcode_readPrinterCirculationAndRepeatTime:
                {
                    NSString *msg = [dic objectForKey:@"msg"];

                    if (!msg) {
                        return;
                    }

                    RBQLog3(@" <-- cmd:%d; [msg]:%@",cmd,msg);

                    NSArray<NSString *> *parameters = [msg componentsSeparatedByString:@","];

                    int circulation_time = [parameters[0] intValue];
                    int repeat_time = [parameters[1] intValue];

                    self.device.cycles = circulation_time;
                    self.device.repeat_time = repeat_time;

                    dispatch_async(dispatch_get_main_queue(), ^{
                        if (weakSelf.onReadCirculationRepeat) {
                            weakSelf.onReadCirculationRepeat(strongSelf.device, circulation_time, repeat_time);
                        }
                        [weakSelf notifyReadCirculationRepeatForDevice:strongSelf.device circulationTime:circulation_time repeatTime:repeat_time];
                    });

                    break;
                }
                case opcode_readPrinterDirectionAndPrintHeadDirection:
                {
                    NSString *msg = [dic objectForKey:@"msg"];

                    if (!msg) {
                        return;
                    }

                    RBQLog3(@" <-- cmd:%d; [msg]:%@",cmd,msg);

                    NSArray<NSString *> *parameters = [msg componentsSeparatedByString:@","];

                    int direction = [parameters[0] intValue];
                    int printHeadDirection = [parameters[1] intValue];

                    self.device.direction = direction;
                    self.device.oldDirection = direction;

                    dispatch_async(dispatch_get_main_queue(), ^{
                        if (weakSelf.onReadDirection) {
                            weakSelf.onReadDirection(strongSelf.device, direction,printHeadDirection);
                        }
                        [weakSelf notifyReadDirectionForDevice:strongSelf.device direction:direction printHeadDirection:printHeadDirection];
                    });

                    break;
                }
                case opcode_readPrinterHeadTemperature:
                {
                    
                    int index = [[dic objectForKey:@"index"] intValue];
                    int temp_get = [[dic objectForKey:@"temp_get"] intValue];
                    int temp_set = [[dic objectForKey:@"temp_set"] intValue];
                    
                    RBQLog3(@" <-- temp_get:%d; temp_set:%d",temp_get,temp_set);
                    
                    self.device.temperature = temp_get;
                    
                    dispatch_async(dispatch_get_main_queue(), ^{
                        if (weakSelf.onReadPrinterHeadTemperature) {
                            weakSelf.onReadPrinterHeadTemperature(strongSelf.device,index, temp_get, temp_set);
                        }
                        [weakSelf notifyReadPrinterHeadTemperatureForDevice:strongSelf.device index:index tempGet:temp_get tempSet:temp_set];
                    });
                    
                    break;
                }
                case opcode_readSilentState:
                {
                    BOOL silentState = [[dic objectForKey:@"msg"] boolValue];//勿扰模式状态
                    self.device.silentState = silentState;
                    dispatch_async(dispatch_get_main_queue(), ^{
                        if (weakSelf.onReadSilentStateForDevice) {
                            weakSelf.onReadSilentStateForDevice(strongSelf.device,silentState);
                        }
                        [weakSelf notifyReadSilentStateForDevice:strongSelf.device silentState:silentState];
                    });
                    break;
                }
                case opcode_readAutoPowerOffState:
                {
                    BOOL autoPowerOffState = [[dic objectForKey:@"msg"] boolValue];//自动关机状态
                    self.device.autoPowerOffState = autoPowerOffState;
                    dispatch_async(dispatch_get_main_queue(), ^{
                        if (weakSelf.onReadAutoPowerOffStateForDevice) {
                            weakSelf.onReadAutoPowerOffStateForDevice(strongSelf.device,autoPowerOffState);
                        }
                        [weakSelf notifyReadAutoPowerOffStateForDevice:strongSelf.device autoPowerOff:autoPowerOffState];
                    });
                    break;
                }
                case 4130:
                {
                    //设备端电量低的时候每5秒发一次低电量提醒
                    
                    break;
                }
                case 4098:
                {
                    //打印头清洗开始
                    
                    break;
                }
                case 4099:
                {
                    //打印头清洗结束
                    
                    break;
                }
                case opcode_readPrintStart:
                {
                    //开始打印
                    NSString *msg = [dic objectForKey:@"msg"];

                    if (!msg) {
                        return;
                    }

                    RBQLog3(@" <-- cmd:%d; [msg]:%@",cmd,msg);
                    
                    NSArray<NSString *> *parameters = [msg componentsSeparatedByString:@","];

                    int beginIndex = [parameters[0] intValue];
                    int endIndex = [parameters[1] intValue];
                    int currentIndex = [parameters[2] intValue];
                    
                    dispatch_async(dispatch_get_main_queue(), ^{
                        if (weakSelf.onPrintStart) {
                            weakSelf.onPrintStart(strongSelf.device,beginIndex, endIndex, currentIndex);
                        }
                        [weakSelf notifyPrintStart:strongSelf.device beginIndex:beginIndex endIndex:endIndex currentIndex:currentIndex];
                    });
                    
                    break;
                }
                case opcode_readPrintCompleted:
                {
                    //结束打印
                    NSString *msg = [dic objectForKey:@"msg"];

                    if (!msg) {
                        return;
                    }

                    RBQLog3(@" <-- cmd:%d; [msg]:%@",cmd,msg);
                    
                    NSArray<NSString *> *parameters = [msg componentsSeparatedByString:@","];

                    int beginIndex = [parameters[0] intValue];
                    int endIndex = [parameters[1] intValue];
                    int currentIndex = [parameters[2] intValue];
                    
                    // 直接响应打印结束指令
                    dispatch_async(dispatch_get_main_queue(), ^{
                        if (weakSelf.onPrintComplete) {
                            weakSelf.onPrintComplete(strongSelf.device,beginIndex, endIndex, currentIndex);
                        }
                        [weakSelf notifyPrintComplete:strongSelf.device beginIndex:beginIndex endIndex:endIndex currentIndex:currentIndex];
                    });
                    
                    
                    if(weakSelf.dataSendType == DataSendCompleteOnceWaitNext){

                        if ([self.multiRowDataPacket hasNextRow]) {

                            //发送下一行数据
                            dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(0.3f * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{

                                [weakSelf.multiRowDataPacket cursorMoveToNext];
                                // 由于机器垃圾，最多只能存8拼，所以文档模式每次都存第一个位置，如果打印多份得传输多次
//                                uint8_t currentRow = self.multiRowDataPacket.currentRow & 0xFF;
                                uint8_t currentRow = 0 & 0xFF;

                    //            RBQLog3(@"&&&& 打印指令 currentRow:%d",currentRow);

                                NSUInteger arrIndexDataSize = weakSelf.multiRowDataPacket.currentRowDataLength;//4byte

                                uint8_t dataSize0 = arrIndexDataSize & 0xFF;
                                uint8_t dataSize1 = (arrIndexDataSize >> 8) & 0xFF;
                                uint8_t dataSize2 = (arrIndexDataSize >> 16) & 0xFF;
                                uint8_t dataSize3 = (arrIndexDataSize >> 24) & 0xFF;
                                uint8_t compress = weakSelf.multiRowDataPacket.compress & 0xFF;

                                uint8_t transmitParams[6] = {currentRow,dataSize0,dataSize1,dataSize2,dataSize3,compress};

                                [weakSelf innerSendCommand:transmitParams lenght:6 opcode:opcode_transmitPicture];

                            });

                        }else{
                            //打印结束，直接反回打印结束事件即可
                            dispatch_async(dispatch_get_main_queue(), ^{

                                weakSelf.multiRowDataPacket.currentTime = [[NSDate date] timeIntervalSince1970];
                                CGFloat size = weakSelf.multiRowDataPacket.totalDataLen /1000.0f;

                                [weakSelf cancelAllPacketStart];
                                weakSelf.isSendingData = NO;
                                
                                if (weakSelf.onDataProgressFinish) {
                                    weakSelf.onDataProgressFinish(size, 100, weakSelf.multiRowDataPacket.progressPrecision, weakSelf.multiRowDataPacket.startTime, weakSelf.multiRowDataPacket.currentTime);
                                }
                                [weakSelf notifyDataProgressFinish:size progress:100 progressPrecision:weakSelf.multiRowDataPacket.progressPrecision startTime:weakSelf.multiRowDataPacket.startTime currentTime:weakSelf.multiRowDataPacket.currentTime];
                            });

                        }
                        
                    }
                    
                    break;
                }
                default:
                    break;
            }

        }else{
            
            RBQLog3(@"收到打印机错误信息:%d",code);
            
        }

    }
    @catch (NSException *exception)
    {
        //异常处理代码
    }
}

-(void)clearWaitResponseTimer{
    @synchronized (self.lock) {
        [self.waitResponseTimer clearScheduledTimer];
    }
}

-(void)dispatchNSDataEven:(NSData *)data{

    if (self.multiRowDataPacket.start) {
        
        [self dispatchMultiRowDataEven:data];
        
    }else if(self.logoDataPacket.start){
        
        [self dispatchLogoDataEven:data];
        
    }else if(self.otaDataPacket.start){
        
        [self dispatchOtaDataEven:data];
    }

}

-(void)dispatchMultiRowDataEven:(NSData *)data {
    
    if (![self.multiRowDataPacket hasData]){
        RBQLog3(@"没有打印数据");
        return;
    }
    
    __weak typeof(self)  weakSelf = self;
//    __strong __typeof(weakSelf) strongSelf = weakSelf;

    //请求数据
    if ([self.multiRowDataPacket isRequestData:data]){//c
        [self clearWaitResponseTimer];
//        RBQLog3(@" <-- 收到第 %d 个请求",self.N_Index);
        //还有下一帧数据，继续发送下一帧数据
        if ([self.multiRowDataPacket hasNextPacketWithCurrentRow]) {
            
            self.N_Index = self.N_Index + 1;
            [self sendNextMultiRowDataPacket];
        }

    }else if ([self.multiRowDataPacket isNAK:data]){//NAK  重传当前数据包请求命令
//        RBQLog3(@"<-- 重复第 %d 个请求",self.N_Index);
        [self sendNakMultiRowDataPacket];

    }else if ([self.multiRowDataPacket isEOT:data]){
        
//        RBQLog3(@"<-- [ 收到打印结束标志 ]");
        self.N_Index = 0;
        if(self.dataSendType == DataSendCompleteOnceWaitNext){

            //发送打印指令  发送打印当前行指令
            dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(0.1f * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
                // 由于机器最多只能存8拼，所以文档模式每次都存第一个位置，如果打印多份得传输多次
//                uint8_t beginIndex = self.multiRowDataPacket.currentRow&0xFF;
//                uint8_t endIndex = (self.multiRowDataPacket.currentRow+1)&0xFF;
//                uint8_t printParams[2] = {beginIndex,endIndex};
                uint8_t printParams[2] = {0,1};
                [weakSelf innerSendCommand:printParams lenght:2 opcode:opcode_printPicture];
    //            RBQLog3(@" &&&& 数据传输完毕 index:%d",index);
            });

        }else {
            
            if ([self.multiRowDataPacket hasNextRow]) {

                dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(0.3f * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{

                    [weakSelf.multiRowDataPacket cursorMoveToNext];

                    uint8_t currentRow = self.multiRowDataPacket.currentRow & 0xFF;

                    RBQLog3(@" 🚴🏻 打印指令 currentRow:%d",currentRow);

                    NSUInteger arrIndexDataSize = weakSelf.multiRowDataPacket.currentRowDataLength;//4byte

                    uint8_t dataSize0 = arrIndexDataSize & 0xFF;
                    uint8_t dataSize1 = (arrIndexDataSize >> 8) & 0xFF;
                    uint8_t dataSize2 = (arrIndexDataSize >> 16) & 0xFF;
                    uint8_t dataSize3 = (arrIndexDataSize >> 24) & 0xFF;
                    uint8_t compress = self.multiRowDataPacket.compress & 0xFF;

                    uint8_t transmitParams[6] = {currentRow,dataSize0,dataSize1,dataSize2,dataSize3,compress};

                    [weakSelf innerSendCommand:transmitParams lenght:6 opcode:opcode_transmitPicture];

                });

            }else{
                //发送打印指令  打印0-totalRowCount行
                dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(0.1f * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
                    
                    uint8_t index = weakSelf.multiRowDataPacket.totalRowCount&0xFF;
                    uint8_t printParams[2] = {0,index};
                    [weakSelf innerSendCommand:printParams lenght:2 opcode:opcode_printPicture];
                    RBQLog3(@" 🚗 数据传输完毕 index:%d",index);

                    weakSelf.multiRowDataPacket.currentTime = [[NSDate date] timeIntervalSince1970];
                    CGFloat size = weakSelf.multiRowDataPacket.totalDataLen /1000.0f;

                    [weakSelf cancelAllPacketStart];
                    weakSelf.isSendingData = NO;
                    
                    if (weakSelf.onDataProgressFinish) {
                        weakSelf.onDataProgressFinish(size, 100, weakSelf.multiRowDataPacket.progressPrecision, weakSelf.multiRowDataPacket.startTime, weakSelf.multiRowDataPacket.currentTime);
                    }
                    [weakSelf notifyDataProgressFinish:size progress:100 progressPrecision:weakSelf.multiRowDataPacket.progressPrecision startTime:weakSelf.multiRowDataPacket.startTime currentTime:weakSelf.multiRowDataPacket.currentTime];
                });
            }
            
        }
        
    }
}

-(void)dispatchLogoDataEven:(NSData *)data{
    
//    RBQLog3(@"dispatchLogoDataEven");

    if (![self.logoDataPacket hasData]){
        RBQLog3(@"没有Logo数据");
        return;
    }
    
    __weak typeof(self)  weakSelf = self;
//    __strong __typeof(weakSelf) strongSelf = weakSelf;

    //请求数据
    if ([self.logoDataPacket isRequestData:data]){//c
        [self clearWaitResponseTimer];
//        RBQLog3(@"请求数据");
        //还有下一帧数据，继续发送下一帧数据
        if ([self.logoDataPacket hasNextPacket]) {
            
//            RBQLog3(@" <-- 收到第 %d 个请求",self.N_Index);
            self.N_Index = self.N_Index + 1;
            
            [self sendNextLogoDataPacket];

        }

    }else if ([self.logoDataPacket isNAK:data]){//NAK  重传当前数据包请求命令

        [self sendNakLogoDataPacket];

    }else if ([self.logoDataPacket isEOT:data]){
        
        self.logoDataPacket.currentTime = [[NSDate date] timeIntervalSince1970];
        CGFloat size = self.logoDataPacket.totalDataLen /1000.0f;

        [self cancelAllPacketStart];
        self.isSendingData = NO;
        
        dispatch_async(dispatch_get_main_queue(), ^{
            if (weakSelf.onDataProgressFinish) {
                weakSelf.onDataProgressFinish(size, 100, weakSelf.logoDataPacket.progressPrecision, weakSelf.logoDataPacket.startTime, weakSelf.logoDataPacket.currentTime);
            }
            [weakSelf notifyDataProgressFinish:size progress:100 progressPrecision:weakSelf.logoDataPacket.progressPrecision startTime:weakSelf.logoDataPacket.startTime currentTime:weakSelf.logoDataPacket.currentTime];
        });
    }
}

-(void)dispatchOtaDataEven:(NSData *)data{
    
//    RBQLog3(@"dispatchOtaDataEven");
    
    if (![self.otaDataPacket hasData]){
        RBQLog3(@"没有Logo数据");
        return;
    }
    __weak typeof(self)  weakSelf = self;
//    __strong __typeof(weakSelf) strongSelf = weakSelf;

    //请求数据
    if ([self.otaDataPacket isRequestData:data]){//c
        [self clearWaitResponseTimer];
//        RBQLog3(@"请求数据");
        //还有下一帧数据，继续发送下一帧数据
        if ([self.otaDataPacket hasNextPacket]) {
            
//            RBQLog3(@" <-- 收到第 %d 个请求",self.N_Index);
            self.N_Index = self.N_Index + 1;
            
            [self sendNextOtaDataPacket];

        }

    }else if ([self.otaDataPacket isNAK:data]){//NAK  重传当前数据包请求命令

        [self sendNakOtaDataPacket];

    }else if ([self.otaDataPacket isEOT:data]){
        
        self.otaDataPacket.currentTime = [[NSDate date] timeIntervalSince1970];
        CGFloat size = self.otaDataPacket.totalDataLen /1000.0f;
        
        [self cancelAllPacketStart];
        self.isSendingData = NO;
        
        dispatch_async(dispatch_get_main_queue(), ^{
            if (weakSelf.onDataProgressFinish) {
                weakSelf.onDataProgressFinish(size, 100, weakSelf.otaDataPacket.progressPrecision, weakSelf.otaDataPacket.startTime, weakSelf.otaDataPacket.currentTime);
            }
            [weakSelf notifyDataProgressFinish:size progress:100 progressPrecision:weakSelf.otaDataPacket.progressPrecision startTime:weakSelf.otaDataPacket.startTime currentTime:weakSelf.otaDataPacket.currentTime];
        });
    }
}


/**
 ******************************************************************************
 * 发送连续的XModem大数据包  <开始位置>
 *******************************************************************************
 */

-(void)cancelSendMultiRowDataPacket{
    
    if (!self.multiRowDataPacket.start) {
        return;
    }
    [self clearWaitResponseTimer];
    [self.multiRowDataPacket clear];
}

-(void)setWithSendMultiRowDataPacket:(MultiRowData *)multiRowImageData{
    int fn = STX_E;
    if (self.isApOrWifiConnType) {
        fn = STX_A;
    }
    [self setWithSendMultiRowDataPacket:multiRowImageData Fn:fn type:DataSendOnceContinuous];
}

-(void)setWithSendMultiRowDataPacket:(MultiRowData *)multiRowImageData Fn:(int)fn{
    [self setWithSendMultiRowDataPacket:multiRowImageData Fn:fn type:DataSendOnceContinuous];
}

-(void)setWithSendMultiRowDataPacket:(MultiRowData *)multiRowImageData type:(DataSendType)type{
    int fn = STX_E;
    if (self.isApOrWifiConnType) {
        fn = STX_A;
    }
    [self setWithSendMultiRowDataPacket:multiRowImageData Fn:fn type:type];
}

-(void)setWithSendMultiRowDataPacket:(MultiRowData *)multiRowImageData Fn:(int)fn type:(DataSendType)type{
    // 如果没连接，则不发送
    if(![self isConnected]){
        return;
    }
    //正在和设备同步数据
    if (self.isSyncingData) {
        NSError *error = [NSError errorWithDomain:@"mxSdk错误，正在和设备进行数据同步中..." code:SyncingDataError userInfo:nil];
        if (self.onDataProgressError) {
            self.onDataProgressError(error);
        }
        [self notifyDataProgressError:error];
        return;
    }
    if (self.commandQueue.count>0) {
        NSError *error = [NSError errorWithDomain:@"mxSdk错误，指令集中还存在指令正在处理，请稍等..." code:CommandQueueIsNoEmptyError userInfo:nil];
        if (self.onDataProgressError) {
            self.onDataProgressError(error);
        }
        [self notifyDataProgressError:error];
        return;
    }
    
    self.N_Index = 0;
    self.dataSendType = type;
    
    [self.multiRowDataPacket set:multiRowImageData fh:fn];
    [self localSetWithSendMultiRowDataPacket];
    __weak typeof(self)  weakSelf = self;
    [self clearWaitResponseTimer];
    [self.waitResponseTimer scheduledGCDTimerWithSartTime:^{
        [weakSelf localSetWithSendMultiRowDataPacket];
    } startTime:retrySendDataTime interval:0 repeats:NO];
}

-(void)localSetWithSendMultiRowDataPacket{

    if (![self.multiRowDataPacket hasData]) {
        RBQLog3(@"【localSetWithSendMultiRowDataPacket】没有打印数据可发送");
        return;
    }
    self.isSendingData = YES;
    __weak typeof(self)  weakSelf = self;
//    __strong __typeof(weakSelf) strongSelf = weakSelf;
    [self endReceivingJson];

    [self startPacket:self.multiRowDataPacket];
    
    [self clearCommandQueue];

    uint8_t currentRow = self.multiRowDataPacket.currentRow&0xFF;

//    RBQLog3(@"&&&& 打印指令 currentRow:%d",currentRow);

    NSUInteger arrIndexDataSize = self.multiRowDataPacket.currentRowDataLength;//4byte

    uint8_t dataSize0 = arrIndexDataSize & 0xFF;
    uint8_t dataSize1 = (arrIndexDataSize >> 8) & 0xFF;
    uint8_t dataSize2 = (arrIndexDataSize >> 16) & 0xFF;
    uint8_t dataSize3 = (arrIndexDataSize >> 24) & 0xFF;
    uint8_t compress = self.multiRowDataPacket.compress & 0xFF;

    uint8_t transmitParams[6] = {currentRow,dataSize0,dataSize1,dataSize2,dataSize3,compress};

    [self innerSendCommand:transmitParams lenght:6 opcode:opcode_transmitPicture tag:1000];

    self.multiRowDataPacket.startTime = [[NSDate date] timeIntervalSince1970];
    CGFloat size =  self.multiRowDataPacket.totalDataLen /1000.0f;
    //发送进度更新事件
    dispatch_async(dispatch_get_main_queue(), ^{
        if (weakSelf.onDataProgressStart) {
            weakSelf.onDataProgressStart(size, 0, weakSelf.multiRowDataPacket.progressPrecision, weakSelf.multiRowDataPacket.startTime);
        }
        [weakSelf notifyDataProgressStart:size progress:0 progressPrecision:weakSelf.multiRowDataPacket.progressPrecision startTime:weakSelf.multiRowDataPacket.startTime];
    });

}


-(void)sendNextMultiRowDataPacket{

    __weak typeof(self)  weakSelf = self;
//    __strong __typeof(weakSelf) strongSelf = weakSelf;
    NSData *data = [self.multiRowDataPacket getNextPacket];
    
//    RBQLog3(@"--> 发送第 %d 包数据",self.multiRowDataPacket.indexInCurrentRowPacket);

    self.multiRowDataPacket.currentTime = [[NSDate date] timeIntervalSince1970];

    BOOL updateProgress = [self.multiRowDataPacket invalidateProgress];
    if (updateProgress){
        float progress = self.multiRowDataPacket.progress;
        float size = (float) self.multiRowDataPacket.totalDataLen /1000.0f;
        //发送进度更新事件
        dispatch_async(dispatch_get_main_queue(), ^{
            if (weakSelf.onDataProgress) {
                weakSelf.onDataProgress(size, progress, weakSelf.multiRowDataPacket.progressPrecision, weakSelf.multiRowDataPacket.startTime, weakSelf.multiRowDataPacket.currentTime);
            }
            [weakSelf notifyDataProgress:size progress:progress progressPrecision:weakSelf.multiRowDataPacket.progressPrecision startTime:weakSelf.multiRowDataPacket.startTime currentTime:weakSelf.multiRowDataPacket.currentTime];
        });
    }
    NSData *formatData = [self.multiRowDataPacket packetFormat:data];
    DataObj *dataObj = [[DataObj alloc] initDataObj:formatData];
    DataObjContext *context = [[DataObjContext alloc] initDataObjContext:dataObj dataObjCallback:self.dataObjCallback];
    [self writeDataObjContext:context];

}

-(void)sendNakMultiRowDataPacket{

//    RBQLog3(@"NAK 重传当前包");
    NSData *data = [self.multiRowDataPacket getCurrentPacket];
    self.multiRowDataPacket.currentTime = [[NSDate date] timeIntervalSince1970];
    NSData *formatData = [self.multiRowDataPacket packetFormat:data];
    DataObj *dataObj = [[DataObj alloc] initDataObj:formatData];
    DataObjContext *context = [[DataObjContext alloc] initDataObjContext:dataObj dataObjCallback:self.dataObjCallback];
    [self writeDataObjContext:context];
}

-(void)cancelSendLogoDataPacket{
    
    if (!self.logoDataPacket.start) {
        return;
    }
    [self clearWaitResponseTimer];
    [self.logoDataPacket clear];
}

-(void)setWithSendLogoDataPacket:(LogoData *)logoData{
    int fn = STX_E;
    if (self.isApOrWifiConnType) {
        fn = STX_A;
    }
    [self setWithSendLogoDataPacket:logoData Fn:fn];
}


-(void)setWithSendLogoDataPacket:(LogoData *)logoData Fn:(int)fn{
    // 如果没连接，则不发送
    if(![self isConnected]){
        return;
    }
    //正在和设备同步数据
    if (self.isSyncingData) {
        NSError *error = [NSError errorWithDomain:@"mxSdk错误，正在和设备进行数据同步中..." code:SyncingDataError userInfo:nil];
        if (self.onDataProgressError) {
            self.onDataProgressError(error);
        }
        [self notifyDataProgressError:error];
        return;
    }
    if (self.commandQueue.count>0) {
        NSError *error = [NSError errorWithDomain:@"mxSdk错误，指令集中还存在指令正在处理，请稍等..." code:CommandQueueIsNoEmptyError userInfo:nil];
        if (self.onDataProgressError) {
            self.onDataProgressError(error);
        }
        [self notifyDataProgressError:error];
        return;
    }
    
    self.N_Index = 0;
    
    [self.logoDataPacket set:logoData fh:fn];
    [self localSetWithSendLogoDataPacket];
    __weak typeof(self)  weakSelf = self;
    [self clearWaitResponseTimer];
    [self.waitResponseTimer scheduledGCDTimerWithSartTime:^{
        [weakSelf localSetWithSendLogoDataPacket];
    } startTime:retrySendDataTime interval:0 repeats:NO];
}

-(void)localSetWithSendLogoDataPacket{

    if (![self.logoDataPacket hasData]) {
        return;
    }
    self.isSendingData = YES;
    __weak typeof(self)  weakSelf = self;
//    __strong __typeof(weakSelf) strongSelf = weakSelf;
    [self endReceivingJson];

    [self startPacket:self.logoDataPacket];
    
    [self clearCommandQueue];

    NSUInteger arrIndexDataSize = self.logoDataPacket.totalDataLen;//4byte

    uint8_t dataSize0 = arrIndexDataSize & 0xFF;
    uint8_t dataSize1 = (arrIndexDataSize >> 8) & 0xFF;
    uint8_t dataSize2 = (arrIndexDataSize >> 16) & 0xFF;
    uint8_t dataSize3 = (arrIndexDataSize >> 24) & 0xFF;

    uint8_t transmitParams[4] = {dataSize0,dataSize1,dataSize2,dataSize3};

    [self innerSendCommand:transmitParams lenght:4 opcode:opcode_transmitLogo];

    self.logoDataPacket.startTime = [[NSDate date] timeIntervalSince1970];
    CGFloat size =  self.logoDataPacket.totalDataLen /1000.0f;
    //发送进度更新事件
    dispatch_async(dispatch_get_main_queue(), ^{
        if (weakSelf.onDataProgressStart) {
            weakSelf.onDataProgressStart(size, 0, weakSelf.logoDataPacket.progressPrecision, weakSelf.logoDataPacket.startTime);
        }
        [weakSelf notifyDataProgressStart:size progress:0 progressPrecision:weakSelf.logoDataPacket.progressPrecision startTime:weakSelf.logoDataPacket.startTime];
    });
}


-(void)sendNextLogoDataPacket{

//    RBQLog3(@"sendNextLogoDataPacket");
    
    __weak typeof(self)  weakSelf = self;
//    __strong __typeof(weakSelf) strongSelf = weakSelf;
    
    NSData *data = [self.logoDataPacket getNextPacket];

    self.logoDataPacket.currentTime = [[NSDate date] timeIntervalSince1970];

    BOOL updateProgress = [self.logoDataPacket invalidateProgress];
    if (updateProgress){
        float progress = self.logoDataPacket.progress;
        float size = (float) self.logoDataPacket.totalDataLen /1000.0f;
        //发送进度更新事件
        dispatch_async(dispatch_get_main_queue(), ^{
            if (weakSelf.onDataProgress) {
                weakSelf.onDataProgress(size, progress, weakSelf.logoDataPacket.progressPrecision, weakSelf.logoDataPacket.startTime, weakSelf.logoDataPacket.currentTime);
            }
            [weakSelf notifyDataProgress:size progress:progress progressPrecision:weakSelf.logoDataPacket.progressPrecision startTime:weakSelf.logoDataPacket.startTime currentTime:weakSelf.logoDataPacket.currentTime];
        });
    }
    NSData *formatData = [self.logoDataPacket packetFormat:data];
    DataObj *dataObj = [[DataObj alloc] initDataObj:formatData];
    DataObjContext *context = [[DataObjContext alloc] initDataObjContext:dataObj dataObjCallback:self.dataObjCallback];
    [self writeDataObjContext:context];

}

-(void)sendNakLogoDataPacket{

    RBQLog3(@"NAK 重传当前包");
    NSData *data = [self.logoDataPacket getCurrentPacket];
    self.logoDataPacket.currentTime = [[NSDate date] timeIntervalSince1970];
    NSData *formatData = [self.logoDataPacket packetFormat:data];
    DataObj *dataObj = [[DataObj alloc] initDataObj:formatData];
    DataObjContext *context = [[DataObjContext alloc] initDataObjContext:dataObj dataObjCallback:self.dataObjCallback];
    [self writeDataObjContext:context];
}

-(void)cancelSendOtaDataPacket{
    
    if (!self.otaDataPacket.start) {
        return;
    }
    [self clearWaitResponseTimer];
    [self.otaDataPacket clear];
}

-(void)setWithSendOtaDataPacket:(NSData *)data{
    int fn = STX_E;
    if (self.isApOrWifiConnType) {
        fn = STX_A;
    }
    [self setWithSendOtaDataPacket:data Fn:fn];
}


-(void)setWithSendOtaDataPacket:(NSData *)data Fn:(int)fn{
    // 如果没连接，则不发送
    if(![self isConnected]){
        return;
    }
    //正在和设备同步数据
    if (self.isSyncingData) {
        NSError *error = [NSError errorWithDomain:@"mxSdk错误，正在和设备进行数据同步中..." code:SyncingDataError userInfo:nil];
        if (self.onDataProgressError) {
            self.onDataProgressError(error);
        }
        [self notifyDataProgressError:error];
        return;
    }
    if (self.commandQueue.count>0) {
        NSError *error = [NSError errorWithDomain:@"mxSdk错误，指令集中还存在指令正在处理，请稍等..." code:CommandQueueIsNoEmptyError userInfo:nil];
        if (self.onDataProgressError) {
            self.onDataProgressError(error);
        }
        [self notifyDataProgressError:error];
        return;
    }
    
    self.N_Index = 0;
    
    [self.otaDataPacket set:data fh:fn];
    [self localSetWithSendOtaDataPacket];
    __weak typeof(self)  weakSelf = self;
    [self clearWaitResponseTimer];
    [self.waitResponseTimer scheduledGCDTimerWithSartTime:^{
        [weakSelf localSetWithSendOtaDataPacket];
    } startTime:retrySendDataTime interval:0 repeats:NO];
}

-(void)localSetWithSendOtaDataPacket{

    if (![self.otaDataPacket hasData]) {
        return;
    }
    self.isSendingData = YES;
    __weak typeof(self)  weakSelf = self;
//    __strong __typeof(weakSelf) strongSelf = weakSelf;
    
    [self endReceivingJson];

    [self startPacket:self.otaDataPacket];
    
    [self clearCommandQueue];

    NSUInteger arrIndexDataSize = self.otaDataPacket.totalDataLen;//4byte

    uint8_t dataSize0 = arrIndexDataSize & 0xFF;
    uint8_t dataSize1 = (arrIndexDataSize >> 8) & 0xFF;
    uint8_t dataSize2 = (arrIndexDataSize >> 16) & 0xFF;
    uint8_t dataSize3 = (arrIndexDataSize >> 24) & 0xFF;

    uint8_t transmitParams[4] = {dataSize0,dataSize1,dataSize2,dataSize3};

    [self innerSendCommand:transmitParams lenght:4 opcode:opcode_updateMcu];

    self.otaDataPacket.startTime = [[NSDate date] timeIntervalSince1970];
    CGFloat size =  self.otaDataPacket.totalDataLen /1000.0f;
    //发送进度更新事件
    dispatch_async(dispatch_get_main_queue(), ^{
        if (weakSelf.onDataProgressStart) {
            weakSelf.onDataProgressStart(size, 0, weakSelf.otaDataPacket.progressPrecision, weakSelf.otaDataPacket.startTime);
        }
        [weakSelf notifyDataProgressStart:size progress:0 progressPrecision:weakSelf.otaDataPacket.progressPrecision startTime:weakSelf.otaDataPacket.startTime];
    });
}

-(void)sendNextOtaDataPacket{

//    RBQLog3(@"sendNextOtaDataPacket");
    __weak typeof(self)  weakSelf = self;
//    __strong __typeof(weakSelf) strongSelf = weakSelf;
    
    NSData *data = [self.otaDataPacket getNextPacket];

    self.otaDataPacket.currentTime = [[NSDate date] timeIntervalSince1970];

    BOOL updateProgress = [self.otaDataPacket invalidateProgress];
    if (updateProgress){
        float progress = self.otaDataPacket.progress;
        float size = (float) self.otaDataPacket.totalDataLen /1000.0f;
        //发送进度更新事件
        dispatch_async(dispatch_get_main_queue(), ^{
            if (weakSelf.onDataProgress) {
                weakSelf.onDataProgress(size, progress, weakSelf.otaDataPacket.progressPrecision, weakSelf.otaDataPacket.startTime, weakSelf.otaDataPacket.currentTime);
            }
            [weakSelf notifyDataProgress:size progress:progress progressPrecision:weakSelf.otaDataPacket.progressPrecision startTime:weakSelf.otaDataPacket.startTime currentTime:weakSelf.otaDataPacket.currentTime];
        });
    }
    NSData *formatData = [self.otaDataPacket packetFormat:data];
    DataObj *dataObj = [[DataObj alloc] initDataObj:formatData];
    DataObjContext *context = [[DataObjContext alloc] initDataObjContext:dataObj dataObjCallback:self.dataObjCallback];
    [self writeDataObjContext:context];

}

-(void)sendNakOtaDataPacket{

    RBQLog3(@"NAK 重传当前包");

    NSData *data = [self.otaDataPacket getCurrentPacket];
    self.otaDataPacket.currentTime = [[NSDate date] timeIntervalSince1970];
    NSData *formatData = [self.otaDataPacket packetFormat:data];
    DataObj *dataObj = [[DataObj alloc] initDataObj:formatData];
    DataObjContext *context = [[DataObjContext alloc] initDataObjContext:dataObj dataObjCallback:self.dataObjCallback];
    [self writeDataObjContext:context];
}


-(int)commandSequence{

    commandSequence = commandSequence + 1;

    if (commandSequence > 255){

        commandSequence = 1;
    }
    return commandSequence;
}

- (NSArray *)dataToArray:(uint8_t *)cmd len:(int)len {
    NSMutableArray *tempArr = [NSMutableArray array];
    for (int i = 0; i<len; i++) {
        [tempArr addObject:@(cmd[i])];
    }
    return [NSArray arrayWithArray:tempArr];
}

- (NSMutableArray *)changeCommandToArray:(uint8_t *)cmd len:(int)len {
    NSMutableArray *arr = [NSMutableArray array];
    for (int i=0; i<len; i++) {
        [arr addObject:@(cmd[i])];
    }
    return arr;
}

/*
-(int)generateSequenceNumber{

    int maxNum = 255;
    if (self.sequenceNumber > maxNum) {
        self.sequenceNumber = ( arc4random() % maxNum);
    }
    self.sequenceNumber++;
    return self.sequenceNumber;
}
*/

- (int)generateSequenceNumber {
    int maxNum = 255;
    self.sequenceNumber = (self.sequenceNumber + 1) % (maxNum + 1);
    return self.sequenceNumber;
}

-(NSUInteger)mx02ConnTypes{
    return ConnTypeBLE;
}

-(NSUInteger)mx06ConnTypes{
    return ConnTypeWiFi|ConnTypeAP;
}

-(NSUInteger)inksi01ConnTypes:(NSUInteger)apWifi{
    return ConnTypeBLE|apWifi;
}

-(NSDictionary *)mx02FirmwareConfigs{
    return @{@(FirmwareTypeMCU):@(ConnTypeBLE)};
}

-(NSDictionary *)mx06FirmwareConfigs{
//    return @{@(FirmwareTypeMCU):@(ConnTypeWiFi|ConnTypeAP),@(FirmwareTypeWiFi):@(ConnTypeWiFi|ConnTypeAP)};
    //这里由于ap配网无法下载，ios中只支持了在线升级，所以这里要求只允许wifi连接的时候可以升级
    return @{@(FirmwareTypeMCU):@(ConnTypeWiFi),@(FirmwareTypeWiFi):@(ConnTypeWiFi)};
}

//-(NSDictionary *)inksi01FirmwareConfigs:(NSUInteger)apWifi{
//这里和上边同样的原因 -> 由于ap配网无法下载，ios中只支持了在线升级，所以这里要求只允许wifi连接的时候可以升级，所以去掉了apWifi参数
-(NSDictionary *)inksi01FirmwareConfigs{
    return @{@(FirmwareTypeWiFi):@(ConnTypeWiFi)};
}

@end
