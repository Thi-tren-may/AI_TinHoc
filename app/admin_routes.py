from flask import Blueprint, render_template
admin_bp = Blueprint('admin', __name__) # Phải có dòng này!

@admin_bp.route('/dashboard')
def dashboard():
    return "Trang quản trị của S3"