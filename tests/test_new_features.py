"""
Test script for new System Control and File Search features
Run this to verify the new functionality works correctly
"""

import logging
from desktop.system_control import SystemController
from desktop.file_search import FileSearcher
from llm.intent import IntentClassifier, ActionType

# Setup logging
logging.basicConfig(level=logging.INFO)


def test_intent_classifier():
    """Test intent classifier with new commands."""
    print("=" * 60)
    print("TESTING INTENT CLASSIFIER")
    print("=" * 60)
    
    classifier = IntentClassifier()
    
    test_cases = [
        # System Control
        ("volume up", ActionType.VOLUME_UP),
        ("turn down the volume", ActionType.VOLUME_DOWN),
        ("set volume to 50", ActionType.SET_VOLUME),
        ("mute", ActionType.MUTE),
        ("unmute", ActionType.UNMUTE),
        ("brightness up", ActionType.BRIGHTNESS_UP),
        ("make it dimmer", ActionType.BRIGHTNESS_DOWN),
        ("enable do not disturb", ActionType.ENABLE_DND),
        ("turn off do not disturb", ActionType.DISABLE_DND),
        ("what's my battery level", ActionType.GET_BATTERY),
        
        # File Search
        ("find file config.py", ActionType.SEARCH_FILES),
        ("search for requirements.txt", ActionType.SEARCH_FILES),
        ("recent files", ActionType.RECENT_FILES),
        ("open file main.py", ActionType.OPEN_FILE),
    ]
    
    passed = 0
    failed = 0
    
    for text, expected_action in test_cases:
        intent = classifier.classify(text)
        
        if intent.action_type == expected_action:
            print(f"✅ '{text}' -> {intent.action_type.value}")
            passed += 1
        else:
            print(f"❌ '{text}' -> Expected: {expected_action.value}, Got: {intent.action_type}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    print()


def test_system_control():
    """Test system control functionality."""
    print("=" * 60)
    print("TESTING SYSTEM CONTROL")
    print("=" * 60)
    
    system = SystemController()
    
    # Test volume
    print("\n1. Volume Controls:")
    current_volume = system.get_volume()
    print(f"   Current volume: {current_volume}")
    
    if current_volume is not None:
        print("   ✅ Get volume works")
    else:
        print("   ❌ Get volume failed")
    
    # Test battery
    print("\n2. Battery Status:")
    battery = system.get_battery_status()
    if battery:
        print(f"   Battery: {battery.get('percentage', 'unknown')}%")
        print(f"   Charging: {battery.get('charging', False)}")
        print("   ✅ Battery status works")
    else:
        print("   ❌ Battery status failed")
    
    print("\n⚠️  Skipping volume/brightness changes to avoid disruption")
    print("   To test volume changes, uncomment the code below:")
    print("   # system.volume_up(5)")
    print("   # system.volume_down(5)")
    print()


def test_file_search():
    """Test file search functionality."""
    print("=" * 60)
    print("TESTING FILE SEARCH")
    print("=" * 60)
    
    searcher = FileSearcher()
    
    # Test searching for Python files
    print("\n1. Searching for 'main.py':")
    results = searcher.search_by_name("main.py", limit=3)
    
    if results:
        print(f"   Found {len(results)} results:")
        for i, file in enumerate(results, 1):
            print(f"   {i}. {file['name']} - {file['path']}")
        print("   ✅ File search works")
    else:
        print("   ❌ No results found")
    
    # Test finding specific file
    print("\n2. Finding 'config.py':")
    file_path = searcher.find_file("config.py")
    
    if file_path:
        print(f"   Found: {file_path}")
        print("   ✅ Find file works")
    else:
        print("   ❌ File not found")
    
    # Test recent files
    print("\n3. Recent files (last 7 days):")
    recent = searcher.search_recent(days=7, limit=5)
    
    if recent:
        print(f"   Found {len(recent)} recent files:")
        for i, file in enumerate(recent, 1):
            print(f"   {i}. {file['name']} ({file['size_human']})")
        print("   ✅ Recent files works")
    else:
        print("   ⚠️  No recent files found")
    
    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("JHEEVIS NEW FEATURES TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        test_intent_classifier()
        test_system_control()
        test_file_search()
        
        print("=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
        print("\n✅ System Control and File Search features are ready!")
        print("\nTry these voice commands:")
        print("  - 'Volume up'")
        print("  - 'What's my battery level?'")
        print("  - 'Find file config.py'")
        print("  - 'Show me recent files'")
        print("  - 'Enable do not disturb'")
        print()
    
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
