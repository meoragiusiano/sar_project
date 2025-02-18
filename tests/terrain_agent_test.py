import pytest
import json
from datetime import datetime, timedelta
from sar_project.agents.terrain_agent import TerrainAnalystAgent
from sar_project.agents.weather_agent import WeatherAgent

class MockKnowledgeBase:
    def __init__(self):
        self.terrain_data = {}
    
    def update_terrain(self, location, data):
        self.terrain_data[location] = data
        return True

class TestTerrainAnalystAgent:
    @pytest.fixture
    def agent(self):
        return TerrainAnalystAgent()
    
    @pytest.fixture
    def agent_with_kb(self):
        agent = TerrainAnalystAgent()
        kb = MockKnowledgeBase()
        agent.set_knowledge_base(kb)
        return agent, kb

    def test_initialization(self, agent):
        assert agent.name == "terrain_analyst"
        assert agent.role == "Terrain Analyst"
        assert agent.mission_status == "standby"
        assert agent.terrain_maps == {}
        assert agent.obstacle_database == {}
        assert agent.current_analysis == {}
        assert agent.knowledge_base is None
        assert isinstance(agent.weather_agent, WeatherAgent)
    
    def test_set_knowledge_base(self, agent):
        kb = MockKnowledgeBase()
        agent.set_knowledge_base(kb)
        assert agent.knowledge_base is kb
    
    def test_analyze_terrain(self, agent):
        location = "mountain_region_1"
        response = agent.analyze_terrain(location)
        
        assert "location" in response
        assert response["location"] == location
        assert "terrain_types" in response
        assert "elevation" in response
        assert isinstance(response["elevation"], dict)
        assert "min" in response["elevation"]
        assert "max" in response["elevation"]
        assert "slope" in response
        assert "vegetation_density" in response
        assert 0 <= response["vegetation_density"] <= 1
        assert "analysis_timestamp" in response
        assert "weather_conditions" in response
        assert "weather_risks" in response
        assert "terrain_weather_interactions" in response
    
    def test_analyze_terrain_without_weather(self, agent):
        location = "mountain_region_2"
        response = agent.analyze_terrain(location, include_weather=False)
        
        assert "location" in response
        assert "weather_conditions" not in response
        assert "weather_risks" not in response
        assert "terrain_weather_interactions" not in response
    
    def test_analyze_terrain_with_knowledge_base(self, agent_with_kb):
        agent, kb = agent_with_kb
        location = "mountain_region_3"
        response = agent.analyze_terrain(location)
        
        assert location in kb.terrain_data
        assert kb.terrain_data[location] == response
    
    def test_identify_obstacles(self, agent):
        location = "dense_forest_area"
        response = agent.identify_obstacles(location)
        
        assert "location" in response
        assert response["location"] == location
        assert "obstacle_count" in response
        assert "obstacles" in response
        assert "analysis_timestamp" in response
        assert "weather_factored" in response
        
        for obstacle in response["obstacles"]:
            assert "type" in obstacle
            assert "severity" in obstacle
            assert "coordinates" in obstacle
            assert "details" in obstacle
    
    def test_identify_obstacles_without_weather(self, agent):
        location = "dense_forest_area_2"
        response = agent.identify_obstacles(location, include_weather=False)
        
        assert "location" in response
        assert "weather_factored" in response
        assert response["weather_factored"] is False
    
    def test_generate_path(self, agent):
        start = "base_camp"
        end = "mountain_ridge"
        response = agent.generate_path(start, end)
        
        assert "start" in response
        assert response["start"] == start
        assert "end" in response
        assert response["end"] == end
        assert "difficulty" in response
        assert "distance_km" in response
        assert "estimated_time_hours" in response
        assert "base_time_hours" in response
        assert "weather_delay_hours" in response
        assert "waypoints" in response
        assert "terrain_challenges" in response
        assert "recommended_equipment" in response
        assert "generated_timestamp" in response
        assert "weather_conditions" in response
        assert "weather_risks" in response
        
        for waypoint in response["waypoints"]:
            assert "id" in waypoint
            assert "coordinates" in waypoint
            assert "estimated_time_from_previous" in waypoint
    
    def test_generate_path_without_weather(self, agent):
        start = "base_camp_2"
        end = "mountain_ridge_2"
        response = agent.generate_path(start, end, include_weather=False)
        
        assert "weather_conditions" not in response
        assert "weather_risks" not in response
    
    def test_get_terrain_map_geojson(self, agent):
        location = "river_valley"
        response = agent.get_terrain_map(location, "geojson")
        
        assert "type" in response
        assert response["type"] == "FeatureCollection"
        assert "features" in response
        assert len(response["features"]) > 0
        
        for feature in response["features"]:
            assert "type" in feature
            assert feature["type"] == "Feature"
            assert "geometry" in feature
            assert "properties" in feature
    
    def test_get_terrain_map_unsupported_format(self, agent):
        location = "river_valley"
        response = agent.get_terrain_map(location, "unsupported_format")
        
        assert "error" in response
        assert "Unsupported format" in response["error"]
    
    def test_monitor_terrain_changes(self, agent):
        location = "coastal_area"
        agent.analyze_terrain(location) 
        
        response = agent.monitor_terrain_changes(location)
        
        assert "location" in response
        assert response["location"] == location
        assert "last_analysis" in response
        assert "current_time" in response
        assert "detected_changes" in response
        assert "requires_reanalysis" in response
        assert "current_weather" in response
    
    def test_monitor_terrain_changes_no_prior_analysis(self, agent):
        location = "unknown_area"
        response = agent.monitor_terrain_changes(location)
        
        assert "location" in response
        assert "error" in response
        assert "No prior analysis available" in response["error"]
    
    def test_process_request_analyze_terrain(self, agent):
        message = {
            "analyze_terrain": True,
            "location": "mountain_valley",
            "resolution": "high"
        }
        response = agent.process_request(message)
        
        assert "location" in response
        assert response["location"] == "mountain_valley"
        assert "resolution" in response
        assert response["resolution"] == "high"
    
    def test_process_request_identify_obstacles(self, agent):
        message = {
            "identify_obstacles": True,
            "location": "rocky_hills"
        }
        response = agent.process_request(message)
        
        assert "location" in response
        assert response["location"] == "rocky_hills"
        assert "obstacles" in response
    
    def test_process_request_generate_path(self, agent):
        message = {
            "generate_path": True,
            "start": "trailhead",
            "end": "summit",
            "difficulty": "hard"
        }
        response = agent.process_request(message)
        
        assert "start" in response
        assert response["start"] == "trailhead"
        assert "end" in response
        assert response["end"] == "summit"
        assert "difficulty" in response
    
    def test_process_request_get_terrain_map(self, agent):
        message = {
            "get_terrain_map": True,
            "location": "forest_ridge",
            "format": "geojson"
        }
        response = agent.process_request(message)
        
        assert "type" in response
        assert response["type"] == "FeatureCollection"
    
    def test_process_request_monitor_terrain_changes(self, agent):
        location = "lake_area"
        agent.analyze_terrain(location)
        
        message = {
            "monitor_terrain_changes": True,
            "location": "lake_area"
        }
        response = agent.process_request(message)
        
        assert "location" in response
        assert response["location"] == "lake_area"
        assert "detected_changes" in response
    
    def test_process_request_unknown(self, agent):
        message = {
            "unknown_request": True
        }
        response = agent.process_request(message)
        
        assert "error" in response
        assert "Unknown request type" in response["error"]
    
    def test_status_update(self, agent):
        response = agent.update_status("active")
        assert response["new_status"] == "active"
        assert agent.get_status() == "active"
        
        response = agent.update_status("on_mission")
        assert response["new_status"] == "on_mission"
        assert agent.get_status() == "on_mission"