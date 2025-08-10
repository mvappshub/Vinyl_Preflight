# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.5.0] - 2025-01-08

### Added
- **Consolidated Mode Support** - Automatic detection and validation of consolidated side projects
- **Advanced WAV File Matching** - Intelligent algorithms for pairing WAV files with PDF sides
- **Detailed Logging System** - Complete audit trail of all operations saved to files
- **Robust Error Handling** - Graceful handling of corrupted PDF and WAV files
- **Comprehensive Test Suite** - Pytest tests covering core functionality
- **Safe Rounding Function** - Consistent decimal handling throughout the application
- **Empty Directory Validation** - Proper handling of empty projects and missing files
- **Archive Size Limits** - Protection against oversized archive files
- **Timeout Controls** - Configurable timeouts for extraction operations

### Changed
- **Improved PDF Extraction** - Better error handling for corrupted PDF files
- **Enhanced WAV Processing** - More reliable duration calculation with error recovery
- **Optimized LLM Communication** - Better request/response logging and error handling
- **Cleaner Code Structure** - Removed redundant comments and improved readability
- **Updated Documentation** - Comprehensive README and contributing guidelines

### Fixed
- **Side C Detection** - Fixed regex patterns to properly detect Side C in consolidated mode
- **WAV File Pairing** - Resolved issues with matching WAV files to PDF sides
- **Memory Management** - Better cleanup of temporary files and resources
- **Cross-platform Compatibility** - Improved path handling for Windows/Linux/macOS

### Security
- **Input Validation** - Enhanced validation of file inputs and API responses
- **Safe File Operations** - Protected file operations with proper error handling

## [2.0.0] - 2024-12-XX

### Added
- **GUI Application** - User-friendly graphical interface
- **Automatic Mode Detection** - Smart detection of project types
- **LLM-powered PDF Extraction** - AI-based text extraction from PDF files
- **Progress Tracking** - Real-time progress updates during processing
- **Archive Support** - Support for ZIP and RAR archives

### Changed
- **Unified Application** - Combined separate tools into single application
- **Improved User Experience** - Streamlined workflow and better feedback

## [1.0.0] - 2024-11-XX

### Added
- **Initial Release** - Basic functionality for vinyl preflight validation
- **WAV Data Extractor** - Extract duration information from WAV files
- **PDF Data Extractor** - Extract track information from PDF files
- **Preflight Validator** - Compare and validate track durations
- **JSON Output** - Structured data output for further processing

### Features
- Basic PDF text extraction
- WAV file duration analysis
- Simple validation reporting
- Command-line interface

---

## Legend

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities
