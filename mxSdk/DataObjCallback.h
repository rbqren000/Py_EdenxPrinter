//
//  DataObjCallback.h
//  Inksi
//
//  Created by rbq on 2024/7/3.
//

#import <UIKit/UIKit.h>
#import "DataObj.h"

NS_ASSUME_NONNULL_BEGIN

@protocol DataObjCallbackDelegate<NSObject>

//@optional下的方法可选择实现   //@required 下的方法必须实现  [方法默认都是@required的]
@optional
-(void)onDataObjWriteSuccess:(DataObj *)dataObj obj:(NSObject *)obj;

@optional
-(void)onDataObjWriteError:(DataObj * _Nullable )dataObj errorMsg:(NSString *)errorMsg;

@optional
-(void)OnDataObjWriteTimeout:(DataObj *)dataObj errorMsg:(NSString *)errorMsg;

@end

typedef void(^OnDataObjWriteSuccess)(DataObj *dataObj, NSObject *obj);
typedef void(^OnDataObjWriteError)( DataObj * _Nullable dataObj, NSString *errorMsg);
typedef void(^OnDataObjWriteTimeout)(DataObj *dataObj, BOOL delayEfficacy);

@interface DataObjCallback : NSObject

@property (nonatomic, copy) OnDataObjWriteSuccess onSuccess;
@property (nonatomic, copy) OnDataObjWriteError onError;
@property (nonatomic, copy) OnDataObjWriteTimeout onTimeout;

@property (nonatomic,weak) id<DataObjCallbackDelegate> dataObjCallbackDelegate;

- (instancetype)initDataObjCallback:(OnDataObjWriteSuccess)onSuccess onError:(OnDataObjWriteError)onError onTimeout:(OnDataObjWriteTimeout)onTimeout;

- (instancetype)initDataObjCallback:(id<DataObjCallbackDelegate>)dataObjCallbackDelegate;

- (instancetype)initDataObjCallback:(id<DataObjCallbackDelegate>)dataObjCallbackDelegate onSuccess:(OnDataObjWriteSuccess)onSuccess onError:(OnDataObjWriteError)onError onTimeout:(OnDataObjWriteTimeout)onTimeout;

@end

NS_ASSUME_NONNULL_END
