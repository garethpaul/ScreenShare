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

    private var appDelegate: AppDelegate? {
        guard let appDelegate = NSApplication.shared.delegate as? AppDelegate else {
            NSLog("ScreenShare application delegate is unavailable.")
            return nil
        }
        return appDelegate
    }
    
    
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
            guard let previewView = self.previewView,
                  let previewViewLayer = previewView.layer else {
                NSLog("Skin preview outlet or backing layer is unavailable.")
                return
            }
            previewViewLayer.backgroundColor = CGColor.black
            
            /* ADDING CONNECTION LATER            self.videoPreviewLayer = AVCaptureVideoPreviewLayer(sessionWithNoConnection: self.session) */
            let videoPreviewLayer = AVCaptureVideoPreviewLayer(session: self.session)
            self.videoPreviewLayer = videoPreviewLayer

            videoPreviewLayer.frame = previewViewLayer.bounds
            videoPreviewLayer.autoresizingMask = [.layerWidthSizable, .layerHeightSizable]
            videoPreviewLayer.videoGravity = .resizeAspect

            previewViewLayer.addSublayer(videoPreviewLayer)
            
            originalPreviewViewBounds = previewView.bounds
        }
    }
    
    func registerNotifications() {
        guard let window = self.window else {
            NSLog("Skin notification window is unavailable.")
            return
        }
        self.notifications.registerObserver(
            NSWindow.didResizeNotification, forObject: window, dispatchAsyncToMainQueue: true, block: { [weak self, weak window] _ in
                guard let self = self,
                      let window = window,
                      let skinView = self.view,
                      let deviceFrameImage = self.deviceFrameImage,
                      let previewView = self.previewView else {
                    NSLog("Skin resize layout window or outlets are unavailable.")
                    return
                }
                self.updateViewsToWindow(
                    windowSize: window.frame.size,
                    window: window,
                    skinView: skinView,
                    deviceFrameImage: deviceFrameImage,
                    previewView: previewView)
        })
    }
    
    func initWithDevice(device: AVCaptureDevice) {
        
        self.session = AVCaptureSession()
        
        // Custom view set to render concurrently in order to have its own layer
        guard let previewView = self.previewView,
              let previewViewLayer = previewView.layer else {
            NSLog("Skin preview outlet or backing layer is unavailable.")
            return
        }
        previewViewLayer.backgroundColor = CGColor.white
        
        /* ADDING CONNECTION LATER        self.videoPreviewLayer = AVCaptureVideoPreviewLayer(sessionWithNoConnection: self.session) */
        let videoPreviewLayer = AVCaptureVideoPreviewLayer(session: self.session)
        self.videoPreviewLayer = videoPreviewLayer

        videoPreviewLayer.frame = previewViewLayer.bounds
        //newPreviewLayer.autoresizingMask = CAAutoresizingMask.LayerWidthSizable | CAAutoresizingMask.LayerHeightSizable
        videoPreviewLayer.videoGravity = .resize
        previewViewLayer.addSublayer(videoPreviewLayer)
        
        
        self.selectedDevice = device
        self.session.startRunning()
        
    }
    
    var selectedDevice : AVCaptureDevice? {
        get {
            return self.input?.device
        }
        set {
            let replacementInput: AVCaptureDeviceInput?
            if let newDevice = newValue {
                do {
                    replacementInput = try AVCaptureDeviceInput(device: newDevice)
                } catch let error as NSError {
                    self.displayError(error: error)
                    return
                }
            } else {
                replacementInput = nil
            }

            self.session.beginConfiguration()
            defer {
                self.session.commitConfiguration()
                self.updateAspect()
                self.setThisAsSelectedDevice()
            }

            let previousInput = self.input
            if let previousInput = previousInput {
                self.session.removeInput(previousInput)
            }
            self.input = nil

            guard let replacementInput = replacementInput else {
                return
            }

            self.session.sessionPreset = .high
            guard self.session.canAddInput(replacementInput) else {
                if let previousInput = previousInput,
                    self.session.canAddInput(previousInput) {
                    self.session.addInput(previousInput)
                    self.input = previousInput
                }
                NSLog("Skin capture session rejected the replacement device input.")
                return
            }

            self.session.addInput(replacementInput)
            self.input = replacementInput

            // Register for format changes that imply orientation changes.
            self.notifications.registerObserver(AVCaptureInput.Port.formatDescriptionDidChangeNotification, dispatchAsyncToMainQueue: true, block: { _ in
                self.updateAspect()
            })

            getDeviceSettings(device: replacementInput.device)
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
                
                guard let window = self.window,
                      let skinView = self.view,
                      let deviceFrameImage = self.deviceFrameImage,
                      let previewView = self.previewView else {
                    NSLog("Skin aspect layout window or outlets are unavailable.")
                    return
                }

                var windowSize = self.device.getWindowSize()
                windowSize = windowSize.orientation != self.device.orientation ? windowSize.rotated() : windowSize

                if let deviceSettings = self.deviceSettings,
                   !ignoreSettings,
                   deviceSettings.hasPreviousLocation(forOrientation: self.device.orientation) {
                    let windowRect = deviceSettings.savedSettingForOrientation(forOrientation: self.device.orientation)
                    windowSize = windowRect.size
                    positionWindow(windowRect: windowRect, window: window)
                } else if let screen = window.screen ?? NSScreen.main {
                    // Leave a small margin for the menu bar and other screen chrome.
                    var screenFrame = screen.visibleFrame
                    screenFrame.size.height -= 50
                    screenFrame.size.width -= 50
                    windowSize = NSSize(fromCGSize: windowSize).scaleToFit(targetSize: screenFrame.size)
                    centerWindow(windowSize: windowSize, window: window, screenFrame: screen.frame)
                } else {
                    NSLog("Skin aspect layout screen is unavailable.")
                    window.aspectRatio = windowSize
                }

                updateViewsToWindow(
                    windowSize: windowSize,
                    window: window,
                    skinView: skinView,
                    deviceFrameImage: deviceFrameImage,
                    previewView: previewView)
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
    
    func centerWindow(windowSize: NSSize, window: NSWindow, screenFrame: NSRect) {
        window.aspectRatio = windowSize
        window.setFrame(DeviceUtils.getCenteredRect(windowSize: windowSize, screenFrame: screenFrame), display: true)
        // self.window?.center() does not work
    }
    func positionWindow(windowRect: NSRect, window: NSWindow) {
        window.aspectRatio = windowRect.size
        window.setFrame(windowRect, display: true)
        // self.window?.center() does not work
    }
    
    func updateViewsToWindow(windowSize: NSSize, window: NSWindow, skinView: NSView,
                             deviceFrameImage: NSImageView, previewView: NSView) {
        
        self.setFrameSize(windowSize)
        self.setFrameOrigin(NSPoint(x: 0,y: 0))
        skinView.frame = self.bounds
        
        deviceFrameImage.image = NSImage(named: self.device.getSkinDeviceImage())
        deviceFrameImage.translatesAutoresizingMaskIntoConstraints = true
        deviceFrameImage.setFrameSize(self.bounds.size)
        deviceFrameImage.setFrameOrigin(NSPoint(x: 0,y: 0))
        deviceFrameImage.needsDisplay = true
        
        let scale  = windowSize.width / ( self.device.orientation == .Portrait ? self.device.skinSize.width : self.device.skinSize.height )
        var size = NSSize(width: originalPreviewViewBounds.size.width * scale, height: originalPreviewViewBounds.size.height * scale)
        if self.device.orientation == .Landscape {
            size = size.rotated()
        }
        
        previewView.translatesAutoresizingMaskIntoConstraints = true
        previewView.setFrameSize(size)
        
        let origin = NSPoint(
            x: windowSize.width / 2 - size.width / 2,
            y: windowSize.height / 2 - size.height / 2)
        
        previewView.setFrameOrigin(origin)
        
        self.videoPreviewLayer?.frame = previewView.bounds
        
        self.needsDisplay = true
        window.invalidateShadow()
        
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
        appDelegate?.selectedDevice = nil
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
        guard let window = self.window,
              let deviceFrameImage = self.deviceFrameImage else {
            NSLog("Skin pointer window or preview outlet is unavailable.")
            initialLocation = nil
            isResize = false
            return
        }

        var pointerLocation = NSEvent.mouseLocation
        pointerLocation.x -= window.frame.origin.x
        pointerLocation.y -= window.frame.origin.y
        initialLocation = pointerLocation

        isResize = (pointerLocation.x > deviceFrameImage.bounds.size.width - ResizeHandleSize)
            && (pointerLocation.y < ResizeHandleSize)
        
        appDelegate?.selectedDevice = self
        
    }
    
    override func mouseDragged(with theEvent: NSEvent) {
        guard let initialLocation = initialLocation,
              let window = self.window else {
            NSLog("Skin drag window or pointer origin is unavailable.")
            return
        }

        if !isResize {
            let curLocation = NSEvent.mouseLocation
            var newOrigin = NSPoint(
                x: curLocation.x - initialLocation.x,
                y: curLocation.y - initialLocation.y)

            if let screenFrame = (window.screen ?? NSScreen.main)?.frame,
               (newOrigin.y + window.frame.size.height) > (screenFrame.origin.y + screenFrame.size.height) {
                newOrigin.y = screenFrame.origin.y + (screenFrame.size.height - window.frame.size.height)
            }

            window.setFrameOrigin(newOrigin)
        }
        updateDeviceSettings()
        
    }
    override func viewDidEndLiveResize() {
        updateDeviceSettings()
    }
    
    //MARK: Device Settings
    func updateDeviceSettings() {
        // Update current device size/location settings based on its current movement
        guard let deviceSettings = self.deviceSettings,
              let window = self.window else {
            NSLog("Skin device settings window or state is unavailable.")
            return
        }
        if self.device.orientation == Device.DeviceOrientation.Portrait {
            deviceSettings.portraitRect = window.frame
        } else {
            deviceSettings.landscapeRect = window.frame
        }
        saveDeviceSettins()
        
    }
    func getDeviceSettings(device: AVCaptureDevice) {
        self.deviceSettings = appDelegate?.findDeviceSettings(device: device)
    }
    func saveDeviceSettins() {
        appDelegate?.saveDeviceSettings()
    }
    func setThisAsSelectedDevice() {
        appDelegate?.selectedDevice = self
    }
    
    
}
