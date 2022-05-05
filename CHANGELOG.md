# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

-   [ ] Allow setting a bus mode from config
-   [x] Fixed bug with gainlayer sync fetching strip label.

## [1.1.0] - 2022-05-05

### Added

-   Ability to set a profile to load on startup

### Changed

-   Add more substantial example profile config files.
-   Minor version bump

### Fixed

-   Fix a bug where minimize->restore is effecting the window size. Now minwidth 400, not ideal
    but acceptable compromise.

## [1.0.0] - 2022-04-27

### Added

-   Example of valid vban.toml to readme

### Changed

-   Sun-Valley theme added as module. Added to pysetup. Img files removed from repo.
-   Major version bump since this is not backwards compatible.

### Fixed

-   Fix issue with bus modes syncing. Added a bus mode cache to App class.

## [0.0.1] - 2022-04-22

### Added

-   App initial commit.
-   Strip/Bus frames implemented
    -   A labelframe for each channel containing a progressbar and slider.
    -   A config frame for setting inputs/outputs, comp, gate, limit, mono, eq, bus modes.
-   Navigation frame implemented
    -   Extending horizontally/vertically implemented.
-   Submixes frames implemented
    -   Each submix frame offers a view of all input devices on a single bus.
    -   Possible to select any one of all 8 buses.
    -   ON button implemented, effectively a mute toggle.
-   Menus implemented.
    -   Voicemeeter action type functions for the main GUI.
    -   Profiles load any profile defined in profiles/ directory for a kind. Reset to defaults.
    -   VBAN Connect connect to any number of connections defined in vban.toml
    -   Extends toggle direction app extends in.
    -   Submixes select the bus the Submix frame will represent. Selecting a new bus will redraw the submix frame if its gridded.
    -   Themes toggle light/dark sunvalley theme.
    -   Help links to sites.

### Changed

-   Only create banner frame if kind is Potato.

### Fixed

-   Fix bug where submixes menu remained disabled if kind changes when switching between vmr and vban interface. (ie banana remote to potato local)
