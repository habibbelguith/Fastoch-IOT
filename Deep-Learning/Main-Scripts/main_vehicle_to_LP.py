import object_detection_yolo as LP_detection
import Hawk_Eye_LP_recognition as LP_reco
from cv2 import imwrite
import os
import argparse

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
output_dir = os.path.join(project_root, "output")
os.makedirs(output_dir, exist_ok=True)

# Parse command line arguments
parser = argparse.ArgumentParser(description='Vehicle License Plate Recognition')
parser.add_argument('--image', required=True, help='Path to image file.')
args = parser.parse_args()

# Check if image exists
if not os.path.isfile(args.image):
    print(f"Error: Image file '{args.image}' does not exist")
    exit(1)

#Licence plate detection
LP_extracted, newImage, top = LP_detection.LP_detection(args.image)

if LP_extracted is None:
    print("Error: Could not detect license plate in the image")
    exit(1)

#Licence plate recognition
final_img = LP_reco.LP_recognition(LP_extracted, newImage, top)

#Saving the final result
path_to_final_img = os.path.join(output_dir, "final_image.jpg")
imwrite(path_to_final_img, final_img)
print(f"Result saved to: {path_to_final_img}")

