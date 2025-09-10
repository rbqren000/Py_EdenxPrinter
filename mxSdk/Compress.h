//
//  Compress.h
//  BelonPrinter
//
//  Created by rbq on 2020/11/2.
//  Copyright © 2020 rbq. All rights reserved.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

@interface Compress : NSObject

+(NSMutableArray<NSData *> *)compressRowDataArr:(NSMutableArray<NSData *> *)data72;

+(NSData *)compressRowData:(uint8_t *)d72 d72Len:(NSInteger)d72Len;
+(NSData *)compressRowData:(NSData *)data72;

+(void)simulationCompressWithUncompress:(uint32_t*)pixels uncompress:(uint32_t *)uncompress width:(int)width height:(int)height;
+(void)mergeSimulationCompressWithUncompress:(uint32_t*)pixels uncompress:(uint32_t *)uncompress width:(int)width height:(int)height;

@end

NS_ASSUME_NONNULL_END
