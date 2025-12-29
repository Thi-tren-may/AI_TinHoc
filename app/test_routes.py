from flask import Blueprint, render_template
test_bp = Blueprint('test', __name__)

@test_bp.route('/quiz')
def quiz():
    return "Trang làm bài của S2"