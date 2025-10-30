# client_simulation.py
import requests
import webbrowser
import jwt

# --- CẤU HÌNH CỦA CLIENT APP ---
CLIENT_ID = "my-awesome-client"
CLIENT_SECRET = "my-super-secret"
REDIRECT_URI = "http://127.0.0.1:5000/callback"
AUTH_SERVER_URL = "http://localhost:8080"
# Scope chúng ta muốn xin: vừa xác thực (openid profile), vừa ủy quyền (profile)
SCOPE = "openid profile"

def main():
    print("--- BẮT ĐẦU LUỒNG OAUTH 2.0 / OIDC ---")
    
    # === Bước 1 & 2: Bắt đầu luồng và chuyển hướng người dùng ===
    auth_url = (
        f"{AUTH_SERVER_URL}/authorize?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPE}"
    )
    print(f"\n[CLIENT] Bước 1: Mở trình duyệt và truy cập URL sau để đăng nhập và cấp quyền:")
    print(f"   ==> {auth_url}")
    webbrowser.open(auth_url)
    
    # === Bước 3 & 4: Người dùng được trả về với authorization_code ===
    print("\n[CLIENT] Bước 2: Sau khi đồng ý, trình duyệt sẽ được chuyển hướng đến một URL lỗi.")
    print("   Hãy copy toàn bộ phần `code` trong URL đó và dán vào đây.")
    auth_code = input("   Nhập authorization_code: ")

    # === Bước 5 & 6: Client đổi code lấy token ===
    print("\n[CLIENT] Bước 3: Gửi request từ backend để đổi code lấy token...")
    token_endpoint = f"{AUTH_SERVER_URL}/token"
    token_payload = {
        "grant_type": "authorization_code",
        "code": auth_code.strip(),
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    
    response = requests.post(token_endpoint, data=token_payload)
    if response.status_code != 200:
        print(f"[CLIENT-ERROR] Lỗi khi lấy token: {response.json()}")
        return
        
    tokens = response.json()
    access_token = tokens.get('access_token')
    id_token = tokens.get('id_token')
    
    print("\n[CLIENT] >> ĐÃ NHẬN ĐƯỢC TOKENS! <<")
    print(f"   Access Token: {access_token[:30]}...")
    print(f"   ID Token:     {id_token[:30]}...")

    # === Bước 7a: Client sử dụng ID Token (OIDC - Xác thực) ===
    print("\n--- PHÂN TÍCH ID TOKEN (OIDC AUTHENTICATION) ---")
    if id_token:
        # Trong thực tế, bạn sẽ xác minh chữ ký bằng public key của issuer
        # Ở đây chúng ta giải mã để xem nội dung
        id_token_payload = jwt.decode(id_token, options={"verify_signature": False})
        print(f"[CLIENT] Giải mã ID Token thành công!")
        print(f"   >> Chào mừng '{id_token_payload.get('name')}'!")
        print(f"   >> ID của bạn trên hệ thống là: '{id_token_payload.get('sub')}'")
        print("   >> Client bây giờ đã BIẾT BẠN LÀ AI và có thể tạo phiên đăng nhập.")
    else:
        print("[CLIENT] Không nhận được ID Token (hãy kiểm tra scope 'openid').")

    # === Bước 7b: Client sử dụng Access Token (OAuth 2.0 - Ủy quyền) ===
    print("\n--- SỬ DỤNG ACCESS TOKEN (OAUTH 2.0 AUTHORIZATION) ---")
    if access_token:
        profile_endpoint = f"{AUTH_SERVER_URL}/profile"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        print("[CLIENT] Gọi đến endpoint tài nguyên được bảo vệ (/profile)...")
        profile_response = requests.get(profile_endpoint, headers=headers)
        
        if profile_response.status_code == 200:
            print("[CLIENT] >> Thành công!")
            print(f"   >> Đã lấy được dữ liệu hồ sơ: {profile_response.json()}")
            print("   >> Access Token đã được dùng để CHỨNG MINH QUYỀN TRUY CẬP.")
        else:
            print(f"[CLIENT-ERROR] Lỗi khi truy cập tài nguyên: {profile_response.status_code} - {profile_response.text}")

if __name__ == "__main__":
    main()