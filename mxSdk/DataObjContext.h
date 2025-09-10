//
//  DataObjContext.h
//  Inksi
//
//  Created by rbq on 2024/7/3.
//

#import <UIKit/UIKit.h>
#import "DataObj.h"
#import "DataObjCallback.h"

NS_ASSUME_NONNULL_BEGIN

@interface DataObjContext : NSObject

@property (nonatomic, strong) DataObj *dataObj;
@property (nonatomic, strong) DataObjCallback *dataObjCallback;

- (instancetype)initDataObjContext:(DataObj *)dataObj dataObjCallback:(DataObjCallback *)dataObjCallback;

@end

NS_ASSUME_NONNULL_END
