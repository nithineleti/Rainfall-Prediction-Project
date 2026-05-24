"""
Fix trailing whitespace in Python files
"""
import pathlib
import re

def fix_trailing_whitespace(file_path):
    """Remove trailing whitespace from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Remove trailing whitespace from each line
        fixed_lines = [line.rstrip() + '\n' if line.strip() else '\n' for line in lines]

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)

        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    # Fix backend files
    backend_files = list(pathlib.Path('backend/app').rglob('*.py'))
    backend_fixed = sum(fix_trailing_whitespace(f) for f in backend_files)
    print(f"✅ Fixed {backend_fixed}/{len(backend_files)} backend files")

    # Fix ML files
    ml_files = list(pathlib.Path('ml/src').rglob('*.py'))
    ml_fixed = sum(fix_trailing_whitespace(f) for f in ml_files)
    print(f"✅ Fixed {ml_fixed}/{len(ml_files)} ML files")

    # Fix root scripts
    root_files = [f for f in pathlib.Path('.').glob('*.py')]
    root_fixed = sum(fix_trailing_whitespace(f) for f in root_files)
    print(f"✅ Fixed {root_fixed}/{len(root_files)} root script files")

    total = backend_fixed + ml_fixed + root_fixed
    print(f"\n🎯 Total: {total} files cleaned")

if __name__ == "__main__":
    main()
