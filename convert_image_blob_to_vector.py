# convert_image_blob_to_vector.py
import oracledb
import pickle
import cv2
import numpy as np
import face_recognition
from face_utils import recognize_face_from_blob, CONN

def convert_blob_to_vector():
    cur = CONN.cursor()

    cur.execute("SELECT id, stt, vector FROM dloginface WHERE vector IS NOT NULL")
    for id_, stt, blob in cur.fetchall():
        try:
            raw = blob.read() if hasattr(blob, "read") else blob
            if raw.startswith(b'\xff\xd8\xff'):
                print(f"🛠️ ID={id_} STT={stt} đang chứa ảnh, sẽ chuyển đổi...")
                np_arr = np.frombuffer(raw, np.uint8)
                image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                faces = face_recognition.face_encodings(rgb)
                if not faces:
                    print(f"⚠️ Không tìm thấy khuôn mặt trong ảnh ID={id_} STT={stt}")
                    continue
                vector = faces[0]
                vector_blob = pickle.dumps(vector)
                cur.execute(
                    "UPDATE dloginface SET vector = :1 WHERE id = :2 AND stt = :3",
                    [vector_blob, id_, stt]
                )
                CONN.commit()
                print(f"✅ Đã chuyển vector cho ID={id_} STT={stt}")
        except Exception as e:
            print(f"❌ Lỗi xử lý ID={id_} STT={stt}: {e}")
if __name__ == "__main__":
    print("[🔍] Bắt đầu dò và chuyển vector từ ảnh JPEG...")
    convert_blob_to_vector()
