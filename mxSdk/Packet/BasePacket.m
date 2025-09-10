//
//  BasePacket.m
//  Inksi
//
//  Created by rbq on 2024/6/17.
//

#import "BasePacket.h"
#import "TransportProtocol.h"

@implementation BasePacket

- (void)setStart:(BOOL)start{
    _start = start;
}

- (void)clear {
    self.start = NO;
}

- (BOOL)isRequestData:(NSData *)data {

    if (!data || !self.start) {
        return NO;
    }

    int length = (int)[data length];
    uint8_t *dataByte = (uint8_t *)[data bytes];

    if (length == 1 && ((dataByte[0] & 0xFF) == C)) {
        return YES;
    }

    NSString *jsonStr = [[[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding]
                               stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]];
    if([[jsonStr lowercaseString] isEqualToString:@"c"]){
        return YES;
    }
    
    BOOL hasN = NO;
    BOOL hasNAK = NO;
    BOOL hasEOT = NO;
    for (int i = 0; i < length; i++) {
        int value = dataByte[i] & 0xFF;
        if (value == C) {
            hasN = YES;
        } else if (value == NAK) {
            hasNAK = YES;
        } else if (value == EOT) {
            hasEOT = YES;
        }
        // 提前终止循环，如果发现NAK或EOT
        if (hasNAK || hasEOT) {
            return NO;
        }
    }
    return hasN;
}

-(BOOL)isNAK:(NSData *)data {
    
    if (!data || !self.start) {
        return NO;
    }

    int length = (int)[data length];
    uint8_t *dataByte = (uint8_t *)[data bytes];

    if (length == 1 && ((dataByte[0] & 0xFF) == NAK)) {
        return YES;
    }

    NSString *jsonStr = [[[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding]
                               stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]];
    if([[jsonStr lowercaseString] isEqualToString:@"r"]){
        return YES;
    }
    
    BOOL hasNAK = NO;
    BOOL hasEOT = NO;
    for (int i = 0; i < length; i++) {
        int value = dataByte[i] & 0xFF;
        if (value == NAK) {
            hasNAK = true;
        } else if (value == EOT) {
            hasEOT = true;
            break;  // 提前终止循环，如果发现EOT
        }
    }
    return hasNAK && !hasEOT;
}

-(BOOL)isEOT:(NSData *)data {
    
    if (!data || !self.start) {
        return NO;
    }

    int length = (int)[data length];
    uint8_t *dataByte = (uint8_t *)[data bytes];

    if (length == 1 && ((dataByte[0] & 0xFF) == EOT)) {
        return YES;
    }

    NSString *jsonStr = [[[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding]
                               stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]];
    if([[jsonStr lowercaseString] isEqualToString:@"d"]){
        return YES;
    }
    
    for (int i = 0; i < length; i++) {
        int value = dataByte[i] & 0xFF;
        if(value == EOT){
            return YES;
        }
    }
    return NO;
}

@end
