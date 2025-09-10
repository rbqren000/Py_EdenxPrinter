//
//  TransportProtocol.h
//  BelonPrinter
//
//  Created by rbq on 2021/7/6.
//  Copyright © 2021 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

//请求数据相关指令  N
static const uint8_t C = 0x4E;
// 指令码  128byte
static const uint8_t SOH = 0x18;
// 指令码  512byte
static const uint8_t STX = 0x19;
// 指令码  1k
static const uint8_t STX_A = 0x1A;
// 指令码  2k
static const uint8_t STX_B = 0x1B;
// 指令码  5k
static const uint8_t STX_C = 0x1C;
// 指令码  10k
static const uint8_t STX_D = 0x1D;
// 指令码  预留  124byte
static const uint8_t STX_E = 0x1E;

//重传当前数据包请求命令  R
static const uint8_t NAK = 0x52;

//接收完毕，结束发送 D
static const uint8_t EOT = 0x44;

// 最大错误（无应答）包数
static const uint8_t MAX_ERRORS = 10;


@interface TransportProtocol : NSObject

@end

NS_ASSUME_NONNULL_END
