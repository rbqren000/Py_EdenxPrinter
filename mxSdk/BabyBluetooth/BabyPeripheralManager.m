//
//  BabyPeripheralManager.m
//  BluetoothStubOnIOS
//
//  Created by 任宝强 on 15/12/12.
//  Copyright © 2015年 任宝强. All rights reserved.
//

#import "BabyPeripheralManager.h"
#import "BabyDefine.h"

#define callbackBlock(...) if ([[babySpeaker callback] __VA_ARGS__])   [[babySpeaker callback] __VA_ARGS__ ]

@implementation BabyPeripheralManager {
    int PERIPHERAL_MANAGER_INIT_WAIT_TIMES;//记录等待peripheralManager打开次数
    int didAddServices;//已经成功添加的服务的个数
    NSTimer *addServiceTask;
    BOOL isStartAdvertising;//用于判断是否需要执行广播发送，这个为认为指令
    BOOL isCallBackSelf;//用于标志是否属于自己回调自己
    NSTimer *loopStartAdvertisingTimer;
}

- (instancetype)init {
    self = [super init];
    if (self) {
        isStartAdvertising = NO;
        isCallBackSelf = NO;
        _localName = @"baby-default-name";
        _peripheralManager = [[CBPeripheralManager alloc]initWithDelegate:self queue:nil options:nil];
    }
    return  self;
}

- (BabyPeripheralManager *(^)(NSString *name))localPeripheralName {
    return ^BabyPeripheralManager*(NSString *name) {
        self->_localName = name;
        return self;
    };
}

- (BabyPeripheralManager *(^)(void))startAdvertising {
    
    return ^BabyPeripheralManager *() {
        
        if (!self->isCallBackSelf) {
            
            self->isStartAdvertising = YES;
            RBQLog4(@"开启广播");
        }
        
        if (self->isStartAdvertising) {
            
            if ([self canStartAdvertising]) {
                
                RBQLog4(@"RBQ 广播打开");
                
                self->PERIPHERAL_MANAGER_INIT_WAIT_TIMES = 0;
                NSMutableArray *UUIDS = [NSMutableArray array];
                for (CBMutableService *s in self->_services) {
                    [UUIDS addObject:s.UUID];
                }
                //启动广播
                if (self->_manufacturerData) {
                    [self->_peripheralManager startAdvertising:
                     @{
                       CBAdvertisementDataServiceUUIDsKey :  UUIDS
                       ,CBAdvertisementDataLocalNameKey : self->_localName,
                       CBAdvertisementDataManufacturerDataKey:self->_manufacturerData
                       }];
                    
                } else {
                    [self->_peripheralManager startAdvertising:
                     @{
                       CBAdvertisementDataServiceUUIDsKey :  UUIDS
                       ,CBAdvertisementDataLocalNameKey : self->_localName
                       }];
                }
                
            }else {
                
                self->PERIPHERAL_MANAGER_INIT_WAIT_TIMES++;
                if (self->PERIPHERAL_MANAGER_INIT_WAIT_TIMES > 5) {
                    RBQLog4(@">>>error： 第%d次等待peripheralManager打开任然失败，请检查蓝牙设备是否可用",self->PERIPHERAL_MANAGER_INIT_WAIT_TIMES);
                }
                if (self->loopStartAdvertisingTimer) {
                    [self->loopStartAdvertisingTimer invalidate];
                    self->loopStartAdvertisingTimer = nil;
                }
                self->loopStartAdvertisingTimer = [NSTimer scheduledTimerWithTimeInterval:2.0 target:self selector:@selector(loopStartAdvertising) userInfo:nil repeats:NO];
                
                RBQLog4(@">>> 第%d次等待peripheralManager打开",self->PERIPHERAL_MANAGER_INIT_WAIT_TIMES);
            }
            
        }
        
        return self;
    };
}

-(void)loopStartAdvertising{
    
    self->isCallBackSelf = YES;
    self.startAdvertising();
}

- (BabyPeripheralManager *(^)(NSString *cbuuid))startAdvertisings{
    
    return ^BabyPeripheralManager *(NSString *cbuuid) {
        
        if (!self->isCallBackSelf) {
            
            self->isStartAdvertising = YES;
            RBQLog4(@"开启广播");
        }
        
        if (self->isStartAdvertising) {
            
            if ([self canStartAdvertising]){
                
                RBQLog4(@"RBQ 广播打开");
                
                self->PERIPHERAL_MANAGER_INIT_WAIT_TIMES = 0;
                //启动广播
                [self->_peripheralManager startAdvertising:@{ CBAdvertisementDataServiceUUIDsKey : @[[CBUUID UUIDWithString:cbuuid],[CBUUID UUIDWithString:@"E2C56DB5-DFFB-48D2-B060-D0F5A71096E0"]], CBAdvertisementDataLocalNameKey : @"BelonLight",CBAdvertisementDataIsConnectable:[NSNumber numberWithBool:YES]}];
                
            }else {
                
                self->PERIPHERAL_MANAGER_INIT_WAIT_TIMES++;
                if (self->PERIPHERAL_MANAGER_INIT_WAIT_TIMES > 5) {
                    RBQLog4(@">>>error： 第%d次等待peripheralManager打开任然失败，请检查蓝牙设备是否可用",self->PERIPHERAL_MANAGER_INIT_WAIT_TIMES);
                }
                if (self->loopStartAdvertisingTimer) {
                    [self->loopStartAdvertisingTimer invalidate];
                    self->loopStartAdvertisingTimer = nil;
                }
                self->loopStartAdvertisingTimer = [NSTimer scheduledTimerWithTimeInterval:2.0 target:self selector:@selector(loopStartAdvertisings:) userInfo:@{@"uuid":cbuuid} repeats:NO];
                
                RBQLog4(@">>> 第%d次等待peripheralManager打开",self->PERIPHERAL_MANAGER_INIT_WAIT_TIMES);
            }
            
        }
        
        return self;
    };
}

