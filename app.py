import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import re
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Trợ Lý Lịch Sử", page_icon="📜", layout="centered")

# --- CSS "HẠT NHÂN" ĐỂ ẨN MỌI THỨ ---
hide_elements = """
<style>
    /* Ẩn Header (cái vạch màu trên cùng) */
    header[data-testid="stHeader"] {
        visibility: hidden;
        height: 0%;
    }
    
    /* Ẩn Decoration (vạch màu cầu vồng) */
    div[data-testid="stDecoration"] {
        visibility: hidden;
        height: 0%;
    }

    /* Ẩn Toolbar (Nút 3 gạch và nút Manage App) */
    div[data-testid="stToolbar"] {
        visibility: hidden;
        display: none;
    }

    /* Ẩn Footer (Dòng Made with Streamlit) */
    footer {
        visibility: hidden;
        display: none;
    }

    /* Ẩn nút Deploy (nếu còn sót) */
    .stDeployButton {
        visibility: hidden;
        display: none;
    }
    
    /* Ẩn thanh trạng thái góc trên bên phải */
    div[data-testid="stStatusWidget"] {
        visibility: hidden;
    }
    
    /* Chỉnh lề trên cùng để web sát lên trên sau khi ẩn header */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
</style>
"""
st.markdown(hide_elements, unsafe_allow_html=True)

# --- CẤU HÌNH AI ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Chưa thiết lập GOOGLE_API_KEY trong Secrets!")
    st.stop()

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
  model_name="gemini-2.5-flash",
  system_instruction="Bạn là một giáo sư Lịch sử uyên bác. Hãy trả lời ngắn gọn, hấp dẫn cho học sinh. QUAN TRỌNG: Cuối mỗi câu trả lời, BẮT BUỘC phải viết thêm một mô tả hình ảnh bằng tiếng Anh trong ngoặc vuông để minh họa, ví dụ: [A painting of Dien Bien Phu battle].",
)

# --- GIAO DIỆN CHÍNH ---
st.title("📜 Trợ Lý Lịch Sử 4.0")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Hỏi thầy lịch sử điều gì?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.spinner("Thầy đang suy nghĩ và vẽ tranh..."):
            response = model.generate_content(prompt)
            raw_text = response.text
            
            # Xử lý lọc ảnh
            image_prompts = re.findall(r'\[(.*?)\]', raw_text)
            final_image_prompt = image_prompts[-1] if image_prompts else ""
            clean_text = re.sub(r'\[.*?\]', '', raw_text).strip()

        with st.chat_message("assistant"):
            st.markdown(clean_text)
            
            if final_image_prompt:
                st.markdown(f"**🖼️ Minh họa:**")
                st.image(f"https://image.pollinations.ai/prompt/{final_image_prompt.replace(' ', '%20')}?width=1024&height=768&nologo=true")
            
            # Tạo Audio (Dùng tên ngẫu nhiên để tránh cache nếu cần, ở đây dùng temp)
            tts = gTTS(text=clean_text, lang='vi')
            tts.save("temp_audio.mp3")
            st.audio("temp_audio.mp3")

        st.session_state.messages.append({"role": "assistant", "content": clean_text})
        
    except Exception as e:
        st.error(f"Có lỗi xảy ra: {e}")
