//
//  ConnectManager.h
//  BelonPrinter
//
//  Created by rbq on 2021/9/23.
//  Copyright © 2021 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "Device.h"
#import "DistNetDevice.h"
#import "ConnModel.h"
#import "MultiRowData.h"
#import "LogoData.h"
#import "MultiRowDataPacket.h"
#import "LogoDataPacket.h"
#import "OtaDataPacket.h"
#import "BabyBluetooth.h"
#import "CommandContext.h"
#import "DataObjContext.h"
#import "DeviceModel.h"

NS_ASSUME_NONNULL_BEGIN

#define ConnectManager_share [ConnectManager share] //获取单例类对象
#define inksi_mobile_printer @"inksi"

#define SyncingDataError 100
#define CommandQueueIsNoEmptyError 200

typedef NS_ENUM(NSUInteger, DeviceConnectState) {
    DeviceConnectIdle = 0,// 空闲
    DeviceConnecting,//正在连接
    DeviceConnected,//已连接
};

typedef NS_ENUM(NSUInteger, DataSendType) {
    DataSendOnceContinuous = 0,// 依次连续传输完成
    DataSendCompleteOnceWaitNext,// 完成一次传输等待打印完成后开始自动传输下一次
};

typedef NS_ENUM(NSUInteger, ScanType) {
    ScanTypeIdle = 0,//空闲
    ScanTypeBle,// 扫描Ble设备
    ScanTypeDNW,
    ScanTypeConnModel //扫描MultiConnModel，这个要根据ble的广播信息来进行判断
};

typedef NS_ENUM(NSUInteger, ConnectType) {
    ConnectTypeIdle = 0,//空闲状态
    ConnectTypeBle,// 正常连接Ble设备模式
    ConnectTypeNetWork, // 连接wifi或ap设备
    ConnectTypeDNW // 配网模式连接ble
};

typedef NS_ENUM(NSUInteger, UdpMonitorType) {
    UdpMonitorTypeIdle = 0,//空闲状态
    UdpMonitorTypeWifi,// 监听设备
    UdpMonitorTypeDNW //监听配网设备，确定是否配网成功
};

@class Device;

typedef void(^OnCentralManagerDidUpdateState)(CBCentralManager *central);

@protocol CentralManagerDelegate <NSObject>
// 定义状态更新的方法
- (void)onCentralManagerDidUpdateState:(CBCentralManager *)central;
@end

#pragma mark  扫描相关事件
typedef void(^OnDeviceStartDiscover)(void);
typedef void(^OnDeviceDiscovered)(Device *device);
typedef void(^OnDeviceStopDiscover)(void);

@protocol DeviceDiscoveryDelegate <NSObject>
// 开始发现设备时调用
@optional
- (void)onDeviceStartDiscover;
// 发现一个设备时调用
@optional
- (void)onDeviceDiscoverDevice:(Device *)device;
// 停止发现设备时调用
@optional
- (void)onDeviceStopDiscover;
@end

typedef void(^OnConnModelStartDiscover)(void);
typedef void(^OnConnModelDiscovered)(ConnModel *model);
typedef void(^OnConnModelStopDiscover)(void);

@protocol ConnModelDiscoveryDelegate <NSObject>
// 开始发现设备时调用
@optional
- (void)onConnModelStartDiscover;
// 发现一个设备时调用
@optional
- (void)onConnModelDiscover:(ConnModel *)model;
// 停止发现设备时调用
@optional
- (void)onConnModelStopDiscover;
@end

#pragma mark  连接相关事件
typedef void(^OnDeviceConnectStart)(void);
typedef void(^OnDeviceConnectSucceed)(void);
typedef void(^OnDeviceDisconnect)(void);
typedef void(^OnDeviceConnectFail)(void);

@protocol DeviceConnectionDelegate <NSObject>
// 设备开始连接时调用
@optional
- (void)onDeviceConnectStart;
// 设备连接成功时调用
@optional
- (void)onDeviceConnectSucceed;
// 设备断开连接时调用
@optional
- (void)onDeviceDisconnect;
// 设备连接失败时调用
@optional
- (void)onDeviceConnectFail;
@end