-(void)loopStartAdvertisings:(NSTimer *)timer{
    
    self->isCallBackSelf = YES;
    NSString *cbuuid = [[timer userInfo] valueForKey:@"uuid"];
    self.startAdvertisings(cbuuid);
}

- (BabyPeripheralManager *(^)(void))stopAdvertising {
    
    return ^BabyPeripheralManager*() {
        
        RBQLog4(@"RBQ停止广播");
        
        if (self->loopStartAdvertisingTimer) {
            [self->loopStartAdvertisingTimer invalidate];
            self->loopStartAdvertisingTimer = nil;
        }
        if ([self canStartAdvertising]) {
            
            [self->_peripheralManager stopAdvertising];
            //调用停止扫描事件
            [self->babySpeaker callback].blockOnPeripheralModelDidStopAdvertising(self->_peripheralManager);
//            callbackBlock(blockOnPeripheralModelDidStopAdvertising)(self->_peripheralManager);
            
        }
        self->isCallBackSelf = NO;
        self->isStartAdvertising = NO;
        self->PERIPHERAL_MANAGER_INIT_WAIT_TIMES = 0;
        return self;
    };
    
}

- (BOOL)canStartAdvertising {
    
    if (_peripheralManager.state != CBPeripheralManagerStatePoweredOn) {
        return NO;
    }
    if (didAddServices != _services.count) {
        return NO;
    }
    return YES;
}

- (BOOL)isPoweredOn {
    if (_peripheralManager.state != CBPeripheralManagerStatePoweredOn) {
        return NO;
    }
    return YES;
}

- (BabyPeripheralManager *(^)(NSArray *array))addServices {
    return ^BabyPeripheralManager*(NSArray *array) {
        self->_services = [NSMutableArray arrayWithArray:array];
        [self addServicesToPeripheral];
        return self;
    };
}

- (BabyPeripheralManager *(^)(void))removeAllServices {
    return ^BabyPeripheralManager*() {
        self->didAddServices = 0;
        [self->_peripheralManager removeAllServices];
        return self;
    };
}

- (BabyPeripheralManager *(^)(NSData *data))addManufacturerData {
    return ^BabyPeripheralManager*(NSData *data) {
        self->_manufacturerData = data;
        return self;
    };
}

- (void)addServicesToPeripheral {
    if ([self isPoweredOn]) {
        for (CBMutableService *s in _services) {
            [_peripheralManager addService:s];
        }
    }
    else {
        [addServiceTask setFireDate:[NSDate distantPast]];
        addServiceTask = [NSTimer scheduledTimerWithTimeInterval:3 target:self selector:@selector(addServicesToPeripheral) userInfo:nil repeats:NO];
    }
}

#pragma mark - peripheralManager delegate

- (void)peripheralManagerDidUpdateState:(CBPeripheralManager *)peripheral {
    switch (peripheral.state) {
        case CBManagerStateUnknown:
            RBQLog4(@">>>CBPeripheralManagerStateUnknown");
            break;
        case CBManagerStateResetting:
            RBQLog4(@">>>CBPeripheralManagerStateResetting");
            break;
        case CBManagerStateUnsupported:
            RBQLog4(@">>>CBPeripheralManagerStateUnsupported");
            break;
        case CBManagerStateUnauthorized:
            RBQLog4(@">>>CBPeripheralManagerStateUnauthorized");
            break;
        case CBManagerStatePoweredOff:
            RBQLog4(@">>>CBPeripheralManagerStatePoweredOff");
            break;
        case CBManagerStatePoweredOn:
            RBQLog4(@">>>CBPeripheralManagerStatePoweredOn");
            //发送centralManagerDidUpdateState通知
            [[NSNotificationCenter defaultCenter]postNotificationName:@"CBPeripheralManagerStatePoweredOn" object:nil];
            break;
        default:
            break;
    }

//    if([babySpeaker callback] blockOnPeripheralModelDidUpdateState) {
//        [currChannel blockOnCancelScan](centralManager);
//    }
    callbackBlock(blockOnPeripheralModelDidUpdateState)(peripheral);
}


- (void)peripheralManager:(CBPeripheralManager *)peripheral didAddService:(CBService *)service error:(NSError *)error {
    didAddServices++;
    callbackBlock(blockOnPeripheralModelDidAddService)(peripheral,service,error);
}

