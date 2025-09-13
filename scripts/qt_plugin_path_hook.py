"""
PyInstaller runtime hook to set Qt plugin paths for bundled applications.
This ensures Qt can find multimedia plugins in the bundled app.
"""

import os
import sys

# Set Qt plugin path for bundled applications
if hasattr(sys, '_MEIPASS'):
    qt_plugin_path = os.path.join(sys._MEIPASS, 'PyQt5', 'Qt5', 'plugins')
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_plugin_path
    os.environ['QT_PLUGIN_PATH'] = qt_plugin_path

    # Also set the library path to include bundled Qt libraries
    qt_lib_path = os.path.join(sys._MEIPASS, 'PyQt5', 'Qt5')
    if 'DYLD_LIBRARY_PATH' in os.environ:
        os.environ['DYLD_LIBRARY_PATH'] = qt_lib_path + ':' + os.environ['DYLD_LIBRARY_PATH']
    else:
        os.environ['DYLD_LIBRARY_PATH'] = qt_lib_path

    # Debug output (remove in production)
    print(f"Qt plugin path set to: {qt_plugin_path}")
    print(f"Qt library path set to: {qt_lib_path}")