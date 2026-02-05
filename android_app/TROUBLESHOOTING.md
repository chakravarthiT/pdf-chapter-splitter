# PDF Splitter - Troubleshooting Guide

## Building Issues

### 1. "buildozer: command not found"

**Cause:** buildozer not installed or not in PATH

**Solution:**
```bash
# Install buildozer (must install Cython first)
pip install cython
pip install buildozer
```

### 2. "No Java SDK found"

**Cause:** Java not installed or JAVA_HOME not set

**Solution - macOS:**
```bash
# Find Java installation
/usr/libexec/java_home

# Set JAVA_HOME
export JAVA_HOME=$(/usr/libexec/java_home -v 17)

# Verify
java -version
```

**Solution - Linux:**
```bash
# Install Java 17
sudo apt-get install openjdk-17-jdk

# Set JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Verify
java -version
```

### 3. "You must install Android SDK components"

**Cause:** First build requires downloading Android SDK/NDK (~5GB)

**Solution:**
```bash
# Ensure 20GB+ free disk space
df -h

# Delete old build cache (if stuck)
rm -rf .buildozer

# Retry build
buildozer android debug
```

**Note:** First build takes 15-30 minutes - be patient!

### 4. "distutils not found" (Python 3.13)

**Cause:** Python 3.13 removed distutils

**Solution:**
```bash
# Use Python 3.11 for buildozer
python3.11 -m pip install buildozer cython

# Use Python 3.11 specifically
python3.11 -m buildozer android debug
```

### 5. "Cython version mismatch"

**Cause:** Incompatible Cython version

**Solution:**
```bash
# Install compatible Cython
pip uninstall cython
pip install cython==3.2.4

# Retry build
buildozer android debug
```

## Runtime Issues

### 6. "App crashes on startup"

**Troubleshooting:**
1. Check logcat output: `adb logcat`
2. Ensure pymupdf is installed
3. Check file permissions on PDF
4. Try smaller PDF file first

### 7. "PDF not found / Permission denied"

**Cause:** Storage permissions not granted

**Solution:**
1. Grant storage permission:
   - Android Settings → Apps → PDF Splitter → Permissions → Storage
2. Or rebuild with proper permissions in buildozer.spec:
   ```
   android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
   ```

### 8. "App freezes when splitting large PDF"

**Cause:** Main thread blocking during PDF processing

**Solution:**
1. Use smaller PDF files (test with <50MB first)
2. Split into smaller batches
3. Upgrade device RAM
4. Check storage space (ensure 1GB+ free)

## File System Issues

### 9. "Cannot find output files after split"

**Default Output Location:**
- `/sdcard/DCIM/PDFSplitter/` (on Android device)

**To access files:**
1. Connect device to computer via USB
2. Enable USB debugging
3. Use adb: `adb pull /sdcard/DCIM/PDFSplitter/`
4. Or use file manager app on device

### 10. "Storage permission denied"

**Solution:**
```bash
# Grant permissions via adb
adb shell pm grant org.pdfsplitter android.permission.WRITE_EXTERNAL_STORAGE
adb shell pm grant org.pdfsplitter android.permission.READ_EXTERNAL_STORAGE

# Or manually on device:
Settings → Apps → PDF Splitter → Permissions → Storage → Allow
```

## GitHub Actions Issues

### 11. "GitHub Actions build failed"

**Check build logs:**
1. Go to repository → Actions tab
2. Click failed workflow run
3. Expand "Build APK" step
4. Check error message

**Common causes:**
- Missing dependencies in buildozer.spec
- Syntax error in main.py
- Requirements version conflicts

### 12. "APK artifact not downloading"

**Troubleshooting:**
1. Check Actions tab - build must succeed (green checkmark)
2. Scroll to "Build APK" step → "Upload APK" action
3. Artifacts available for 90 days only
4. Ensure artifact wasn't manually deleted

## Installation Issues

### 13. "Cannot install APK - Unknown error"

**Causes & Solutions:**

1. **APK corrupted:**
   - Re-download from GitHub
   - Verify file size (~50MB)

2. **Android version incompatible:**
   - Check device Android version
   - Required: Android 5.1 (API 21) or higher
   - Recommended: Android 9+ (API 29+)

3. **Insufficient storage:**
   - Clear device cache: Settings → Storage → Cached data
   - Free up at least 100MB

4. **APK unsigned (debug APK):**
   - Allow installation from unknown sources:
     - Settings → Security → Unknown Sources (enable)

### 14. "Installation blocked by Play Protect"

**Solution:**
1. Open Google Play Protect app
2. Tap Profile → Settings
3. Disable "Scan apps with Play Protect"
4. Retry installation
5. Re-enable after installation

## Performance Issues

### 15. "App runs slowly on device"

**Optimization tips:**
1. Close other apps running in background
2. Restart device
3. Clear app cache: Settings → Apps → PDF Splitter → Storage → Clear Cache
4. Reduce PDF file size before splitting

## Debug Information

### Getting Debug Logs

**Using adb:**
```bash
# Connect device via USB (enable USB debugging)
adb devices

# View live logs
adb logcat | grep pdfsplitter

# Save logs to file
adb logcat > app.log
```

### Common Log Messages

```
[INFO] PDF Splitter: Initializing...          ✓ Normal startup
[WARNING] Memory low: Consider smaller files  ⚠ Performance warning
[ERROR] PDF corrupted                         ✗ File issue
[ERROR] Storage permission denied             ✗ Permissions issue
```

## Version Compatibility

| Component | Minimum | Recommended | Current |
|-----------|---------|-------------|---------|
| Android | 5.1 (API 21) | 9+ (API 29+) | — |
| Python | 3.8 | 3.11 | 3.11 |
| Kivy | 2.0 | 2.3+ | 2.3.1 |
| PyMuPDF | 1.20 | 1.25+ | 1.26.7 |

## Still Having Issues?

1. Check GitHub Issues: https://github.com/[owner]/split-pdf-with-chapters/issues
2. Review logs carefully for specific error messages
3. Provide:
   - Device model and Android version
   - Error message or log excerpt
   - Steps to reproduce
   - PDF file characteristics (size, bookmarks, format)

## Useful Commands

```bash
# Clear buildozer cache
rm -rf .buildozer

# View build output
buildozer android debug -- verbose

# Connect to Android device
adb connect device_ip:5555

# Install APK directly
adb install bin/pdfsplitter-1.0.0-debug.apk

# Uninstall app
adb uninstall org.pdfsplitter

# View device storage
adb shell df -h

# Clear app data
adb shell pm clear org.pdfsplitter
```
