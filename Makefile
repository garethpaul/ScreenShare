.PHONY: build check lint test verify

PYTHON ?= python3
XCODEBUILD ?= xcodebuild
override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

lint:
	sh -n "$(ROOT)/build.sh"
	$(PYTHON) "$(ROOT)/scripts/check-screenshare-source.py" --mode project

test:
	$(PYTHON) "$(ROOT)/scripts/check-screenshare-source.py" --mode behavior

build: lint
	@if command -v "$(XCODEBUILD)" >/dev/null 2>&1; then \
		"$(XCODEBUILD)" -project "$(ROOT)/Screenshare.xcodeproj" -scheme Screenshare -destination 'platform=macOS' CODE_SIGNING_ALLOWED=NO build; \
	else \
		echo "xcodebuild not found; static project checks completed"; \
	fi

verify: lint test build

check: verify
