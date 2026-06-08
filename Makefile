.PHONY: lint test build verify

PYTHON ?= python3
XCODEBUILD ?= xcodebuild

lint:
	sh -n build.sh
	$(PYTHON) scripts/check-screenshare-source.py --mode project

test:
	$(PYTHON) scripts/check-screenshare-source.py --mode behavior

build: lint
	@if command -v "$(XCODEBUILD)" >/dev/null 2>&1; then \
		"$(XCODEBUILD)" -project Screenshare.xcodeproj -scheme Screenshare -destination 'platform=OS X' CODE_SIGNING_ALLOWED=NO build; \
	else \
		echo "xcodebuild not found; static project checks completed"; \
	fi

verify: lint test build
