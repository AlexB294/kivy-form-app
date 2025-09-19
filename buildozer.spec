[app]

# (str) Title of your application
title = Formular Montaj

# (str) Package name
package.name = formapp

# (str) Package domain (reverse DNS style, can be anything unique)
package.domain = org.example

# (str) Source code directory
source.dir = .

# (list) Files to include
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 1.0.0

# (str) Supported orientations (portrait, landscape, sensor)
orientation = portrait

# (list) Application requirements
# All your Python libraries must be listed here.
requirements = python3,kivy,requests,msal,reportlab,pyjnius,setuptools,wheel

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# --- ANDROID CONFIGURATION ---
# API / SDK / NDK versions
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.build_tools_version = 33.0.2

# (list) Architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (list) Permissions your app needs
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# (str) Application entry point
entrypoint = mobile_app.py

# (str) Package format (aab or apk)
package.format = apk

# Force SDK/NDK paths
android.sdk_path = /opt/android-sdk
android.ndk_path = /opt/android-ndk

[buildozer]

# (int) Log level (0-2)
log_level = 2
