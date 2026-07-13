[app]
title = Sono Profundo
package.name = sonoprofundo
package.domain = org.feliphealex
source.dir = .
source.include_exts = py,png,jpg,jpeg,webp,wav,mp3,ogg,json,txt
source.exclude_dirs = __pycache__,.git,.venv,venv
version = 1.0.0
requirements = python3,pygame
orientation = portrait
fullscreen = 1
android.permissions = VIBRATE
android.api = 35
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
