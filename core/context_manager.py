import tiktoken
from typing import List, Dict, Optional

# Token budget constants
BUDGET_SYSTEM_PROMPT  = 500
BUDGET_WORKING_MEM    = 2000
BUDGET_RETRIEVED_MEM  = 500
BUDGET_THREAD_SUMMARY = 1000
BUDGET_RESPONSE       = 2000
BUDGET_TOTAL          = BUDGET_SYSTEM_PROMPT + BUDGET_WORKING_MEM + BUDGET_RETRIEVED_MEM + BUDGET_THREAD_SUMMARY + BUDGET_RESPONSE

def count_tokens(text, model="gpt-4o"):
    try:
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def count_messages_tokens(messages, model="gpt-4o"):
    total = 0
    for m in messages:
        total += count_tokens(m.get("content", ""), model)
        total += 4
    return total

def trim_to_budget(messages, budget, keep_system=True):
    result = []
    system_msgs = [m for m in messages if m.get("role") == "system"] if keep_system else []
    other_msgs = [m for m in messages if m.get("role") != "system"]
    system_tokens = count_messages_tokens(system_msgs)
    remaining = budget - system_tokens
    kept = []
    for msg in reversed(other_msgs):
        t = count_tokens(msg.get("content", ""))
        if remaining - t >= 0:
            kept.insert(0, msg)
            remaining -= t
        else:
            break
    return system_msgs + kept

def build_context(system_prompt, thread_summary=None, retrieved_memories=None, recent_messages=None):
    messages = []
    system_parts = [system_prompt]
    if thread_summary:
        system_parts.append("[CONVERSATION SUMMARY]" + chr(10) + thread_summary)
    if retrieved_memories:
        system_parts.append("[RELEVANT MEMORIES]" + chr(10) + retrieved_memories)
    messages.append({"role": "system", "content": chr(10).join(system_parts)})
    if recent_messages:
        trimmed = trim_to_budget(recent_messages, BUDGET_WORKING_MEM + BUDGET_THREAD_SUMMARY)
        messages.extend(trimmed)
    total = count_messages_tokens(messages)
    return messages, total

def get_budget_report():
    return {
        "system_prompt": BUDGET_SYSTEM_PROMPT,
        "working_memory": BUDGET_WORKING_MEM,
        "retrieved_memories": BUDGET_RETRIEVED_MEM,
        "thread_summary": BUDGET_THREAD_SUMMARY,
        "response_buffer": BUDGET_RESPONSE,
        "total_target": BUDGET_TOTAL,
        "note": "Efficient context - not burning 128k on every call"
    }