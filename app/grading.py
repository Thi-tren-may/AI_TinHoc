# app/grading.py
# Module này chịu trách nhiệm tính toán điểm số

def tinh_diem(danh_sach_cau_hoi, dap_an_nguoi_dung):
    """
    Hàm tính điểm bài thi.
    - danh_sach_cau_hoi: List chứa thông tin câu hỏi lấy từ DB (bao gồm đáp án đúng).
    - dap_an_nguoi_dung: Dictionary chứa {id_cau_hoi: 'A'/'B'...} user chọn.
    
    Trả về: 
    - tong_diem (thang 10)
    - so_cau_dung
    - chi_tiet_ket_qua (List các dict để lưu vào DB)
    """
    so_cau_dung = 0
    tong_so_cau = len(danh_sach_cau_hoi)
    chi_tiet_ket_qua = [] # Dùng để lưu vào bảng StudentResults sau này

    for cau_hoi in danh_sach_cau_hoi:
        cau_hoi_id = str(cau_hoi['Id']) # Chuyển về string để khớp với form HTML
        dap_an_dung = cau_hoi['CorrectOption'] # Ví dụ: 'A'
        
        # Lấy đáp án user chọn, nếu không chọn thì mặc định là None
        dap_an_chon = dap_an_nguoi_dung.get(cau_hoi_id)

        is_correct = 0 # Mặc định là sai
        if dap_an_chon == dap_an_dung:
            so_cau_dung += 1
            is_correct = 1
        
        # Đóng gói kết quả từng câu để trả về
        chi_tiet_ket_qua.append({
            'exam_id': None, # Sẽ điền sau khi tạo bài thi
            'exercise_id': int(cau_hoi_id),
            'selected_option': dap_an_chon,
            'is_correct': is_correct
        })

    # Tính điểm hệ 10 (Làm tròn 2 chữ số thập phân)
    if tong_so_cau > 0:
        diem_so = round((so_cau_dung / tong_so_cau) * 10, 2)
    else:
        diem_so = 0

    return diem_so, so_cau_dung, chi_tiet_ket_qua