"""Find and list skipped expected_result tests"""
from pathlib import Path

def whats_there(pattern, text):
    """Return what's on the end of the line after pattern in text"""
    x = text.find(pattern)
    if x < 0:
        return None
    
    x = x + len(pattern)
    y = text.find("\n",x)
    return text[x:y]


solution_root = Path(__file__).parents[1]/"solution"

for p in solution_root.glob('*/tests/test_*.py'):
    text = p.read_text(encoding='utf-8')

    # check that it is the right kind of test file.  skips oceans, custom test files
    if "expected_result_tester" not in text:
        continue

    solution_name = p.parents[1].name
    skips = []

    skipping = whats_there("\nSCENARIO_SKIP", text)
    if skipping is None:
        print("Error, could not find SCENARIO_SKIP in {p.name}")

    if "None" not in skipping:
        skips.append("scenarios")
    
    skipping = whats_there("\nTEST_SKIP", text)
    if skipping is None:
        print("Error, could not find TEST_SKIP in {p.name}")
    
    if "None" not in skipping:
        skips.append("tests")
    
    if len(skips):
        print(f"{solution_name} skips {', '.join(skips)}")
