
import os

LOG_FILE = 'app.log'
TARGET_STRING = '[Engine]' # Search for any engine start
MAX_LINES_TO_CHECK = 100000
chunk_size = 8192

def analyze_logs():
    if not os.path.exists(LOG_FILE):
        print("Log file not found.")
        return

    file_size = os.path.getsize(LOG_FILE)
    print(f"Log file size: {file_size / (1024*1024):.2f} MB")
    
    found_lines = []
    
    try:
        with open(LOG_FILE, 'rb') as f:
            # Simple approach: Read line by line from the end is hard efficiently in Python without external libs
            # We will read the last N bytes approx (assuming ~150 bytes per line)
            seek_pos = max(0, file_size - (MAX_LINES_TO_CHECK * 200)) 
            f.seek(seek_pos)
            
            content = f.read().decode('utf-8', errors='ignore')
            lines = content.splitlines()
            
            for line in lines:
                if TARGET_STRING in line:
                    found_lines.append(line)
                    
    except Exception as e:
        print(f"Error reading log: {e}")
        return

    print(f"Found {len(found_lines)} entries for {TARGET_STRING}")
    if found_lines:
        print("\nLast 20 entries:")
        for line in found_lines[-20:]:
            print(line)

if __name__ == "__main__":
    analyze_logs()
