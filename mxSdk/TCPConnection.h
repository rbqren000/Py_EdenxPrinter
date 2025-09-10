//
//  TCPConnection.h
//  Inksi
//
//  Created by rbq on 2024/11/1.
//

#import <UIKit/UIKit.h>
#import "ConnectionStrategy.h"

NS_ASSUME_NONNULL_BEGIN

@protocol TCPConnectionStrategy <ConnectionStrategy>

// TCP 独有的方法
- (void)startListeningUdp;
- (void)stopListeningUdp;

@end


@interface TCPConnection : NSObject<TCPConnectionStrategy>

@end

NS_ASSUME_NONNULL_END
