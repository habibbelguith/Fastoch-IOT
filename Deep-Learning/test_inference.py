"""
Test script for Vehicle License Plate Recognition System
This script tests the inference pipeline with a sample image.
"""

import os
import sys
import argparse

# Add Main-Scripts to path
script_dir = os.path.dirname(os.path.abspath(__file__))
main_scripts_dir = os.path.join(script_dir, "Main-Scripts")
sys.path.insert(0, main_scripts_dir)

def main():
    parser = argparse.ArgumentParser(description='Test License Plate Recognition Inference')
    parser.add_argument('--image', 
                       help='Path to test image file',
                       default=os.path.join(script_dir, "Licence_Plate_Recognition", "LP_extraction_test", "test.png"))
    args = parser.parse_args()
    
    # Check if image exists
    if not os.path.isfile(args.image):
        print(f"Error: Image file '{args.image}' does not exist")
        print("\nAvailable test images:")
        test_dir = os.path.join(script_dir, "Licence_Plate_Recognition", "LP_extraction_test")
        if os.path.isdir(test_dir):
            for f in os.listdir(test_dir):
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    print(f"  - {os.path.join(test_dir, f)}")
        return 1
    
    print(f"Testing inference with image: {args.image}")
    print("-" * 60)
    
    try:
        # Import and run the main script
        import object_detection_yolo as LP_detection
        import Hawk_Eye_LP_recognition as LP_reco
        from cv2 import imwrite
        
        print("Step 1: License plate detection...")
        LP_extracted, newImage, top = LP_detection.LP_detection(args.image)
        
        if LP_extracted is None or (hasattr(LP_extracted, 'size') and LP_extracted.size == 0):
            print("ERROR: Could not detect license plate in the image")
            print("   - The image may not contain a visible license plate")
            print("   - Try a different image with a clearer license plate")
            print("   - Make sure the license plate is clearly visible and not obstructed")
            return 1
        
        print("Step 2: License plate recognition...")
        try:
            final_img = LP_reco.LP_recognition(LP_extracted, newImage, top)
        except Exception as e:
            print(f"ERROR during recognition: {type(e).__name__}: {e}")
            return 1
        
        # Save result
        output_dir = os.path.join(script_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "test_result.jpg")
        imwrite(output_path, final_img)
        
        print("-" * 60)
        print(f"SUCCESS! Result saved to: {output_path}")
        return 0
        
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        return 1
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