#pragma mark  数据传输相关事件
typedef void(^OnDataProgressStart)(CGFloat size, CGFloat progress, NSInteger progressPrecision, NSTimeInterval startTime);//打印开始
typedef void(^OnDataProgress)(CGFloat size, CGFloat progress, NSInteger progressPrecision, NSTimeInterval startTime, NSTimeInterval currentTime);//打印过程进度更新
typedef void(^OnDataProgressFinish)(CGFloat size, CGFloat progress, NSInteger progressPrecision, NSTimeInterval startTime, NSTimeInterval currentTime);//打印完成
typedef void(^OnDataProgressError)(NSError *error);//打印错误


@protocol DataProgressDelegate <NSObject>
// 数据处理开始时调用
@optional
- (void)onDataProgressStart:(CGFloat)size progress:(CGFloat)progress progressPrecision:(NSInteger)progressPrecision startTime:(NSTimeInterval)startTime;
// 数据处理进度更新时调用
@optional
- (void)onDataProgress:(CGFloat)size progress:(CGFloat)progress progressPrecision:(NSInteger)progressPrecision startTime:(NSTimeInterval)startTime currentTime:(NSTimeInterval)currentTime;
// 数据处理完成时调用
@optional
- (void)onDataProgressFinish:(CGFloat)size progress:(CGFloat)progress progressPrecision:(NSInteger)progressPrecision startTime:(NSTimeInterval)startTime currentTime:(NSTimeInterval)currentTime;
// 数据处理出错时调用
@optional
- (void)onDataProgressError:(NSError *)error;
@end


#pragma mark 数据分发相关black
typedef void(^OnReadBattery)(Device *device,int bat);
typedef void(^OnReadParameter)(Device *device,int headValue,int l_pix,int p_pix,int distance);
typedef void(^OnReadCirculationRepeat)(Device *device,int circulation_time,int repeat_time);
typedef void(^OnReadDirection)(Device *device,int direction,int printHeadDirection);
typedef void(^OnReadDeviceInfo)(Device *device,NSString * deviceId,NSString *name,NSString *mcu_ver,NSString *date);
typedef void(^OnReadPrinterHeadTemperature)(Device *device,int index,int temp_get,int temp_set);
typedef void(^OnReadSilentStateForDevice)(Device *device,BOOL silentState);
typedef void(^OnReadAutoPowerOffStateForDevice)(Device *device,BOOL autoPowerOff);


@protocol DeviceReadMsgDelegate <NSObject>
// 读取电池信息时调用
@optional
- (void)onReadBatteryForDevice:(Device *)device batteryLevel:(int)batteryLevel;
// 读取参数信息时调用
@optional
- (void)onReadParameterForDevice:(Device *)device headValue:(int)headValue lPix:(int)lPix pPix:(int)pPix distance:(int)distance;
// 读取循环重复信息时调用
@optional
- (void)onReadCirculationRepeatForDevice:(Device *)device circulationTime:(int)circulationTime repeatTime:(int)repeatTime;
// 读取方向信息时调用
@optional
- (void)onReadDirectionForDevice:(Device *)device direction:(int)direction printHeadDirection:(int)printHeadDirection;
// 读取设备信息时调用
@optional
- (void)onReadDeviceInfoForDevice:(Device *)device deviceId:(NSString *)deviceId name:(NSString *)name mcuVersion:(NSString *)mcuVersion date:(NSString *)date;
// 读取打印头温度时调用
@optional
- (void)onReadPrinterHeadTemperatureForDevice:(Device *)device index:(int)index tempGet:(int)tempGet tempSet:(int)tempSet;
@optional
- (void)onReadSilentStateForDevice:(Device *)device silentState:(BOOL)silentState;
@optional
- (void)onReadAutoPowerOffStateForDevice:(Device *)device autoPowerOff:(BOOL)autoPowerOff;

@end

typedef void(^OnPrintStart)(Device *device,int beginIndex,int endIndex,int currentIndex);
typedef void(^OnPrintComplete)(Device *device,int beginIndex,int endIndex,int currentIndex);

