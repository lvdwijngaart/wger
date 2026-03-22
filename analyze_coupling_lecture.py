import os
import ast
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# 1. Define your target modules (subsystems)
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
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports

def analyze_wger_mq(root_dir):
    module_file_counts = defaultdict(int)
    intra_edges = defaultdict(int)
    inter_edges = defaultdict(lambda: defaultdict(int))

    for root, dirs, files in os.walk(root_dir):
        parts = os.path.normpath(root).split(os.sep)
        current_mod = next((m for m in TARGET_MODULES if m in parts), None)
        if not current_mod: continue

        for file in files:
            if file.endswith('.py'):
                module_file_counts[current_mod] += 1
                found_imports = get_imports_from_file(os.path.join(root, file))
                for imp in found_imports:
                    for target in TARGET_MODULES:
                        if f"wger.{target}" in imp or imp.startswith(target):
                            if target == current_mod:
                                intra_edges[current_mod] += 1
                            else:
                                inter_edges[current_mod][target] += 1

    # Calculate Ai
    ai_values = {mod: (intra_edges[mod] / (module_file_counts[mod]**2) if module_file_counts[mod] > 0 else 0) for mod in TARGET_MODULES}

    # Calculate Ei,j Matrix
    ei_j_matrix = defaultdict(dict)
    ei_j_list = []
    for i, mod_i in enumerate(TARGET_MODULES):
        for j, mod_j in enumerate(TARGET_MODULES):
            if i == j: continue
            ni, nj = module_file_counts[mod_i], module_file_counts[mod_j]
            epsilon_ij = inter_edges[mod_i][mod_j] + inter_edges[mod_j][mod_i]
            e_ij = epsilon_ij / (2 * ni * nj) if (ni > 0 and nj > 0) else 0
            ei_j_matrix[mod_i][mod_j] = e_ij
            if i < j: ei_j_list.append(e_ij)

    # Final MQ
    k = len(TARGET_MODULES)
    avg_ai = sum(ai_values.values()) / k
    num_pairs = (k * (k - 1)) / 2
    avg_ei_j = sum(ei_j_list) / num_pairs if num_pairs > 0 else 0
    mq = avg_ai - avg_ei_j
    
    return mq, ai_values, ei_j_matrix, avg_ai, avg_ei_j

def plot_interconnectivity_heatmap(ei_j_matrix, modules):
    # 1. Convert the nested dictionary to a structured DataFrame
    df_data = []
    for m1 in modules:
        row = []
        for m2 in modules:
            # Diagonals (intra-connectivity) are usually 0 or NaN in an Eij matrix
            val = ei_j_matrix[m1].get(m2, 0) if m1 != m2 else 0
            row.append(val)
        df_data.append(row)
    
    df = pd.DataFrame(df_data, index=modules, columns=modules)

    # 2. Setup the visual style
    plt.figure(figsize=(12, 10))
    sns.set_theme(style="white")
    
    # 3. Create the heatmap
    # cmap='YlGnBu' (Yellow-Green-Blue) is great for density
    ax = sns.heatmap(
        df, 
        annot=True,       # Show the actual Eij values in the cells
        fmt=".4f",        # Format to 4 decimal places
        cmap="YlGnBu", 
        linewidths=.5, 
        cbar_kws={"label": "Coupling Density (Ei,j)"}
    )

    plt.title('WGER Subsystem Inter-connectivity Heatmap (Coupling Density)', fontsize=16, pad=20)
    plt.xlabel('Target Module', fontsize=12)
    plt.ylabel('Source Module', fontsize=12)
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.show()

# --- Execution and Enhanced Printing ---
final_mq, all_ai, all_ei_j, avg_ai, avg_ei_j = analyze_wger_mq('wger')

print("="*90)
print(f"{'WGER ARCHITECTURAL METRICS (LECTURE 03)':^90}")
print("="*90)

# 1. Intra-connectivity Table
print(f"\n[PART 1: INTRA-CONNECTIVITY (Ai) - Internal Cohesion]")
print(f"{'-'*45}")
print(f"{'Module':<15} | {'Ai Score':<10}")
print(f"{'-'*45}")
for mod, ai in all_ai.items():
    print(f"{mod:<15} | {ai:.6f}")

# 2. Inter-connectivity Matrix (The missing piece)
print(f"\n[PART 2: INTER-CONNECTIVITY (Ei,j) MATRIX - Coupling Density]")
header = " " * 12 + "".join([f"{m[:5]:>8}" for m in TARGET_MODULES])
print(header)
for m1 in TARGET_MODULES:
    row = f"{m1[:10]:<12}"
    for m2 in TARGET_MODULES:
        if m1 == m2:
            row += f"{'-':>8}"
        else:
            val = all_ei_j[m1].get(m2, 0)
            row += f"{val:.4f}".replace("0.", ".") if val > 0 else f"{'0':>8}"
    print(row)

# 3. Final Calculation Summary
print(f"\n[PART 3: MODULARITY QUALITY (MQ) SUMMARY]")
print(f"{'='*45}")
print(f"Average Intra-connectivity (Avg Ai):   {avg_ai:.6f}")
print(f"Average Inter-connectivity (Avg Eij):  {avg_ei_j:.6f}")
print(f"{'-'*45}")
print(f"FINAL SYSTEM MQ (Avg Ai - Avg Eij):    {final_mq:.6f}")
print(f"{'='*45}")
print("INTERPRETATION: Higher MQ indicates better modularity (high cohesion, low coupling).")

plot_interconnectivity_heatmap(all_ei_j, TARGET_MODULES)