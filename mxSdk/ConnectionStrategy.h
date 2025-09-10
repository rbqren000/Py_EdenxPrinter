//
//  ConnectionStrategy.h
//  Inksi
//
//  Created by rbq on 2024/11/1.
//

#import <UIKit/UIKit.h>
#import "RBQLog.h"

NS_ASSUME_NONNULL_BEGIN

@protocol ConnectionStrategy <NSObject>
// 存放公共行为
- (void)connect;
- (void)disConnect;
- (void)sendData:(NSData *)data;
- (void)receiveData:(NSData *)data;
@end

NS_ASSUME_NONNULL_END
