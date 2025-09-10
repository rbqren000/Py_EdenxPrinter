//
//  LogoData.h
//  Inksi
//
//  Created by rbq on 2024/6/21.
//

#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

@interface LogoData : NSObject

@property (nonatomic, strong) NSString *dataPath;
@property (nonatomic, assign) NSUInteger dataLength;
@property (nonatomic, strong) NSString *imagePath;

- (instancetype)init NS_UNAVAILABLE;
- (instancetype)initLogoData:(NSString *)dataPath dataLength:(NSUInteger)dataLength imagePath:(NSString *)imagePath;

-(NSUInteger)totalPacketCount:(NSUInteger)usefulDataLen;
-(NSData *)data;

@end

NS_ASSUME_NONNULL_END
