#!/usr/bin/env python3
import re

def update_chapter_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Replace GitHub reference patterns like [\[1\]](...) with citations
    content = re.sub(r'\[\\\[(\d+)\\\]\]\([^)]+\)', r'\\citep{AndroidCameraX, NordicBLE}', content)
    
    # Replace figure patterns like ![Figure X.Y: ...](path) with appendix references
    content = re.sub(r'!\[Figure (\d+\.\d+):[^\]]*\]\([^)]*\)', 
                    r'See Figure \1 (Appendix H.2) for \\2.', content)
    
    # Replace **Figure X.Y** patterns
    content = re.sub(r'\*\*Figure (\d+\.\d+)\*\*', r'See Figure \1 (Appendix H.2)', content)
    
    # Replace code listing patterns
    content = re.sub(r'\*\*Listing (\d+\.\d+):[^\*]*\*\*', 
                    r'See Listing \1 (Appendix H.4)', content)
    
    # Remove standalone code blocks and replace with appendix references
    content = re.sub(r'```[a-z]*\n.*?\n```', 'See Appendix H.4 for implementation details.', 
                    content, flags=re.DOTALL)
    
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"Updated {filename}")

# Update both files
update_chapter_file('4.md')
update_chapter_file('5.md')
