import cv2
import sys

print("=" * 50)
print("CAMERA TEST SCRIPT")
print("=" * 50)

# Test multiple camera indices
for i in range(5):
    print(f"\nTesting camera index {i}...")
    cap = cv2.VideoCapture(i)
    
    if cap.isOpened():
        print(f"✅ Camera {i} opened successfully!")
        
        ret, frame = cap.read()
        if ret:
            print(f"✅ Camera {i} can read frames!")
            print(f"   Frame shape: {frame.shape}")
            
            # Try to display it
            cv2.imshow(f'Camera {i} Test', frame)
            print(f"   Window created. Press any key to close...")
            cv2.waitKey(2000)  # Wait 2 seconds
            cv2.destroyAllWindows()
            print(f"✅ Camera {i} WORKS!")
        else:
            print(f"❌ Camera {i} opened but can't read frames")
        
        cap.release()
    else:
        print(f"❌ Camera {i} not accessible")

print("\n" + "=" * 50)
print("TEST COMPLETE")
print("=" * 50)

# Check OpenCV version
print(f"\nOpenCV version: {cv2.__version__}")
print(f"Python version: {sys.version}")

input("\nPress Enter to exit...")