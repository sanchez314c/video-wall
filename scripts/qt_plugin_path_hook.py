"""
PyInstaller runtime hook to set Qt plugin paths and GStreamer paths
for bundled applications on Linux, macOS, and Windows.
"""

import os
import sys
import platform

if hasattr(sys, '_MEIPASS'):
    bundle_dir = sys._MEIPASS
    system = platform.system()

    # Set Qt plugin paths
    qt_plugin_path = os.path.join(bundle_dir, 'PyQt5', 'Qt5', 'plugins')
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_plugin_path
    os.environ['QT_PLUGIN_PATH'] = qt_plugin_path

    # Set Qt library path
    qt_lib_path = os.path.join(bundle_dir, 'PyQt5', 'Qt5', 'lib')
    if system == 'Darwin':
        existing = os.environ.get('DYLD_LIBRARY_PATH', '')
        os.environ['DYLD_LIBRARY_PATH'] = qt_lib_path + (':' + existing if existing else '')
    elif system == 'Linux':
        existing = os.environ.get('LD_LIBRARY_PATH', '')
        os.environ['LD_LIBRARY_PATH'] = qt_lib_path + (':' + existing if existing else '')

    # GStreamer plugin paths (critical for video playback on Linux)
    if system == 'Linux':
        # Check for bundled GStreamer plugins first
        bundled_gst = os.path.join(bundle_dir, 'gstreamer-1.0')
        system_gst_paths = [
            '/usr/lib/x86_64-linux-gnu/gstreamer-1.0',
            '/usr/lib/gstreamer-1.0',
            '/usr/lib64/gstreamer-1.0',
        ]

        gst_paths = []
        if os.path.isdir(bundled_gst):
            gst_paths.append(bundled_gst)

        # Always include system GStreamer plugins as fallback
        for p in system_gst_paths:
            if os.path.isdir(p):
                gst_paths.append(p)

        if gst_paths:
            os.environ['GST_PLUGIN_SYSTEM_PATH'] = ':'.join(gst_paths)
            os.environ['GST_PLUGIN_PATH'] = ':'.join(gst_paths)

        # Point GStreamer scanner to system if not bundled
        gst_scanner_paths = [
            '/usr/lib/x86_64-linux-gnu/gstreamer1.0/gstreamer-1.0/gst-plugin-scanner',
            '/usr/libexec/gstreamer-1.0/gst-plugin-scanner',
        ]
        for scanner in gst_scanner_paths:
            if os.path.isfile(scanner):
                os.environ['GST_PLUGIN_SCANNER'] = scanner
                break

    print(f"[VideoWall] Bundle dir: {bundle_dir}")
    print(f"[VideoWall] Qt plugins: {qt_plugin_path}")
    if system == 'Linux':
        print(f"[VideoWall] GST_PLUGIN_SYSTEM_PATH: {os.environ.get('GST_PLUGIN_SYSTEM_PATH', 'NOT SET')}")
