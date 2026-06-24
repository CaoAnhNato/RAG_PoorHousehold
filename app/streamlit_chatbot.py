from __future__ import annotations

import sys
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import json
import os
import queue
import re
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import streamlit as st
import plotly.io as pio
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.query_control.answer_engine import ChatbotAnswerEngine
from src.query_control.clarification_engine import ClarificationEngine
from src.query_control.conversation_memory import ConversationMemory
from src.query_control.data_engine import DuckDBEngine
from src.query_control.domain_gate import DomainGate
from src.query_control.observability import ObservabilityLogger
from src.query_control.query_cache import QueryCache
from src.query_control.query_planner import QueryPlanner
from src.query_control.semantic_retriever import SemanticRetriever
from src.query_control.sql_compiler import SQLCompiler
from src.query_control.visualization_planner import VisualizationPlanner
from src.query_control.chart_validator import ChartValidator
from src.query_control.chart_renderer import ChartRenderer

PROCESSED_DIR = PROJECT_ROOT / "Processed" / "metadata" / "query_control"
SCHEMA_GRAPH_PATH = PROCESSED_DIR / "schema_graph.json"
SEMANTIC_LAYER_PATH = PROCESSED_DIR / "semantic_layer.json"
QUERY_PLAN_SCHEMA_PATH = PROCESSED_DIR / "query_plan_schema.json"
DOMAIN_GATE_CONFIG_PATH = PROCESSED_DIR / "domain_gate_config.json"
DUCKDB_CONFIG_PATH = PROCESSED_DIR / "duckdb_config.json"
CACHE_CONFIG_PATH = PROCESSED_DIR / "cache_config.json"
OBSERVABILITY_CONFIG_PATH = PROCESSED_DIR / "observability_config.json"
CLARIFICATION_CONFIG_PATH = PROCESSED_DIR / "clarification_config.json"
MEMORY_CONFIG_PATH = PROCESSED_DIR / "memory_config.json"
QDRANT_CONFIG_PATH = PROCESSED_DIR / "qdrant_index_config.json"
UI_HISTORY_DIR = PROJECT_ROOT / "Runtime" / "ui_history"

STAGE_LABELS = {
    "conversation_memory_load": "Đang tải ngữ cảnh hội thoại",
    "rule_extractor": "Đang tách thực thể và tín hiệu nghiệp vụ",
    "domain_gate": "Đang phân loại tuyến xử lý câu hỏi",
    "general_knowledge": "Đang sinh câu trả lời kiến thức chung",
    "planner": "Đang lập kế hoạch truy vấn",
    "query_plan_validation": "Đang kiểm định kế hoạch truy vấn",
    "cache_lookup": "Đang kiểm tra bộ nhớ đệm",
    "sql_compiler": "Đang biên dịch SQL",
    "duckdb_execution": "Đang thực thi truy vấn dữ liệu",
    "answer_formatting": "Đang định dạng câu trả lời",
    "conversation_memory_update": "Đang cập nhật bộ nhớ phiên",
    "final": "Đã hoàn tất xử lý",
    "error": "Đã phát sinh lỗi trong pipeline",
}


@dataclass
class SessionSummary:
    session_id: str
    title: str
    created_at: str
    updated_at: str
    turn_count: int


