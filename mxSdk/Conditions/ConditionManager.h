//
//  ConditionManager.h
//  Inksi
//
//  Created by rbq on 2024/12/23.
//

// ConditionManager.h
#import <UIKit/UIKit.h>
#import "ConditionChecker.h"
#import "ConditionCallback.h"

@interface ConditionManager : NSObject

- (void)addChecker:(id<ConditionChecker>)checker;
- (void)checkConditions:(UIViewController *)viewController callback:(id<ConditionCallback>)callback;
- (void)onConditionResult:(UIViewController *)viewController key:(NSString *)key granted:(BOOL)granted;

@end

