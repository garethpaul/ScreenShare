//
//  NotificationManager.swift
//

import Foundation

struct NotificationGroup {
    let entries: [Notification.Name]
    
    init(_ newEntries: Notification.Name...) {
        entries = newEntries
    }
    
}

class NotificationManager {
    private var observerTokens: [NSObjectProtocol] = []
    
    deinit {
        deregisterAll()
    }
    
    func deregisterAll() {
        for token in observerTokens {
            NotificationCenter.default.removeObserver(token)
        }
        
        observerTokens = []
    }
    
    func registerObserver(_ name: Notification.Name, block: @escaping (Notification) -> Void) {
        let newToken = NotificationCenter.default.addObserver(forName: name, object: nil, queue: nil, using: { note in
            block(note)
        })
        
        observerTokens.append(newToken)
    }
    func registerObserver(_ name: Notification.Name, dispatchAsyncToMainQueue: Bool, block: @escaping (Notification) -> Void) {
        let newToken = NotificationCenter.default.addObserver(forName: name, object: nil, queue: nil, using: { note in
            if dispatchAsyncToMainQueue {
                DispatchQueue.main.async {
                    block(note)
                }
            } else {
                block(note)
            }
        })
        
        observerTokens.append(newToken)
    }
    
    func registerObserver(_ name: Notification.Name, forObject object: Any?, block: @escaping (Notification) -> Void) {
        self.registerObserver(name, forObject: object, dispatchAsyncToMainQueue: false, block: block)
    }
    func registerObserver(_ name: Notification.Name, forObject object: Any?, dispatchAsyncToMainQueue: Bool, block: @escaping (Notification) -> Void) {
        let newToken = NotificationCenter.default.addObserver(forName: name, object: object, queue: nil, using: { note in
            if dispatchAsyncToMainQueue {
                DispatchQueue.main.async {
                    block(note)
                }
            } else {
                block(note)
            }
        })
        
        observerTokens.append(newToken)
    }
    
    
    
    func registerGroupObserver(_ group: NotificationGroup, block: @escaping (Notification) -> Void) {
        for name in group.entries {
            self.registerObserver(name, block: block)
        }
    }
}
