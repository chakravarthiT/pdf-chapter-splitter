# Android APK Build Guide

This guide covers building the PDF Splitter APK for Android devices.

## Prerequisites

- Python 3.8+
- Java Development Kit (JDK 17+)
- 20GB+ free disk space
- Linux, macOS, or Windows with WSL2

## Option 1: GitHub Actions (Easiest - Recommended)

The repository includes automated GitHub Actions workflow that builds the APK on every push.

1. Push to `main` or `develop` branch
2. GitHub Actions automatically builds the APK
3. Download from:
   - **Artifacts tab**: APK available for 90 days
   - **Releases page**: Latest APK in releases
   - **Repository**: Committed to `android_app/bin/`

**Advantages:**
- No local setup required
- Consistent Linux build environment
- Automatic versioning and release creation
- 90-day artifact retention

## Option 2: Docker Build (Recommended for Local)

### Prerequisites
- Docker installed and running

### Steps

```bash
cd android_app

# Build Docker image (one-time setup)
docker build -t pdfsplitter-builder -f Dockerfile .

# Build APK using Docker
docker run --rm -v $(pwd):/workspace pdfsplitter-builder

# APK will be in: bin/pdfsplitter-1.0.0-debug.apk
```

**Advantages:**
- Isolated environment
- No native dependencies to install
- Works on any OS

## Option 3: Direct Buildozer (Advanced)

### Prerequisites

#### macOS
```bash
# Install Homebrew dependencies
brew install python@3.11 java17 autoconf automake libtool pkg-config

# Install Cython and buildozer
pip install buildozer cython kivy pymupdf
```

#### Ubuntu/Debian
```bash
sudo apt-get install -y \
  python3.11 python3.11-dev \
  openjdk-17-jdk \
  build-essential git \
  ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
  libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
  zlib1g-dev libgstreamer1.0-0 gstreamer1.0-plugins-base \
  autoconf automake libtool pkg-config

pip install buildozer cython kivy pymupdf
```

### Build Steps

```bash
cd android_app

# First build (takes 15-30 minutes)
buildozer android debug

# APK location: bin/pdfsplitter-1.0.0-debug.apk
```

### Troubleshooting

**Issue: `buildozer command not found`**
```bash
# Make sure Cython is installed first
pip install cython
pip install buildozer
```

**Issue: `No Java SDK found`**
```bash
# Set JAVA_HOME
export JAVA_HOME=/usr/libexec/java_home -v 17  # macOS
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64  # Linux
```

**Issue: `Android SDK/NDK not found`**
- First buildozer run downloads ~5GB of Android SDK/NDK
- Ensure 20GB+ free disk space
- Be patient - first build takes 15-30 minutes

## Installation on Android Device

### From APK
1. Transfer APK to Android device via USB or file sharing
2. Open file manager, navigate to APK file
3. Tap APK → Install
4. Grant permissions when prompted

### From GitHub Release
1. Go to repository Releases page
2. Download latest APK
3. Open on Android device and install

## Building for Release

To build release APK with signing:

```bash
cd android_app
buildozer android release
```

Requires keystore setup - see Kivy documentation for details.

## Build Configuration

Modify `buildozer.spec` for:
- `title`: App name in launcher
- `version`: Semantic version (major.minor.patch)
- `android.permissions`: App permissions
- `android.api`: Target Android API level
- `android.minapi`: Minimum Android API level

## APK Output

**Debug APK:**
- Location: `bin/pdfsplitter-1.0.0-debug.apk`
- ~50MB file size
- Good for testing and development
- Can be installed on any Android device

**Release APK:**
- Location: `bin/pdfsplitter-1.0.0-release.apk`
- ~45MB file size
- Optimized and signed
- Required for Google Play Store

## Version Information

- **Kivy**: 2.3.1
- **PyMuPDF**: 1.26.7
- **Python**: 3.11 (in build environment)
- **Android API**: 29 (min: 21)
- **Architecture**: ARM64 (arm64-v8a)

## Performance Tips

1. **Faster builds**: Subsequent builds are faster (first build: 15-30 min, subsequent: 3-5 min)
2. **Cache**: buildozer caches downloaded files in `.buildozer/`
3. **Parallel builds**: GitHub Actions can handle multiple builds simultaneously
4. **Storage**: Keep 30GB+ free for build cache and SDKs

## CI/CD Integration

GitHub Actions workflow automatically:
1. Builds APK on every push to main/develop
2. Uploads APK as artifact (90-day retention)
3. Creates GitHub Release with APK attached
4. Commits APK back to repository
5. Posts build summary

See `.github/workflows/build-apk.yml` for configuration details.

## Additional Resources

- [Kivy Documentation](https://kivy.org/doc/stable/)
- [Buildozer Documentation](https://buildozer.readthedocs.io/)
- [PyMuPDF Documentation](https://pymupdf.io/)
- [Android Development](https://developer.android.com/)