@protocol PrintDelegate <NSObject>
// 打印开始时调用
@optional
- (void)onPrintStartForDevice:(Device *)device beginIndex:(int)beginIndex endIndex:(int)endIndex currentIndex:(int)currentIndex;
// 打印完成时调用
@optional
- (void)onPrintCompleteForDevice:(Device *)device beginIndex:(int)beginIndex endIndex:(int)endIndex currentIndex:(int)currentIndex;
@end

/**配网相关事件*/
#pragma mark 配网设备扫描相关事件
typedef void(^OnDistNetDeviceDiscoverStart)(void);
typedef void(^OnDistNetDeviceDiscover)(DistNetDevice *device);
typedef void(^OnDistNetDeviceDiscoverCancel)(void);

@protocol DistNetDeviceDiscoveryDelegate <NSObject>
// 设备发现开始时调用
@optional
- (void)onDistNetDeviceDiscoverStart;
// 设备发现时调用
@optional
- (void)onDistNetDeviceDiscover:(DistNetDevice *)device;
// 设备发现取消时调用
@optional
- (void)onDistNetDeviceDiscoverCancel;
@end

typedef void(^OnDistributionNetworkStart)(void);
typedef void(^OnDistributionNetworkSucceed)(Device *device);
typedef void(^OnDistributionNetworkProgress)(CGFloat progress);
typedef void(^OnDistributionNetworkFail)(void);
typedef void(^OnDistributionNetworkTimeOut)(void);

@protocol DistributionNetworkDelegate <NSObject>
// 分布式网络配置开始时调用
@optional
- (void)onDistributionNetworkStart;
// 分布式网络配置成功时调用
@optional
- (void)onDistributionNetworkSucceed:(Device *)device;
// 分布式网络配置进度更新时调用
@optional
- (void)onDistributionNetworkProgress:(CGFloat)progress;
// 分布式网络配置失败时调用
@optional
- (void)onDistributionNetworkFail;
// 分布式网络配置超时时调用
@optional
- (void)onDistributionNetworkTimeOut;
@end

/**指令写入成功与否事件**/
typedef void(^OnCommandWriteSuccess)(Command *command, NSObject *object);
typedef void(^OnCommandWriteError)(Command *command, NSString *errorMsg);

@protocol CommandWriteDelegate <NSObject>
// 定义写入成功的方法
@optional
- (void)onWriteCommandSuccess:(Command *)command withObject:(NSObject *)object;
// 定义写入失败的方法
@optional
- (void)onWriteCommandError:(Command *)command withErrorMsg:(NSString *)errorMsg;
@end

/**数据是否写入成功的事件**/
typedef void(^OnDataWriteSuccess)(DataObj *dataObj, NSObject *object);
typedef void(^OnDataWriteError)(DataObj *dataObj, NSString *errorMsg);

@protocol DataWriteDelegate <NSObject>
// 定义写入成功的方法
@optional
- (void)onDataWriteSuccess:(DataObj *)dataObj withObject:(NSObject *)object;
// 定义写入失败的方法
@optional
- (void)onDataWriteError:(DataObj *)dataObj withErrorMsg:(NSString *)errorMsg;
@end

@interface ConnectManager : NSObject

#pragma mark 定义蓝牙状态事件
@property (nonatomic, copy) OnCentralManagerDidUpdateState onCentralManagerDidUpdateState;

@property (nonatomic, strong) NSMutableArray<id<CentralManagerDelegate>> *centralManagerdelegates;

- (NSMutableArray<id<CentralManagerDelegate>> *)centralManagerdelegates;
- (void)registerCentralManagerDelegate:(id<CentralManagerDelegate>)delegate;
- (void)unregisterCentralManagerDelegate:(id<CentralManagerDelegate>)delegate;
- (void)notifyCentralManagerDidUpdateState:(CBCentralManager *)central;

#pragma mark 设备扫描返回事件
@property (nonatomic, copy) OnDeviceStartDiscover onDeviceStartDiscover;
@property (nonatomic, copy) OnDeviceDiscovered onDeviceDiscovered;
@property (nonatomic, copy) OnDeviceStopDiscover onDeviceStopDiscover;