- (void)peripheralManagerDidStartAdvertising:(CBPeripheralManager *)peripheral error:(NSError *)error {
    callbackBlock(blockOnPeripheralModelDidStartAdvertising)(peripheral,error);
}

- (void)peripheralManager:(CBPeripheralManager *)peripheral didReceiveReadRequest:(CBATTRequest *)request {
    callbackBlock(blockOnPeripheralModelDidReceiveReadRequest)(peripheral, request);
}

- (void)peripheralManager:(CBPeripheralManager *)peripheral didReceiveWriteRequests:(NSArray *)requests {
    callbackBlock(blockOnPeripheralModelDidReceiveWriteRequests)(peripheral,requests);
}

- (void)peripheralManagerIsReadyToUpdateSubscribers:(CBPeripheralManager *)peripheral {
    callbackBlock(blockOnPeripheralModelIsReadyToUpdateSubscribers)(peripheral);
}

- (void)peripheralManager:(CBPeripheralManager *)peripheral central:(CBCentral *)central didSubscribeToCharacteristic:(CBCharacteristic *)characteristic {
    callbackBlock(blockOnPeripheralModelDidSubscribeToCharacteristic)(peripheral,central,characteristic);
}

- (void)peripheralManager:(CBPeripheralManager *)peripheral central:(CBCentral *)central didUnsubscribeFromCharacteristic:(CBCharacteristic *)characteristic {
    callbackBlock(blockOnPeripheralModelDidUnSubscribeToCharacteristic)(peripheral,central,characteristic);
}


@end

void makeCharacteristicToService(CBMutableService *service,NSString *UUID,NSString *properties,NSString *descriptor) {

    //paramter for properties
    CBCharacteristicProperties prop = 0x00;
    if ([properties containsString:@"r"]) {
        prop =  prop | CBCharacteristicPropertyRead;
    }
    if ([properties containsString:@"w"]) {
        prop =  prop | CBCharacteristicPropertyWrite;
    }
    if ([properties containsString:@"n"]) {
        prop =  prop | CBCharacteristicPropertyNotify;
    }
    if (properties == nil || [properties isEqualToString:@""]) {
        prop = CBCharacteristicPropertyRead | CBCharacteristicPropertyWrite;
    }

    CBMutableCharacteristic *c = [[CBMutableCharacteristic alloc]initWithType:[CBUUID UUIDWithString:UUID] properties:prop  value:nil permissions:CBAttributePermissionsReadable | CBAttributePermissionsWriteable];
    
    //paramter for descriptor
    if (!(descriptor == nil || [descriptor isEqualToString:@""])) {
        //c设置description对应的haracteristics字段描述
        CBUUID *CBUUIDCharacteristicUserDescriptionStringUUID = [CBUUID UUIDWithString:CBUUIDCharacteristicUserDescriptionString];
        CBMutableDescriptor *desc = [[CBMutableDescriptor alloc]initWithType: CBUUIDCharacteristicUserDescriptionStringUUID value:descriptor];
        [c setDescriptors:@[desc]];
    }
    
    if (!service.characteristics) {
        service.characteristics = @[];
    }
    NSMutableArray *cs = [service.characteristics mutableCopy];
    [cs addObject:c];
    service.characteristics = [cs copy];
}
void makeStaticCharacteristicToService(CBMutableService *service,NSString *UUID,NSString *descriptor,NSData *data) {
    
    CBMutableCharacteristic *c = [[CBMutableCharacteristic alloc]initWithType:[CBUUID UUIDWithString:UUID] properties:CBCharacteristicPropertyRead  value:data permissions:CBAttributePermissionsReadable];
    
    //paramter for descriptor
    if (!(descriptor == nil || [descriptor isEqualToString:@""])) {
        //c设置description对应的haracteristics字段描述
        CBUUID *CBUUIDCharacteristicUserDescriptionStringUUID = [CBUUID UUIDWithString:CBUUIDCharacteristicUserDescriptionString];
        CBMutableDescriptor *desc = [[CBMutableDescriptor alloc]initWithType: CBUUIDCharacteristicUserDescriptionStringUUID value:descriptor];
        [c setDescriptors:@[desc]];
    }
    
    if (!service.characteristics) {
        service.characteristics = @[];
    }
    NSMutableArray *cs = [service.characteristics mutableCopy];
    [cs addObject:c];
    service.characteristics = [cs copy];
}


CBMutableService* makeCBService(NSString *UUID)
{
    CBMutableService *s = [[CBMutableService alloc]initWithType:[CBUUID UUIDWithString:UUID] primary:YES];
    return s;
}

NSString * genUUID()
{
    CFUUIDRef uuid_ref = CFUUIDCreate(NULL);
    CFStringRef uuid_string_ref= CFUUIDCreateString(NULL, uuid_ref);
    
    CFRelease(uuid_ref);
    NSString *uuid = [NSString stringWithString:(__bridge NSString*)uuid_string_ref];
    
    CFRelease(uuid_string_ref);
    return uuid;
}

