//
//  Device.swift
//

import Foundation
import AVKit
import AVFoundation

class Device: NSObject, NSCoding {
    
    var name: String
    var uid: String
    var portraitRect: NSRect
    var landscapeRect: NSRect
    
    struct PropertyKey {
        static let nameKey = "name"
        static let uidKey = "uid"
        static let portraitRectKey = "p_rect"
        static let landscapeRectKey = "l_rect"
    }
    
    enum DeviceType {
        case Phone
        case Tablet
    }
    enum DeviceOrientation {
        case Portrait
        case Landscape
    }
    
    
    static let ArchivePath = NSHomeDirectory().appending("/devices")

    convenience init(fromDevice device: AVCaptureDevice) {
        self.init(name: device.localizedName, uid: device.uniqueID, portraitRect:NSRect(), landscapeRect:NSRect())
    }
    init(name: String, uid: String, portraitRect:NSRect, landscapeRect:NSRect) {
        self.name = name
        self.uid = uid
        self.portraitRect = portraitRect
        self.landscapeRect = landscapeRect
        
        super.init()
    }
    
    func hasPreviousLocation(forOrientation: DeviceOrientation) -> Bool {
        return savedSettingForOrientation(forOrientation: forOrientation).hasUsableWindowGeometry
    }
    func savedSettingForOrientation(forOrientation: DeviceOrientation) -> NSRect {
        if forOrientation == DeviceOrientation.Portrait {
            return portraitRect
        } else {
            return landscapeRect
        }
    }

    
    //MARK: NSCoding
    func encode(with aCoder: NSCoder) {
        aCoder.encode(name, forKey: PropertyKey.nameKey)
        aCoder.encode(uid, forKey: PropertyKey.uidKey)
        
        aCoder.encode(NSStringFromRect(portraitRect), forKey: PropertyKey.portraitRectKey)
        aCoder.encode(NSStringFromRect(landscapeRect), forKey: PropertyKey.landscapeRectKey)
        
    }
    
    required convenience init?(coder aDecoder: NSCoder) {
        guard let name = aDecoder.decodeObject(forKey: PropertyKey.nameKey) as? String,
            let uid = aDecoder.decodeObject(forKey: PropertyKey.uidKey) as? String,
            let portraitRect = aDecoder.decodeObject(forKey: PropertyKey.portraitRectKey) as? String,
            let landscapeRect = aDecoder.decodeObject(forKey: PropertyKey.landscapeRectKey) as? String else {
                return nil
        }

        let pRect = NSRectFromString(portraitRect)
        let lRect = NSRectFromString(landscapeRect)
        
        // Must call designated initializer.
        self.init(name: name, uid: uid, portraitRect:pRect, landscapeRect:lRect)
    }
    
}
