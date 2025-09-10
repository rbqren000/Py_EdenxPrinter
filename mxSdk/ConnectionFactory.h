//
//  ConnectionFactory.h
//  Inksi
//
//  Created by rbq on 2024/11/1.
//

#import <UIKit/UIKit.h>
#import "ConnectionStrategy.h"
#import "BLEConnection.h"
#import "TCPConnection.h"

NS_ASSUME_NONNULL_BEGIN

// 定义一个枚举来标识连接类型
typedef NS_ENUM(NSUInteger, ConnectionType) {
    ConnectionTypeBLE,
    ConnectionTypeTCP
};

@interface ConnectionFactory : NSObject

+ (id<ConnectionStrategy>)connectionStrategyForType:(ConnectionType)type;

@end

NS_ASSUME_NONNULL_END
