import pandas as pd

no_memory_file = "data/llm_paths_all_gpt4omini_no_memory.tsv"
memory_file = "data/llm_paths_all_gpt40mini_memory.tsv"

no_memory_df = pd.read_csv(no_memory_file, sep="\t")
memory_df = pd.read_csv(memory_file, sep="\t")

# no_memory_paths = no_memory_df.set_index('path_id')['path'].to_dict()

# Prendre en compte les chemins qui ne se terminent pas par "LOOP_DETECTED"
no_memory_filtered = no_memory_df[~no_memory_df['path'].str.endswith("LOOP_DETECTED")]
no_memory_paths = no_memory_filtered.set_index("path_id")["path"].to_dict()

results = []

for _, row in memory_df.iterrows():
    path_id = row['path_id']
    memory_path = row['path']

    if path_id in no_memory_paths:
        no_memory_path = no_memory_paths[path_id]
        is_same = memory_path == no_memory_path
        results.append({
            'path_id': path_id,
            'memory_path': memory_path,
            'no_memory_path': no_memory_path,
            'memory_path_length': len(memory_path.split(';')),
            'no_memory_path_length': len(no_memory_path.split(';')),
            'is_same': is_same
        })

results_df = pd.DataFrame(results)

results_df.to_csv("comparison_results.csv", index=False)

total = len(results)
same_count = results_df['is_same'].sum()
different_count = total - same_count

print(f"Nombre total de chemins: {total}")
print(f"Nombre de chemins identiques: {same_count}")
print(f"Nombre de chemins différents: {different_count}")
print(f"Pourcentage de chemins identiques: {same_count / total * 100:.2f}%")

length_diff = results_df['memory_path_length'] - results_df['no_memory_path_length']
print(f"Différence moyenne de longueur de chemin: {length_diff.mean():.2f}")
print(f"Différence maximale de longueur de chemin: {length_diff.max()}")
print(f"Différence minimale de longueur de chemin: {length_diff.min()}")
print(f"Pourcentage de chemins avec une meme longueur: {((length_diff == 0).sum() / total) * 100:.2f}%")

print("La comparaison est terminée. Les résultats sont enregistrés dans 'comparison_results.csv'.")