@property (nonatomic, strong) NSMutableArray<id<DeviceDiscoveryDelegate>> *deviceDiscoveryDelegates;
- (void)registerDeviceDiscoveryDelegate:(id<DeviceDiscoveryDelegate>)delegate;
- (void)unregisterDeviceDiscoveryDelegate:(id<DeviceDiscoveryDelegate>)delegate;
- (void)notifyDeviceStartDiscover;
- (void)notifyDeviceDiscover:(Device *)device;
- (void)notifyDeviceStopDiscover;


@property (nonatomic, copy) OnConnModelStartDiscover onConnModelStartDiscover;
@property (nonatomic, copy) OnConnModelDiscovered onConnModelDiscovered;
@property (nonatomic, copy) OnConnModelStopDiscover onConnModelStopDiscover;

@property (nonatomic, strong) NSMutableArray<id<ConnModelDiscoveryDelegate>> *connModelDiscoveryDelegates;
- (void)registerConnModelDiscoveryDelegate:(id<ConnModelDiscoveryDelegate>)delegate;
- (void)unregisterConnModelDiscoveryDelegate:(id<ConnModelDiscoveryDelegate>)delegate;
- (void)notifyConnModelStartDiscover;
- (void)notifyConnModelDiscover:(ConnModel *)model;
- (void)notifyConnModelStopDiscover;

#pragma mark 设备连接事件
@property (nonatomic, copy) OnDeviceConnectStart onDeviceConnectStart;
@property (nonatomic, copy) OnDeviceConnectSucceed onDeviceConnectSucceed;
@property (nonatomic, copy) OnDeviceDisconnect onDeviceDisconnect;
@property (nonatomic, copy) OnDeviceConnectFail onDeviceConnectFail;

@property (nonatomic, strong) NSMutableArray<id<DeviceConnectionDelegate>> *deviceConnectionDelegates;
- (void)registerDeviceConnectionDelegate:(id<DeviceConnectionDelegate>)delegate;
- (void)unregisterDeviceConnectionDelegate:(id<DeviceConnectionDelegate>)delegate;
- (void)notifyDeviceConnectStart;
- (void)notifyDeviceConnectSucceed;
- (void)notifyDeviceDisconnect;
- (void)notifyDeviceConnectFail;

//图片打印black
@property (nonatomic, copy) OnDataProgressStart onDataProgressStart;
@property (nonatomic, copy) OnDataProgress onDataProgress;
@property (nonatomic, copy) OnDataProgressFinish onDataProgressFinish;
@property (nonatomic, copy) OnDataProgressError onDataProgressError;

@property (nonatomic, strong) NSMutableArray<id<DataProgressDelegate>> *dataProgressDelegates;
- (void)registerDataProgressDelegate:(id<DataProgressDelegate>)delegate;
- (void)unregisterDataProgressDelegate:(id<DataProgressDelegate>)delegate;
- (void)notifyDataProgressStart:(CGFloat)size progress:(CGFloat)progress progressPrecision:(NSInteger)progressPrecision startTime:(NSTimeInterval)startTime;
- (void)notifyDataProgress:(CGFloat)size progress:(CGFloat)progress progressPrecision:(NSInteger)progressPrecision startTime:(NSTimeInterval)startTime currentTime:(NSTimeInterval)currentTime;
- (void)notifyDataProgressFinish:(CGFloat)size progress:(CGFloat)progress progressPrecision:(NSInteger)progressPrecision startTime:(NSTimeInterval)startTime currentTime:(NSTimeInterval)currentTime;
- (void)notifyDataProgressError:(NSError *)error;

