"""
💬 STREAMLIT CHAT INTERFACE - VINUNI AGENTIC AI
Giao diện Chatbot & ReAct Agent Tra Cứu Đơn Hàng & Xử Lý Đổi Trả.
Chạy ứng dụng: streamlit run src/steam.py
"""

import os
import sys
import json
import streamlit as st

# Đảm bảo import các module trong thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from providers import get_llm_provider
from tools import AVAILABLE_TOOLS
from app import run_react_agent, run_baseline_chatbot, load_test_cases

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & CUSTOM STYLES
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="VinUni AI Agent - Chatbot & ReAct Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS cho giao diện hiện đại & đẹp mắt
st.markdown(
    """
    <style>
    /* Main container tweaks */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }
    
    /* Header styling */
    .header-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 24px;
        color: #f8fafc;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .header-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        color: #38bdf8;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .header-subtitle {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-top: 6px;
        margin-bottom: 0;
    }
    
    /* Status Badge */
    .badge-provider {
        background-color: #0284c7;
        color: white;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-mode {
        background-color: #10b981;
        color: white;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Trace Accordion Styling */
    .react-step-box {
        background-color: rgba(30, 41, 59, 0.5);
        border-left: 4px solid #38bdf8;
        padding: 10px 14px;
        margin: 8px 0;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.9rem;
    }
    
    /* Action & Observation blocks */
    .action-tag {
        color: #f59e0b;
        font-weight: bold;
    }
    .obs-tag {
        color: #10b981;
        font-weight: bold;
    }
    .thought-tag {
        color: #38bdf8;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "test_cases" not in st.session_state:
    try:
        st.session_state.test_cases = load_test_cases()
    except Exception:
        st.session_state.test_cases = []

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/96/bot.png", width=64)
    st.title("⚙️ Cấu Hình Agent")

    st.subheader("1. Chọn LLM Provider")
    provider_option = st.selectbox(
        "Nhà cung cấp LLM:",
        options=["mock", "gemini", "openai", "anthropic", "openrouter"],
        index=0,
        help="Chọn Provider đã cấu hình API Key trong file .env hoặc chọn mock để chạy offline test.",
    )

    st.subheader("2. Chọn Chế Độ Chạy")
    mode_option = st.radio(
        "Chế độ hoạt động:",
        options=["ReAct Agent", "Baseline Chatbot"],
        index=0,
        help="ReAct Agent hỗ trợ suy luận nhiều bước và gọi Tool. Baseline Chatbot chỉ sử dụng prompt thông thường.",
    )

    st.markdown("---")
    st.subheader("🧪 Mẫu Test Cases (Role 1)")
    if st.session_state.test_cases:
        selected_test = st.selectbox(
            "Chọn câu hỏi mẫu:",
            options=["-- Chọn câu hỏi --"] + [f"#{t['id']} - {t['category']}" for t in st.session_state.test_cases],
        )
        if selected_test != "-- Chọn câu hỏi --":
            test_id = int(selected_test.split(" - ")[0].replace("#", ""))
            case_data = next((c for c in st.session_state.test_cases if c["id"] == test_id), None)
            if case_data:
                st.info(f"**Kỳ vọng:** {case_data.get('expected_behavior', '')}")
                if st.button("📥 Nạp câu hỏi này"):
                    st.session_state.preset_prompt = case_data["question"]
                    st.rerun()

    st.markdown("---")
    st.subheader("🛠️ Registry Tools")
    with st.expander(f"Danh sách ({len(AVAILABLE_TOOLS)} tools)", expanded=False):
        for tool_name, tool_func in AVAILABLE_TOOLS.items():
            doc = tool_func.__doc__.split('\n')[0] if tool_func.__doc__ else "No doc"
            st.markdown(f"**`{tool_name}`**")
            st.caption(f"{doc}")

    st.markdown("---")
    if st.button("🗑️ Xóa Lịch Sử Chat", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.rerun()

# -----------------------------------------------------------------------------
# MAIN INTERFACE
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="header-box">
        <div class="header-title">
            🤖 VinUni AI Agent Studio
            <span class="badge-provider">{provider_option.upper()}</span>
            <span class="badge-mode">{mode_option}</span>
        </div>
        <div class="header-subtitle">
            Hệ thống Chăm Sóc Khách Hàng - Tra Cứu Đơn Hàng & Đổi Trả Tự Động bằng ReAct Pattern
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])
        
        # Display trace logs if available for assistant
        if msg["role"] == "assistant" and "trace" in msg and msg["trace"]:
            with st.expander("🔍 Xem chi tiết chuỗi suy luận ReAct (Trace Logs)", expanded=False):
                for step_data in msg["trace"]:
                    st.markdown(f"#### 🔄 Step {step_data.get('step', '?')}")
                    if "model_output" in step_data:
                        st.markdown(f"**Output từ Agent:**")
                        st.code(step_data["model_output"], language="text")
                    if "observation" in step_data:
                        st.markdown(f"**👁️ Observation:**")
                        st.info(step_data["observation"])
                    if "final_answer" in step_data:
                        st.markdown(f"**✅ Final Answer:** {step_data['final_answer']}")

# Handle User Input
preset_val = st.session_state.pop("preset_prompt", None)
user_prompt = st.chat_input("Nhập câu hỏi hoặc mã đơn hàng (Ví dụ: Tra cứu đơn DH10234)...")

if preset_val:
    user_prompt = preset_val

if user_prompt:
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_prompt)

    # 2. Get provider instance
    try:
        provider = get_llm_provider(provider_option)
    except Exception as exc:
        st.error(f"Lỗi khởi tạo Provider [{provider_option}]: {exc}")
        st.stop()

    # 3. Generate response based on selected mode
    with st.chat_message("assistant", avatar="🤖"):
        if mode_option == "ReAct Agent":
            st.markdown("⌛ *Đang suy luận và thực thi công cụ...*")
            status_container = st.status("🔄 Tiến trình ReAct đang thực thi...", expanded=True)
            
            # Call ReAct Agent
            result = run_react_agent(user_prompt, provider)
            
            # Update status container with trace steps
            status_container.update(
                label=f"✅ Hoàn tất ({result['steps']} bước, {result['tool_calls']} tool calls, Status: {result['status']})",
                state="complete" if result["status"] == "completed" else "error",
                expanded=False,
            )
            
            answer_text = result["answer"]
            st.markdown(answer_text)
            
            # Display step details inside expander
            if result.get("trace"):
                with st.expander("🔍 Chi tiết chuỗi suy luận ReAct (Thought -> Action -> Observation)", expanded=True):
                    for idx, step_item in enumerate(result["trace"], 1):
                        st.markdown(f"**Bước {step_item.get('step', idx)}:**")
                        if "model_output" in step_item:
                            st.code(step_item["model_output"], language="markdown")
                        if "observation" in step_item:
                            st.caption(f"👁️ **Observation:** {step_item['observation']}")
                        st.divider()

            # Save to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer_text,
                "trace": result.get("trace", []),
                "result": result
            })

        else: # Baseline Chatbot
            with st.spinner("🤖 Chatbot đang suy nghĩ..."):
                response = run_baseline_chatbot(user_prompt, provider)
                st.markdown(response)
                
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })
