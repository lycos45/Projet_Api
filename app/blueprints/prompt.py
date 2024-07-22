from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import get_db_connection

prompt_bp = Blueprint('prompt', __name__)

@prompt_bp.route('/get_prompt_points/<int:prompt_id>', methods=['GET'])
@jwt_required()
def get_prompt_points(prompt_id):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT total_points FROM prompt_points WHERE prompt_id = %s", (prompt_id,))
        result = cur.fetchone()
        if result:
            total_points = result[0]
            return jsonify({'prompt_id': prompt_id, 'total_points': total_points}), 200
        else:
            return jsonify({'error': 'Prompt not found or no points available'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve points: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()
