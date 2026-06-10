//
//  Skin.swift
//  Screenshare
//
//  Created by Gareth on 6/30/16.
//  Copyright © 2016 GPJ. All rights reserved.
//

import Cocoa
import AVFoundation
import AVKit


class Skin: NSView {
    
    @IBOutlet var view: NSView!
    
    @IBOutlet weak var previewView: NSView!
    //@IBOutlet weak var lblResolution: NSTextField!
    @IBOutlet weak var deviceFrameImage: NSImageView!
    
    @IBOutlet weak var resizeHandle: NSImageView!
    
    var session : AVCaptureSession!
    var input   : AVCaptureDeviceInput?
    var device = DeviceUtils(deviceType: .Phone)
    var deviceSettings : Device?
    
    var deviceDimensionsObtained = false
    var deviceInitializationRetries = 0
    let deviceInitializationMaxRetries = 3
    
    let notifications = NotificationManager()
    internal var ownerWindow : NSWindow?
    
    var videoPreviewLayer : AVCaptureVideoPreviewLayer?
    var originalPreviewViewBounds : NSRect = NSRect()
    
    var initialLocation : NSPoint?
    var initialMouseDrag : NSPoint?
    var isResize = false
    var trackingArea : NSTrackingArea?
    
    let ResizeHandleSize : CGFloat = 30
    let appDelegate = NSApplication.shared.delegate as! AppDelegate
    
    
    override init(frame frameRect: NSRect) {
        super.init(frame: frameRect)
        self.frame = frameRect
        
        self.loadSkinForDevice()
    }
    
    override var mouseDownCanMoveWindow : Bool {
        get {
            return true
        }
    }
    
    required init?(coder: NSCoder) {
        super.init(coder:coder)
        self.loadSkinForDevice()
    }
    
    private func loadSkinForDevice() {
        
        let newDev = DeviceUtils.initWithDimensions(dimensions: self.device.videDimensions)
        if( self.device.type != newDev.type || self.view == nil ) {
            self.device = newDev
            loadSkinFromNib(skin: self.device.skin)
            
            let size = newDev.getWindowSize()
            let frame = NSMakeRect(0, 0, size.width, size.height)
            self.ownerWindow?.setFrame(frame, display: true)
        }
    }
    
    
    private func loadSkinFromNib(skin : String) {
        
        if(self.view != nil) {
            self.view.removeFromSuperview()
        }
        
        if Bundle.main.loadNibNamed(skin, owner: self, topLevelObjects: nil) {
            
            NSApplication.shared.presentationOptions = [.autoHideDock, .autoHideMenuBar]
                    
            self.view.frame = self.bounds
            self.addSubview(self.view)
            
            // Custom view set to render concurrently in order to have its own layer
            let previewViewLayer = self.previewView.layer
            previewViewLayer!.backgroundColor = CGColor.black
            
            /* ADDING CONNECTION LATER            self.videoPreviewLayer = AVCaptureVideoPreviewLayer(sessionWithNoConnection: self.session) */
            self.videoPreviewLayer = AVCaptureVideoPreviewLayer(session: self.session)
            
            self.videoPreviewLayer!.frame = previewViewLayer!.bounds
            self.videoPreviewLayer!.autoresizingMask = [.layerWidthSizable, .layerHeightSizable]
            self.videoPreviewLayer!.videoGravity = .resizeAspect
            
            previewViewLayer?.addSublayer(self.videoPreviewLayer!)
            
            originalPreviewViewBounds = self.previewView.bounds
        }
    }
    
    func registerNotifications() {
        self.notifications.registerObserver(
            NSWindow.didResizeNotification, forObject: self.window!, dispatchAsyncToMainQueue: true, block: {note in
                self.updateViewsToWindow(windowSize: self.window!.frame.size)
        })
    }
    
    func initWithDevice(device: AVCaptureDevice) {
        
        self.session = AVCaptureSession()
        
        // Custom view set to render concurrently in order to have its own layer
        let previewViewLayer = self.previewView.layer
        previewViewLayer!.backgroundColor = CGColor.white
        
        /* ADDING CONNECTION LATER        self.videoPreviewLayer = AVCaptureVideoPreviewLayer(sessionWithNoConnection: self.session) */
        self.videoPreviewLayer = AVCaptureVideoPreviewLayer(session: self.session)
        
        self.videoPreviewLayer!.frame = previewViewLayer!.bounds
        //newPreviewLayer.autoresizingMask = CAAutoresizingMask.LayerWidthSizable | CAAutoresizingMask.LayerHeightSizable
        self.videoPreviewLayer!.videoGravity = .resize
        previewViewLayer?.addSublayer(self.videoPreviewLayer!)
        
        
        self.selectedDevice = device
        self.session.startRunning()
        
    }
    
