//
//  ConditionManager.m
//  Inksi
//
//  Created by rbq on 2024/12/23.
//

// ConditionManager.m
#import "ConditionManager.h"

@interface ConditionManager ()

@property (nonatomic, strong) NSMutableArray<id<ConditionChecker>> *checkers;
@property (nonatomic, strong) NSMutableDictionary<NSString *, NSNumber *> *conditionStatus;
@property (nonatomic, weak) id<ConditionCallback> callback;

@end

@implementation ConditionManager

- (instancetype)init {
    self = [super init];
    if (self) {
        _checkers = [NSMutableArray array];
        _conditionStatus = [NSMutableDictionary dictionary];
    }
    return self;
}

- (void)addChecker:(id<ConditionChecker>)checker {
    if ([self.checkers containsObject:checker]) {
        return;
    }
    [self.checkers addObject:checker];
    self.conditionStatus[[checker.getConditionAction getKey]] = @(NO);
}

- (void)checkConditions:(UIViewController *)viewController callback:(id<ConditionCallback>)callback {
    self.callback = callback;

    for (id<ConditionChecker> checker in self.checkers) {
        id<ConditionAction> action = [checker getConditionAction];
        if ([action isConditionMet:viewController]) {
            self.conditionStatus[[action getKey]] = @(YES);
            [action onConditionMet];
        } else {
            [action requestCondition:viewController conditionManager:self];
        }
    }

    if ([self allConditionsProcessed:viewController]) {
        [self notifyCallback];
    }
}

- (void)onConditionResult:(UIViewController *)viewController key:(NSString *)key granted:(BOOL)granted {
    
    self.conditionStatus[key] = @(granted);

    for (id<ConditionChecker> checker in self.checkers) {
        if ([[checker.getConditionAction getKey] isEqualToString:key]) {
            if (granted) {
                [checker.getConditionAction onConditionMet];
            }
            break;
        }
    }

    if ([self allConditionsProcessed:viewController]) {
        [self notifyCallback];
    }
}

-(void)olayCheckWithSetConditions:(UIViewController *)viewController{
    for (id<ConditionChecker> checker in self.checkers) {
        id<ConditionAction> action = [checker getConditionAction];
        if ([action isConditionMet:viewController]) {
            self.conditionStatus[[action getKey]] = @(YES);
        }
    }
}

- (BOOL)allConditionsProcessed:(UIViewController *)viewController {
    [self olayCheckWithSetConditions:viewController];
    for (NSNumber *status in self.conditionStatus.allValues) {
        if (![status boolValue]) {
            return NO;
        }
    }
    return YES;
}

- (void)notifyCallback {
    if (!self.callback) return;

    NSMutableArray<NSString *> *unmetConditions = [NSMutableArray array];
    for (NSString *key in self.conditionStatus) {
        if (![self.conditionStatus[key] boolValue]) {
            [unmetConditions addObject:key];
        }
    }

    if (unmetConditions.count == 0) {
        [self.callback onAllConditionsMet];
    } else {
        [self.callback onConditionsUnmet:unmetConditions];
    }
}

@end

