//
//  ConditionCallback.h
//  Inksi
//
//  Created by rbq on 2024/12/23.
//

// ConditionCallback.h
#import <UIKit/UIKit.h>

@protocol ConditionCallback <NSObject>

- (void)onAllConditionsMet;
- (void)onConditionsUnmet:(NSArray<NSString *> *)unmetConditions;

@end

