"""
Test Enhanced Vision Reasoning
Demonstrates scene understanding, activity recognition, and object relationships
"""

import sys
sys.path.append('/Users/jino/Projects/jheevis')

from vision.camera import Camera
from vision.detector import ObjectDetector
from vision.scene_analyzer import SceneAnalyzer
import time


def test_enhanced_vision():
    """Test the enhanced vision capabilities."""
    print("=" * 70)
    print("ENHANCED VISION REASONING TEST")
    print("=" * 70)
    print()
    
    # Initialize components
    print("📸 Initializing camera and vision system...")
    camera = Camera()
    detector = ObjectDetector(confidence=0.25)
    analyzer = SceneAnalyzer(detector, history_size=10)
    
    if not camera.open():
        print("❌ Failed to open camera")
        return
    
    print("✅ Camera ready")
    print()
    
    try:
        # Test 1: Basic scene analysis
        print("=" * 70)
        print("TEST 1: Basic Scene Analysis")
        print("=" * 70)
        
        frame = camera.capture_multiple_frames(num_frames=3)
        if frame is not None:
            context = analyzer.analyze_scene(frame, use_history=False)
            
            print(f"📝 Description: {context.description}")
            print(f"🎯 Activity: {context.activity}")
            print(f"👥 People: {context.people_count}")
            print(f"📦 Objects detected: {len(context.objects)}")
            print(f"✨ Confidence: {context.confidence:.1%}")
            
            if context.relationships:
                print(f"\n🔗 Spatial Relationships:")
                for rel in context.relationships:
                    print(f"   • {rel}")
        
        print()
        time.sleep(1)
        
        # Test 2: Multi-frame temporal analysis
        print("=" * 70)
        print("TEST 2: Multi-Frame Temporal Analysis")
        print("=" * 70)
        print("Capturing multiple frames for context...")
        
        for i in range(5):
            frame = camera.capture_frame()
            if frame is not None:
                context = analyzer.analyze_scene(frame, use_history=True)
                print(f"  Frame {i+1}: {context.activity} (confidence: {context.confidence:.1%})")
            time.sleep(0.5)
        
        print()
        
        # Test 3: Activity summary
        print("=" * 70)
        print("TEST 3: Activity Summary")
        print("=" * 70)
        
        summary = analyzer.get_activity_summary()
        print(f"📊 {summary}")
        
        print()
        time.sleep(1)
        
        # Test 4: Detailed analysis with relationships
        print("=" * 70)
        print("TEST 4: Detailed Scene Understanding")
        print("=" * 70)
        
        frame = camera.capture_multiple_frames(num_frames=5)
        if frame is not None:
            context = analyzer.analyze_scene(frame, use_history=True)
            
            print(f"🖼️  Full Scene Analysis:")
            print(f"   {context.description}")
            print()
            
            if context.objects:
                print(f"📦 Detected Objects ({len(context.objects)}):")
                object_counts = {}
                for obj in context.objects:
                    cls = obj['class']
                    object_counts[cls] = object_counts.get(cls, 0) + 1
                
                for obj, count in sorted(object_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"   • {obj}: {count}")
            
            print()
            
            if context.relationships:
                print(f"🔗 Object Relationships:")
                for rel in context.relationships:
                    print(f"   • {rel}")
            
            print()
            
            if context.activity not in ['idle', 'present']:
                activity_name = context.activity.replace('_', ' ')
                print(f"🎬 Activity Recognition: {activity_name}")
        
        print()
        
        # Test 5: Context history
        print("=" * 70)
        print("TEST 5: Context History")
        print("=" * 70)
        
        print(f"📚 Frame history size: {len(analyzer.frame_history)}")
        print(f"📈 Context history size: {len(analyzer.context_history)}")
        
        if analyzer.context_history:
            print(f"\n📊 Recent activities:")
            for i, ctx in enumerate(list(analyzer.context_history)[-5:], 1):
                print(f"   {i}. {ctx.activity} - {len(ctx.objects)} objects")
        
        print()
        
    finally:
        camera.close()
        print("=" * 70)
        print("✅ Test complete!")
        print("=" * 70)


def test_voice_commands():
    """Show example voice commands that trigger enhanced vision."""
    print()
    print("=" * 70)
    print("ENHANCED VISION VOICE COMMANDS")
    print("=" * 70)
    print()
    print("Try these commands with Jheevis:")
    print()
    print("🔷 Basic Vision:")
    print("   • 'What do you see?'")
    print("   • 'Who is here?'")
    print("   • 'Count people'")
    print()
    print("🔷 Enhanced Understanding:")
    print("   • 'Analyze the scene' - Detailed analysis with relationships")
    print("   • 'What am I doing?' - Activity recognition")
    print("   • 'What's happening?' - Context-aware description")
    print("   • 'Tell me everything you see' - Comprehensive analysis")
    print()
    print("🔷 Activity Tracking:")
    print("   • 'What have I been doing?' - Recent activity summary")
    print("   • 'Activity summary' - Historical context")
    print("   • 'What's my recent activity?' - Temporal analysis")
    print()
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test enhanced vision reasoning')
    parser.add_argument('--commands', action='store_true', help='Show voice commands')
    args = parser.parse_args()
    
    if args.commands:
        test_voice_commands()
    else:
        test_enhanced_vision()
        test_voice_commands()
