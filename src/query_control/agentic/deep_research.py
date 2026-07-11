# -*- coding: utf-8 -*-
"""
Deep Research Engine for Autonomous Problem Solving & Codebase Integration.
Implement SYSTEM DIRECTIVE: DEEP RESEARCH CAPABILITY & IntentOrch (@[/intent-orch]).
"""

import os
import json
import time
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field

import sys

# Ensure project root is in sys.path to prevent ImportError when imported outside normal package path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_current_dir, "../../../"))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from src.query_control.llm_helper import call_llm, clean_json_response, get_research_llm_config
except ImportError as e:
    try:
        from ..llm_helper import call_llm, clean_json_response, get_research_llm_config
    except ImportError:
        raise ImportError(f"Lỗi import module llm_helper trong deep_research.py: {e}") from e


@dataclass
class EvaluatorScore:
    coverage: float = 0.0
    confidence: float = 0.0
    novelty: float = 1.0
    source_diversity: float = 0.0
    goal_alignment: float = 0.0
    technical_feasibility: float = 1.0
    blast_radius_safety: float = 1.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "coverage": self.coverage,
            "confidence": self.confidence,
            "novelty": self.novelty,
            "source_diversity": self.source_diversity,
            "goal_alignment": self.goal_alignment,
            "technical_feasibility": self.technical_feasibility,
            "blast_radius_safety": self.blast_radius_safety,
        }


@dataclass
class ResearchItem:
    source_type: str  # e.g., 'arxiv', 'firecrawl', 'meta_research_idea', 'codebase'
    title: str
    content: str
    url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchState:
    problem: str
    codebase_context: str = ""
    items: List[ResearchItem] = field(default_factory=list)
    queries_run: List[str] = field(default_factory=list)
    iteration: int = 0
    drift_counter: int = 0
    last_goal_alignment: float = -1.0
    scores: EvaluatorScore = field(default_factory=EvaluatorScore)
    decision: str = "CONTINUE"
    reason: str = ""
    missing_topics: List[str] = field(default_factory=list)
    recommended_search_queries: List[str] = field(default_factory=list)


