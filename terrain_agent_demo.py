from sar_project.agents.terrain_agent import TerrainAnalystAgent
import json
import os

def demo_terrain_agent():
    terrain_agent = TerrainAnalystAgent()
    
    terrain_agent.update_status("active")
    print(f"Agent status: {terrain_agent.get_status()}")
    
    search_areas = ["mountain_valley_east", "river_crossing_north", "dense_forest_west"]
    
    # 1. Analyze terrain for multiple search areas
    print("\n--- TERRAIN ANALYSIS ---")
    analyses = {}
    for area in search_areas:
        analysis = terrain_agent.analyze_terrain(area)
        analyses[area] = analysis
        print(f"\nTerrain Analysis for {area}:")
        print(json.dumps(analysis, indent=2))
    
    # 2. Identify obstacles in each area
    print("\n--- OBSTACLE IDENTIFICATION ---")
    obstacles_data = {}
    for area in search_areas:
        obstacles = terrain_agent.identify_obstacles(area)
        obstacles_data[area] = obstacles
        print(f"\nObstacles in {area}:")
        print(json.dumps(obstacles, indent=2))
    
    # 3. Generate paths between different locations
    print("\n--- PATH GENERATION ---")
    paths = [
        {"start": "base_camp_alpha", "end": "ridge_overlook", "difficulty": "normal"},
        {"start": "river_crossing_north", "end": "mountain_valley_east", "difficulty": "hard"},
        {"start": "dense_forest_west", "end": "base_camp_alpha", "difficulty": "extreme"}
    ]
    
    for path_info in paths:
        path = terrain_agent.generate_path(
            path_info["start"],
            path_info["end"],
            difficulty=path_info["difficulty"]
        )
        print(f"\nPath from {path_info['start']} to {path_info['end']} ({path_info['difficulty']} difficulty):")
        print(json.dumps(path, indent=2))
    
    # 4. Get terrain maps in GeoJSON format
    print("\n--- TERRAIN MAPS ---")
    maps_dir = "terrain_maps"
    os.makedirs(maps_dir, exist_ok=True)
    
    for area in search_areas:
        terrain_map = terrain_agent.get_terrain_map(area)
        map_file = os.path.join(maps_dir, f"{area}_map.geojson")
        
        with open(map_file, "w") as f:
            json.dump(terrain_map, f, indent=2)
        print(f"Saved terrain map for {area} to {map_file}")
    
    # 5. Monitor terrain changes (assuming some time has passed)
    print("\n--- TERRAIN MONITORING ---")
    for area in search_areas:
        changes = terrain_agent.monitor_terrain_changes(area)
        print(f"\nTerrain changes for {area}:")
        print(json.dumps(changes, indent=2))
    
    # 6. Evaluate crossing difficulty for specific obstacles
    print("\n--- CROSSING DIFFICULTY EVALUATION ---")
    obstacle_types = ["water_crossing", "steep_slope", "dense_vegetation"]
    
    for area in search_areas:
        for obstacle_type in obstacle_types:
            evaluation = terrain_agent.evaluate_crossing_difficulty(area, obstacle_type)
            if "error" not in evaluation:
                print(f"\nCrossing difficulty for {obstacle_type} in {area}:")
                print(json.dumps(evaluation, indent=2))

if __name__ == "__main__":
    demo_terrain_agent()