//读取到的数据分发black
@property (nonatomic, copy) OnReadBattery onReadBattery;
@property (nonatomic, copy) OnReadParameter onReadParameter;
@property (nonatomic, copy) OnReadCirculationRepeat onReadCirculationRepeat;
@property (nonatomic, copy) OnReadDirection onReadDirection;
@property (nonatomic, copy) OnReadDeviceInfo onReadDeviceInfo;
@property (nonatomic, copy) OnReadPrinterHeadTemperature onReadPrinterHeadTemperature;
@property (nonatomic, copy) OnReadSilentStateForDevice onReadSilentStateForDevice;
@property (nonatomic, copy) OnReadAutoPowerOffStateForDevice onReadAutoPowerOffStateForDevice;

@property (nonatomic, strong) NSMutableArray<id<DeviceReadMsgDelegate>> *deviceReadMsgDelegates;
- (void)registerDeviceReadMsgDelegate:(id<DeviceReadMsgDelegate>)delegate;
- (void)unregisterDeviceReadMsgDelegate:(id<DeviceReadMsgDelegate>)delegate;
- (void)notifyReadBatteryForDevice:(Device *)device batteryLevel:(int)batteryLevel;
- (void)notifyReadParameterForDevice:(Device *)device headValue:(int)headValue lPix:(int)lPix pPix:(int)pPix distance:(int)distance;
- (void)notifyReadCirculationRepeatForDevice:(Device *)device circulationTime:(int)circulationTime repeatTime:(int)repeatTime;
- (void)notifyReadDirectionForDevice:(Device *)device direction:(int)direction printHeadDirection:(int)printHeadDirection;
- (void)notifyReadDeviceInfoForDevice:(Device *)device deviceId:(NSString *)deviceId name:(NSString *)name mcuVersion:(NSString *)mcuVersion date:(NSString *)date;
- (void)notifyReadPrinterHeadTemperatureForDevice:(Device *)device index:(int)index tempGet:(int)tempGet tempSet:(int)tempSet;
- (void)notifyReadSilentStateForDevice:(Device *)device silentState:(BOOL)silentState;
- (void)notifyReadAutoPowerOffStateForDevice:(Device *)device autoPowerOff:(BOOL)autoPowerOff;

@property (nonatomic, copy) OnPrintStart onPrintStart;
@property (nonatomic, copy) OnPrintComplete onPrintComplete;

@property (nonatomic, strong) NSMutableArray<id<PrintDelegate>> *printDelegates;
- (void)registerPrintDelegate:(id<PrintDelegate>)delegate;
- (void)unregisterPrintDelegate:(id<PrintDelegate>)delegate;
- (void)notifyPrintStart:(Device *)device beginIndex:(int)beginIndex endIndex:(int)endIndex currentIndex:(int)currentIndex;
- (void)notifyPrintComplete:(Device *)device beginIndex:(int)beginIndex endIndex:(int)endIndex currentIndex:(int)currentIndex;

@property (nonatomic, copy) OnDistNetDeviceDiscoverStart onDistNetDeviceDiscoverStart;
@property (nonatomic, copy) OnDistNetDeviceDiscover onDistNetDeviceDiscover;
@property (nonatomic, copy) OnDistNetDeviceDiscoverCancel onDistNetDeviceDiscoverCancel;

@property (nonatomic, strong) NSMutableArray<id<DistNetDeviceDiscoveryDelegate>> *distNetDeviceDelegates;
- (void)registerDistNetDeviceDiscoveryDelegate:(id<DistNetDeviceDiscoveryDelegate>)delegate;
- (void)unregisterDistNetDeviceDiscoveryDelegate:(id<DistNetDeviceDiscoveryDelegate>)delegate;
- (void)notifyDistNetDeviceDiscoverStart;
- (void)notifyDistNetDeviceDiscover:(DistNetDevice *)device;
- (void)notifyDistNetDeviceDiscoverCancel;

@property (nonatomic, copy) OnDistributionNetworkStart onDistributionNetworkStart;
@property (nonatomic, copy) OnDistributionNetworkSucceed onDistributionNetworkSucceed;
@property (nonatomic, copy) OnDistributionNetworkProgress onDistributionNetworkProgress;
@property (nonatomic, copy) OnDistributionNetworkFail onDistributionNetworkFail;
@property (nonatomic, copy) OnDistributionNetworkTimeOut onDistributionNetworkTimeOut;

