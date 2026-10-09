
Plex Album Backdater

A cross-platform Python automation script that lets you cleanly remove music albums from your Plex Media Server's "Recently Added" hub. It achieves this by modifying the internal Plex SQLite database and safely adjusting the album's added_at timestamp into the past.
The script features an interactive menu that prints your newest additions and accepts precise user strings to modify standalone files, batch windows, or complex mixed arrays.

Features

• Platform Agnostic: Automatically searches and verifies the Plex com.plexapp.plugins.library.db database path across Windows, macOS, Linux (Standard & Snap packs), and Docker configurations.

• Granular Controls: Process items using versatile input arguments:
	• Single selection: 5
	• Consecutive ranges: 1-5
	• Targeted structures: 2, 6, 9
	• Hybrid entries: 1-3, 5, 8-10
  
• Safe Interactivity: Performs text calculations directly inside Python to remain entirely backward-compatible with older machine-level SQLite version dependencies. It also prints an explicit data manifest before committing changes to disk.

Prerequisites

Before running the application, make sure your host machine has:
• Python 3.x installed.
• Python's standard sqlite3 library (packaged natively with standard installations).


Step-by-Step Usage Guide


1. ⚠️ Shut Down Your Plex Server

You must stop your Plex Media Server software completely before running the code. If Plex attempts to write metadata to the database while a separate script locks the tables, you risk total database corruption.

2. 💾 Create a Database Backup
```
Locate your database directory and duplicate com.plexapp.plugins.library.db to a safe backup location.
• Windows: %LOCALAPPDATA%\Plex Media Server\Plug-in Support\Databases\
• Linux / Docker: /var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-in Support/Databases/
• macOS: ~/Library/Application Support/Plex Media Server/Plug-in Support/Databases/
```
3. Run the Program

4. Example
```
⚠️ Crucial: Ensure Plex Media Server is completely closed down before running this script.
Have you backed up your DB and stopped Plex? (y/n): y
✅ Connected to Plex DB at: /var/lib/plexmediaserver/.../com.plexapp.plugins.library.db

--- MOST RECENTLY ADDED ALBUMS ---
[1] Pink Floyd - 'The Dark Side of the Moon' (Added: 2026-10-08 14:20:10)
[2] Daft Punk - 'Random Access Memories' (Added: 2026-10-07 09:15:32)
[3] Miles Davis - 'Kind of Blue' (Added: 2026-10-05 18:44:00)
----------------------------------

Options for selection:
 - Single number: 5
 - Batch range:   1-5
 - Specific list: 1, 3, 7
 - Combined:      1-3, 5, 8-10

Select which albums to backdate (1-3): 1, 3

You selected the following items to push back by 1 year:
 ➔ Pink Floyd - 'The Dark Side of the Moon'
 ➔ Miles Davis - 'Kind of Blue'

Apply changes and write to database? (y/n): y

🎉 Success! 2 database rows modified.
```
