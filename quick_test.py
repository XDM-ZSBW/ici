print("Starting validation...")
import sys
sys.path.insert(0, '.')

try:
    from backend.factory import create_app
    print("Factory import: OK")
except Exception as e:
    print(f"Factory import: FAILED - {e}")

try:
    from backend.utils.memory_utils import is_statement_worth_remembering
    result = is_statement_worth_remembering("Tommy should go at 2pm")
    print(f"Memory utils: OK - {result}")
except Exception as e:
    print(f"Memory utils: FAILED - {e}")

print("Validation complete.")
