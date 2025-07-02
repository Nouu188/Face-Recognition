import oracledb
import numpy as np
import cv2
import base64
import pickle
import json
import face_recognition
import os

USERNAME = os.environ.get("DATABASE_USERNAME")
PASSWORD = os.environ.get("DATABASE_PASSWORD")
DSN = os.environ.get("DATABASE_DSN")

CONN = oracledb.connect(user=USERNAME, password=PASSWORD, dsn=DSN)

THRESHOLD = 0.35

def decode_image(image_data):
    try:
        if not isinstance(image_data, str):
            raise ValueError("Giá trị truyền vào decode_image phải là chuỗi base64")

        header, encoded = image_data.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Không đọc được ảnh từ buffer")

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        print(f"[🧪] Kích thước ảnh RGB: {rgb.shape}")
        cv2.imwrite("debug_rgb.jpg", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))

        face_locations = face_recognition.face_locations(rgb)
        print(f"[🧪] Số khuôn mặt phát hiện: {len(face_locations)}")

        if not face_locations:
            raise ValueError("Không tìm thấy khuôn mặt")

        top, right, bottom, left = face_locations[0]
        face_only = rgb[top:bottom, left:right]

        face_only_resized = cv2.resize(face_only, (160, 160))

        print(f"[ℹ️] Ảnh nhận vào: shape={face_only_resized.shape}")
        cv2.imwrite("debug_input.jpg", cv2.cvtColor(face_only_resized, cv2.COLOR_RGB2BGR))

        return frame, face_only_resized

    except Exception as e:
        print(f"[⚠️] Lỗi khi giải mã ảnh base64: {e}")
        raise e

def load_all_encodings(idbv=0):
    cur = CONN.cursor()
    
    if idbv:
        print(f"[🧪] Đang truy vấn vector với IDBV = {idbv}")
        cur.execute("SELECT id, vector FROM dloginface WHERE idbv = :1 AND vector IS NOT NULL", [idbv])
    else:
        print("[ℹ️] Không có IDBV → bỏ qua truy vấn vector")
        return [], []

    encs, ids = [], []
    for uid, vec in cur.fetchall():
        try:
            raw = vec.read() if hasattr(vec, 'read') else vec
            encoding = pickle.loads(raw)
            if isinstance(encoding, np.ndarray):
                encs.append(encoding)
                ids.append(uid)
        except Exception as e:
            print(f"[⚠️] Lỗi khi đọc vector (BLOB) của ID={uid}: {e}")
    
    print(f"[✅] Tìm thấy {len(encs)} vector cho IDBV = {idbv}")
    return encs, ids

def recognize_face_from_blob(image_data, idbv=0):
    try:
        if not idbv:
            print("[ℹ️] idbv = 0 → Bỏ qua so sánh khuôn mặt")
            return None, 1.0 

        rgb = decode_image(image_data)
        encs = face_recognition.face_encodings(rgb)
        if not encs:
            return None, 1.0

        test_encoding = encs[0]
        known_encodings, known_ids = load_all_encodings(idbv)
        if not known_encodings:
            return None, 1.0

        distances = face_recognition.face_distance(known_encodings, test_encoding)
        min_dist = np.min(distances)
        if min_dist < THRESHOLD:
            best_idx = np.argmin(distances)
            return known_ids[best_idx], float(min_dist)
        return None, float(min_dist)
    except Exception as e:
        print(f"[❌] Lỗi khi nhận diện khuôn mặt: {e}")
        return None, 1.0

def find_invalid_vectors():
    cur = CONN.cursor()
    cur.execute("SELECT id, stt, vector FROM dloginface WHERE vector IS NOT NULL")
    result = []
    for record_id, stt, vector_lob in cur.fetchall():
        try:
            raw = vector_lob.read() if hasattr(vector_lob, 'read') else vector_lob
            pickle.loads(raw)
        except:
            result.append({"id": record_id, "stt": stt})
    return result

def export_invalid_vectors_to_file(path="invalid_vectors.json"):
    data = find_invalid_vectors()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Exported invalid vectors to {path}")

def jpeg_base64_to_vector_blob(image_data):
    _, face_rgb = decode_image(image_data)
    encodings = face_recognition.face_encodings(face_rgb)
    if not encodings:
        raise ValueError("Không tìm được khuôn mặt")

    return pickle.dumps(encodings[0])

