//
//  DeviceUtils.swift
//  Screenshare
//
//  Created by Gareth on 6/30/16.
//  Copyright © 2016 GPJ. All rights reserved.
//

import Foundation
import CoreMediaIO
import Cocoa
import AVKit
import AVFoundation


class DeviceUtils {
    
    var type: Device.DeviceType
    var skinSize: NSSize!
    var skin = "Skin"
    var orientation = Device.DeviceOrientation.Portrait
    
    var videDimensions: CMVideoDimensions = CMVideoDimensions(width: 0,height: 0) {
        didSet {
            orientation = videDimensions.width > videDimensions.height ? .Landscape : .Portrait
        }
    }
    
    init(deviceType:Device.DeviceType) {
        self.type = deviceType
        self.skinSize = getSkinSize()
        switch deviceType {
        case .Phone:
            skin = "Skin"
        case .Tablet:
            skin = "Skin_tablet"
        }
    }
    
    class func initWithDimensions(dimensions:CMVideoDimensions) -> DeviceUtils {
        
        var device : DeviceUtils
        if((dimensions.width == 1024 && dimensions.height == 768)
            || (dimensions.width == 768 && dimensions.height == 1024)
            || (dimensions.width == 900 && dimensions.height == 1200)
            || (dimensions.width == 1200 && dimensions.height == 900)
            || (dimensions.width == 1200 && dimensions.height == 1600)
            || (dimensions.width == 1600 && dimensions.height == 1200)) {
            device = DeviceUtils(deviceType: .Tablet)
        } else {
            device = DeviceUtils(deviceType: .Phone)
        }
        
        device.videDimensions = dimensions
        return device
    }
    

    func getSkinDeviceImage() -> String {
        let imgLandscape = self.orientation == .Landscape ? "_landscape" : ""
        let imgtype = self.type == .Tablet ? "tablet" : "phone"
        return "\(imgtype)_white\(imgLandscape)"
    }

    func getSkinSize() -> NSSize {
        var size : NSSize
        switch self.type {
        case .Phone:
            size = NSSize(width: 350,height: 700)
        case .Tablet:
            size = NSSize(width: 435,height: 646)
        }
        return self.orientation == .Portrait ?
            NSSize(width: size.width, height: size.height) :
            NSSize(width: size.height, height: size.width)
    }
    
    func getFrame() -> CGRect {
        return CGRectMake(0, 0, skinSize.width, skinSize.height)
    }
    
    func getWindowSize() -> NSSize {
        if(self.orientation == .Portrait) {
            return NSSize(width: skinSize.width, height: skinSize.height)
        } else {
            return NSSize(width: skinSize.height, height: skinSize.width)
        }
    }
    
    class func getCenteredRect(windowSize : NSSize, screenFrame: NSRect) -> NSRect{
        let origin = NSPoint(
            x: screenFrame.width / 2 - windowSize.width / 2,
            y: screenFrame.height / 2 - windowSize.height / 2 )

        return NSRect(origin: origin, size: windowSize)
    }
    
    
    class func registerForScreenCaptureDevices() {
        
        var prop : CMIOObjectPropertyAddress = CMIOObjectPropertyAddress(
            mSelector: CMIOObjectPropertySelector(kCMIOHardwarePropertyAllowScreenCaptureDevices),
            mScope: CMIOObjectPropertyScope(kCMIOObjectPropertyScopeGlobal),
            mElement: CMIOObjectPropertyElement(kCMIOObjectPropertyElementMaster))
        
        var allow:UInt32 = 1
        
        CMIOObjectSetPropertyData( CMIOObjectID(kCMIOObjectSystemObject),
            &prop,
            0,
            nil,
            UInt32(sizeofValue(allow)),
            &allow)
        
    }
}