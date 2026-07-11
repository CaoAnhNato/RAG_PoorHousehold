# -*- coding: utf-8 -*-
"""
Automated unit tests for Deep Research Engine (/deep_research).
Verifies 5-dimension Evaluator Loop, drift counter stopping rules, saturation detection, and markdown report synthesis.
"""

import os
import shutil
import tempfile
import unittest
from src.query_control.agentic.deep_research import (
    DeepResearchOrchestrator,
    ResearchState,
    ResearchItem,
    EvaluatorScore
)


class TestDeepResearchOrchestrator(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.orchestrator = DeepResearchOrchestrator(workspace_path=self.test_dir, max_iterations=5)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_evaluator_drift_stop(self):
        """Test that 2 consecutive iterations without goal_alignment improvement trigger STOP."""
        state = ResearchState(problem="Test Drift Problem")
        state.last_goal_alignment = 0.80

        # Iteration 1: goal_alignment drops to 0.75 -> drift_counter becomes 1
        override_1 = {
            "scores": {
                "coverage": 0.5, "confidence": 0.6, "novelty": 0.3,
                "source_diversity": 0.5, "goal_alignment": 0.75
            },
            "reason": "First drop"
        }
        res1 = self.orchestrator.evaluate_state(state, override_scores=override_1)
        self.assertEqual(res1["drift_counter"], 1)
        self.assertEqual(res1["decision"], "CONTINUE")

        # Iteration 2: goal_alignment stays 0.75 (no improvement) -> drift_counter becomes 2 -> STOP
        override_2 = {
            "scores": {
                "coverage": 0.6, "confidence": 0.7, "novelty": 0.2,
                "source_diversity": 0.6, "goal_alignment": 0.75
            },
            "reason": "Second drop/stagnation"
        }
        res2 = self.orchestrator.evaluate_state(state, override_scores=override_2)
        self.assertEqual(res2["drift_counter"], 2)
        self.assertEqual(res2["decision"], "STOP")
        self.assertIn("Research Drift detected", res2["reason"])

    def test_evaluator_saturation_stop(self):
        """Test that reaching quality saturation thresholds across 7 dimensions triggers STOP."""
        state = ResearchState(problem="Test Saturation Problem")
        override_sat = {
            "scores": {
                "coverage": 0.92,
                "confidence": 0.88,
                "novelty": 0.03,
                "source_diversity": 0.75,
                "goal_alignment": 0.90,
                "technical_feasibility": 0.85,
                "blast_radius_safety": 0.90
            },
            "reason": "High quality across all 7 dimensions"
        }
        res = self.orchestrator.evaluate_state(state, override_scores=override_sat)
        self.assertEqual(res["decision"], "STOP")
        self.assertIn("Research Saturation reached", res["reason"])

    def test_evaluator_continue(self):
        """Test normal progression where quality is improving and thresholds not met."""
        state = ResearchState(problem="Test Continue Problem")
        state.last_goal_alignment = 0.50
        override_cont = {
            "scores": {
                "coverage": 0.40,
                "confidence": 0.50,
                "novelty": 0.80,
                "source_diversity": 0.40,
                "goal_alignment": 0.70
            },
            "reason": "Found good initial papers",
            "recommended_search_queries": ["query A", "query B"]
        }
        res = self.orchestrator.evaluate_state(state, override_scores=override_cont)
        self.assertEqual(res["decision"], "CONTINUE")
        self.assertEqual(res["drift_counter"], 0)
        self.assertEqual(res["recommended_search_queries"], ["query A", "query B"])

    def test_evaluator_hard_fail_technical_feasibility(self):
        """Test that technical_feasibility < 0.3 triggers immediate Hard Fail STOP."""
        state = ResearchState(problem="Test Hard Fail Feasibility")
        override_fail = {
            "scores": {
                "coverage": 0.80,
                "confidence": 0.80,
                "novelty": 0.50,
                "source_diversity": 0.80,
                "goal_alignment": 0.85,
                "technical_feasibility": 0.20,
                "blast_radius_safety": 0.90
            },
            "reason": "Solution requires rewriting the entire compiler in Assembly"
        }
        res = self.orchestrator.evaluate_state(state, override_scores=override_fail)
        self.assertEqual(res["decision"], "STOP")
        self.assertIn("Hard Fail: Technical Feasibility < 0.3", res["reason"])

    def test_evaluator_hard_fail_blast_radius(self):
        """Test that blast_radius_safety < 0.3 triggers immediate Hard Fail STOP."""
        state = ResearchState(problem="Test Hard Fail Blast Radius")
        override_fail = {
            "scores": {
                "coverage": 0.85,
                "confidence": 0.85,
                "novelty": 0.40,
                "source_diversity": 0.80,
                "goal_alignment": 0.85,
                "technical_feasibility": 0.80,
                "blast_radius_safety": 0.15
            },
            "reason": "Solution modifies core Route 1 & 2 shared schemas without backwards compatibility"
        }
        res = self.orchestrator.evaluate_state(state, override_scores=override_fail)
        self.assertEqual(res["decision"], "STOP")
        self.assertIn("Hard Fail: Blast Radius Safety < 0.3", res["reason"])

    def test_report_synthesis_format(self):
        """Test that generated markdown report contains required 3 sections and code snippets."""
        state = ResearchState(
            problem="Tối ưu hóa Route 3 dưới 7s",
            codebase_context="Route 3 đang mất 9.2s cho LLM re-write và SQL execution.",
            decision="STOP",
            reason="Saturation reached."
        )
        state.items.append(ResearchItem(
            source_type="arxiv",
            title="Fast LLM Routing and Caching",
            content="Semantic caching reduces latency by 75%.",
            url="https://arxiv.org/abs/2401.00000"
        ))

        report_dir = os.path.join(self.test_dir, "artifacts", "research")
        report_path = self.orchestrator.generate_report(state, output_dir=report_dir)

        self.assertTrue(os.path.exists(report_path))
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("# Deep Research Report: Tối ưu hóa Route 3 dưới 7s", content)
        self.assertIn("## 1. Root Cause Analysis & Codebase Context", content)
        self.assertIn("## 2. Evaluation of Discovered Solutions", content)
        self.assertIn("### 2.1. Fast LLM Routing and Caching `[ARXIV]`", content)
        self.assertIn("## 3. Actionable Recommendations & Code Snippets", content)
        self.assertIn("def optimized_handler(", content)


if __name__ == "__main__":
    unittest.main()
