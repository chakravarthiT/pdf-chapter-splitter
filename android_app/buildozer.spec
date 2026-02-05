[app]
# Title of your application
title = PDF Splitter

# Package name
package.name = pdfsplitter

# Package domain (needed for android/ios packaging)
package.domain = org.pdfsplitter

# Source code directory
source.dir = .

# Source files to include
source.include_exts = py,png,jpg,kv,atlas,json

# Application version
version = 1.0.0

# Application requirements
requirements = python3,kivy,pymupdf

# Supported orientations
orientation = portrait

# Android specific
fullscreen = 0

# Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android API level
android.api = 29
android.minapi = 21
android.ndk = 25.1.8937393

# Architecture
android.archs = arm64-v8a

# Build features
android.features = android.hardware.touchscreen

[buildozer]
log_level = 2
warn_on_root = 1
