import os
from pydriller import Repository
from collections import Counter

# --- CONFIGURATION ---
urls = ["https://github.com/wger-project/wger.git"]
TARGET_MODULES = ['core', 'exercises', 'gym', 'nutrition', 'manager', 'measurements', 'weight']
local_path = os.path.join(os.getcwd(), "wger_repo")

maintenance_counts = Counter()
refactor_count = 0
bug_fix_count = 0
total_analyzed = 100

print(f"Cloning/Opening repository at: {local_path}")
print(f"Mining the last {total_analyzed} commits...")

try:
    count = 0
    for commit in Repository(urls, order='reverse', clone_repo_to=local_path).traverse_commits():
        if count >= total_analyzed:
            break
        
        count += 1
        msg = commit.msg.lower()
        
        # Maintenance keywords
        is_refactor = any(word in msg for word in ['refactor', 'cleanup', 'style', 'restructure'])
        is_fix = any(word in msg for word in ['fix', 'bug', 'issue', 'close', 'patch'])
        
        if is_refactor: refactor_count += 1
        if is_fix: bug_fix_count += 1

        # Improved path detection
        if is_refactor or is_fix:
            found_modules_in_this_commit = set()
            for m in commit.modified_files:
                # Use both new and old path to catch deletions/renames
                path = m.new_path or m.old_path
                if path:
                    # Normalize path separators for Windows/Linux consistency
                    normalized_path = path.replace('\\', '/').split('/')
                    
                    for module in TARGET_MODULES:
                        # Check if the module name exists as a directory in the path
                        if module in normalized_path:
                            found_modules_in_this_commit.add(module)
            
            for module in found_modules_in_this_commit:
                maintenance_counts[module] += 1
        
        # Progress indicator so you know it's not frozen
        print(f"[{count}/{total_analyzed}] Analyzed: {commit.hash[:7]}", end='\r')

    # --- OUTPUT ---
    print("\n" + "="*65)
    print(" WGER SOFTWARE MAINTENANCE ANALYSIS")
    print("="*65)
    print(f"Total Refactoring Events: {refactor_count}")
    print(f"Total Bug Fix Events:      {bug_fix_count}")
    print("-" * 65)
    print(f"{'Module':<15} | {'Maint. Activity':<18} | {'Insight'}")
    print("-" * 65)

    for mod in TARGET_MODULES:
        activity = maintenance_counts[mod]
        if activity > 10:
            insight = "High Flux (Frequent Changes)"
        elif activity > 0:
            insight = "Active Maintenance"
        else:
            insight = "No Recent Changes"
        print(f"{mod:<15} | {activity:<18} | {insight}")

    print("="*65)

except Exception as e:
    print(f"\nAn error occurred: {e}")