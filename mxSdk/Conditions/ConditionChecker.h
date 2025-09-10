//
//  ConditionChecker.h
//  Inksi
//
//  Created by rbq on 2024/12/23.
//

// ConditionChecker.h
#import <UIKit/UIKit.h>
#import "ConditionAction.h"

@protocol ConditionChecker <NSObject>

- (id<ConditionAction>)getConditionAction;
- (void)checkCondition:(UIViewController *)viewController;

@end

