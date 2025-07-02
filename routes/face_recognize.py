from flask import request, jsonify, redirect, url_for
from face_utils import recognize_face_from_blob, CONN

def recognize_handler():
    try:
        data = request.get_json()
        print(f"[DEBUG] JSON nhận được từ client: {data}")
        image_data = data.get("image")
        idbv = int(data.get("idbv", 0))

        if not isinstance(image_data, str):
            return jsonify({"status": "error", "message": "Ảnh truyền không hợp lệ"}), 400

        cur = CONN.cursor()
        cur.execute("SELECT COUNT(*) FROM dloginface WHERE idbv = :1", [idbv])
        count = cur.fetchone()[0]

        if count == 0:
            return jsonify({"status": "fail", "message": "❌ IDBV không tồn tại trong hệ thống"}), 400

        user_id, dist = recognize_face_from_blob(image_data, idbv)

        if user_id:
            return redirect(url_for("face_bp.welcome", user_id=user_id))

        return jsonify({
            "status": "fail",
            "message": "❌ Khuôn mặt không khớp với ID đã nhập",
            "distance": dist
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
