# list_detection_diagnostic.py
import os
import re
import sys
from pathlib import Path

def analyze_codebase_for_list_parsing(base_dir="."):
    """Analyze the codebase to find where list parsing happens."""
    
    print("🔍 Searching for PDF parsing and list detection code...")
    print("="*60)
    
    # Key directories to check
    key_dirs = [
        "docvision/",
        "format/pdf/",
        "pdfminer/",
        "format/",
        "translator/"
    ]
    
    findings = {}
    
    for dir_path in key_dirs:
        full_path = Path(base_dir) / dir_path
        if not full_path.exists():
            print(f"  ⚠️ Directory not found: {full_path}")
            continue
            
        print(f"\n📂 Examining: {dir_path}")
        
        for py_file in full_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for list-related patterns
                    list_keywords = [
                        ('bullet', r'bullet|•|\u2022|\u2023|\u25E6|\u2043|\u2219'),
                        ('numbered', r'numbered|list.*item|\d+\.\s|\d+\)\s'),
                        ('list', r'list|enumeration'),
                        ('paragraph', r'paragraph|text.*block|line.*group'),
                        ('indent', r'indent|indentation|x0|bbox.*\[0\]'),
                    ]
                    
                    file_findings = []
                    for keyword_type, pattern in list_keywords:
                        if re.search(pattern, content, re.IGNORECASE):
                            # Count occurrences
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            file_findings.append((keyword_type, len(matches)))
                    
                    if file_findings:
                        rel_path = py_file.relative_to(base_dir)
                        findings[str(rel_path)] = file_findings
                        
                        # Show a sample of relevant lines
                        lines = content.split('\n')
                        relevant_lines = []
                        for i, line in enumerate(lines[:100]):
                            if any(re.search(pattern, line, re.IGNORECASE) for _, pattern in list_keywords):
                                if len(line.strip()) > 0:
                                    relevant_lines.append(f"  Line {i+1}: {line.strip()[:80]}")
                        
                        if relevant_lines:
                            print(f"  📄 {rel_path}")
                            for finding in file_findings[:3]:
                                print(f"    - {finding[0]}: {finding[1]} occurrences")
                            if relevant_lines:
                                print("    Sample lines:")
                                for line in relevant_lines[:3]:
                                    print(line)
                                if len(relevant_lines) > 3:
                                    print(f"      ... and {len(relevant_lines)-3} more")
            
            except Exception as e:
                print(f"  ⚠️ Error reading {py_file}: {e}")
                continue
    
    return findings

def check_specific_files(base_dir="."):
    """Check specific important files for list handling."""
    
    print("\n" + "="*60)
    print("🔎 CHECKING SPECIFIC FILES")
    print("="*60)
    
    important_files = [
        "docvision/paragraph_finder.py",
        "format/pdf/reconstructor.py",
        "format/pdf/high_level.py",
        "docvision/doclayout.py",
        "format/pdf/translator.py",
        "pdfminer/pdf_parser.py",
    ]
    
    for file_path in important_files:
        full_path = Path(base_dir) / file_path
        if full_path.exists():
            print(f"\n📄 {file_path} - EXISTS")
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    patterns = {
                        'list/bullet': r'bullet|•|\d+\.\s|1\.|2\.|a\.|b\.',
                        'paragraph': r'paragraph|text.*group',
                        'text extraction': r'get_text|extract.*text',
                        'bbox/coordinates': r'bbox|\[x0|x1|y0|y1\]',
                        'translation': r'translat|render.*text',
                    }
                    
                    found_patterns = []
                    for name, pattern in patterns.items():
                        if re.search(pattern, content, re.IGNORECASE):
                            found_patterns.append(name)
                    
                    if found_patterns:
                        print(f"  Contains: {', '.join(found_patterns)}")
                        
                        file_size = os.path.getsize(full_path)
                        print(f"  Size: {file_size} bytes")
                        
                        line_count = len(content.split('\n'))
                        print(f"  Lines: {line_count}")
                        
                        print("  First 5 lines:")
                        for i, line in enumerate(content.split('\n')[:5]):
                            print(f"    {i+1}: {line.strip()}")
                    
            except Exception as e:
                print(f"  ⚠️ Error reading: {e}")
        else:
            print(f"\n❌ {file_path} - NOT FOUND")

def main():
    print("🚀 BABEL LIST DETECTION DIAGNOSTIC")
    print("="*60)
    
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    
    # Check if we're in babeldoc directory
    if not (current_dir / "babeldoc").exists():
        print("\n⚠️  Looking for babeldoc directory...")
        
        # Try to find it
        for item in current_dir.iterdir():
            if item.is_dir() and "babel" in item.name.lower():
                print(f"Found: {item.name}")
                print(f"Try navigating to: {item}")
    
    # Run the diagnostic
    findings = analyze_codebase_for_list_parsing()
    
    # Check specific files
    check_specific_files()
    
    print("\n" + "="*60)
    print("💡 NEXT STEPS")
    print("="*60)
    print("""
1. Look for files related to:
   - Paragraph detection
   - Text grouping  
   - PDF reconstruction
   - Text extraction

2. Search for these terms in the codebase:
   - 'paragraph'
   - 'text_block'
   - 'bbox' or 'coordinates'
   - 'get_text' or 'extract_text'
   - 'render' or 'reconstruct'
    """)

if __name__ == "__main__":
    main()