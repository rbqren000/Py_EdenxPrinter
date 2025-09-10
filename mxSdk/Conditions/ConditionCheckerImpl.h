//
//  ConditionCheckerImpl.h
//  Inksi
//
//  Created by rbq on 2024/12/23.
//

// ConditionCheckerImpl.h
#import <UIKit/UIKit.h>
#import "ConditionChecker.h"
#import "ConditionManager.h"

@interface ConditionCheckerImpl : NSObject <ConditionChecker>

- (instancetype)initWithConditionManager:(ConditionManager *)conditionManager
                        conditionAction:(id<ConditionAction>)conditionAction;

@end

