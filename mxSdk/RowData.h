//
//  SingleRowImageData.h
//  BelonPrinter
//
//  Created by rbq on 2021/7/5.
//  Copyright © 2021 rbq. All rights reserved.
//

#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

@interface RowData : NSObject

@property (nonatomic, assign) NSUInteger dataLength;
@property (nonatomic, strong) NSString *rowDataPath;
@property (nonatomic, assign) BOOL compress;

-(NSUInteger)totalPacketCount:(NSUInteger)usefulDataLen;
-(NSData *)data;

@end

NS_ASSUME_NONNULL_END
