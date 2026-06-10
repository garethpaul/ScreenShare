//
//  Document.swift
//  PresentIO
//
//  Created by Gonçalo Borrêga on 27/02/15.
//  Copyright (c) 2015 Borrega. All rights reserved.
//

import Cocoa
import AVFoundation
import AVKit



class Document: NSDocument {
    
    @IBOutlet weak var cmbSource: NSPopUpButton!
    @IBOutlet weak var previewView: NSView!
    @IBOutlet weak var lblResolution: NSTextField!
    
    var session : AVCaptureSession = AVCaptureSession()
    var input   : AVCaptureDeviceInput?
    var aspectXonY : CGFloat = 1024/768
    var videoDimensions = CMVideoDimensions(width: 1024,height: 768)
    
    dynamic var devices : [AVCaptureDevice] = []
    
    let notifications = NotificationManager()
    
    override init() {
        super.init()
        
        self.loadObservers()
        
        self.refreshDevices()
        
        // Select devices if any exist
        let videoDevice = AVCaptureDevice.default(for: .muxed)
        if( videoDevice != nil ) {
            self.selectedDevice = videoDevice
        } else {
            self.selectedDevice = AVCaptureDevice.default(for: .video)
        }
        
    }
    

    override func windowControllerDidLoadNib(_ windowController: NSWindowController) {
        super.windowControllerDidLoadNib(windowController)
        // Add any code here that needs to be executed once the windowController has loaded the document's window.
        
        self.windowForSheet?.isMovableByWindowBackground = true
        
        
        // Custom view set to render concurrently in order to have its own layer
        guard let previewView = self.previewView else {
            NSLog("Document preview view outlet is missing.")
            return
        }
        guard let previewViewLayer = previewView.layer else {
            NSLog("Document preview view is missing a backing layer.")
            return
        }
        previewViewLayer.backgroundColor = CGColor.black
        
        let newPreviewLayer = AVCaptureVideoPreviewLayer(session: self.session)
        newPreviewLayer.frame = previewViewLayer.bounds
        newPreviewLayer.autoresizingMask = [.layerWidthSizable, .layerHeightSizable]
        newPreviewLayer.videoGravity = .resizeAspect
        
        previewViewLayer.addSublayer(newPreviewLayer)
        
        self.session.startRunning()

        // Update Aspect will run recurrently to account for changes in orientation we cannot catch
        // TODO: Optimize to only do this for ios devices and listening for changes to the formatDescription of the video AVCaptureInputPort associated with the device.
        Timer.scheduledTimer(timeInterval: 1, target: self, selector: #selector(updateAspect), userInfo: nil, repeats: true)
        
    }
    
    
    
    func update() {
        self.updateAspect()
    }
    
    func refreshDevices() {
        
        self.devices = AVCaptureDevice.devices(for: .video)
            + AVCaptureDevice.devices(for: .muxed)
        
        self.session.beginConfiguration()
        
        if let selectedDevice = self.selectedDevice, !self.devices.contains(selectedDevice) {
            self.selectedDevice = nil
        }
        
        self.session.commitConfiguration()
        
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
                } catch let error as NSError {
                    self.displayError(error: error)
                }
                
            }
            
            self.session.commitConfiguration()
            
            self.updateAspect()
        }
    }
    
    @objc func updateAspect() {
        
        guard let port = self.input?.ports.first,
            let window = self.windowForSheet,
            let description = port.formatDescription else {
                resetResolutionStatus()
                return
        }

        let dimensions = CMVideoFormatDescriptionGetDimensions(description)
        if( dimensions.width != 0 && dimensions.height != 0
            && (dimensions.width != self.videoDimensions.width || dimensions.height != self.videoDimensions.height) ) {

                self.videoDimensions = dimensions
                self.aspectXonY = CGFloat(dimensions.width) / CGFloat(dimensions.height)

                let windowFrame = window.frame
                let newFrame = CGRectMake(windowFrame.origin.x, windowFrame.origin.y, windowFrame.size.width, windowFrame.size.width / self.aspectXonY)

                //window!.setFrame(newFrame, display: true, animate: true)
                //window!.aspectRatio = NSSize(width: CGFloat(dimensions.width), height: CGFloat(dimensions.height))

                lblResolution?.stringValue = "w:\(dimensions.width), h:\(dimensions.height)"

        }

    }

    private func resetResolutionStatus() {
        self.windowForSheet?.resizeIncrements = CGSize(width:1.0,height:1.0)
        lblResolution?.stringValue = "Calculating resolution"

    }
    
    func displayError(error: NSError?) {
        guard let error = error else {
            NSLog("Capture device input failed without NSError metadata")
            return
        }
        DispatchQueue.main.async {
            self.presentError(error)
        }
    }
    
    func loadObservers() {
        
        notifications.registerObserver(AVCaptureSession.runtimeErrorNotification, forObject: session, dispatchAsyncToMainQueue: true, block: {note in
            if let err = note.userInfo?[AVCaptureSessionErrorKey] as? NSError {
                self.presentError(err)
            } else {
                NSLog("Capture session runtime error notification missing NSError metadata")
            }
        })
        
        
        notifications.registerObserver(AVCaptureDevice.wasConnectedNotification, forObject: nil, block: {note in
            self.refreshDevices()
        })
        notifications.registerObserver(AVCaptureDevice.wasDisconnectedNotification, forObject: nil, block: {note in
            self.refreshDevices()
        })
        
        
    }
    
    func windowWillClose(_ notification: Notification) {
        self.session.stopRunning()
        self.notifications.deregisterAll()
    }
    
    //    override class func autosavesInPlace() -> Bool {
    //        return true
    //    }
    
    override var windowNibName: String? {
        // Returns the nib file name of the document
        // If you need to use a subclass of NSWindowController or if your document supports multiple NSWindowControllers, you should remove this property and override -makeWindowControllers instead.
        return "Document"
    }
    
    override func dataOfType(typeName: String, error outError: NSErrorPointer) -> NSData? {
        // Insert code here to write your document to data of the specified type. If outError != nil, ensure that you create and set an appropriate error when returning nil.
        // You can also choose to override fileWrapperOfType:error:, writeToURL:ofType:error:, or writeToURL:ofType:forSaveOperation:originalContentsURL:error: instead.
        outError.memory = NSError(domain: NSOSStatusErrorDomain, code: unimpErr, userInfo: nil)
        return nil
    }
    
    override func readFromData(data: NSData, ofType typeName: String, error outError: NSErrorPointer) -> Bool {
        // Insert code here to read your document from the given data of the specified type. If outError != nil, ensure that you create and set an appropriate error when returning false.
        // You can also choose to override readFromFileWrapper:ofType:error: or readFromURL:ofType:error: instead.
        // If you override either of these, you should also override -isEntireFileLoaded to return NO if the contents are lazily loaded.
        outError.memory = NSError(domain: NSOSStatusErrorDomain, code: unimpErr, userInfo: nil)
        return false
    }
    
    
    
}
