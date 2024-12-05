import json
import cv2
from VehicleDetectionTracker.VehicleDetectionTracker import VehicleDetectionTracker

video_path = r"resources\vehicle.mp4"
start_time = 495  # in seconds
end_time = 500  # in seconds

# Get the frame rate of the video
cap = cv2.VideoCapture(video_path)
frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
cap.release()

# Convert time in seconds to frame numbers
start_frame = start_time * frame_rate
end_frame = end_time * frame_rate

vehicle_detection = VehicleDetectionTracker()
unique_vehicles = {}
detected_vehicles = []
allowed_vehicle_types = {"car", "motorcycle", "truck", "bus", "van", "train"}


def result_callback(result):
    for vehicle in result["detected_vehicles"]:
        vehicle_id = vehicle["vehicle_id"]
        vehicle_type = vehicle["vehicle_type"]
        if vehicle_id not in unique_vehicles and vehicle_type in allowed_vehicle_types:
            unique_vehicles[vehicle_id] = {
                "vehicle_id": vehicle_id,
                "vehicle_type": vehicle_type,
                "detection_confidence": vehicle["detection_confidence"],
                "color_info": vehicle["color_info"],
                "model_info": vehicle["model_info"],
                "speed_info": vehicle["speed_info"],
            }
            detected_vehicles.append(unique_vehicles[vehicle_id])


vehicle_detection.process_video(
    video_path, result_callback, start_frame=start_frame, end_frame=end_frame
)

# Write the detected vehicles to a JSON file
with open("detected_vehicles.json", "w") as json_file:
    json.dump(detected_vehicles, json_file, indent=4)


def analyze_json_file(json_file_path, output_txt_file_path):
    from datetime import datetime
    import statistics

    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)

    vehicle_count = len(data)
    vehicle_types_count = {}
    colors = {}

    for vehicle in data:
        vehicle_type = vehicle["vehicle_type"]
        vehicle_types_count[vehicle_type] = vehicle_types_count.get(vehicle_type, 0) + 1

        if "color_info" in vehicle and vehicle["color_info"]:
            color = vehicle["color_info"]
            colors[color] = colors.get(color, 0) + 1

    # Write with UTF-8 encoding
    with open(output_txt_file_path, "w", encoding="utf-8") as txt_file:
        # Header
        txt_file.write("=" * 50 + "\n")
        txt_file.write("Vehicle Detection Analysis Report\n")
        txt_file.write(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        txt_file.write("=" * 50 + "\n\n")

        # Overall Statistics
        txt_file.write("Overall Statistics\n")
        txt_file.write("-" * 30 + "\n")
        txt_file.write(f"Total vehicles detected: {vehicle_count}\n\n")

        # Vehicle Types Distribution
        txt_file.write("Vehicle Types Distribution\n")
        txt_file.write("-" * 30 + "\n")
        for vehicle_type, count in sorted(
            vehicle_types_count.items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (count / vehicle_count) * 100
            bar = "#" * int(percentage / 2)
            txt_file.write(
                f"{vehicle_type.capitalize():12} : {count:3} ({percentage:5.1f}%) {bar}\n"
            )
        txt_file.write("\n")

        # Footer
        txt_file.write("=" * 50 + "\n")
        txt_file.write("End of Analysis Report\n")


# Analyze the JSON file and write the results to a text file
analyze_json_file("detected_vehicles.json", "vehicle_analysis.txt")
