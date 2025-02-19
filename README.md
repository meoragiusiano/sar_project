# Terrain Analyst Agent

## Overview
The Terrain Analyst Agent is a component of the Search and Rescue (SAR) operations system, designed to analyze terrain conditions, identify obstacles, and generate path recommendations for SAR missions. This agent integrates terrain analysis with real-time weather data to provide comprehensive environmental assessments for SAR operations.

NOTE: I have added a terrain_agent_demo.py script for an easy test of this agent. Run to see typical output of this agent

## Key Features

### 1. Terrain Analysis
- Comprehensive terrain type identification
- Elevation analysis
- Slope assessment
- Vegetation density evaluation
- Soil type classification
- Weather condition integration

### 2. Obstacle Identification
- Detection and classification of various obstacles:
  - Steep slopes
  - Water crossings
  - Dense vegetation
  - Flash flood areas
  - Sandy terrain
  - Boggy ground
  - Low visibility areas
  - Wind hazards
- Severity assessment for each obstacle
- Weather impact consideration on obstacles

### 3. Path Generation
- Path planning between two points
- Waypoint generation with time estimates
- Difficulty assessment based on terrain and weather
- Equipment recommendations
- Weather delay calculations
- Terrain challenge identification and mitigation strategies

### 4. Terrain Mapping
- GeoJSON format support
- Integrated weather overlay
- Obstacle visualization
- Terrain-weather interaction mapping

### 5. Real-time Monitoring
- Continuous terrain condition monitoring
- Detection of weather-induced changes
- Assessment of terrain-weather interactions
- Updates on crossing difficulties

## Usage

### Basic Initialization
```python
from sar_project.agents.terrain_agent import TerrainAnalystAgent
from sar_project.agents.weather_agent import WeatherAgent

# Initialize with optional weather agent
weather_agent = WeatherAgent()
terrain_agent = TerrainAnalystAgent(weather_agent=weather_agent)
```

### Analyzing Terrain
```python
analysis = terrain_agent.analyze_terrain(
    location="mountain_area_1",
    resolution="medium",
    include_weather=True
)
```

### Identifying Obstacles
```python
obstacles = terrain_agent.identify_obstacles(
    location="river_crossing_2",
    include_weather=True
)
```

### Generating Path
```python
path = terrain_agent.generate_path(
    start="base_camp",
    end="target_location",
    difficulty="normal",
    include_weather=True
)
```

### Getting Terrain Map
```python
terrain_map = terrain_agent.get_terrain_map(
    location="search_area_3",
    format="geojson",
    include_weather=True
)
```

## Key Methods

### analyze_terrain()
Performs comprehensive terrain analysis including:
- Terrain type identification
- Elevation analysis
- Weather condition integration
- Terrain-weather interaction assessment

### identify_obstacles()
Identifies and catalogs obstacles in a given location:
- Categorizes obstacle types
- Assigns severity ratings
- Considers weather impacts
- Provides detailed obstacle characteristics

### generate_path()
Creates optimal path recommendations:
- Generates waypoints
- Calculates time estimates
- Accounts for weather delays
- Provides equipment recommendations

### evaluate_crossing_difficulty()
Assesses specific crossing challenges:
- Difficulty rating calculation
- Weather impact consideration
- Crossing time estimation
- Safety recommendations

### monitor_terrain_changes()
Tracks changes in terrain conditions:
- Weather-induced changes
- Terrain condition updates
- Risk assessment updates

## Integration with Weather System

The agent integrates with a WeatherAgent to provide:
- Real-time weather condition monitoring
- Weather impact assessment on terrain
- Weather-based difficulty adjustments
- Terrain-weather interaction analysis

## Data Structures

### Terrain Analysis Output
```python
{
    "location": str,
    "terrain_types": list,
    "elevation": {
        "min": int,
        "max": int
    },
    "slope": int,
    "vegetation_density": float,
    "soil_type": str,
    "weather_conditions": dict,
    "terrain_weather_interactions": list
}
```

### Obstacle Data
```python
{
    "type": str,
    "severity": str,
    "coordinates": list,
    "details": dict
}
```

### Path Data
```python
{
    "start": str,
    "end": str,
    "difficulty": str,
    "distance_km": float,
    "estimated_time_hours": float,
    "waypoints": list,
    "terrain_challenges": list,
    "recommended_equipment": list
}
```

## Limitations

- Relies on simulated coordinate generation (replace with real geocoding in production)
- Weather data integration requires active WeatherAgent
- Terrain data is currently simulated (integrate with real GIS data in production)
- Distance calculations use simplified Haversine formula
