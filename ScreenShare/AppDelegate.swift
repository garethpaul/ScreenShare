//
//  AppDelegate.swift
//  Screenshare
//

import Cocoa

import AVFoundation
import AVKit

@NSApplicationMain
class AppDelegate: NSObject, NSApplicationDelegate, NSMenuDelegate {
    
    @IBOutlet var window: NSWindow!
    
    @IBOutlet weak var progressIndicator: NSProgressIndicator!
    
    var session : AVCaptureSession = AVCaptureSession()

    let notifications = NotificationManager()
    var devices : [AVCaptureDevice] = []
    var deviceSessions : [AVCaptureDevice: Skin] = [:]
    
    var deviceSettings : [Device] = []
    var deviceSettingsLoaded = false
    
    var selectedDevice : Skin?

    func applicationDidFinishLaunching(aNotification: NSNotification) {

        self.selectedDevice = nil
        
        self.progressIndicator.startAnimation(self)
        
        // Opt-in for getting visibility on connected screen capture devices
        DeviceUtils.registerForScreenCaptureDevices()
        
        self.loadObservers()
        self.refreshDevices()
    }
    
    func loadDeviceSettings() {
        let loaded = NSKeyedUnarchiver.unarchiveObject(withFile: Device.ArchivePath) as? [Device]
        if loaded != nil {
            self.deviceSettings = loaded!
        } else {
            self.deviceSettings = []
        }
        deviceSettingsLoaded = true
    }
    
    
    func saveDeviceSettings() {
        let isSuccessfulSave = NSKeyedArchiver.archiveRootObject(self.deviceSettings, toFile: Device.ArchivePath)
        if !isSuccessfulSave {
            NSLog("Failed to save device settings.")
        }
        deviceSettingsLoaded = true
    }
    func findDeviceSettings(device: AVCaptureDevice) -> Device {
        if (!deviceSettingsLoaded ) {
            loadDeviceSettings()
        }
        for d in deviceSettings {
            if d.uid == device.uniqueID {
                return d
            }
        }
        
        let newDevice = Device(fromDevice: device)
        self.deviceSettings.append(newDevice)
        return newDevice
    }
    

    func applicationWillTerminate(_ notification: Notification) {
        
        self.notifications.deregisterAll()
    }

    func loadObservers() {
        
        notifications.registerObserver(AVCaptureSession.runtimeErrorNotification, forObject: session, dispatchAsyncToMainQueue: true, block: {note in
            if let err = note.userInfo?[AVCaptureSessionErrorKey] as? NSError {
                //self.window.presentError( err )
                NSLog(err.description)
            } else {
                NSLog("Capture session runtime error notification missing NSError metadata")
            }
        })
        
        
        notifications.registerObserver(AVCaptureSession.didStartRunningNotification, forObject: session, block: {note in
            self.refreshDevices()
        })

                
        notifications.registerObserver(AVCaptureDevice.wasConnectedNotification, forObject: nil, dispatchAsyncToMainQueue: true, block: {note in
            self.refreshDevices()
        })
        notifications.registerObserver(AVCaptureDevice.wasDisconnectedNotification, forObject: nil, dispatchAsyncToMainQueue: true, block: {note in
            self.refreshDevices()
        })
        
        
    }
    
    func startNewSession(device:AVCaptureDevice) -> Skin {
        
        let size = DeviceUtils(deviceType: .Phone).skinSize
        let screenFrame = NSScreen.main?.frame ?? NSMakeRect(0, 0, size.width, size.height)
        let frame = DeviceUtils.getCenteredRect(windowSize: size, screenFrame: screenFrame)
        
        let window = NSWindow(contentRect: frame,
            styleMask: .borderless,
            backing: .buffered, defer: false)
        
        window.isMovableByWindowBackground = true
        let frameView = NSMakeRect(0, 0,size.width, size.height)
        
        let skin = Skin(frame: frameView)
        skin.initWithDevice(device: device)
        skin.ownerWindow = window
        guard let contentView = window.contentView else {
            NSLog("Device session window content view is missing.")
            return skin
        }
        contentView.addSubview(skin)
        
        skin.registerNotifications()
        skin.updateAspect()
        
        window.backgroundColor = NSColor.clear
        window.isOpaque = false
        
        window.makeKeyAndOrderFront(NSApp)

        return skin
    }

    func refreshDevices() {
        
        self.devices = AVCaptureDevice.devices(for: .muxed)
            + AVCaptureDevice.devices(for: .video)
        
        // A running device was disconnected?
        for(device, deviceView) in deviceSessions {
            if ( !self.devices.contains(device) ) {
                deviceView.endSession()
                deviceView.window?.close()
                self.deviceSessions[device] = nil
            }
        }
        
        
        // A new device connected?
        for device in self.devices {
            if device.modelID == "iOS Device" {
                if (!self.deviceSessions.keys.contains(device)) {
        
                    // support only one session for now, until multiple devices videos start working
                    if(self.deviceSessions.count > 0) {
                        let alert = NSAlert()
                        alert.messageText = "Only one device supported"
                        alert.addButton(withTitle: "OK")
                        alert.informativeText = "You can only display one device at a time. Please disconnect your other device."
                        alert.runModal()

                        break;
                    } else {
                        self.deviceSessions[device] = startNewSession(device: device)
                    }
            }
        }
        }

        guard let window = self.window else {
            NSLog("Main device list window outlet is missing.")
            return
        }

        if self.deviceSessions.count > 0 {
           window.close()
        } else {
           window.makeKeyAndOrderFront(NSApp)
        }

        
    }
}
