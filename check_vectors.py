import oracledb
import pickle
from face_utils import recognize_face_from_blob, CONN

cur = CONN.cursor()

target_id = 4202
cur.execute("SELECT stt, vector FROM dloginface WHERE id = :1", [target_id])

print(f"🧪 Kiểm tra vector của ID = {target_id}")
for stt, vector in cur.fetchall():
    try:
        raw = vector.read() if hasattr(vector, 'read') else vector
        pickle.loads(raw)
        print(f"✅ STT {stt}: vector hợp lệ")
    except Exception as e:
        print(f"❌ STT {stt}: lỗi vector – {e}")
