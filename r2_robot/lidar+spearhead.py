import cv2
import json
from ultralytics import YOLO
import time
import serial

#min 176 max 526

arduino = serial.Serial(
    port='COM13',
    baudrate= 115200,
    timeout=0
)
time.sleep(2)
arduino.reset_input_buffer()


# MODEL_PATH = r"D:\My Model\Spearhead\Spearhead Photos from Phone\runs\detect\train\weights\best.pt"
MODEL_PATH = r"/home/rishi/robocon26/src/r2_robot/r2_robot/spearhead_yolo_nas.pt (1)"
CAMERA_ID = 0

FRAME_WIDTH = 640
FRAME_HEIGHT = 640

CENTER_TOLERANCE = 25          
CONF_THRESHOLD = 0.7

TARGET_AREA = 20000 
TARGET_HEIGHT = 525           
MAX_STRENGTH = 60
MIN_STRENGTH = 20
ALIGN_STRENGTH = 30




json_str = ""
def loc(command, rot_strength, theta, strength) :

    data = {
        "LOC": f"{command}{rot_strength}{theta}{strength}"
    }
    
    print(data)
    arduino.write((json.dumps(data)+ "\n").encode())

# def read_arduino():
#     try:
#         while arduino.in_waiting:
#             line = arduino.readline().decode().strip()
#             if line:
#                 print("Arduino:", line)
#     except:
#         pass




def give_strength(height):
    error = TARGET_HEIGHT - height
    print(error)
    if 1 <= abs(error) <= 6:
        return 0
    else :
        strength = (error/abs(error))*(MIN_STRENGTH + (abs(error) / TARGET_HEIGHT))
        return int(max(MIN_STRENGTH, min(MAX_STRENGTH, strength)))





def get_command(detections, frame_width):
    frame_center_x = frame_width / 2
    nearest = None
    min_dist = float("inf") 

    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        box_center_x = (x1 + x2) / 2
        
        dist = abs(box_center_x - frame_center_x)

        if dist < min_dist:
            min_dist = dist
            box_height = y2-y1
            nearest = {
                "class_id": det["class_id"],
                "confidence": det["confidence"],
                "bbox": det["bbox"],
                "center_x": box_center_x,
                "height": int(box_height)
            }
        # print(nearest["height"])

    if nearest is None:
        # return {
        #     "cmd": "SEARCH",
        #     "strength": 0
        # }
        return loc("S","000","000","000")

    error_x = nearest["center_x"] - frame_center_x

    if abs(error_x) > CENTER_TOLERANCE:
        # return {
        #     "cmd": "MOVE_RIGHT" if error_x > 0 else "MOVE_LEFT",
        #     "error_x": int(error_x),
        #     "strength": ALIGN_STRENGTH
        # }
        stnght = MIN_STRENGTH + int(abs(error_x) / 20)
        if error_x > 0:
            return loc('S', "000", "000", f"0{stnght}")
        return loc('S', "000", "180", f"0{stnght}")
    

    elif nearest["height"] <= TARGET_HEIGHT:  
        error = TARGET_HEIGHT - nearest["height"]
        if 1 <= abs(error) <= 6:
            return loc('G',"000","000","000")
        else:
            return loc('S', "000", "90", give_strength(nearest["height"]))
    

def main():
    model = YOLO(MODEL_PATH)

    cap = cv2.VideoCapture(CAMERA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("Camera not opened")
        return

    print("Camera started... Press Q to exit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, conf=CONF_THRESHOLD, verbose=False)

        detections = []

        for r in results:
            if r.boxes is None:
                continue

            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                detections.append({
                    "class_id": cls_id,
                    "confidence": conf,
                    "bbox": [x1, y1, x2, y2]
                })

                cv2.rectangle(
                    frame,
                    (int(x1), int(y1)),
                    (int(x2), int(y2)),
                    (0, 255, 0),
                    2
                )

        command = get_command(detections, FRAME_WIDTH)

        cv2.line(
            frame,
            (FRAME_WIDTH // 2, 0),
            (FRAME_WIDTH // 2, FRAME_HEIGHT),
            (255, 0, 0),
            2
        )

        cv2.putText(
            frame,
            "Spearhead Detection",
            # f"{command['cmd']} | Strength: {command.get('strength', 0)}",
            # f"{command['cmd']} | Strength: {command.get('strength', 0)}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 0, 255),
            2
        )

        cv2.imshow("YOLO Vision Control", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()