class UIHistoryStore:
    def __init__(self, history_dir: Path):
        self.history_dir = history_dir
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def path_for(self, session_id: str) -> Path:
        return self.history_dir / f"{session_id}.json"

    def load(self, session_id: str) -> dict[str, Any]:
        path = self.path_for(session_id)
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "session_id": session_id,
            "created_at": self._now(),
            "updated_at": self._now(),
            "turns": [],
        }

    def save(self, session_data: dict[str, Any]) -> None:
        session_data["updated_at"] = self._now()
        self.path_for(session_data["session_id"]).write_text(
            json.dumps(session_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def append_turn(self, session_id: str, question: str, answer: str, chart_json: str | None = None, data_json: str | None = None) -> None:
        session_data = self.load(session_id)
        session_data["turns"].append(
            {
                "question": question,
                "answer": answer,
                "chart_json": chart_json,
                "data_json": data_json,
                "timestamp": self._now(),
            }
        )
        self.save(session_data)

    def list_sessions(self) -> list[SessionSummary]:
        summaries: list[SessionSummary] = []
        for path in sorted(self.history_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            turns = data.get("turns", [])
            title = turns[0]["question"] if turns else data.get("session_id", path.stem)
            summaries.append(
                SessionSummary(
                    session_id=data.get("session_id", path.stem),
                    title=self._truncate(title),
                    created_at=data.get("created_at", ""),
                    updated_at=data.get("updated_at", ""),
                    turn_count=len(turns),
                )
            )
        return summaries

    @staticmethod
    def _truncate(text: str, limit: int = 42) -> str:
        compact = re.sub(r"\s+", " ", text).strip()
        if len(compact) <= limit:
            return compact
        return compact[: limit - 3].rstrip() + "..."

    @staticmethod
    def _now() -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


class StreamlitObservabilityLogger(ObservabilityLogger):
    def __init__(self, config_path: str, event_queue: queue.Queue[str] | None = None):
        super().__init__(config_path=config_path)
        self.event_queue = event_queue
        self._seen_stages: set[str] = set()

    def log_event(self, trace_id: str, stage: str, payload: dict[str, Any]):
        super().log_event(trace_id, stage, payload)
        self._push_stage(stage)

    def log_error(self, trace_id: str, stage: str, error: dict[str, Any]):
        super().log_error(trace_id, stage, error)
        self._push_stage("error")

    def _push_stage(self, stage: str) -> None:
        if not self.event_queue or stage in self._seen_stages:
            return
        self._seen_stages.add(stage)
        self.event_queue.put(stage)


def make_session_id() -> str:
    return f"streamlit_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


@st.cache_resource(show_spinner=False)
def get_shared_pipeline() -> Any:
    # Busted cache to reload DomainGate changes
    from src.query_control.agentic.agent_pipeline import AgenticPipeline
    return AgenticPipeline()

def build_engine(session_id: str, event_queue: queue.Queue[str] | None = None) -> Any:
    # AgenticPipeline is stateless, reuse the shared instance
    return get_shared_pipeline()


def bootstrap_state(history_store: UIHistoryStore) -> None:
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = make_session_id()
    if "loaded_session_id" not in st.session_state:
        st.session_state.loaded_session_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_options" not in st.session_state:
        st.session_state.pending_options = []
    if "current_mode" not in st.session_state:
        st.session_state.current_mode = "Auto"
    load_session_into_state(st.session_state.current_session_id, history_store)


def load_session_into_state(session_id: str, history_store: UIHistoryStore) -> None:
    if st.session_state.loaded_session_id == session_id:
        return
    data = history_store.load(session_id)
    st.session_state.current_session_id = session_id
    st.session_state.loaded_session_id = session_id
    st.session_state.pending_options = []
    st.session_state.messages = []
    for turn in data.get("turns", []):
        st.session_state.messages.append({"role": "user", "content": turn.get("question", "")})
        
        assistant_msg = {"role": "assistant", "content": turn.get("answer", "")}
        if turn.get("chart_json"):
            try:
                assistant_msg["chart_fig"] = pio.from_json(turn.get("chart_json"))
            except Exception:
                pass
                
        if turn.get("data_json"):
            try:
                import pandas as pd
                assistant_msg["data"] = pd.read_json(turn.get("data_json"), orient="split")
            except Exception:
                pass
                
        st.session_state.messages.append(assistant_msg)


def create_new_session(history_store: UIHistoryStore) -> None:
    new_session_id = make_session_id()
    load_session_into_state(new_session_id, history_store)


def render_sidebar(history_store: UIHistoryStore) -> None:
    st.sidebar.title("Cài đặt")
    modes = ["Auto", "Hỏi - Đáp", "Biểu đồ", "Báo Cáo"]
    default_idx = modes.index(st.session_state.current_mode) if st.session_state.current_mode in modes else 0
    st.session_state.current_mode = st.sidebar.selectbox("Chế độ (Mode)", options=modes, index=default_idx)
    
    st.sidebar.divider()
    st.sidebar.title("Lịch sử phiên")
    if st.sidebar.button("Tạo phiên mới", width="stretch"):
        create_new_session(history_store)
        st.rerun()

    sessions = history_store.list_sessions()
    if st.session_state.current_session_id not in {item.session_id for item in sessions}:
        sessions.insert(
            0,
            SessionSummary(
                session_id=st.session_state.current_session_id,
                title="Phiên hiện tại",
                created_at="",
                updated_at="",
                turn_count=len(st.session_state.messages) // 2,
            ),
        )

    options = [summary.session_id for summary in sessions]
    labels = {
        summary.session_id: f"{summary.title} · {summary.turn_count} lượt"
        for summary in sessions
    }

    default_index = 0
    if st.session_state.current_session_id in options:
        default_index = options.index(st.session_state.current_session_id)

    selected_session = st.sidebar.radio(
        "Chọn phiên để xem lại",
        options=options,
        index=default_index,
        format_func=lambda session_id: labels[session_id],
    )
    if selected_session != st.session_state.current_session_id:
        load_session_into_state(selected_session, history_store)
        st.rerun()

    active_summary = next(item for item in sessions if item.session_id == selected_session)
    st.sidebar.caption(f"Mã phiên: `{active_summary.session_id}`")
    st.sidebar.caption(f"Cập nhật: {active_summary.updated_at}")


def stream_text(text: str):
    for chunk in re.split(r"(\s+)", text):
        if chunk:
            yield chunk
            time.sleep(0.015)


def resolve_option_input(option: dict[str, Any], session_id: str) -> str:
    value = option.get("value")
    if isinstance(value, dict) and "route_override" in value:
        core_session_path = PROJECT_ROOT / "Runtime" / "conversations" / f"{session_id}.json"
        if core_session_path.exists():
            try:
                data = json.loads(core_session_path.read_text(encoding="utf-8"))
                turns = data.get("turns", [])
                if turns:
                    return f"{turns[-1].get('user_question', '').strip()} ({option.get('label', '')})".strip()
            except Exception:
                pass
        return option.get("label", "")
    if value is None:
        return option.get("label", "")
    return str(value)


def drain_stage_queue(event_queue: queue.Queue[str], stages: list[str]) -> None:
    while True:
        try:
            stage = event_queue.get_nowait()
        except queue.Empty:
            return
        if stage not in stages:
            stages.append(stage)


def render_status_lines(stages: list[str], pulse_index: int) -> str:
    if not stages:
        dots = "." * ((pulse_index % 3) + 1)
        return f"⏳ Đang khởi động pipeline{dots}"

    lines: list[str] = []
    for index, stage in enumerate(stages):
        icon = "✅" if index < len(stages) - 1 else "⏳"
        label = STAGE_LABELS.get(stage, stage)
        if index == len(stages) - 1:
            dots = "." * ((pulse_index % 3) + 1)
            lines.append(f"{icon} {label}{dots}")
        else:
            lines.append(f"{icon} {label}")
    return "\n\n".join(lines)


def run_pipeline(user_prompt: str, session_id: str, mode: str) -> dict[str, Any]:
    event_queue: queue.Queue[str] = queue.Queue()
    status_placeholder = st.empty()
    stages: list[str] = []

    def _worker() -> dict[str, Any]:
        engine = build_engine(session_id=session_id, event_queue=event_queue)
        return engine.process(user_prompt, mode=mode)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_worker)
        pulse_index = 0
        while not future.done():
            drain_stage_queue(event_queue, stages)
            status_placeholder.markdown(render_status_lines(stages, pulse_index))
            time.sleep(0.12)
            pulse_index += 1

        drain_stage_queue(event_queue, stages)
        status_placeholder.markdown(render_status_lines(stages + ["final"], pulse_index))
        response = future.result()
        time.sleep(0.25)
        status_placeholder.empty()
        return response


def format_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Gộp các dòng trùng giá trị bằng cách thiết lập MultiIndex
    idx_candidates = ["Năm", "Huyện", "Xã", "Thôn/Bon", "Phân loại hộ", "Loại hộ", "Thiếu hụt"]
    idx_cols = [c for c in df.columns if c in idx_candidates]
    if idx_cols:
        df = df.sort_values(by=idx_cols)
        df = df.set_index(idx_cols)
    return df

def assistant_text_from_response(response: dict[str, Any]) -> Any:
    return response.get("answer", "Không nhận được nội dung phản hồi từ pipeline.")


def handle_prompt(user_prompt: str, history_store: UIHistoryStore) -> None:
    session_id = st.session_state.current_session_id
    mode = st.session_state.current_mode
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        response = run_pipeline(user_prompt=user_prompt, session_id=session_id, mode=mode)
        
        ans = assistant_text_from_response(response)
        
        # Nếu LLM quyết định trả về bảng (do > 5 dòng)
        if hasattr(ans, 'to_markdown'):
            formatted_ans = format_dataframe(ans)
            hide_idx = True if formatted_ans.index.name is None and not isinstance(formatted_ans.index, pd.MultiIndex) else False
            st.dataframe(formatted_ans, hide_index=hide_idx)
            final_text = "Kết quả bảng dữ liệu."
            response["data"] = formatted_ans
        else:
            streamed_text = st.write_stream(stream_text(str(ans)))
            final_text = streamed_text if isinstance(streamed_text, str) else str(ans)
            
        if response.get("chart_fig"):
            st.plotly_chart(response["chart_fig"], width="stretch", key="current_chart")
            
        # Nếu có data đi kèm (trong chế độ Biểu đồ hoặc data chưa được in ra)
        if response.get("data") is not None and not response.get("data").empty and not hasattr(ans, 'to_markdown'):
            formatted_data = format_dataframe(response["data"])
            hide_idx = True if formatted_data.index.name is None and not isinstance(formatted_data.index, pd.MultiIndex) else False
            st.dataframe(formatted_data, hide_index=hide_idx)
            response["data"] = formatted_data

    assistant_msg = {"role": "assistant", "content": final_text}
    chart_json_str = None
    data_json_str = None
    
    if response.get("chart_fig"):
        try:
            assistant_msg["chart_fig"] = response["chart_fig"]
            chart_json_str = response["chart_fig"].to_json()
        except Exception:
            pass
            
    if response.get("data") is not None and not response.get("data").empty:
        try:
            assistant_msg["data"] = response["data"]
            data_json_str = response["data"].to_json(orient="split")
        except Exception:
            pass

    st.session_state.messages.append(assistant_msg)
    st.session_state.pending_options = []
    history_store.append_turn(session_id=session_id, question=user_prompt, answer=final_text, chart_json=chart_json_str, data_json=data_json_str)


def render_pending_options(history_store: UIHistoryStore) -> None:
    options = st.session_state.pending_options
    if not options:
        return

    st.markdown("**Làm rõ yêu cầu**")
    columns = st.columns(len(options))
    for index, option in enumerate(options):
        label = option.get("label", f"Lựa chọn {index + 1}")
        if columns[index].button(label, key=f"clarify_{index}", width="stretch"):
            st.session_state.pending_options = []
            prompt = resolve_option_input(option, st.session_state.current_session_id)
            handle_prompt(prompt, history_store)
            st.rerun()


def main() -> None:
    st.set_page_config(
        page_title="Chatbot Q&A Đắk Nông",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Chatbot Q&A rà soát hộ nghèo")
    st.caption(
        "UI Streamlit dùng lại pipeline Q&A hiện có, lưu lịch sử phiên trong Runtime và phát phản hồi theo kiểu streaming."
    )

    history_store = UIHistoryStore(UI_HISTORY_DIR)
    bootstrap_state(history_store)
    render_sidebar(history_store)

    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("chart_fig"):
                st.plotly_chart(message["chart_fig"], width="stretch", key=f"history_chart_{idx}")
            if "data" in message and message.get("data") is not None and not message["data"].empty:
                df = message["data"]
                hide_idx = True if df.index.name is None and not isinstance(df.index, pd.MultiIndex) else False
                st.dataframe(df, hide_index=hide_idx)

    render_pending_options(history_store)

    user_prompt = st.chat_input("Nhập câu hỏi về nghiệp vụ hoặc số liệu rà soát hộ nghèo...")
    if user_prompt:
        handle_prompt(user_prompt, history_store)
        st.rerun()


if __name__ == "__main__":
    main()
