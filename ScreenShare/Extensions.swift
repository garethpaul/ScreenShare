//
//  Extensions.swift
//

import Foundation

extension Int {
    func format(_ f: String) -> String {
        return String(format: "%\(f)d", self)
    }
}

extension Double {
    func format(_ f: String) -> String {
        return String(format: "%\(f)f", self)
    }
    func to_CGFloat() -> CGFloat {
        return CGFloat(self)
    }
}

extension CGFloat {
    func format(_ f: String) -> String {
        return Double(self).format(f)
    }
}

extension NSSize {
    init(fromCGSize size:CGSize) {
        self.init(width: size.width, height: size.height)
    }
    func rotated() -> NSSize {
        return NSSize(width: self.height, height: self.width)
    }
    func toIntegerSizes() -> NSSize {
        return NSSize(width: Int(self.width), height: Int(self.height))
    }
    var orientation : Device.DeviceOrientation {
        get {
            return self.height >= self.width ? .Portrait : .Landscape
        }
    }
    var isFinitePositive: Bool {
        return width.isFinite && height.isFinite && width > 0 && height > 0
    }
    func scaleToFit(targetSize: NSSize) -> NSSize {

        guard self.isFinitePositive && targetSize.isFinitePositive else {
            return NSSize.zero
        }

        if NSEqualSizes(self, targetSize) {
            return self
        }
        
        let widthFactor  = targetSize.width / width
        let heightFactor = targetSize.height / height

        var scaleFactor :CGFloat = 0.0
        if ( widthFactor < heightFactor ) {
            scaleFactor = widthFactor
        } else {
            scaleFactor = heightFactor
        }
        
        let scaledWidth  = width  * scaleFactor;
        let scaledHeight = height * scaleFactor;
        
        return NSSize(width: scaledWidth, height: scaledHeight)
        
    }
}
extension NSRect {
    var hasUsableWindowGeometry: Bool {
        return origin.x.isFinite && origin.y.isFinite && size.isFinitePositive
    }
}
extension NSPoint {
    func rounded() -> NSPoint {
        return NSPoint(x: Int(self.x), y: Int(self.y))
    }
}
