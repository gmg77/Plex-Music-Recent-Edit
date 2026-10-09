import sqlite3
import time
from datetime import datetime
import os
import platform
import re
from pathlib import Path

def get_plex_db_path():
    """ Automatically resolves the Plex Library DB path across platforms """
    system = platform.system()
    home = Path.home()
    
    docker_path = Path("/config/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db")
    if docker_path.exists():
        return docker_path

    if system == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "Plex Media Server" / "Plug-in Support" / "Databases" / "com.plexapp.plugins.library.db"
    elif system == "Darwin":
        return home / "Library" / "Application Support" / "Plex Media Server" / "Plug-in Support" / "Databases" / "com.plexapp.plugins.library.db"
    elif system == "Linux":
        standard_linux = Path("/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db")
        snap_linux = home / "snap" / "plexmediaserver" / "common" / "Library" / "Application Support" / "Plex Media Server" / "Plug-in Support" / "Databases" / "com.plexapp.plugins.library.db"
        if standard_linux.exists(): return standard_linux
        if snap_linux.exists(): return snap_linux
        return standard_linux
    raise FileNotFoundError("Could not locate the Plex directory.")

def parse_user_selection(user_input, max_val):
    """ Parses formats like '5', '1-5', '1, 3, 5' into a set of 0-based indices """
    indices = set()
    # Normalize input: remove spaces
    clean_input = re.sub(r'\s+', '', user_input)
    
    # Split by commas for individual tokens or ranges
    tokens = clean_input.split(',')
    
    for token in tokens:
        if not token:
            continue
        if '-' in token:
            # Handle ranges like 1-5
            try:
                start_str, end_str = token.split('-', 1)
                start = int(start_str)
                end = int(end_str)
                if 1 <= start <= max_val and 1 <= end <= max_val:
                    # Convert to 0-based index and include the end of the range
                    indices.update(range(min(start, end) - 1, max(start, end)))
                else:
                    print(f"⚠️ Range '{token}' out of bounds (1-{max_val}). Skipping.")
            except ValueError:
                print(f"⚠️ Invalid range format '{token}'. Skipping.")
        else:
            # Handle single items like 5
            try:
                val = int(token)
                if 1 <= val <= max_val:
                    indices.add(val - 1)
                else:
                    print(f"⚠️ Item '{val}' out of bounds (1-{max_val}). Skipping.")
            except ValueError:
                print(f"⚠️ Invalid selection item '{token}'. Skipping.")
                
    return sorted(list(indices))

def list_and_modify_albums():
    try:
        resolved_path = get_plex_db_path()
        if not resolved_path.exists():
            print(f"❌ DB File not found at structural path: {resolved_path}")
            return
            
        print(f"✅ Connected to Plex DB at: {resolved_path}")
        conn = sqlite3.connect(str(resolved_path))
        cursor = conn.cursor()
        
        # Uses self-join to dynamically load real artist parent text fields
        fetch_query = """
            SELECT albums.id, albums.title, artists.title, albums.added_at 
            FROM metadata_items AS albums
            LEFT JOIN metadata_items AS artists ON albums.parent_id = artists.id
            WHERE albums.metadata_type = 9 
            ORDER BY albums.added_at DESC 
            LIMIT 30;
        """
        cursor.execute(fetch_query)
        albums = cursor.fetchall()
        
        if not albums:
            print("No albums found in the database.")
            return

        print("\n--- MOST RECENTLY ADDED ALBUMS ---")
        for index, (db_id, title, artist, added_at) in enumerate(albums, 1):
            readable_date = datetime.fromtimestamp(added_at).strftime('%Y-%m-%d %H:%M:%S')
            artist_name = artist if artist else "Unknown Artist"
            print(f"[{index}] {artist_name} - '{title}' (Added: {readable_date})")
        print("----------------------------------")
        
        print("\nOptions for selection:")
        print(" - Single number: 5")
        print(" - Batch range:   1-5")
        print(" - Specific list: 1, 3, 7")
        print(" - Combined:      1-3, 5, 8-10")
        
        user_input = input(f"\nSelect which albums to backdate (1-{len(albums)}): ")
        selected_indices = parse_user_selection(user_input, len(albums))
        
        if not selected_indices:
            print("❌ No valid items selected. Exiting.")
            return

        # Extract targeted item rows based on chosen indices
        target_albums = [albums[i] for i in selected_indices]
        target_ids = [album[0] for album in target_albums]
        
        print("\nYou selected the following items to push back by 1 year:")
        for _, title, artist, _ in target_albums:
            print(f" ➔ {artist if artist else 'Unknown Artist'} - '{title}'")
            
        confirm = input("\nApply changes and write to database? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation aborted.")
            return

        # Calculate target timestamp exactly using Python time math (1 year ago)
        seconds_in_a_year = 365 * 24 * 60 * 60
        backdated_timestamp = int(time.time() - seconds_in_a_year)

        # Execute parameterized update
        placeholders = ','.join(['?'] * len(target_ids))
        update_query = f"""
            UPDATE metadata_items 
            SET added_at = ? 
            WHERE id IN ({placeholders});
        """
        
        cursor.execute(update_query, [backdated_timestamp] + target_ids)
        conn.commit()
        
        print(f"\n🪄 Success! {cursor.rowcount} database rows modified.🪄")
        
    except sqlite3.Error as e:
        print(f"\n❌ A database operational error occurred: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("⚠️⚠️ Crucial: Ensure Plex Media Server is completely closed down before running this script.⚠️⚠️")
    safety = input("Have you backed up your DB and stopped Plex? (y/n): ")
    if safety.lower() == 'y':
        list_and_modify_albums()
    else:
        print("Cancelled.")