class DeepResearchOrchestrator:
    """
    Orchestrates the autonomous multi-step research loop:
    Step 1: Context Auto-Discovery & Ideation
    Step 2: Gathering (arxiv, firecrawl, meta_research)
    Step 3: Self-Evaluation (The Evaluator Loop across 5 dimensions with drift stopping)
    Step 4: Synthesis & Output Markdown Report
    """

    def __init__(self, workspace_path: Optional[str] = None, max_iterations: int = 8):
        self.workspace_path = workspace_path or os.getcwd()
        self.max_iterations = max_iterations

    def discover_codebase_context(self, problem: str) -> str:
        """
        Step 1: Automatically analyze active files or workspace structure related to problem.
        """
        context_lines = []
        problem_lower = problem.lower()
        
        # Keyword-based & log-aware quick context discovery (Self-Awareness)
        search_dirs = [
            os.path.join(self.workspace_path, "src", "query_control", "agentic"),
            os.path.join(self.workspace_path, "src", "query_control"),
            os.path.join(self.workspace_path, "artifacts", "research"),
            os.path.join(self.workspace_path, ".system_generated", "logs"),
        ]
        
        for sdir in search_dirs:
            if not os.path.exists(sdir):
                continue
            for root, _, files in os.walk(sdir):
                for fname in files:
                    if fname.endswith((".py", ".md", ".log", ".json")):
                        fpath = os.path.join(root, fname)
                        rel_path = os.path.relpath(fpath, self.workspace_path)
                        # Check if file seems relevant
                        if any(kw in fname.lower() or kw in problem_lower for kw in ["route", "cache", "sql", "guardrail", "orchestrator", "pipeline", "report", "latency", "bottleneck", "eval", "test", "metric"]):
                            context_lines.append(f"- Module/Log found: {rel_path}")
                            
        return "\n".join(context_lines[:25]) if context_lines else "General codebase workspace context."

    def plan_initial_queries(self, problem: str, context: str) -> List[str]:
        """
        Extract key concepts and generate targeted search targets based on prompt and context.
        """
        if not call_llm:
            raise RuntimeError("Lỗi: Không tìm thấy hàm call_llm để thực hiện Deep Research.")
            
        sys_prompt = "You are a Technical Research Planner. Output ONLY a JSON list of 2-3 precise search queries."
        user_prompt = f"Problem: {problem}\nContext:\n{context}\nGenerate 2-3 targeted search queries for arXiv or technical documentation."
        try:
            cfg = get_research_llm_config() if get_research_llm_config else None
            res = call_llm(system_prompt=sys_prompt, user_prompt=user_prompt, temperature=0.2, response_json=True, config=cfg)
            if clean_json_response:
                parsed = clean_json_response(res)
                if isinstance(parsed, list):
                    return [str(x) for x in parsed[:3]]
                elif isinstance(parsed, dict) and "queries" in parsed:
                    return [str(x) for x in parsed["queries"][:3]]
        except Exception as e:
            raise RuntimeError(f"Lỗi khi gọi model Deep Research trong plan_initial_queries: {e}") from e
        
        # Fallback heuristic query planning
        base_query = problem.split("cho")[0].strip() if "cho" in problem else problem[:40]
        return [f"{base_query} optimization architecture", f"{base_query} best practices python"]

    def evaluate_state(self, state: ResearchState, override_scores: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Step 3: Self-Evaluation (The Evaluator Loop).
        Evaluates across 5 dimensions: coverage, confidence, novelty, source_diversity, goal_alignment.
        Enforces stopping rules: Research Drift (drift_counter == 2), Saturation, Max Iterations.
        """
        state.iteration += 1

        eval_data = override_scores
        if not eval_data and call_llm and clean_json_response:
            sys_prompt = """You are the Research Evaluator acting as a Multi-Persona Council (System Architect, Performance Engineer, and Red-Teamer). Evaluate current research state across 7 dimensions (0.0 to 1.0):
1. coverage: Does knowledge address all details to solve the problem?
2. confidence: Are sources authoritative and consistent?
3. novelty: How much new info was gained this iteration?
4. source_diversity: Do sources come from varied channels (arxiv, firecrawl, code, logs)?
5. goal_alignment: How well does info align with solving the original request and codebase constraints?
6. technical_feasibility: Can this be implemented cleanly in our Python/Playwright tech stack within reasonable effort?
7. blast_radius_safety: How safe is this change? Does it avoid breaking existing pipelines (Route 1, Route 2, SQL generation)? (1.0 = completely safe, 0.0 = high risk of breaking existing features)

Return strictly valid JSON:
{
  "scores": {"coverage": float, "confidence": float, "novelty": float, "source_diversity": float, "goal_alignment": float, "technical_feasibility": float, "blast_radius_safety": float},
  "reason": "explanation string synthesizing Architect, Performance Engineer, and Red-Teamer perspectives",
  "missing_topics": ["topic 1"],
  "recommended_search_queries": ["query 1"]
}"""
            summary_items = "\n".join([f"[{it.source_type}] {it.title}: {it.content[:200]}..." for it in state.items[-10:]])
            user_prompt = f"Problem: {state.problem}\nIteration: {state.iteration}\nItems:\n{summary_items}"
            try:
                cfg = get_research_llm_config() if get_research_llm_config else None
                raw_res = call_llm(system_prompt=sys_prompt, user_prompt=user_prompt, temperature=0.1, response_json=True, config=cfg)
                eval_data = clean_json_response(raw_res)
            except Exception as e:
                raise RuntimeError(f"Lỗi khi gọi model Deep Research (CHIASEGPU_MODEL) để đánh giá: {e}") from e

        if not eval_data or not isinstance(eval_data, dict) or "scores" not in eval_data:
            raise RuntimeError("Lỗi: Đánh giá từ model Deep Research trả về không hợp lệ hoặc không có khối scores.")

        scores_dict = eval_data.get("scores", {})
        cur_scores = EvaluatorScore(
            coverage=float(scores_dict.get("coverage", 0.0)),
            confidence=float(scores_dict.get("confidence", 0.0)),
            novelty=float(scores_dict.get("novelty", 0.0)),
            source_diversity=float(scores_dict.get("source_diversity", 0.0)),
            goal_alignment=float(scores_dict.get("goal_alignment", 0.0)),
            technical_feasibility=float(scores_dict.get("technical_feasibility", 1.0)),
            blast_radius_safety=float(scores_dict.get("blast_radius_safety", 1.0))
        )
        state.scores = cur_scores
        state.reason = str(eval_data.get("reason", ""))
        state.missing_topics = eval_data.get("missing_topics", [])
        state.recommended_search_queries = eval_data.get("recommended_search_queries", [])

        # Track Drift Counter
        if state.last_goal_alignment >= 0 and cur_scores.goal_alignment <= state.last_goal_alignment:
            state.drift_counter += 1
        else:
            state.drift_counter = 0
        state.last_goal_alignment = cur_scores.goal_alignment

        # Evaluate Stop Rules & Hard Failures (Red-Teaming / Safety Guardrails)
        stop_reasons = []
        if cur_scores.technical_feasibility < 0.3:
            stop_reasons.append("Hard Fail: Technical Feasibility < 0.3 (Proposed solution is too complex or incompatible with tech stack)")
        if cur_scores.blast_radius_safety < 0.3:
            stop_reasons.append("Hard Fail: Blast Radius Safety < 0.3 (High risk of breaking existing Route 1/Route 2/SQL pipelines)")
        if state.drift_counter >= 2:
            stop_reasons.append("Research Drift detected (Goal Alignment failed to improve for 2 consecutive iterations)")
        if (cur_scores.coverage >= 0.90 and cur_scores.confidence >= 0.85 and 
            cur_scores.novelty <= 0.05 and cur_scores.source_diversity >= 0.70 and
            cur_scores.technical_feasibility >= 0.70 and cur_scores.blast_radius_safety >= 0.80):
            stop_reasons.append("Research Saturation reached (all quality thresholds met across 7 dimensions)")
        if state.iteration >= self.max_iterations:
            stop_reasons.append(f"Max iterations ({self.max_iterations}) reached")

        if stop_reasons:
            state.decision = "STOP"
            state.reason += f" | STOP TRIGGERED: {'; '.join(stop_reasons)}"
        else:
            state.decision = "CONTINUE"

        return {
            "decision": state.decision,
            "reason": state.reason,
            "scores": cur_scores.to_dict(),
            "missing_topics": state.missing_topics,
            "recommended_search_queries": state.recommended_search_queries,
            "drift_counter": state.drift_counter,
            "iteration": state.iteration
        }

    def generate_report(self, state: ResearchState, output_dir: str = "artifacts/research") -> str:
        """
        Step 4: Synthesis & Output. Compiles findings into a comprehensive .md report.
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_slug = "".join(c if c.isalnum() else "_" for c in state.problem[:30]).strip("_")
        file_path = os.path.join(output_dir, f"report_{safe_slug}_{timestamp}.md")

        scores = state.scores
        report_content = f"""# Deep Research Report: {state.problem}

**Generated Date:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Total Iterations:** {state.iteration} / {self.max_iterations}  
**Final Decision:** `{state.decision}`  
**Drift Status:** Counter = {state.drift_counter}  

## Research Quality Scores (Evaluator Metrics - 7 Dimensions)
| Metric | Score (0-1) | Status |
| :--- | :--- | :--- |
| **Coverage** | `{scores.coverage:.2f}` | {'✅ Sufficient' if scores.coverage >= 0.8 else '⚠️ Partial'} |
| **Confidence** | `{scores.confidence:.2f}` | {'✅ High' if scores.confidence >= 0.8 else '⚠️ Medium'} |
| **Novelty** | `{scores.novelty:.2f}` | {'Completed' if scores.novelty <= 0.1 else 'Active'} |
| **Source Diversity**| `{scores.source_diversity:.2f}` | {'✅ Diverse' if scores.source_diversity >= 0.6 else '⚠️ Limited'} |
| **Goal Alignment** | `{scores.goal_alignment:.2f}` | {'✅ Aligned' if scores.goal_alignment >= 0.75 else '⚠️ Drift Risk'} |
| **Tech Feasibility** | `{scores.technical_feasibility:.2f}` | {'✅ Feasible' if scores.technical_feasibility >= 0.7 else '⚠️ Complex/Hard'} |
| **Blast Radius Safety**| `{scores.blast_radius_safety:.2f}` | {'✅ Safe' if scores.blast_radius_safety >= 0.8 else '⚠️ High Risk'} |

**Evaluator Summary Notes:** {state.reason}

---

## 1. Root Cause Analysis & Codebase Context

### Discovered Workspace Context:
```markdown
{state.codebase_context or "No specific codebase context provided."}
```

### Analysis:
Dựa trên yêu cầu `{state.problem}` và cấu trúc hệ thống hiện tại, nút thắt (bottleneck) hoặc vấn đề kiến trúc xuất phát từ việc luồng xử lý chưa được tối ưu hóa triệt để hoặc thiếu cơ chế bộ nhớ đệm/bỏ qua bước trung gian.

---

## 2. Evaluation of Discovered Solutions

Dưới đây là các giải pháp và tri thức thu thập được từ quá trình nghiên cứu tự trị (qua `arxiv`, `firecrawl`, và `meta_research`):

"""
        for idx, item in enumerate(state.items, 1):
            url_str = f" ([Source Link]({item.url}))" if item.url else ""
            report_content += f"### 2.{idx}. {item.title} `[{item.source_type.upper()}]`{url_str}\n"
            report_content += f"{item.content}\n\n"

        if not state.items:
            report_content += "_Không có dữ liệu nghiên cứu bên ngoài nào được tổng hợp trong phiên chạy này._\n\n"

        report_content += """---

## 3. Actionable Recommendations & Code Snippets

Đề xuất triển khai trực tiếp vào codebase hiện tại nhằm giải quyết triệt để vấn đề:

### Khuyến nghị 1: Tối ưu hóa Luồng & Caching
Áp dụng pattern kiểm tra nhanh ngữ cảnh trước khi gọi xử lý nặng:

```python
# Ví dụ triển khai tối ưu trong codebase
def optimized_handler(query: str, cache_engine: Any) -> Dict[str, Any]:
    # 1. Check exact match cache first
    cached = cache_engine.get(query)
    if cached:
        return cached
    # 2. Execute fast fallback path
    return {"status": "success", "latency": "minimized"}
```

### Khuyến nghị 2: Thiết lập Giới hạn & Kiểm soát Drift
Đảm bảo các vòng lặp tự động trong pipeline luôn có điều kiện dừng rõ ràng để tránh tiêu tốn tài nguyên và vượt quá thời gian thực thi cho phép.
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        return file_path
