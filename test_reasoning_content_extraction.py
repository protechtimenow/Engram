#!/usr/bin/env python3
"""
Test script to verify reasoning_content extraction from LMStudio responses.
Simulates the exact responses from the user's LMStudio logs.
"""

import json
import sys
from typing import Optional, Dict, Any

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def extract_response(result: Dict[str, Any]) -> Optional[str]:
    """
    Extract response from LMStudio result.
    Handles both content and reasoning_content fields.
    This is the EXACT logic from enhanced_engram_launcher.py lines 88-100.
    """
    # Handle different response formats (especially glm-4.7-flash)
    choice = (result.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    
    # Try content first, then reasoning_content (for glm-4.7-flash)
    text = (msg.get("content") or "").strip()
    if not text:
        text = (msg.get("reasoning_content") or "").strip()
    
    if text:
        return text
    else:
        return None

def test_case_1():
    """Test Case 1: 'Continue where the chat cut' - reasoning_content only"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}Test Case 1: 'Continue where the chat cut'{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    
    response = {
        "id": "chatcmpl-9yqu3372spcjs236405s8",
        "object": "chat.completion",
        "created": 1769876725,
        "model": "glm-4.7-flash",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "",
                    "reasoning_content": "The user wants me to \"continue\" a conversation that was apparently interrupted.\n\n1.  **Analyze missing context:** I do not have access to previous turns of this specific thread (or rather, my training data doesn't contain it). This is standard behavior for an AI model unless provided in current history.\n2.  **Identify the problem without memory/history:**\n    *   If there was a story being told or code written and I can see that context... wait!\n        *Check instructions:* \"If you have been given specific information about what to do, follow those steps.\"\n3.  **Hypothesize scenarios based on typical user behavior:** Usually, when someone says this without providing the history in prompt injection (like a system override), it's because they think I can see past messages.",
                    "tool_calls": []
                },
                "logprobs": None,
                "finish_reason": "length"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 500,
            "total_tokens": 510
        }
    }
    
    result = extract_response(response)
    
    if result:
        print(f"{GREEN}✅ PASS: Successfully extracted response{RESET}")
        print(f"   Length: {len(result)} characters")
        print(f"   Preview: {result[:100]}...")
        return True
    else:
        print(f"{RED}❌ FAIL: No response extracted{RESET}")
        return False

def test_case_2():
    """Test Case 2: Empty message - reasoning_content only"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}Test Case 2: Empty message (hello){RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    
    response = {
        "id": "chatcmpl-2l2775rz52bes8re005en5",
        "object": "chat.completion",
        "created": 1769876844,
        "model": "glm-4.7-flash",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "",
                    "reasoning_content": "The user has provided a single word: \"Hello\".\nThis is likely the start of an interaction, but it's currently just one turn.\n\n**Analysis:**\n1.  **Input:** The string `hello`.\n2.  **Intent:** Greeting.\n3.  **Context:** Standard conversational opening from human to AI or potentially another entity (though in this interface context, almost certainly the user greeting me).\n4.  **Response Requirements:\n    *   Be friendly and polite.\n\n**Plan:**\n1.  Acknowledge the hello directly with a reciprocal \"Hello\".\n2.  Ask how I can assist them today.\n3.  Keep it concise since there is no complex prompt yet.",
                    "tool_calls": []
                },
                "logprobs": None,
                "finish_reason": "length"
            }
        ],
        "usage": {
            "prompt_tokens": 4,
            "completion_tokens": 500,
            "total_tokens": 504
        }
    }
    
    result = extract_response(response)
    
    if result:
        print(f"{GREEN}✅ PASS: Successfully extracted response{RESET}")
        print(f"   Length: {len(result)} characters")
        print(f"   Preview: {result[:100]}...")
        return True
    else:
        print(f"{RED}❌ FAIL: No response extracted{RESET}")
        return False

