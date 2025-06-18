import cv2
import mediapipe as mp
import numpy as np

class EyeTracker:
    def __init__(self, ear_threshold=0.25, consecutive_frames=15):
        self.ear_threshold = ear_threshold
        self.consecutive_frames = consecutive_frames
        self.counter = 0
        self.sleep_alert=False

        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]

    def _eye_aspect_ratio(self, landmarks, eye_indices, image_width, image_height):
        points = [(int(landmarks[idx].x * image_width), int(landmarks[idx].y * image_height)) for idx in eye_indices]

        A = np.linalg.norm(np.array(points[1]) - np.array(points[5]))
        B = np.linalg.norm(np.array(points[2]) - np.array(points[4]))
        C = np.linalg.norm(np.array(points[0]) - np.array(points[3]))

        ear = (A + B) / (2.0 * C)

        return ear
    
    def analyze_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        height, width = frame.shape[:2]
        ear_left = ear_right = None

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            ear_left = self._eye_aspect_ratio(landmarks, self.LEFT_EYE, width, height)
            ear_right = self._eye_aspect_ratio(landmarks, self.RIGHT_EYE, width, height)
            ear_avg = (ear_left + ear_right) / 2.0

            if ear_avg < self.ear_threshold:
                self.counter += 1
            else:
                self.counter = 0

            self.sleep_alert = self.counter >= self.consecutive_frames

            return {
                "ear": ear_avg,
                "sleep_alert": self.sleep_alert,
                "counter": self.counter
            }
        
        return {
            "ear": None,
            "sleep_alert": False,
            "counter": 0
        }
