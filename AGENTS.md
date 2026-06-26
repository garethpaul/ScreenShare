# AGENTS.md

## Repository purpose

`garethpaul/ScreenShare` is an Apple platform application or Swift sample. ScreenShare is a great demo tool that allows you to mirror your iOS devices to your screen to create the perfect demo.

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `Screenshare.xcodeproj` - Xcode project
- `plans` - repository source or sample assets
- `ScreenShare` - repository source or sample assets
- `ScreenShareScreenshots` - repository source or sample assets
- `ScreenShareTests` - repository source or sample assets
- `ScreenshareUITests` - repository source or sample assets

## Development commands

- Install dependencies: no repository-specific install command is documented.
- Full baseline: `make check`
- Combined verification: `make verify`
- Lint/static checks: `make lint`
- Tests: `make test`
- Build: `make build`
- Local Apple development: `open Screenshare.xcodeproj`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: Swift (9), shell (1).
- Preserve legacy Xcode project settings and signing assumptions unless the change is explicitly about modernization.

## Testing guidance

- Test-related files detected: `Screenshare.xcodeproj/xcshareddata/xcschemes/ScreenshareUITests.xcscheme`, `Screenshare.xcodeproj/xcshareddata/xcschemes/ScreenshareUnitTests.xcscheme`, `ScreenShareTests/ScreenShareTests.swift`, `ScreenshareUITests/ScreenshareUITests.swift`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.
- This looks like an Apple platform project or sample. Xcode, Swift, CocoaPods, and deployment target versions may need to match the original project era.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-screenshare-baseline.md` for the canonical mirroring privacy and runtime-error baseline.
- Skin capture device switch rollback preserves the prior working input when a
  replacement cannot be constructed or admitted.
- Initial Skin sessions reject unattached capture devices before window and
  view attachment.
- Document aspect updates run once after session start and then only for the
  active input port's format-change notifications; device switches replace the
  observer and window teardown removes it.
- See `docs/plans/2026-06-08-device-archive-decoding.md` for the local device-settings archive guard.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