@property (nonatomic, strong) NSMutableArray<id<DistributionNetworkDelegate>> *networkDelegates;
- (void)registerNetworkDelegate:(id<DistributionNetworkDelegate>)delegate;
- (void)unregisterNetworkDelegate:(id<DistributionNetworkDelegate>)delegate;
- (void)notifyDistributionNetworkStart;
- (void)notifyDistributionNetworkSucceed:(Device *)device;
- (void)notifyDistributionNetworkProgress:(CGFloat)progress;
- (void)notifyDistributionNetworkFail;
- (void)notifyDistributionNetworkTimeOut;

@property (nonatomic, copy) OnCommandWriteSuccess onCommandWriteSuccess;
@property (nonatomic, copy) OnCommandWriteError onCommandWriteError;

@property (nonatomic, strong) NSMutableArray<id<CommandWriteDelegate>> *commandWriteDelegates;
- (void)registerCommandWriteDelegate:(id<CommandWriteDelegate>)delegate;
- (void)unregisterCommandWriteDelegate:(id<CommandWriteDelegate>)delegate;
- (void)notifyWriteCommandSuccess:(Command *)command withObject:(NSObject *)object;
- (void)notifyWriteCommandError:(Command *)command withErrorMsg:(NSString *)errorMsg;


@property (nonatomic, copy) OnDataWriteSuccess onDataWriteSuccess;
@property (nonatomic, copy) OnDataWriteError onDataWriteError;

@property (nonatomic, strong) NSMutableArray<id<DataWriteDelegate>> *dataWriteDelegates;
- (void)registerDataWriteDelegate:(id<DataWriteDelegate>)delegate;
- (void)unregisterDataWriteDelegate:(id<DataWriteDelegate>)delegate;
- (void)notifyDataWriteSuccess:(DataObj *)dataObj withObject:(NSObject *)object;
- (void)notifyDataWriteError:(DataObj *)dataObj withErrorMsg:(NSString *)errorMsg;


@property (nonatomic, strong) MultiRowDataPacket *multiRowDataPacket;
@property (nonatomic, strong) LogoDataPacket *logoDataPacket;
@property (nonatomic, strong) OtaDataPacket *otaDataPacket;
@property (nonatomic, strong, nullable,readonly) Device *device;

@property (nonatomic, assign,readonly) BOOL isConnected;
@property (nonatomic, strong, nullable, readonly) Device *connectedDevice;
/**蓝牙是否打开*/
@property (nonatomic, assign,readonly) BOOL isEnable;
@property (nonatomic, assign,readonly) BOOL isBleConnType;
@property (nonatomic, assign,readonly) BOOL isApConnType;
@property (nonatomic, assign,readonly) BOOL isWifiConnType;
@property (nonatomic, assign,readonly) BOOL isApOrWifiConnType;
/**是否正在扫描设备*/
@property (nonatomic, assign,readonly) BOOL isDiscoveringBleDevice;

@property (nonatomic, strong, nullable,readonly) DistNetDevice *disNetDevice;
/**
 是否允许发送数据  这里主要指打印数据，用来取消打印时使用
 */
@property (nonatomic, assign,readonly) BOOL allowSendData;

/**是否正在和打印机同步数据中**/
@property (nonatomic, assign,readonly) BOOL isSyncingData;

//ble的扫描模式
@property (nonatomic, assign,readonly) ScanType scanType;
@property (nonatomic, assign,readonly) BOOL isScanTypeIdle;
@property (nonatomic, assign,readonly) BOOL isScanTypeBle;
@property (nonatomic, assign,readonly) BOOL isScanTypeDNW;
@property (nonatomic, assign,readonly) BOOL isScanTypeConnModel;
//ble的连接类型
@property (nonatomic, assign,readonly) ConnectType connectType;
@property (nonatomic, assign,readonly) BOOL isConnectTypeIdle;
@property (nonatomic, assign,readonly) BOOL isConnectTypeBle;
@property (nonatomic, assign,readonly) BOOL isConnectTypeNetWork;
@property (nonatomic, assign,readonly) BOOL isConnectTypeDNW;
// udp的监听模式
@property (nonatomic, assign,readonly) UdpMonitorType udpMonitorType;
@property (nonatomic, assign,readonly) BOOL isUdpMonitorTypeIdle;
@property (nonatomic, assign,readonly) BOOL isUdpMonitorTypeWifi;
@property (nonatomic, assign,readonly) BOOL isUdpMonitorTypeDNW;

