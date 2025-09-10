//
//  BLEConnection.h
//  Inksi
//
//  Created by rbq on 2024/11/1.
//

#import <UIKit/UIKit.h>
#import "ConnectionStrategy.h"

NS_ASSUME_NONNULL_BEGIN

@protocol BLEConnectionStrategy <ConnectionStrategy>

// BLE 独有的方法
- (void)scanForDevices;
- (void)stopScanning;

@end

@interface BLEConnection : NSObject<BLEConnectionStrategy>

@end

NS_ASSUME_NONNULL_END
