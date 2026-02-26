"""
R2HC AI System - Main Entry Point
Ant Farm Architecture: Queen (Orchestrator) + Worker Agents
Run: python3 main.py
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import Orchestrator

def main():
    print("=" * 60)
    print("  R2HC AI SYSTEM - ANT FARM ARCHITECTURE")
    print("  Security | Memory | Efficiency | Multi-Agent")
    print("=" * 60)
    orc = Orchestrator()

    # Spin up a session
    tid = orc.new_thread("Main Session")
    print("\nType your message (or 'status', 'threads', 'quit'):\n")

    while True:
        try:
            user_input = input("You> ").strip()
            if not user_input:
                continue
            if user_input.lower() == "quit":
                break
            if user_input.lower() == "status":
                print(json.dumps(orc.status(), indent=2, default=str))
                continue
            if user_input.lower() == "threads":
                from memory.thread_store import list_threads
                print(json.dumps(list_threads(10), indent=2, default=str))
                continue

            response = orc.process(user_input, tid)
            print(f"\nSystem> {response}\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[ERROR] {e}")

    orc.shutdown()
    print("\nBye! All memory saved to threads.db")

if __name__ == "__main__":
    main()
