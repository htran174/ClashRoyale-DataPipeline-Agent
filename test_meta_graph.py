from src.workflows.meta_workflow import build_meta_graph

graph = build_meta_graph()

state = graph.invoke({})

print("State keys:", state.keys())
print("Top players:", len(state.get("top_players", [])))
print("Selected players:", len(state.get("selected_players", [])))
print("Used indices:", len(state.get("used_player_indices", [])))
print("Notes:")
for note in state.get("notes", []):
    print(" -", note)
