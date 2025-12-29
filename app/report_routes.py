from flask import Blueprint, render_template
report_bp = Blueprint('report', __name__)

@report_bp.route('/view')
def view_report():
    return "Trang thống kê của S4"