import os
import ast
from collections import defaultdict
import matplotlib.pyplot as plt

TARGET_MODULES = ['core', 'exercises', 'gallery', 'mailer', 'trophies', 'gym', 'nutrition', 'manager', 'measurements', 'weight']

def get_imports_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read())
        except Exception:
            return []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names: imports.append(n.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports

def analyze_fan_metrics(root_dir):
    fan_out_relations = defaultdict(set) 
    fan_in_relations = defaultdict(set)

    for root, dirs, files in os.walk(root_dir):
        parts = os.path.normpath(root).split(os.sep)
        current_mod = next((m for m in TARGET_MODULES if m in parts), None)
        if not current_mod: continue

        for file in files:
            if file.endswith('.py'):
                imports = get_imports_from_file(os.path.join(root, file))
                for imp in imports:
                    for target in TARGET_MODULES:
                        if (f"wger.{target}" in imp or imp.startswith(target)) and target != current_mod:
                            fan_out_relations[current_mod].add(target)
                            fan_in_relations[target].add(current_mod)
    return fan_in_relations, fan_out_relations

# --- Execution ---
fan_in_map, fan_out_map = analyze_fan_metrics('wger')

# Prepare data for plotting
names = []
fan_ins = []
fan_outs = []

print("="*65)
print(f"{'Module':<15} | {'Fan-in':<10} | {'Fan-out':<10} | {'Metric Type'}")
print("="*65)

for mod in TARGET_MODULES:
    fi = len(fan_in_map[mod])
    fo = len(fan_out_map[mod])
    names.append(mod)
    fan_ins.append(fi)
    fan_outs.append(fo)
    
    if fi > fo: m_type = "High Fan-in (Server/Utility)"
    elif fo > fi: m_type = "High Fan-out (Controller)"
    else: m_type = "Balanced"
    print(f"{mod:<15} | {fi:<10} | {fo:<10} | {m_type}")

# --- Generate Scatter Plot ---
fig, ax = plt.subplots(figsize=(10, 8))
ax.scatter(fan_outs, fan_ins, color='blue', s=100, zorder=3)

# Add labels to points
for i, txt in enumerate(names):
    ax.annotate(txt, (fan_outs[i], fan_ins[i]), xytext=(8, 8), 
                textcoords='offset points', fontsize=9)

# Define quadrant midpoints
max_x = max(fan_outs) + 1 if fan_outs else 10
max_y = max(fan_ins) + 1 if fan_ins else 10
mid_x = max_x / 2
mid_y = max_y / 2

# Quadrant Labels using Coordinate Transformation (0,0 is bottom-left, 1,1 is top-right)
# Horizontal alignment (ha) and Vertical alignment (va) prevent overlap with edges
ax.text(0.02, 0.95, 'UTILITIES / STABLE\n(High Fan-in, Low Fan-out)', 
        transform=ax.transAxes, fontsize=10, color='green', fontweight='bold', va='top')

ax.text(0.98, 0.95, 'COMPLEX / TANGLED\n(High Fan-in, High Fan-out)', 
        transform=ax.transAxes, fontsize=10, color='red', fontweight='bold', va='top', ha='right')

ax.text(0.02, 0.05, 'ISOLATED / LEAVES\n(Low Fan-in, Low Fan-out)', 
        transform=ax.transAxes, fontsize=10, color='gray', fontweight='bold', va='bottom')

ax.text(0.98, 0.05, 'CONTROLLERS / VOLATILE\n(Low Fan-in, High Fan-out)', 
        transform=ax.transAxes, fontsize=10, color='orange', fontweight='bold', va='bottom', ha='right')

# Styling the plot
ax.set_title('Wger Architecture: Fan-in vs Fan-out Analysis', fontsize=14, pad=20)
ax.set_xlabel('Fan-out (Structural Complexity / Efferent)', fontsize=12)
ax.set_ylabel('Fan-in (Stability / Afferent)', fontsize=12)

# Set limits and draw quadrant dividers
ax.set_xlim(-0.5, max_x)
ax.set_ylim(-0.5, max_y)
ax.axhline(mid_y, color='black', linestyle='--', alpha=0.2)
ax.axvline(mid_x, color='black', linestyle='--', alpha=0.2)
ax.grid(True, which='both', linestyle=':', alpha=0.4)

plt.tight_layout() # Automatically adjusts subplots to fit labels
plt.show()