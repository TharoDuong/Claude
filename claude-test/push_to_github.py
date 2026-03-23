import os
import base64
import requests
import sys
from datetime import datetime

# ========== CẤU HÌNH ==========
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_USERNAME = "TharoDuong"
REPO_NAME = "Claude"
FOLDER = "claude-test"
# ================================

if not GITHUB_TOKEN:
    print("❌ Chưa có token! Hãy chạy lệnh sau trước:")
    print('   export GITHUB_TOKEN="ghp_..."')
    sys.exit(1)

def push_file(local_file_path):
    """Đẩy một file lên GitHub repo"""
    
    if not os.path.exists(local_file_path):
        print(f"❌ Không tìm thấy file: {local_file_path}")
        return False

    filename = os.path.basename(local_file_path)
    github_path = f"{FOLDER}/{filename}"
    
    # Đọc nội dung file
    with open(local_file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{github_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Kiểm tra file đã tồn tại chưa (để lấy sha nếu cần update)
    check = requests.get(url, headers=headers)
    sha = check.json().get("sha") if check.status_code == 200 else None

    # Tạo commit message
    commit_message = f"Add {filename} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    payload = {
        "message": commit_message,
        "content": content
    }
    if sha:
        payload["sha"] = sha  # Cập nhật file đã có

    response = requests.put(url, json=payload, headers=headers)

    if response.status_code in [200, 201]:
        action = "✅ Cập nhật" if sha else "✅ Tạo mới"
        print(f"{action} thành công: {github_path}")
        print(f"🔗 Link: https://github.com/{GITHUB_USERNAME}/{REPO_NAME}/blob/main/{github_path}")
        return True
    else:
        print(f"❌ Lỗi: {response.status_code} - {response.json().get('message')}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python push_to_github.py <đường_dẫn_file>")
        print("Ví dụ:     python push_to_github.py my_code.py")
    else:
        for file_path in sys.argv[1:]:
            push_file(file_path)
