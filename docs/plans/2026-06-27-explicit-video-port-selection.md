# Select capture video ports explicitly

Status: Completed

## Problem

`Document` and `Skin` observed and measured `input.ports.first`. Apple documents
that one capture input can provide multiple media streams, each represented by
its own port. A muxed device can therefore expose audio and video ports without
promising that the video stream is first.

References:

- <https://developer.apple.com/documentation/avfoundation/avcaptureinput>
- <https://developer.apple.com/documentation/avfoundation/avcaptureinput/port>

## Fix

- Add one `AVCaptureDeviceInput.videoPort` selector filtered by `.video`.
- Use that port for Document and Skin format notifications and dimensions.
- Fail closed to the existing unavailable-dimensions behavior when no video
  stream exists.

## Test First

The focused behavior gate failed because no filtered video-port selector
existed and both capture paths still depended on `ports.first`.

## Verification

- Run `make test` for the focused source contract and hostile mutation.
- Run `make check` from the checkout and an external working directory.
- Run Python compilation, shell syntax checks, and `git diff --check`.
- Require hosted unsigned macOS compilation and CodeQL on the exact PR head.
