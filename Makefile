.DEFAULT_GOAL := check
.PHONY: build check lint root-test test verify

override SHELL := /bin/sh
override .SHELLFLAGS := -c
override PYTHONDONTWRITEBYTECODE := 1
export PYTHONDONTWRITEBYTECODE
ifneq ($(strip $(MAKEFILES)),)
$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)
endif
override MAKEFILES :=
ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; path=$$(printf '%s' "$$path" | /usr/bin/sed 's/^ //'); [ -f "$$path" ] || exit 1; directory=$$(/usr/bin/dirname -- "$$path"); CDPATH= cd -- "$$directory" && /bin/pwd -P)
export ROOT
ifeq ($(strip $(ROOT)),)
$(error repository Makefile path could not be resolved)
endif
override PYTHON := $(ROOT)/scripts/run-python.sh
override XCODEBUILD := $(ROOT)/scripts/run-xcodebuild.sh
export PYTHON XCODEBUILD

lint:
	/bin/sh -n "$$ROOT/build.sh"
	"$$PYTHON" "$$ROOT/scripts/check-screenshare-source.py" --mode project

test:
	"$$PYTHON" "$$ROOT/scripts/check-screenshare-source.py" --mode behavior
	"$$PYTHON" "$$ROOT/scripts/test-screenshare-contracts.py"

build: lint
	@if [ -x /usr/bin/xcodebuild ]; then \
		cd "$$ROOT" && "$$XCODEBUILD" -project Screenshare.xcodeproj -scheme Screenshare -destination 'platform=macOS' CODE_SIGNING_ALLOWED=NO build; \
	else \
		echo "xcodebuild not found; static project checks completed"; \
	fi

root-test:
	/bin/sh "$$ROOT/scripts/test-makefile-root.sh"

verify: root-test lint test build

check: verify
