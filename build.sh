#!/bin/sh

set -eu

ci_lib() {
    xcodebuild -project Screenshare.xcodeproj \
               -scheme "Screenshare" \
               -destination "platform=macOS" \
               CODE_SIGNING_ALLOWED=NO \
               test
}
ci_lib "$@"
