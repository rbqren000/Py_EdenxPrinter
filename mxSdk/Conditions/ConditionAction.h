//
//  ConditionAction.h
//  Inksi
//
//  Created by rbq on 2024/12/23.
//

// ConditionAction.h
#import <UIKit/UIKit.h>

@class ConditionManager;

@protocol ConditionAction <NSObject>

- (NSString *)getKey;
- (BOOL)isConditionMet:(UIViewController *)viewController;
- (void)onConditionMet;
- (void)requestCondition:(UIViewController *)viewController
       conditionManager:(ConditionManager *)conditionManager;

@end

