//
//  MultiConditionAction.m
//  Inksi
//
//  Created by rbq on 2024/12/25.
//

#import "MultiConditionAction.h"

@implementation MultiConditionAction

- (instancetype)initWithActions:(NSArray<id<ConditionAction>> *)actions {
    self = [super init];
    if (self) {
        _actions = actions;
    }
    return self;
}

- (NSString *)getKey {
    // 使用固定的 Key 表示组合条件
    return @"MultiPermissionAction";
}

- (BOOL)isConditionMetWithViewController:(UIViewController *)viewController {
    // 遍历所有条件，任一条件未通过，则返回 NO
    for (id<ConditionAction> action in self.actions) {
        if (![action isConditionMet:viewController]) {
            return NO;
        }
    }
    return YES;
}

- (void)onConditionMet {
    // 组合条件无需特定操作，可根据需要扩展
}

- (BOOL)isConditionMet:(UIViewController *)viewController { 
    return false;
}


- (void)requestCondition:(UIViewController *)viewController conditionManager:(ConditionManager *)conditionManager { 
    
}


- (void)requestConditionWithViewController:(UIViewController *)viewController
                        conditionManager:(ConditionManager *)conditionManager {
    // 遍历所有未满足的条件并请求
    for (id<ConditionAction> action in self.actions) {
        if (![action isConditionMet:viewController]) {
            [action requestCondition:viewController conditionManager:conditionManager];
        }
    }
}

@end