+(ConnectManager *)share;

/**只扫描设备*/
-(void)discoverBleDevice:(NSTimeInterval)scanTimeout;
/**停止扫描*/
- (void)cancelDiscoverBleDevice;

/**
 *只扫描设备连接支持类型对象
 */
-(void)discoverConnModel:(NSTimeInterval)scanTimeout;

/**
停止扫描
 */
- (void)cancelDiscoverConnModel;

-(void)discoverApDevice:(NSTimeInterval)scanTimeout;
-(void)cancelDiscoverApDevice;

- (BOOL)isConnected:(Device *)device;

/**连接设备*/
- (void)connect:(Device *)device;
/**断开连接*/
- (void)disConnect;

-(void)sendCommand:(int)opcode;
-(void)sendCommand:(int)opcode tag:(int)tag;
-(void)sendCommand:(uint8_t *)params lenght:(int)paramsLen opcode:(int)opcode;
-(void)sendCommand:(uint8_t *)params lenght:(int)paramsLen opcode:(int)opcode tag:(int)tag;
-(void)sendCommand:(NSData *)paramsData opcode:(int)opcode;
-(void)sendCommand:(NSData *)paramsData opcode:(int)opcode tag:(int)tag;
-(void)sendCommand:(int)opcode delayTime:(NSTimeInterval)delayTime;
-(void)sendCommand:(int)opcode delayTime:(NSTimeInterval)delayTime tag:(int)tag;
-(void)sendCommand:(uint8_t *)params lenght:(int)paramsLen opcode:(int)opcode delayTime:(NSTimeInterval)delayTime;
-(void)sendCommand:(uint8_t *)params lenght:(int)paramsLen opcode:(int)opcode delayTime:(NSTimeInterval)delayTime tag:(int)tag;
-(void)sendCommand:(NSData *)paramsData opcode:(int)opcode delayTime:(NSTimeInterval)delayTime;
-(void)sendCommand:(NSData *)paramsData opcode:(int)opcode delayTime:(NSTimeInterval)delayTime tag:(int)tag;

-(void)cancelSendMultiRowDataPacket;
-(void)setWithSendMultiRowDataPacket:(MultiRowData *)multiRowImageData;
-(void)setWithSendMultiRowDataPacket:(MultiRowData *)multiRowImageData Fn:(int)fn;
-(void)setWithSendMultiRowDataPacket:(MultiRowData *)multiRowImageData type:(DataSendType)type;
-(void)setWithSendMultiRowDataPacket:(MultiRowData *)multiRowImageData Fn:(int)fn type:(DataSendType)type;

-(void)cancelSendLogoDataPacket;
-(void)setWithSendLogoDataPacket:(LogoData *)logoData;
-(void)setWithSendLogoDataPacket:(LogoData *)logoData Fn:(int)fn;

-(void)cancelSendOtaDataPacket;
-(void)setWithSendOtaDataPacket:(NSData *)data;
-(void)setWithSendOtaDataPacket:(NSData *)data Fn:(int)fn;

-(void)discoverDistNetDevice:(NSTimeInterval)scanTimeout;
-(void)cancelDiscoverDistNetDevice;
/**distributionNetwork(DistNetDevice distNetDevice, String ssid, String password, float timeoutValue)*/
-(void)distributionNetwork:(DistNetDevice *)distNetDevice ssid:(NSString *)ssid pw:(NSString *)password timeout:(NSTimeInterval)timeoutValue;

-(void)discoverWifiDevice:(NSTimeInterval)scanTimeout;
-(void)cancelDiscoverWifiDevice;

-(void)startMonitorHeartData:(int)start;
-(void)stopMonitorHeartData;

@end

NS_ASSUME_NONNULL_END
