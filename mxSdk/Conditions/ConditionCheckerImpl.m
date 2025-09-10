//
//  ConditionCheckerImpl.m
//  Inksi
//
//  Created by rbq on 2024/12/23.
//

// ConditionCheckerImpl.m
#import "ConditionCheckerImpl.h"

@interface ConditionCheckerImpl ()

@property (nonatomic, strong) ConditionManager *conditionManager;
@property (nonatomic, strong) id<ConditionAction> conditionAction;

@end

@implementation ConditionCheckerImpl

- (instancetype)initWithConditionManager:(ConditionManager *)conditionManager
                        conditionAction:(id<ConditionAction>)conditionAction {
    self = [super init];
    if (self) {
        _conditionManager = conditionManager;
        _conditionAction = conditionAction;
    }
    return self;
}

- (id<ConditionAction>)getConditionAction {
    return _conditionAction;
}

- (void)checkCondition:(UIViewController *)viewController {
    if (self.conditionAction) {
        if (![self.conditionAction isConditionMet:viewController]) {
            [self.conditionAction requestCondition:viewController conditionManager:self.conditionManager];
        } else {
            [self.conditionManager onConditionResult:viewController key:[self.conditionAction getKey] granted:YES];
        }
    }
}

@end

