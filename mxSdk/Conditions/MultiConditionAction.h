//
//  MultiConditionAction.h
//  Inksi
//
//  Created by rbq on 2024/12/25.
//

#import <UIKit/UIKit.h>
#import "ConditionAction.h"
#import "ConditionManager.h"

@interface MultiConditionAction : NSObject <ConditionAction>

@property (nonatomic, strong, readonly) NSArray<id<ConditionAction>> *actions;

- (instancetype)initWithActions:(NSArray<id<ConditionAction>> *)actions;

@end

