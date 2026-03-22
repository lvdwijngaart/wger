import os
import ast
from collections import defaultdict

# Define the modules you want to track based on wger's structure
TARGET_MODULES = ['core', 'exercises', 'gallery', 'mailer', 'trophies', 'gym', 'nutrition', 'manager', 'measurements', 'weight']

def get_imports_from_file(file_path):
    """Extracts all top-level imports from a python file using AST."""
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read())
        except Exception: # Catch syntax errors or encoding issues
            return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports

def analyze_wger_coupling(root_dir):
    dependency_map = defaultdict(lambda: defaultdict(int))
    
    # Track totals for stability metrics
    efferent_count = defaultdict(int) # Ce: Outgoing
    afferent_count = defaultdict(int) # Ca: Incoming

    for root, dirs, files in os.walk(root_dir):
        parts = os.path.normpath(root).split(os.sep)
        current_mod = next((m for m in TARGET_MODULES if m in parts), None)
        
        if not current_mod:
            continue

        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                found_imports = get_imports_from_file(full_path)

                for imp in found_imports:
                    for target in TARGET_MODULES:
                        # Check if it's an internal wger import but not a self-import
                        if (f"wger.{target}" in imp or imp.startswith(target)) and target != current_mod:
                            dependency_map[current_mod][target] += 1
                            efferent_count[current_mod] += 1
                            afferent_count[target] += 1

    return dependency_map, efferent_count, afferent_count

def get_insight(source, target, strength, dep_map):
    """Generates a brief architectural insight based on the coupling data."""
    if strength > 30:
        return "Strong Dependency: Architectural Backbone"
    if target == 'core' and strength > 10:
        return "Standard: Feature-to-Core dependency"
    if source == 'core':
        return "Warning: Potential Leakage (Core depending on Feature)"
    if target in dep_map and source in dep_map[target]:
        return "Refactor Alert: Bidirectional/Circular Coupling"
    return "Loose Coupling: Good Modularity"

# --- Execute and Print ---
results, ce_map, ca_map = analyze_wger_coupling('wger')

header = f"{'Source (Ce)':<15} | {'Target (Ca)':<15} | {'Strength':<8} | {'Architectural Insight'}"
print("\n" + "="*85)
print(" WGER SOFTWARE METRICS: COUPLING ANALYSIS")
print("="*85)
print(header)
print("-" * 85)

for source, targets in sorted(results.items()):
    for target, count in sorted(targets.items(), key=lambda x: x[1], reverse=True):
        insight = get_insight(source, target, count, results)
        # We append the total Ce and Ca in parentheses for academic clarity
        s_label = f"{source} ({ce_map[source]})"
        t_label = f"{target} ({ca_map[target]})"
        print(f"{s_label:<15} | {t_label:<15} | {count:<8} | {insight}")

print("-" * 85)
print("METRIC KEY:")
print("Ce (Efferent): Outgoing dependencies. Higher = More fragile.")
print("Ca (Afferent): Incoming dependencies. Higher = More stable/central.")
print("="*85)