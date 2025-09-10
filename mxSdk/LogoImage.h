//
//  LogoImage.h
//  Inksi
//
//  Created by rbq on 2024/6/21.
//

#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

@interface LogoImage : NSObject

/**行图的路径*/
@property (nonatomic, strong) NSString *imagePath;

- (instancetype)init NS_UNAVAILABLE;
- (instancetype)initLogoImage:(NSString *)imagePath;

@end

NS_ASSUME_NONNULL_END