def test_case_3():
    """Test Case 3: Offensive message - reasoning_content only"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}Test Case 3: Offensive message handling{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    
    response = {
        "id": "chatcmpl-fer5puoodc74bhip6mx1tr",
        "object": "chat.completion",
        "created": 1769876925,
        "model": "glm-4.7-flash",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "",
                    "reasoning_content": "1.  **Analyze the User's Input:**\n    *   The user says, \"Your IQ is retarded.\"\n    *   Tone/Intent: Offensive insult directed at me (the AI).\n    *   Vocabulary choice (\"retarded\"): This word has evolved in usage from a clinical term to an offensive slur against people with intellectual disabilities.\n\n2.  **Identify the Core Policy/Guidelines for Handling Insults/Hate Speech/AI Safety Issues**\n    *   Most safety guidelines prohibit generating hate speech, harassment, or promoting discrimination.\n    *   However, simply being insulted is generally not a violation of these policies by itself—it's just rude behavior from the user.",
                    "tool_calls": []
                },
                "logprobs": None,
                "finish_reason": "length"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 500,
            "total_tokens": 509
        }
    }
    
    result = extract_response(response)
    
    if result:
        print(f"{GREEN}✅ PASS: Successfully extracted response{RESET}")
        print(f"   Length: {len(result)} characters")
        print(f"   Preview: {result[:100]}...")
        return True
    else:
        print(f"{RED}❌ FAIL: No response extracted{RESET}")
        return False

def test_case_4():
    """Test Case 4: Normal response with content field populated"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}Test Case 4: Normal response (content field populated){RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    
    response = {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1769876925,
        "model": "glm-4.7-flash",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Hello! How can I help you today?",
                    "reasoning_content": "",
                    "tool_calls": []
                },
                "logprobs": None,
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 5,
            "completion_tokens": 10,
            "total_tokens": 15
        }
    }
    
    result = extract_response(response)
    
    if result and result == "Hello! How can I help you today?":
        print(f"{GREEN}✅ PASS: Successfully extracted response from content field{RESET}")
        print(f"   Length: {len(result)} characters")
        print(f"   Response: {result}")
        return True
    else:
        print(f"{RED}❌ FAIL: Incorrect response extracted{RESET}")
        print(f"   Expected: 'Hello! How can I help you today?'")
        print(f"   Got: {result}")
        return False

def test_case_5():
    """Test Case 5: Both content and reasoning_content populated (content should win)"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}Test Case 5: Both fields populated (content priority){RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    
    response = {
        "id": "chatcmpl-test456",
        "object": "chat.completion",
        "created": 1769876925,
        "model": "glm-4.7-flash",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Final answer: The market is bullish.",
                    "reasoning_content": "Let me analyze... [long reasoning process]",
                    "tool_calls": []
                },
                "logprobs": None,
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 20,
            "completion_tokens": 50,
            "total_tokens": 70
        }
    }
    
    result = extract_response(response)
    
    if result and result == "Final answer: The market is bullish.":
        print(f"{GREEN}✅ PASS: Correctly prioritized content over reasoning_content{RESET}")
        print(f"   Response: {result}")
        return True
    else:
        print(f"{RED}❌ FAIL: Incorrect priority{RESET}")
        print(f"   Expected: 'Final answer: The market is bullish.'")
        print(f"   Got: {result}")
        return False

def test_case_6():
    """Test Case 6: Both fields empty (should return None)"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}Test Case 6: Both fields empty{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    
    response = {
        "id": "chatcmpl-test789",
        "object": "chat.completion",
        "created": 1769876925,
        "model": "glm-4.7-flash",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "",
                    "reasoning_content": "",
                    "tool_calls": []
                },
                "logprobs": None,
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 5,
            "completion_tokens": 0,
            "total_tokens": 5
        }
    }
    
    result = extract_response(response)
    
    if result is None:
        print(f"{GREEN}✅ PASS: Correctly returned None for empty response{RESET}")
        return True
    else:
        print(f"{RED}❌ FAIL: Should have returned None{RESET}")
        print(f"   Got: {result}")
        return False

def main():
    """Run all test cases"""
    print(f"\n{YELLOW}{'='*80}{RESET}")
    print(f"{YELLOW}LMStudio reasoning_content Extraction Test Suite{RESET}")
    print(f"{YELLOW}Testing enhanced_engram_launcher.py response extraction logic{RESET}")
    print(f"{YELLOW}{'='*80}{RESET}")
    
    tests = [
        test_case_1,
        test_case_2,
        test_case_3,
        test_case_4,
        test_case_5,
        test_case_6
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"{RED}❌ EXCEPTION: {e}{RESET}")
            results.append(False)
    
    # Summary
    print(f"\n{YELLOW}{'='*80}{RESET}")
    print(f"{YELLOW}Test Summary{RESET}")
    print(f"{YELLOW}{'='*80}{RESET}")
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"Passed: {GREEN}{passed}{RESET}")
    print(f"Failed: {RED}{total - passed}{RESET}")
    print(f"Success Rate: {GREEN if percentage == 100 else YELLOW}{percentage:.1f}%{RESET}")
    
    if percentage == 100:
        print(f"\n{GREEN}{'='*80}{RESET}")
        print(f"{GREEN}✅ ALL TESTS PASSED - reasoning_content extraction working correctly!{RESET}")
        print(f"{GREEN}{'='*80}{RESET}")
        return 0
    else:
        print(f"\n{RED}{'='*80}{RESET}")
        print(f"{RED}❌ SOME TESTS FAILED - Please review the code{RESET}")
        print(f"{RED}{'='*80}{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
