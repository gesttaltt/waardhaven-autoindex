#!/usr/bin/env python3
"""
Hook to find duplicate documentation files and suggest consolidation
"""

import os
import sys
import hashlib
from pathlib import Path
from collections import defaultdict
import difflib

def get_file_hash(filepath):
    """Generate hash of file content"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def find_similar_names(docs_dir):
    """Find files with similar names"""
    files = {}
    similar = defaultdict(list)
    
    for root, dirs, filenames in os.walk(docs_dir):
        for filename in filenames:
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                base_name = filename.lower().replace('-', '_').replace(' ', '_')
                similar[base_name].append(filepath)
    
    duplicates = {k: v for k, v in similar.items() if len(v) > 1}
    return duplicates

def find_content_duplicates(docs_dir):
    """Find files with identical content"""
    hashes = defaultdict(list)
    
    for root, dirs, filenames in os.walk(docs_dir):
        for filename in filenames:
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                file_hash = get_file_hash(filepath)
                if file_hash:
                    hashes[file_hash].append(filepath)
    
    duplicates = {k: v for k, v in hashes.items() if len(v) > 1}
    return duplicates

def check_similar_topics(docs_dir):
    """Find files covering similar topics"""
    topics = {
        'api_architecture': [],
        'schemas': [],
        'testing': [],
        'migration': [],
        'service': [],
        'provider': [],
        'frontend': [],
        'deployment': [],
        'environment': [],
    }
    
    for root, dirs, filenames in os.walk(docs_dir):
        for filename in filenames:
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                lower_name = filename.lower()
                
                for topic, files in topics.items():
                    if topic.replace('_', '') in lower_name.replace('-', '').replace('_', ''):
                        files.append(filepath)
    
    return {k: v for k, v in topics.items() if len(v) > 1}

def main():
    docs_dir = 'docs'
    if not os.path.exists(docs_dir):
        print("No docs directory found")
        return
    
    print("Searching for duplicate documentation files...\n")
    
    # Find similar names
    similar_names = find_similar_names(docs_dir)
    if similar_names:
        print("Files with similar names:")
        for base, files in similar_names.items():
            print(f"\n  Topic: {base}")
            for f in files:
                size = os.path.getsize(f)
                mtime = os.path.getmtime(f)
                print(f"    - {f} ({size} bytes, modified: {mtime})")
    
    # Find identical content
    identical = find_content_duplicates(docs_dir)
    if identical:
        print("\nFiles with identical content:")
        for hash_val, files in identical.items():
            print(f"\n  Identical files:")
            for f in files:
                print(f"    - {f}")
    
    # Find similar topics
    similar_topics = check_similar_topics(docs_dir)
    if similar_topics:
        print("\nFiles covering similar topics:")
        for topic, files in similar_topics.items():
            if files:
                print(f"\n  {topic.replace('_', ' ').title()}:")
                for f in files:
                    print(f"    - {f}")
    
    print("\nDuplicate scan complete")

if __name__ == "__main__":
    main()