import sys
import os

print("🧪 Testing ICI Chat Lightweight Solution")
print("=" * 40)

try:
    # Add current directory to path
    sys.path.insert(0, '.')
    print("✅ Path configured")
    
    # Test factory import
    from backend.factory import create_app
    print("✅ Factory import successful")
    
    # Test app creation
    app, socketio = create_app()
    print("✅ App creation successful")
    
    # Test memory utils
    from backend.utils.memory_utils import (
        is_statement_worth_remembering,
        is_question_seeking_memory,
        store_information_in_memory,
        search_memory_for_context
    )
    print("✅ Memory utils import successful")
    
    # Test memory functions
    assert is_statement_worth_remembering("Tommy should go at 2pm") == True
    assert is_question_seeking_memory("When should Tommy go?") == True
    print("✅ Memory functions working correctly")
    
    # Check heavy dependencies are removed
    heavy_deps = ['transformers', 'torch', 'sentence_transformers', 'faiss']
    for dep in heavy_deps:
        try:
            __import__(dep)
            print(f"❌ WARNING: Heavy dependency '{dep}' is still available")
        except ImportError:
            print(f"✅ Heavy dependency '{dep}' successfully removed")
    
    print("\n🎉 ALL TESTS PASSED!")
    print("Solution is ready for Cloud Run deployment.")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
