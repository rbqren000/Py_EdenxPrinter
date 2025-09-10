//
//  PeakView.m
//  BelonPrinter
//
//  Created by rbq on 2021/5/26.
//  Copyright © 2021 rbq. All rights reserved.
//

#import "DotView.h"

@implementation DotView

- (instancetype)initWithFrame:(CGRect)frame
{
    self = [super initWithFrame:frame];
    if (self) {
        [self setUp];
    }
    return self;
}

- (instancetype)initWithCoder:(NSCoder *)coder
{
    self = [super initWithCoder:coder];
    if (self) {
        [self setUp];
    }
    return self;
}

-(void)setUp{
    
}

- (void)setLocation:(DotLocation)location{
    _location = location;
}

- (void)setPoint:(CGPoint)point {
    _point = point;
    self.center = point;
}

@end
