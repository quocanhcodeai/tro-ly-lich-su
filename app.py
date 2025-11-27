import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import re
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Trợ Lý Lịch Sử", page_icon="📜", layout="centered")

# --- ẨN GIAO DIỆN MẶC ĐỊNH CỦA STREAMLIT (Nút Fork, Menu, Footer) ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- CẤU HÌNH AI (Lấy Key từ két sắt bí mật) ---
# Đảm bảo đã cài đặt secrets trên share.streamlit.io
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Chưa thiết lập GOOGLE_API_KEY trong Secrets!")
    st.stop()

genai.configure(api_key=API_KEY)

# Dùng model 2.5 flash cho thông minh
model = genai.GenerativeModel(
  model_name="gemini-2.5-flash",
  system_instruction="Bạn là một giáo sư Lịch sử uyên bác. Hãy trả lời ngắn gọn, hấp dẫn cho học sinh. QUAN TRỌNG: Cuối mỗi câu trả lời, BẮT BUỘC phải viết thêm một mô tả hình ảnh bằng tiếng Anh trong ngoặc vuông để minh họa, ví dụ: [A painting of Dien Bien Phu battle].",
)

# --- GIAO DIỆN CHÍNH ---
st.title("📜 Trợ Lý Lịch Sử 4.0")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Lưu ý: Phiên bản đơn giản này không hiện lại ảnh/audio cũ khi F5

if prompt := st.chat_input("Hỏi thầy lịch sử điều gì?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.spinner("Thầy đang suy nghĩ và vẽ tranh..."):
            response = model.generate_content(prompt)
            raw_text = response.text
            
            # --- XỬ LÝ LỌC BỎ TIẾNG ANH ---
            # 1. Tìm tất cả các đoạn trong ngoặc [] để lấy làm lệnh vẽ tranh
            image_prompts = re.findall(r'\[(.*?)\]', raw_text)
            final_image_prompt = image_prompts[-1] if image_prompts else ""
            
            # 2. Xóa sạch các đoạn [...] khỏi văn bản hiển thị
            clean_text = re.sub(r'\[.*?\]', '', raw_text).strip()

        # --- HIỂN THỊ KẾT QUẢ ---
        with st.chat_message("assistant"):
            # Chỉ hiện văn bản tiếng Việt sạch sẽ
            st.markdown(clean_text)
            
            # Hiện ảnh minh họa
            if final_image_prompt:
                st.markdown(f"**🖼️ Minh họa:**")
                # Thêm tham số để ảnh nét hơn và không hiện logo Pollinations
                st.image(f"https://image.pollinations.ai/prompt/{final_image_prompt.replace(' ', '%20')}?width=1024&height=768&nologo=true")
            
            # Tạo giọng đọc (chỉ đọc phần tiếng Việt)
            # Dùng tên file tạm thời để tránh lỗi cache trên server
            tts = gTTS(text=clean_text, lang='vi')
            tts.save("temp_audio.mp3")
            st.audio("temp_audio.mp3")

        # Lưu vào lịch sử (Lưu bản sạch)
        st.session_state.messages.append({"role": "assistant", "content": clean_text})
        
    except Exception as e:
        st.error(f"Có lỗi xảy ra: {e}")