    var selectedDevice : AVCaptureDevice? {
        get {
            return self.input?.device
        }
        set {
            self.session.beginConfiguration()
            
            if let input = self.input {
                session.removeInput(input)
                self.input = nil
            }
            
            if let newDevice = newValue {
                
                do {
                    let newDeviceInput = try AVCaptureDeviceInput(device: newDevice)
                    
                    self.session.sessionPreset = .high
                    self.session.addInput(newDeviceInput)
                    self.input = newDeviceInput
                    
                    // Register for notifications in format change which imply orientation change
                    self.notifications.registerObserver(AVCaptureInput.Port.formatDescriptionDidChangeNotification, dispatchAsyncToMainQueue: true, block: {notif in
                        self.updateAspect()
                    })
                    
                    // load existing device settings that might have been previously saved
                    getDeviceSettings(device: newDevice)
                    
                    
                } catch let error as NSError {
                    self.displayError(error: error)
                }
                
            }
            
            self.session.commitConfiguration()
            
            updateAspect()
            
            setThisAsSelectedDevice()
            
        }
    }
    
    func getVideoDimensions() -> CMVideoDimensions {
        
        // let window = self.windowForSheet
        if( window != nil) {
            if let port = self.input?.ports.first {
                
                if let description = port.formatDescription {
                    deviceDimensionsObtained = true
                    return CMVideoFormatDescriptionGetDimensions(description)
                } else {
                    retryOrShutdownSession()
                }
            }
        }
        return CMVideoDimensions(width: 0,height: 0)
    }
    
    
    
    func updateAspect() {
        updateAspect(ignoreSettings: false)
    }
    func updateAspect(ignoreSettings:Bool) {
        
        let dimensions = self.getVideoDimensions()
        
        if( dimensions.width != 0 && dimensions.height != 0 ) {
            
            if (dimensions.width != self.device.videDimensions.width || dimensions.height != self.device.videDimensions.height || ignoreSettings ) {
                
                self.device.videDimensions = dimensions
                self.loadSkinForDevice()
                
                if (self.window != nil) {
                    var windowSize = self.device.getWindowSize() //self.window!.frame.size //self.device.getWindowSize()
                    windowSize = windowSize.orientation != self.device.orientation ? windowSize.rotated() : windowSize
                    
                    if (    self.deviceSettings != nil
                        &&  !ignoreSettings
                        &&  self.deviceSettings?.hasPreviousLocation(forOrientation: self.device.orientation) == true ) {
                            
                            let windowRect = self.deviceSettings!.savedSettingForOrientation(forOrientation: self.device.orientation)
                            windowSize =  windowRect.size
                            positionWindow(windowRect: windowRect)
                            
                            
                    } else {
                        // Calculate new size to fit screen. -50 is just to give some margins for OS menubar, etc.
                        var screenFrame = self.window!.screen!.visibleFrame
                        screenFrame.size.height -= 50
                        screenFrame.size.width -= 50
                        windowSize = NSSize(fromCGSize: windowSize).scaleToFit(targetSize: screenFrame.size)
                        
                        // Center the window on screen
                        centerWindow(windowSize: windowSize)
                    }
                    
                    // Resize the internal view to the calculated size / rect
                    updateViewsToWindow(windowSize: windowSize)
                    
                }
            }
            return
            
        }
        
    }
    
    func scaleToFit(forgetSettings:Bool) {
        
        if forgetSettings {
            self.deviceSettings?.portraitRect = NSRect()
            self.deviceSettings?.landscapeRect = NSRect()
            saveDeviceSettins()
        }
        
        updateAspect(ignoreSettings: true)
        
    }
    
    func centerWindow(windowSize : NSSize) {
        self.window!.aspectRatio = windowSize
        self.window!.setFrame(DeviceUtils.getCenteredRect(windowSize: windowSize, screenFrame: self.window!.screen!.frame), display:true)
        // self.window?.center() does not work
    }
    func positionWindow(windowRect : NSRect) {
        self.window!.aspectRatio = windowRect.size
        self.window!.setFrame(windowRect, display:true)
        // self.window?.center() does not work
    }
    
