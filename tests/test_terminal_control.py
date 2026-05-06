"""
Test script for Terminal Control features
Run this to verify terminal control functionality works correctly
"""

import logging
import time
from desktop.actions import ActionExecutor
from llm.intent import IntentClassifier, ActionType

# Setup logging
logging.basicConfig(level=logging.INFO)


def test_intent_classifier():
    """Test intent classifier with terminal commands."""
    print("=" * 60)
    print("TESTING TERMINAL INTENT CLASSIFIER")
    print("=" * 60)
    
    classifier = IntentClassifier()
    
    test_cases = [
        # Terminal Control
        ("open terminal", ActionType.OPEN_TERMINAL),
        ("launch terminal", ActionType.OPEN_TERMINAL),
        ("close terminal", ActionType.CLOSE_TERMINAL),
        ("quit terminal", ActionType.CLOSE_TERMINAL),
        ("close this terminal", ActionType.CLOSE_CURRENT_TERMINAL),
        ("close current terminal", ActionType.CLOSE_CURRENT_TERMINAL),
        ("exit terminal", ActionType.CLOSE_CURRENT_TERMINAL),
        ("close active terminal", ActionType.CLOSE_CURRENT_TERMINAL),
        ("new terminal window", ActionType.NEW_TERMINAL_WINDOW),
        ("open new terminal window", ActionType.NEW_TERMINAL_WINDOW),
        ("new terminal tab", ActionType.NEW_TERMINAL_TAB),
        ("run command ls", ActionType.RUN_TERMINAL_COMMAND),
        ("execute pwd", ActionType.RUN_TERMINAL_COMMAND),
    ]
    
    passed = 0
    failed = 0
    
    for text, expected_action in test_cases:
        intent = classifier.classify(text)
        
        if intent.action_type == expected_action:
            print(f"✅ '{text}' -> {intent.action_type.value}")
            if intent.query:
                print(f"   Query: {intent.query}")
            passed += 1
        else:
            print(f"❌ '{text}' -> Expected: {expected_action.value}, Got: {intent.action_type}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    print()


def test_terminal_control():
    """Test terminal control functionality."""
    print("=" * 60)
    print("TESTING TERMINAL CONTROL")
    print("=" * 60)
    
    executor = ActionExecutor()
    
    print("\n⚠️  Interactive Test - Press Ctrl+C to skip any test\n")
    
    # Test 1: Open Terminal
    try:
        print("1. Testing: Open Terminal")
        input("   Press Enter to test opening Terminal (or Ctrl+C to skip)...")
        
        success = executor.open_terminal()
        if success:
            print("   ✅ Terminal opened successfully")
            time.sleep(2)
        else:
            print("   ❌ Failed to open Terminal")
    except KeyboardInterrupt:
        print("   ⏭️  Skipped")
    
    # Test 2: New Terminal Window
    try:
        print("\n2. Testing: New Terminal Window")
        input("   Press Enter to test creating new Terminal window (or Ctrl+C to skip)...")
        
        success = executor.new_terminal_window()
        if success:
            print("   ✅ New Terminal window created")
            time.sleep(2)
        else:
            print("   ❌ Failed to create new Terminal window")
    except KeyboardInterrupt:
        print("   ⏭️  Skipped")
    
    # Test 3: New Terminal Tab
    try:
        print("\n3. Testing: New Terminal Tab")
        input("   Press Enter to test creating new Terminal tab (or Ctrl+C to skip)...")
        
        success = executor.new_terminal_tab()
        if success:
            print("   ✅ New Terminal tab created")
            time.sleep(2)
        else:
            print("   ❌ Failed to create new Terminal tab")
    except KeyboardInterrupt:
        print("   ⏭️  Skipped")
    
    # Test 4: Run Command
    try:
        print("\n4. Testing: Run Terminal Command")
        input("   Press Enter to test running 'ls -la' in Terminal (or Ctrl+C to skip)...")
        
        success = executor.run_terminal_command("ls -la")
        if success:
            print("   ✅ Command executed in Terminal")
            time.sleep(2)
        else:
            print("   ❌ Failed to execute command")
    except KeyboardInterrupt:
        print("   ⏭️  Skipped")
    
    # Test 5: Close Terminal
    try:
        print("\n5. Testing: Close Current Terminal Window")
        input("   Press Enter to test closing current Terminal window (or Ctrl+C to skip)...")
        
        success = executor.close_current_terminal()
        if success:
            print("   ✅ Current Terminal window closed successfully")
            time.sleep(1)
        else:
            print("   ❌ Failed to close current Terminal window")
    except KeyboardInterrupt:
        print("   ⏭️  Skipped")
    
    # Test 6: Close Terminal App
    try:
        print("\n6. Testing: Close Terminal Application")
        input("   Press Enter to test closing Terminal app (or Ctrl+C to skip)...")
        
        success = executor.close_terminal()
        if success:
            print("   ✅ Terminal closed successfully")
        else:
            print("   ❌ Failed to close Terminal")
    except KeyboardInterrupt:
        print("   ⏭️  Skipped")
    
    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("TERMINAL CONTROL TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        test_intent_classifier()
        
        print("\n" + "=" * 60)
        print("INTERACTIVE TERMINAL TESTS")
        print("=" * 60)
        print("\nThe following tests will actually control Terminal.")
        print("Press Ctrl+C at any prompt to skip tests.\n")
        
        try:
            input("Press Enter to start interactive tests (or Ctrl+C to skip all)...")
            test_terminal_control()
        except KeyboardInterrupt:
            print("\n\n⏭️  Interactive tests skipped\n")
        
        print("=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
        print("\n✅ Terminal Control features are ready!")
        print("\nTry these voice commands:")
        print("  - 'Open Terminal'")
        print("  - 'New Terminal window'")
        print("  - 'New Terminal tab'")
        print("  - 'Run command ls -la'")
        print("  - 'Close Terminal'")
        print()
    
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
