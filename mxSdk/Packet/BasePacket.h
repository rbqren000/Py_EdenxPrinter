//
//  BasePacket.h
//  Inksi
//
//  Created by rbq on 2024/6/17.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

@interface BasePacket : NSObject

@property (nonatomic, assign) BOOL start;

-(void)clear;
/**包含N且不能包含NAK和EOT**/
- (BOOL)isRequestData:(NSData *)data;
/**不能包含EOT，但是必须包含NAK**/
-(BOOL)isNAK:(NSData *)data;
/**只要有EOT则认为是EOT，既请求结束**/
-(BOOL)isEOT:(NSData *)data;

@end

NS_ASSUME_NONNULL_END
