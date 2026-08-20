# ==============================================================================
# Enterprise QA RAG CLI Tool
# Command Line Interface to Index, Generate Tests, and Analyze Failures
# Usage:
#   python utils/rag_cli.py index
#   python utils/rag_cli.py generate --prompt "Test Driveway permit creation"
#   python utils/rag_cli.py analyze --trace "TimeoutError: element #btn-submit not visible"
# ==============================================================================

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.rag_engine import QARagEngine

def main():
    parser = argparse.ArgumentParser(description="Enterprise QA RAG Command Line Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available Commands")

    # Index command
    index_parser = subparsers.add_parser("index", help="Index all Page Objects and Test Data into Vector Store")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate Pytest Playwright Test Script using RAG Memory")
    gen_parser.add_argument("--prompt", type=str, required=True, help="Test requirement in plain English")
    gen_parser.add_argument("--project", type=str, default="NJDOT_EPermitting_System", help="Target sub-project name")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a Playwright Test Failure Trace")
    analyze_parser.add_argument("--trace", type=str, required=True, help="Failure error traceback text")
    analyze_parser.add_argument("--test-name", type=str, default="TestFailure", help="Name of failing test")
    analyze_parser.add_argument("--url", type=str, default=None, help="Target URL where failure occurred")

    args = parser.parse_args()
    engine = QARagEngine(PROJECT_ROOT)

    if args.command == "index":
        print("[RAG CLI] Indexing workspace Page Objects and Test Data...")
        res = engine.index_workspace()
        print(f"[RAG CLI] Result: {res}")

    elif args.command == "generate":
        print(f"[RAG CLI] Generating test script for requirement: '{args.prompt}'...")
        script = engine.generate_test_script(args.prompt, target_project=args.project)
        print("\n" + "="*80)
        print("🤖 AUTO-GENERATED PLAYWRIGHT TEST SCRIPT:")
        print("="*80)
        print(script)
        print("="*80 + "\n")

    elif args.command == "analyze":
        print(f"[RAG CLI] Analyzing test failure trace...")
        analysis = engine.analyze_failure(args.test_name, args.trace, page_url=args.url)
        print("\n" + "="*80)
        print("🔍 AI RAG ROOT CAUSE DIAGNOSTIC REPORT:")
        print("="*80)
        print(analysis)
        print("="*80 + "\n")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
