
import os
import sys
import django
import hashlib
from collections import defaultdict

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add project root
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import Music, VideoProject

def get_file_hash(file_path):
    """Returns MD5 hash of a file."""
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            buf = f.read(65536)
            while buf:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    except FileNotFoundError:
        return None

def clean_filename(name):
    """Returns a simplified version of the filename for preference scoring."""
    # Shorter is generally better, no random suffixes
    import re
    # Remove random django suffixes (e.g. _mkHlqkO)
    # Pattern: _[a-zA-Z0-9]{7}\.
    return len(name), re.sub(r'_[a-zA-Z0-9]{7}\.', '.', name)

def main():
    print("--- Starting Music Deduplication ---")
    
    all_music = Music.objects.all()
    print(f"Total Music records in DB: {all_music.count()}")
    
    # Group by Hash
    content_map = defaultdict(list)
    missing_files = []
    
    for m in all_music:
        if not m.file:
            continue
            
        full_path = m.file.path
        if not os.path.exists(full_path):
            missing_files.append(m)
            continue
            
        file_hash = get_file_hash(full_path)
        if file_hash:
            content_map[file_hash].append(m)
            
    print(f"Unique content hashes found: {len(content_map)}")
    
    # Process duplicates
    deleted_count = 0
    updated_projects = 0
    
    for file_hash, music_list in content_map.items():
        if len(music_list) < 2:
            continue
            
        print(f"\nDuplicate group detected (Hash: {file_hash}):")
        
        # Sort by preference: 
        # 1. Matches "Clean" name heuristic
        # 2. Shortest filename
        # 3. Oldest ID (created first)
        
        music_list.sort(key=lambda x: (len(os.path.basename(x.file.name)), x.id))
        
        master = music_list[0]
        duplicates = music_list[1:]
        
        print(f"  KEEPING: [ID: {master.id}] {os.path.basename(master.file.name)}")
        
        for dup in duplicates:
            print(f"  REMOVING: [ID: {dup.id}] {os.path.basename(dup.file.name)}")
            
            # Update referenced projects
            projects = VideoProject.objects.filter(background_music=dup)
            if projects.exists():
                print(f"    -> Updating {projects.count()} projects to use Master...")
                for p in projects:
                    p.background_music = master
                    p.save()
                    updated_projects += 1
            
            # Delete file and record
            try:
                file_path = dup.file.path
                dup.delete()
                if os.path.exists(file_path):
                    os.remove(file_path)
                deleted_count += 1
                print("    -> Deleted.")
            except Exception as e:
                print(f"    -> ERROR deleting: {e}")

    print(f"Deleted {deleted_count} duplicate music files (DB registered).")
    print(f"Updated {updated_projects} project references.")

    # --- PHASE 2: Orphan File Cleanup ---
    print("\n--- Phase 2: Orphan File Cleanup ---")
    
    media_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media', 'music')
    if not os.path.exists(media_root):
        print(f"Media root not found: {media_root}")
        return

    # Get all DB files (names)
    db_files = set()
    db_hashes = set()
    for m in all_music:
        if m.file:
             db_files.add(os.path.normpath(m.file.path))
             h = get_file_hash(m.file.path)
             if h: db_hashes.add(h)

    orphan_deleted = 0
    total_space_saved = 0
    
    for filename in os.listdir(media_root):
        file_path = os.path.join(media_root, filename)
        if not os.path.isfile(file_path):
            continue
            
        # Skip if in DB
        if os.path.normpath(file_path) in db_files:
            continue
            
        # It is an orphan. Check if it's a duplicate of something we have.
        # Heuristic: Hash match or Name pattern match with existing DB file
        f_hash = get_file_hash(file_path)
        
        if f_hash in db_hashes:
            # It's a binary duplicate of a known music file
            print(f"  [ORPHAN DUPLICATE] {filename} (Hash match)")
            try:
                size = os.path.getsize(file_path)
                os.remove(file_path)
                orphan_deleted += 1
                total_space_saved += size
                print("    -> Deleted.")
            except Exception as e:
                print(f"    -> ERROR: {e}")
        else:
             # Unique orphan? Maybe keep it or warn
             # For now, only delete PROVEN duplicates
             # print(f"  [ORPHAN UNIQUE] {filename} - Keeping")
             pass

    print(f"\nPhase 2 Summary:")
    print(f"Deleted {orphan_deleted} orphan duplicate files.")
    print(f"Freed {total_space_saved / 1024 / 1024:.2f} MB.")
    
    print("\nDone.")

if __name__ == "__main__":
    main()
