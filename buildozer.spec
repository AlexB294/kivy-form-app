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
requirements = python3,kivy,pyjnius,reportlab

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/data/icon.png

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_api = 21
android.build_tools_version = 33.0.2
# (list) Permissions your app needs
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target API level
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API
android.ndk_api = 21

# (str) Architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (str) Application entry point
entrypoint = main.py

# (str) Package format (aab or apk)
package.format = apk


[buildozer]

# (int) Log level (0 = quiet, 1 = normal, 2 = verbose, 3 = debug)
log_level = 2

# (bool) Warn if root is detected
warn_on_root = 1
