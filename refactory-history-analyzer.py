import json
import matplotlib.pyplot as plt
from collections import Counter

# --- CONFIGURATION ---
JSON_FILE = 'wger_results.json'
TARGET_MODULES = ['core', 'exercises', 'gallery', 'mailer', 'trophies', 'gym', 'nutrition', 'manager', 'measurements', 'weight']

# Replace these with the actual results from your first script
# Higher Ai = Better internal cohesion
AI_SCORES = {
    'core': 0.054, 'exercises': 0.042, 'gallery': 0.120, 'mailer': 0.090, 
    'trophies': 0.110, 'gym': 0.065, 'nutrition': 0.078, 'manager': 0.045, 
    'measurements': 0.088, 'weight': 0.092
}

def run_modularity_evolution_analysis(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return

    # 1. Initialize Counters
    module_counts = Counter()
 
    # 2. Process JSON (Extracting refactoring counts per module)
    for commit in data.get('commits', []):
        for ref in commit.get('refactorings', []):
            affected_modules = set()
            for loc in ref.get('rightSideLocations', []):
                path = loc.get('filePath', '')
                for mod in TARGET_MODULES:
                    # Logic: is the module name a folder in the path?
                    if f"/{mod}/" in f"/{path}": 
                        affected_modules.add(mod)
            
            for mod in affected_modules:
                module_counts[mod] += 1

    # 3. Prepare Plotting Data
    refactoring_activity = [module_counts[mod] for mod in TARGET_MODULES]
    cohesion_scores = [AI_SCORES.get(mod, 0) for mod in TARGET_MODULES]

    # 4. GENERATE PLOT
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Refactoring Activity (Bars) - The "Effort"
    ax1.set_xlabel('Wger Subsystems', fontweight='bold')
    ax1.set_ylabel('Refactoring Events (Count)', color='tab:blue', fontweight='bold')
    bars = ax1.bar(TARGET_MODULES, refactoring_activity, color='tab:blue', alpha=0.5, label='Refactoring Effort')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Intra-connectivity (Line) - The "Quality"
    ax2 = ax1.twinx()
    ax2.set_ylabel('Intra-connectivity (Ai Score)', color='tab:green', fontweight='bold')
    ax2.plot(TARGET_MODULES, cohesion_scores, color='tab:green', marker='D', linewidth=3, label='Internal Cohesion (Ai)')
    ax2.tick_params(axis='y', labelcolor='tab:green')

    # Add labels to the bars for clarity
    ax1.bar_label(bars, padding=3)

    plt.title('Evolution vs. Modularity: Is Refactoring improving Cohesion?', fontsize=15)
    fig.tight_layout()
    
    # Legend
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper right')

    plt.show()

if __name__ == "__main__":
    run_modularity_evolution_analysis(JSON_FILE)