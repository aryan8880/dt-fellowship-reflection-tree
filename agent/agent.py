#!/usr/bin/env python3
"""
Daily Reflection Tree — CLI Agent
Part B of the DT Fellowship Assignment.

Loads reflection-tree.json and walks the employee through
a fully deterministic, LLM-free reflection session.

Usage:
    python agent.py
    python agent.py --tree path/to/reflection-tree.json
    python agent.py --transcript   # saves session to transcripts/
"""

import json
import sys
import os
import time
import argparse
from datetime import datetime
from pathlib import Path


# ─── Colour helpers ───────────────────────────────────────────────────────────

def c(text, code):
    """Wrap text in an ANSI colour code (skipped when not a TTY)."""
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"

GREEN   = lambda t: c(t, "32")
CYAN    = lambda t: c(t, "36")
YELLOW  = lambda t: c(t, "33")
DIM     = lambda t: c(t, "2")
BOLD    = lambda t: c(t, "1")
MAGENTA = lambda t: c(t, "35")


# ─── Tree loader ──────────────────────────────────────────────────────────────

def load_tree(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    nodes = {n["id"]: n for n in data["nodes"]}
    return nodes


# ─── State management ─────────────────────────────────────────────────────────

class SessionState:
    def __init__(self):
        self.answers: dict   = {}   # node_id → chosen option label
        self.values: dict    = {}   # node_id → chosen option value
        self.signals: dict   = {    # axis tallies
            "axis1": {"internal": 0, "external": 0},
            "axis2": {"contribution": 0, "entitlement": 0},
            "axis3": {"altrocentric": 0, "self_centric": 0},
        }
        self.path: list      = []   # visited node IDs in order

    def record_answer(self, node_id: str, label: str, value: str, signal: str | None):
        self.answers[node_id] = label
        self.values[node_id]  = value
        if signal:
            axis, pole = signal.split(":")
            self.signals[axis][pole] += 1
        self.path.append(node_id)

    def record_visit(self, node_id: str):
        self.path.append(node_id)

    def dominant(self, axis: str) -> str:
        tallies = self.signals[axis]
        keys = list(tallies.keys())
        if tallies[keys[0]] >= tallies[keys[1]]:
            return keys[0]
        return keys[1]

    def interpolate(self, text: str) -> str:
        """Replace {node_id.value} placeholders with recorded answers."""
        import re
        def replacer(match):
            ref  = match.group(1)  # e.g. "A1_OPEN.value"
            parts = ref.split(".")
            node_id = parts[0]
            attr    = parts[1] if len(parts) > 1 else "value"
            if attr == "value":
                return self.values.get(node_id, f"[{node_id}]")
            elif attr == "answer":
                return self.answers.get(node_id, f"[{node_id}]")
            # axis summary shortcuts
            elif node_id.startswith("axis") and attr == "dominant":
                return self.dominant(node_id)
            return match.group(0)
        text = re.sub(r"\{([^}]+)\}", replacer, text)
        # Replace axis placeholders
        for ax in ["axis1", "axis2", "axis3"]:
            text = text.replace(f"{{{ax}.dominant}}", self.dominant(ax))
        return text

    def summary_key(self) -> str:
        return "_".join([
            self.dominant("axis1"),
            self.dominant("axis2"),
            self.dominant("axis3"),
        ])


# ─── Routing engine ───────────────────────────────────────────────────────────

def evaluate_condition(condition: str, state: SessionState) -> bool:
    """
    Evaluate a simple condition string. Supported forms:
        node_id.value IN [a, b, c]
        axis1.dominant == internal
    """
    condition = condition.strip()

    # Form: axis1.dominant == internal
    if ".dominant ==" in condition:
        parts = condition.split("==")
        axis  = parts[0].strip().split(".")[0].strip()
        pole  = parts[1].strip()
        return state.dominant(axis) == pole

    # Form: node_id.value IN [a, b]
    if " IN " in condition:
        parts    = condition.split(" IN ")
        ref      = parts[0].strip()
        node_id  = ref.split(".")[0]
        raw_list = parts[1].strip().strip("[]")
        values   = [v.strip() for v in raw_list.split(",")]
        actual   = state.values.get(node_id, "")
        return actual in values

    return False


def next_node_id(node: dict, state: SessionState) -> str | None:
    """Determine the next node to visit."""
    ntype = node["type"]

    if ntype == "decision":
        for opt in node["options"]:
            if evaluate_condition(opt["condition"], state):
                return opt["target"]
        return None

    # For question nodes: target is the next node (could be a decision)
    if node.get("target"):
        return node["target"]

    return None


# ─── Renderer ─────────────────────────────────────────────────────────────────

def print_separator():
    print("\n" + DIM("─" * 56) + "\n")

def slow_print(text: str, delay: float = 0.012):
    """Print text character by character for a slightly human feel."""
    if not sys.stdout.isatty():
        print(text)
        return
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()

def render_start(node: dict, state: SessionState, transcript: list):
    text = state.interpolate(node["text"])
    print_separator()
    slow_print(BOLD(CYAN("✦  " + text)))
    transcript.append(f"\n[START]\n{text}")
    print()
    input(DIM("  Press Enter to begin..."))

def render_bridge(node: dict, state: SessionState, transcript: list):
    text = state.interpolate(node["text"])
    print_separator()
    slow_print(MAGENTA("◈  " + text))
    transcript.append(f"\n[BRIDGE]\n{text}")
    print()
    time.sleep(0.8)

def render_reflection(node: dict, state: SessionState, transcript: list):
    text = state.interpolate(node["text"])
    print_separator()
    slow_print(GREEN("❧  " + text))
    transcript.append(f"\n[REFLECTION]\n{text}")
    print()
    input(DIM("  Take a moment. Press Enter when ready..."))

def render_question(node: dict, state: SessionState, transcript: list) -> tuple[str, str]:
    text    = state.interpolate(node["text"])
    options = node["options"]
    print_separator()
    slow_print(BOLD("   " + text))
    print()
    for i, opt in enumerate(options, 1):
        print(f"  {CYAN(str(i))}.  {opt['label']}")
    print()
    transcript.append(f"\n[Q: {node['id']}]\n{text}")
    for i, opt in enumerate(options, 1):
        transcript.append(f"  {i}. {opt['label']}")

    while True:
        raw = input(DIM("  Your choice (1-" + str(len(options)) + "): ")).strip()
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                chosen = options[idx]
                print(f"\n  {DIM('→')} {chosen['label']}")
                transcript.append(f"\n  → {chosen['label']}")
                return chosen["label"], chosen["value"], chosen.get("signal")
        print(DIM("  Please enter a number between 1 and " + str(len(options))))

def render_summary(node: dict, state: SessionState, transcript: list):
    reflections = node.get("summary_reflections", {})
    key         = state.summary_key()
    summary_ref = reflections.get(key, "Every day holds something worth noticing. That's enough.")
    text        = state.interpolate(node["text"])
    text        = text.replace("{summary_reflection}", summary_ref)
    print_separator()
    print(BOLD(YELLOW("━" * 56)))
    print(BOLD(YELLOW("  TODAY'S REFLECTION")))
    print(BOLD(YELLOW("━" * 56)))
    print()
    slow_print(text, delay=0.008)
    print()
    print(DIM(f"  Path: {' → '.join(state.path)}"))
    print(DIM(f"  Axis signals: {state.signals}"))
    transcript.append(f"\n[SUMMARY]\n{text}")
    transcript.append(f"\nPath: {' → '.join(state.path)}")

def render_end(node: dict, state: SessionState, transcript: list):
    text = state.interpolate(node["text"])
    print_separator()
    slow_print(CYAN("  " + text))
    transcript.append(f"\n[END]\n{text}")
    print()


# ─── Main walker ──────────────────────────────────────────────────────────────

def walk(nodes: dict, save_transcript: bool = False):
    state      = SessionState()
    transcript = [f"=== Daily Reflection Session | {datetime.now().strftime('%Y-%m-%d %H:%M')} ==="]
    current_id = "START"

    while current_id is not None:
        node  = nodes[current_id]
        ntype = node["type"]

        state.record_visit(current_id)

        if ntype == "start":
            render_start(node, state, transcript)
            current_id = node.get("target") or next_node_id(node, state)

        elif ntype == "question":
            label, value, signal = render_question(node, state, transcript)
            state.record_answer(current_id, label, value, signal)
            current_id = next_node_id(node, state)

        elif ntype == "decision":
            current_id = next_node_id(node, state)

        elif ntype == "reflection":
            render_reflection(node, state, transcript)
            current_id = node.get("target") or next_node_id(node, state)

        elif ntype == "bridge":
            render_bridge(node, state, transcript)
            current_id = node.get("target") or next_node_id(node, state)

        elif ntype == "summary":
            render_summary(node, state, transcript)
            current_id = node.get("target") or next_node_id(node, state)

        elif ntype == "end":
            render_end(node, state, transcript)
            current_id = None

        else:
            print(f"[Unknown node type: {ntype}]")
            current_id = None

    if save_transcript:
        ts_dir = Path("transcripts")
        ts_dir.mkdir(exist_ok=True)
        fname = ts_dir / f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(transcript))
        print(DIM(f"\n  Session saved to {fname}"))


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Daily Reflection Tree CLI Agent")
    parser.add_argument("--tree",       default="tree/reflection-tree.json",
                        help="Path to the tree JSON file")
    parser.add_argument("--transcript", action="store_true",
                        help="Save session to transcripts/")
    args = parser.parse_args()

    if not os.path.exists(args.tree):
        print(f"Error: tree file not found at '{args.tree}'")
        sys.exit(1)

    nodes = load_tree(args.tree)
    walk(nodes, save_transcript=args.transcript)


if __name__ == "__main__":
    main()
