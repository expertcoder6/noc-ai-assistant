#!/usr/bin/env python3
"""Intent regression test runner.

Loads the 50+ question→intent fixture from backend/tests/fixtures/intents.json
and calls the live Gemini API to verify each question maps to the expected intent.

Usage:
    python scripts/test_intents.py

Environment variables required (same as .env):
    GEMINI_API_KEY  - Your Gemini API key

Output:
    - Per-question PASS/FAIL with reason
    - Summary: X/Y passed (Z%)
    - Exit code 0 on success, 1 if failure rate exceeds threshold (>10%)
"""
import sys
import os
import json
import asyncio
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

FIXTURE_PATH = os.path.join(PROJECT_ROOT, "backend", "tests", "fixtures", "intents.json")
FAILURE_THRESHOLD = 0.10  # Doc requirement: parse failure rate must stay below 10%

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


async def run_regression():
    from backend.app.llm.client import GeminiClient

    # Load fixture
    with open(FIXTURE_PATH, "r") as f:
        cases = json.load(f)

    client = GeminiClient()

    passed = 0
    failed = 0
    errors = 0
    results = []

    print(f"\n{BOLD}🔍 Running intent regression test — {len(cases)} cases{RESET}\n")
    print(f"{'#':>3}  {'Question':<55} {'Expected':<20} {'Got':<20} {'Result'}")
    print("-" * 110)

    for i, case in enumerate(cases, 1):
        question = case["input"]
        expected = case["expected_intent"]
        start = time.time()

        try:
            result = await client.extract_intent(question)
            got_intent = result.get("intent", "MISSING")
            latency = int((time.time() - start) * 1000)

            if got_intent == expected:
                passed += 1
                status = f"{GREEN}PASS{RESET}"
            else:
                failed += 1
                status = f"{RED}FAIL{RESET}"

            results.append({
                "question": question,
                "expected": expected,
                "got": got_intent,
                "latency_ms": latency,
                "pass": got_intent == expected
            })

            q_short = question[:52] + "..." if len(question) > 52 else question
            print(f"{i:>3}  {q_short:<55} {expected:<20} {got_intent:<20} {status}  ({latency}ms)")

        except Exception as exc:
            errors += 1
            status = f"{YELLOW}ERROR{RESET}"
            print(f"{i:>3}  {question[:52]:<55} {expected:<20} {'ERROR':<20} {status}  ({exc})")
            results.append({"question": question, "expected": expected, "got": "ERROR", "pass": False})

        # Throttle to avoid rate limiting (Gemini free tier: 20 req/min)
        if i % 15 == 0:
            print(f"\n  ⏳ Pausing 65s to stay within API rate limits...\n")
            await asyncio.sleep(65)
        else:
            await asyncio.sleep(2.0)

    total = len(cases)
    pass_rate = passed / total if total > 0 else 0
    fail_rate = (failed + errors) / total if total > 0 else 0

    print("\n" + "=" * 110)
    print(f"\n{BOLD}📊 Results Summary{RESET}")
    print(f"  Total cases : {total}")
    print(f"  Passed      : {GREEN}{passed}{RESET}")
    print(f"  Failed      : {RED}{failed}{RESET}")
    print(f"  Errors      : {YELLOW}{errors}{RESET}")
    print(f"  Pass rate   : {BOLD}{pass_rate*100:.1f}%{RESET}")

    if fail_rate > FAILURE_THRESHOLD:
        print(f"\n{RED}❌ REGRESSION ALERT: Failure rate {fail_rate*100:.1f}% exceeds {FAILURE_THRESHOLD*100:.0f}% threshold.{RESET}")
        print("   → Review and update prompts in backend/app/llm/prompts.py\n")
        sys.exit(1)
    else:
        print(f"\n{GREEN}✅ Regression passed — failure rate {fail_rate*100:.1f}% is within the {FAILURE_THRESHOLD*100:.0f}% threshold.{RESET}\n")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(run_regression())
