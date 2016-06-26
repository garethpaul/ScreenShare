#!/bin/sh

set -eu

function ci_lib() {
    xcodebuild -project Screenshare.xcodeproj \
               -scheme "Screenshare" \
               -destination "platform=OS X" \
               test
}
ci_lib
