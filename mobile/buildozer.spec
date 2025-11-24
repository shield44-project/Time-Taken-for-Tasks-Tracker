[app]
title = Task Time Tracker
package.name = tasktimetracker
package.domain = org.industrial

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy,kivymd,requests

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 31
android.minapi = 21
android.ndk = 23b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