    func updateViewsToWindow(windowSize : NSSize) {
        
        self.setFrameSize(windowSize)
        self.setFrameOrigin(NSPoint(x: 0,y: 0))
        self.view.frame = self.bounds
        
        self.deviceFrameImage.image = NSImage(named: self.device.getSkinDeviceImage())
        self.deviceFrameImage.translatesAutoresizingMaskIntoConstraints = true
        self.deviceFrameImage.setFrameSize(self.bounds.size)
        self.deviceFrameImage.setFrameOrigin(NSPoint(x: 0,y: 0))
        self.deviceFrameImage.needsDisplay = true
        
        let scale  = windowSize.width / ( self.device.orientation == .Portrait ? self.device.skinSize.width : self.device.skinSize.height )
        var size = NSSize(width: originalPreviewViewBounds.size.width * scale, height: originalPreviewViewBounds.size.height * scale)
        if self.device.orientation == .Landscape {
            size = size.rotated()
        }
        
        self.previewView.translatesAutoresizingMaskIntoConstraints = true
        self.previewView.setFrameSize(size)
        
        let origin = NSPoint(
            x: windowSize.width / 2 - size.width / 2,
            y: windowSize.height / 2 - size.height / 2)
        
        self.previewView.setFrameOrigin(origin)
        
        self.videoPreviewLayer?.frame = self.previewView.bounds
        
        self.needsDisplay = true
        self.window!.invalidateShadow()
        
        if trackingArea != nil {
            self.removeTrackingArea(trackingArea!)
        }
        trackingArea = NSTrackingArea(rect: self.bounds,
            options: [.activeAlways, .mouseEnteredAndExited], owner: self, userInfo: nil)
        self.addTrackingArea(trackingArea!)
    }
    
    //MARK: Session handling
    
    func retryOrShutdownSession() {
        // Delay execution of retry logic for 5 seconds.
        DispatchQueue.main.asyncAfter(deadline: .now() + 5) {
            
            if self.deviceDimensionsObtained {  // We were successfull meanwhile in obtaining the video stream
                return
            }
            
            self.deviceInitializationRetries += 1
            if self.deviceInitializationRetries < self.deviceInitializationMaxRetries {
                if( self.input != nil) {
                    NSLog("Port is empty. Screen may be blank. Reinitializing device")
                    self.session.stopRunning()
                    self.selectedDevice = self.input!.device
                    self.session.startRunning()
                }
                
            } else {
                NSLog("Port still empty after \(self.deviceInitializationRetries) tries. Shutting down session")
                if( self.window != nil) {
                    let alert = NSAlert()
                    alert.messageText = "Error streaming device"
                    alert.addButton(withTitle: "OK")
                    alert.informativeText = "We were unable to connect to your device's video stream. Please try reconnecting the lightning cable."
                    alert.beginSheetModal(for: self.window!, completionHandler: nil)
                    self.endSession()
                }
            }
            
        }
        
    }
    
    func displayError(error: NSError?) {
        guard let error = error else { return }
        DispatchQueue.main.async {
            self.presentError(error)
        }
    }
    
    
    func endSession() {
        appDelegate.selectedDevice = nil
        notifications.deregisterAll()
        session.stopRunning()
        ownerWindow = nil
    }
    
    
    
    //MARK: Dragging & Resizing
    override func mouseEntered(with theEvent: NSEvent) {
        self.resizeHandle.isHidden = false
    }
    override func mouseExited(with theEvent: NSEvent) {
        self.resizeHandle.isHidden = true
        self.window?.invalidateShadow()
    }
    override func mouseDown(with theEvent: NSEvent) {
        initialLocation = NSEvent.mouseLocation
        
        initialLocation?.x -= self.window!.frame.origin.x
        initialLocation?.y -= self.window!.frame.origin.y
        
        isResize = (initialLocation!.x > self.deviceFrameImage!.bounds.size.width - ResizeHandleSize)
            && (initialLocation!.y < ResizeHandleSize)
        
        appDelegate.selectedDevice = self
        
    }
    
    override func mouseDragged(with theEvent: NSEvent) {
        
        if !isResize {
            
            let curLocation = NSEvent.mouseLocation
            
            var newOrigin = NSPoint(
                x: curLocation.x - initialLocation!.x,
                y: curLocation.y - initialLocation!.y)
            
            let screenFrame = NSScreen.main?.frame
            if((newOrigin.y + window!.frame.size.height) > (screenFrame!.origin.y + screenFrame!.size.height)) {
                newOrigin.y = screenFrame!.origin.y + (screenFrame!.size.height - window!.frame.size.height)
            }
            
            self.window!.setFrameOrigin(newOrigin)
        }
        updateDeviceSettings()
        
    }
    override func viewDidEndLiveResize() {
        updateDeviceSettings()
    }
    
    //MARK: Device Settings
    func updateDeviceSettings() {
        // Update current device size/location settings based on its current movement
        if(self.deviceSettings != nil) {
            if self.device.orientation == Device.DeviceOrientation.Portrait {
                self.deviceSettings!.portraitRect = window!.frame
            } else {
                self.deviceSettings!.landscapeRect = window!.frame
            }
        }
        saveDeviceSettins()
        
    }
    func getDeviceSettings(device: AVCaptureDevice) {
        self.deviceSettings = appDelegate.findDeviceSettings(device: device)
    }
    func saveDeviceSettins() {
        appDelegate.saveDeviceSettings()
    }
    func setThisAsSelectedDevice() {
        appDelegate.selectedDevice = self
    }
    
    
}
