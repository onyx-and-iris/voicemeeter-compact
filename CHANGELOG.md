# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

-   [ ] Add support for forest theme (if rbende adds it to pypi)

## [1.7.0] - 2023-06-26

### Changed

-   There are changes to how some parameters must be set in user toml configs.
    -   use `comp.knob` to set a strip comp slider.
    -   use `gate.knob` to set a strip gate slider.
    -   use `eq.on` to set a bus eq.on button.
    -   use `eq.ab` to set a bus eq.ab button.

Check example configs.

-   `configs` directory may now be located in one of the following locations:
    -   \<current working directory>/configs/
    -   \<user home directory>/.configs/vm-compact/configs/
    -   \<user home directory>/Documents/Voicemeeter/configs/

-   dependency updates:
    -   sv_ttk updated to v2.4.5.
    -   voicemeeter-api updated to v2.0.1.
    -   vban-cmd updated to v2.0.0.

### Fixed

-   A number of changes that reduce the amount of api calls being made.

## [1.6.0] - 2022-09-29

### Added

-   Logging module used in place of print statements across the interface.

## [1.5.1] - 2022-09-16

### Added

-   1.5.1 binary to releases

### Changed

-   sv_ttk updated to v2.0.
-   event toggles used to pause updates when dragging sliders.

## [1.4.2] - 2022-09-03

### Added

-   tomli/tomllib compatibility layer to support python 3.10
-   1.4.2 binary to releases

## [1.3.0] - 2022-07-14

### Added

-   GUI now packaged with poetry and available on Pypi.
-   Bus modes may now be set in user config (see example configs)

### Changed

-   Reload user configs from memory into app if switching kind between connections.
-   Levels rework, now using is_updated in callback.
-   Some logic regarding callbacks reworked, timings reduced for updates.
-   Directory structure changed, no more profiles/. All configs should go into configs/
-   Configs section in readme updated to reflect changes.
-   Installation instructions updated for python 311 and pypi.

### Fixed

-   Fixed bug causing bus level to hang when toggling composite mode
-   Fixed bug with submix frames failing to redraw when selected from menu.
-   Version fastforward in pyproject to match changelog.

### Removed

-   Requirement to install Git.

## [1.2.6] - 2022-05-16

### Added

-   Added a gain label to each channel labelframe.

### Changed

-   Changes to menus, extends, themes and submixes merged into layout.
-   A number of changes to code organisation:
    -   builders module added, widget creation delegated to builder classes.
    -   app now subscribes to lower level interfaces as an observer for updates.
    -   Min width of app reduced to 275. Should only effect if less than 3 combined strips/buses.
-   VBAN Connections named by 'streamname' in VBAN menu, ie.. 'workpc', 'gamingpc' etc..
-   GUI Lock menu commands 'Lock', 'Unlock' are now checkbuttons.

### Fixed

-   Fixed bug setting default submix
-   Fixed bug with gainlayer sync failing to fetch strip label.

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
