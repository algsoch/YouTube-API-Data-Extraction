"""
Validation script to check if the project is ready to run.
Run this before starting the data extraction to ensure everything is configured correctly.
"""

import os
import sys

def check_python_version():
    """Check if Python version is 3.7 or higher."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✓ Python version {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} detected. Need Python 3.7+")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'googleapiclient',
        'google.auth',
        'pandas',
        'dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ Package '{package}' is installed")
        except ImportError:
            print(f"✗ Package '{package}' is missing")
            missing.append(package)
    
    if missing:
        print(f"\nInstall missing packages with: pip install -r requirements.txt")
        return False
    return True

def check_env_file():
    """Check if .env file exists and contains API key."""
    if not os.path.exists('.env'):
        print("✗ .env file not found")
        print("  Create it with: copy .env.example .env")
        print("  Then edit .env and add your YouTube API key")
        return False
    
    print("✓ .env file exists")
    
    # Check if API key is configured
    with open('.env', 'r') as f:
        content = f.read()
        if 'YOUTUBE_API_KEY=' in content:
            # Check if it's not still the placeholder
            if 'your_api_key_here' not in content:
                print("✓ API key appears to be configured")
                return True
            else:
                print("✗ API key is still set to placeholder value")
                print("  Edit .env and replace 'your_api_key_here' with your actual key")
                return False
        else:
            print("✗ YOUTUBE_API_KEY not found in .env file")
            return False

def check_project_files():
    """Check if all required project files exist."""
    required_files = [
        'main.py',
        'youtube_client.py',
        'video_extractor.py',
        'channel_extractor.py',
        'data_exporter.py',
        'requirements.txt'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} is missing")
            missing.append(file)
    
    return len(missing) == 0

def check_output_directory():
    """Check if output directory can be created."""
    try:
        if not os.path.exists('data'):
            os.makedirs('data')
            print("✓ Created 'data' output directory")
        else:
            print("✓ 'data' output directory exists")
        return True
    except Exception as e:
        print(f"✗ Cannot create output directory: {e}")
        return False

def main():
    """Run all validation checks."""
    print("="*70)
    print("YouTube Data Extraction - Pre-flight Check")
    print("="*70)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_dependencies),
        ("Environment File", check_env_file),
        ("Project Files", check_project_files),
        ("Output Directory", check_output_directory)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\nChecking {name}:")
        print("-" * 70)
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Error during check: {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("="*70)
    print("Summary:")
    print("="*70)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to run the extraction.")
        print("\nRun: python main.py")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above before running.")
        print("\nQuick fixes:")
        print("  - Install packages: pip install -r requirements.txt")
        print("  - Configure API key: copy .env.example .env, then edit .env")
    
    print()
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
