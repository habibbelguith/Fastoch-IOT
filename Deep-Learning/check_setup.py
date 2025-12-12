"""
Setup verification script for Vehicle Recognition System
Checks if all required files and dependencies are present
"""

import os
import sys

def check_file(filepath, description):
    """Check if a file exists"""
    exists = os.path.isfile(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    if exists:
        size = os.path.getsize(filepath) / (1024 * 1024)  # Size in MB
        print(f"   Size: {size:.2f} MB")
    return exists

def check_directory(dirpath, description):
    """Check if a directory exists"""
    exists = os.path.isdir(dirpath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {dirpath}")
    return exists

def check_python_package(package_name):
    """Check if a Python package is installed"""
    try:
        __import__(package_name)
        print(f"✅ {package_name}: Installed")
        return True
    except ImportError:
        print(f"❌ {package_name}: NOT INSTALLED")
        return False

def main():
    print("=" * 70)
    print("Vehicle Recognition System - Setup Verification")
    print("=" * 70)
    print()
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    all_ok = True
    
    # Check Python version
    print("Python Version:")
    print(f"  Version: {sys.version}")
    print()
    
    # Check required Python packages
    print("Required Python Packages:")
    packages = ['tensorflow', 'cv2', 'numpy', 'matplotlib']
    for pkg in packages:
        if not check_python_package(pkg):
            all_ok = False
    print()
    
    # Check YOLO detection files
    print("License Plate Detection Files (YOLO):")
    yolo_dir = os.path.join(script_dir, "Licence_plate_detection")
    weights_file = os.path.join(yolo_dir, "lapi.weights")
    cfg_file = os.path.join(yolo_dir, "darknet-yolov3.cfg")
    classes_file = os.path.join(yolo_dir, "classes.names")
    
    if not check_file(weights_file, "YOLO Weights"):
        all_ok = False
        print("   ⚠️  ACTION REQUIRED: Download from Dropbox link in README.md")
    check_file(cfg_file, "YOLO Config")
    check_file(classes_file, "Classes Names")
    print()
    
    # Check OCR model files
    print("License Plate Recognition Files (OCR):")
    ocr_dir = os.path.join(script_dir, "Licence_Plate_Recognition")
    ocr_model = os.path.join(ocr_dir, "ocrmodel.h5")
    check_file(ocr_model, "OCR Model")
    print()
    
    # Check main scripts
    print("Main Scripts:")
    main_scripts_dir = os.path.join(script_dir, "Main-Scripts")
    scripts = [
        ("object_detection_yolo.py", "YOLO Detection Script"),
        ("Hawk_Eye_LP_recognition.py", "OCR Recognition Script"),
        ("main_vehicle_to_LP.py", "Main Pipeline Script")
    ]
    for script, desc in scripts:
        script_path = os.path.join(main_scripts_dir, script)
        if not check_file(script_path, desc):
            all_ok = False
    print()
    
    # Check test script
    print("Test Scripts:")
    test_script = os.path.join(script_dir, "test_inference.py")
    check_file(test_script, "Test Inference Script")
    print()
    
    # Check test images
    print("Test Images:")
    test_dir = os.path.join(ocr_dir, "LP_extraction_test")
    if check_directory(test_dir, "Test Images Directory"):
        test_images = [f for f in os.listdir(test_dir) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        print(f"   Found {len(test_images)} test images")
        if test_images:
            print(f"   Example: {test_images[0]}")
    print()
    
    # Check output directory
    print("Output Directory:")
    output_dir = os.path.join(script_dir, "output")
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"✅ Created: {output_dir}")
    else:
        print(f"✅ Exists: {output_dir}")
    print()
    
    # Final summary
    print("=" * 70)
    if all_ok:
        print("✅ SETUP COMPLETE! All required files are present.")
        print("   You can now run inference using:")
        print("   python test_inference.py --image Licence_Plate_Recognition/LP_extraction_test/test.png")
    else:
        print("⚠️  SETUP INCOMPLETE! Some files are missing.")
        print("   Please check the items marked with ❌ above.")
        if not os.path.isfile(weights_file):
            print()
            print("   IMPORTANT: Download lapi.weights from:")
            print("   https://www.dropbox.com/s/fxyblp7dezmy2jp/Attachments.zip?dl=0")
            print("   Place it in: Licence_plate_detection/lapi.weights")
    print("=" * 70)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())

