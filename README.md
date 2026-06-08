# ScreenShare
ScreenShare is a great demo tool that allows you to mirror your iOS devices to your screen.

### This is great for:
  - Creating extremely clean demos.
  - When you have a demo and want it to look amazing!
  - When you don't have a Wi-Fi network available, or your customer won't let you on theirs.
  - Doing a demo of your app's offline capabilities
  - Live demos in front of thousands of people.

![ScreenShare streaming](https://garethjones-apps.s3.amazonaws.com/apps/screenshare/screenshot.png)

## Running the Project

ScreenShare is a macOS Xcode project. The app runs on your Mac and displays a connected iPhone or iPad as a capture device.

### Prerequisites

- A Mac with Xcode installed.
- An iPhone or iPad connected to the Mac over USB and unlocked.
- An Xcode toolchain that can open or migrate a Swift 2.3 project.

The project was last configured for macOS 10.9 and Swift 2.3. Modern versions of Xcode may prompt you to migrate the Swift source before the app can build.

### Run from Xcode

1. Clone or download the repository.
2. Open `Screenshare.xcodeproj` in Xcode.
3. Select the `Screenshare` scheme.
4. Choose `My Mac` as the run destination.
5. Connect and unlock the iOS device you want to mirror.
6. Press Run.

When the app launches, it scans for connected iOS capture devices. If a device is detected, ScreenShare opens a window using the matching phone or tablet frame.

### Command-Line Build Check

If your Xcode installation supports this project, you can also run the existing test wrapper:

```sh
./build.sh
```

That script runs:

```sh
xcodebuild -project Screenshare.xcodeproj -scheme "Screenshare" -destination "platform=OS X" test
```

### Troubleshooting

- If Xcode cannot compile the project, check whether it is asking to migrate the Swift 2.3 sources.
- If Xcode reports a signing error, select the `Screenshare` target and choose a valid macOS development team or local signing identity.
- If the Run button is disabled, make sure the `Screenshare` scheme and `My Mac` destination are selected.
- If no device window appears, reconnect the iPhone or iPad, unlock it, and confirm the device is visible to macOS before running the app again.
