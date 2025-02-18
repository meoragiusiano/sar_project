from sar_project.agents.base_agent import SARBaseAgent
from sar_project.agents.weather_agent import WeatherAgent
import json
import random
import os
from datetime import datetime, timedelta

class TerrainAnalystAgent(SARBaseAgent):
    def __init__(self, name="terrain_analyst", weather_agent=None):
        super().__init__(
            name=name,
            role="Terrain Analyst",
            system_message="""You are a terrain analyst for SAR operations. Your role is to:
            1. Analyze terrain data for path planning
            2. Identify obstacles and challenging terrain features
            3. Provide terrain maps and data to search planners
            4. Generate path recommendations based on terrain analysis and weather conditions
            5. Monitor terrain conditions that may affect operations
            6. Assess terrain-weather interactions for operational safety"""
        )
        self.terrain_maps = {}
        self.obstacle_database = {}
        self.current_analysis = {}
        self.mission_status = "standby"
        self.weather_agent = weather_agent if weather_agent else WeatherAgent()
        self.knowledge_base = None
        
    def set_knowledge_base(self, knowledge_base):
        """Set a knowledge base for persistent storage"""
        self.knowledge_base = knowledge_base
        
    def process_request(self, message):
        """Process terrain-related requests"""
        try:
            if "analyze_terrain" in message:
                return self.analyze_terrain(
                    message["location"], 
                    message.get("resolution", "medium"),
                    message.get("include_weather", True)
                )
            elif "identify_obstacles" in message:
                return self.identify_obstacles(
                    message["location"],
                    message.get("include_weather", True)
                )
            elif "generate_path" in message:
                return self.generate_path(
                    message["start"], 
                    message["end"], 
                    message.get("difficulty", "normal"),
                    message.get("include_weather", True)
                )
            elif "get_terrain_map" in message:
                return self.get_terrain_map(
                    message["location"], 
                    message.get("format", "geojson"),
                    message.get("include_weather", True)
                )
            elif "monitor_terrain_changes" in message:
                return self.monitor_terrain_changes(message["location"])
            elif "evaluate_crossing_difficulty" in message:
                return self.evaluate_crossing_difficulty(
                    message["location"],
                    message["obstacle_type"]
                )
            else:
                return {"error": "Unknown request type"}
        except Exception as e:
            return {"error": str(e)}

    def analyze_terrain(self, location, resolution="medium", include_weather=True):
        """Analyze terrain for a specific location with optional weather integration"""
        # I'm making up this data, in real life call external GIS APIs'
        
        terrain_types = ["forest", "mountain", "river", "plains", "urban", "desert", "tundra", "swamp"]
        elevation_range = {"min": 100, "max": 1500}
        
        analysis = {
            "location": location,
            "resolution": resolution,
            "terrain_types": random.sample(terrain_types, min(3, len(terrain_types))),
            "elevation": {
                "min": random.randint(elevation_range["min"], elevation_range["max"] - 200),
                "max": random.randint(elevation_range["max"] - 200, elevation_range["max"])
            },
            "slope": random.randint(0, 60),
            "water_bodies": random.randint(0, 5),
            "vegetation_density": random.uniform(0, 1),
            "soil_type": random.choice(["rocky", "sandy", "clay", "loam", "peat"]),
            "analysis_timestamp": self._get_timestamp()
        }
        
        if include_weather:
            weather_data = self.weather_agent.get_current_conditions(location)
            weather_risks = self.weather_agent.assess_weather_risk(location)
            
            analysis["weather_conditions"] = weather_data
            analysis["weather_risks"] = weather_risks["risks"]
            analysis["terrain_weather_interactions"] = self._analyze_terrain_weather_interactions(
                analysis, 
                weather_data
            )
        
        self.current_analysis[location] = analysis
        
        if self.knowledge_base:
            self.knowledge_base.update_terrain(location, analysis)
        
        return analysis
    
    def identify_obstacles(self, location, include_weather=True):
        """Identify obstacles in a specific location with weather considerations"""
        if location not in self.current_analysis:
            self.analyze_terrain(location, include_weather=include_weather)
            
        analysis = self.current_analysis[location]
        
        obstacles = []

        obstacles.append({
            "type": "generic_obstacle",
            "severity": "medium",
            "coordinates": self._generate_random_coordinates(location),
            "details": {
                "description": "General terrain challenge",
                "area_sq_meters": random.randint(50, 500)
            }
        })
        
        # Terrain-based obstacles
        if "mountain" in analysis["terrain_types"]:
            obstacles.append({
                "type": "steep_slope",
                "severity": "high",
                "coordinates": self._generate_random_coordinates(location),
                "details": {
                    "slope_degrees": random.randint(30, 60),
                    "length_meters": random.randint(100, 500)
                }
            })
            
        if "river" in analysis["terrain_types"] or "obstacle_type" in location:
            obstacles.append({
                "type": "water_crossing",
                "severity": "medium",
                "coordinates": self._generate_random_coordinates(location),
                "details": {
                    "width_meters": random.randint(5, 30),
                    "depth_meters": random.uniform(0.5, 3.0),
                    "current_speed": random.uniform(1.0, 5.0)
                }
            })
            
        if analysis["vegetation_density"] > 0.7:
            obstacles.append({
                "type": "dense_vegetation",
                "severity": "medium",
                "coordinates": self._generate_random_coordinates(location),
                "details": {
                    "area_sq_meters": random.randint(100, 5000),
                    "visibility_meters": random.randint(1, 10),
                    "vegetation_type": random.choice(["thick brush", "dense forest", "thorny bushes"])
                }
            })
            
        if "desert" in analysis["terrain_types"]:
            obstacles.append({
                "type": "sandy_terrain",
                "severity": "medium",
                "coordinates": self._generate_random_coordinates(location),
                "details": {
                    "area_sq_meters": random.randint(500, 10000),
                    "sand_depth_cm": random.randint(10, 100)
                }
            })
        
        if "swamp" in analysis["terrain_types"]:
            obstacles.append({
                "type": "boggy_ground",
                "severity": "high",
                "coordinates": self._generate_random_coordinates(location),
                "details": {
                    "area_sq_meters": random.randint(50, 2000),
                    "depth_meters": random.uniform(0.3, 2.0)
                }
            })
        
        if include_weather and "weather_conditions" in analysis:
            weather = analysis["weather_conditions"]
            
            if weather.get("precipitation", 0) > 30:  # Significant rain
                obstacles.append({
                    "type": "flash_flood",
                    "severity": "extreme",
                    "coordinates": self._generate_random_coordinates(location),
                    "details": {
                        "depth_meters": random.uniform(0.5, 2.0),
                        "current_speed": random.uniform(2.0, 8.0),
                        "caused_by": "heavy rainfall"
                    }
                })
            
            if weather.get("visibility", 10) < 3:  # Low visibility
                obstacles.append({
                    "type": "low_visibility_area",
                    "severity": "high",
                    "coordinates": self._generate_random_coordinates(location),
                    "details": {
                        "visibility_meters": weather.get("visibility", 0) * 1000,
                        "caused_by": "fog" if weather.get("temperature", 20) < 15 else "haze"
                    }
                })
                
            if weather.get("wind_speed", 0) > 40:  # High winds
                obstacles.append({
                    "type": "wind_hazard",
                    "severity": "high",
                    "coordinates": self._generate_random_coordinates(location),
                    "details": {
                        "wind_speed_kph": weather.get("wind_speed", 0),
                        "risk": "falling branches" if "forest" in analysis["terrain_types"] else "reduced stability"
                    }
                })
        
        self.obstacle_database[location] = obstacles
        
        return {
            "location": location,
            "obstacle_count": len(obstacles),
            "obstacles": obstacles,
            "weather_factored": include_weather,
            "analysis_timestamp": self._get_timestamp()
        }
    
    def generate_path(self, start, end, difficulty="normal", include_weather=True):
        """Generate path recommendation between two points with weather considerations"""
        if start not in self.current_analysis:
            self.analyze_terrain(start, include_weather=include_weather)
        if end not in self.current_analysis:
            self.analyze_terrain(end, include_weather=include_weather)
            
        if start not in self.obstacle_database:
            self.identify_obstacles(start, include_weather=include_weather)
        if end not in self.obstacle_database:
            self.identify_obstacles(end, include_weather=include_weather)
            
        distance = self._calculate_distance_between_locations(start, end)
        
        num_waypoints = random.randint(3, 7)
        waypoints = self._generate_waypoints(start, end, num_waypoints)
        
        time_multipliers = {"easy": 0.7, "normal": 1.0, "hard": 1.5, "extreme": 2.0}
        estimated_time = distance * time_multipliers.get(difficulty, 1.0)
        
        weather_delay = 0
        if include_weather:
            start_weather = self.weather_agent.get_current_conditions(start)
            end_weather = self.weather_agent.get_current_conditions(end)
            
            avg_weather = {
                "temperature": (start_weather.get("temperature", 20) + end_weather.get("temperature", 20)) / 2,
                "wind_speed": (start_weather.get("wind_speed", 0) + end_weather.get("wind_speed", 0)) / 2,
                "precipitation": (start_weather.get("precipitation", 0) + end_weather.get("precipitation", 0)) / 2,
                "visibility": (start_weather.get("visibility", 10) + end_weather.get("visibility", 10)) / 2
            }
            
            if avg_weather["wind_speed"] > 30:
                weather_delay += 0.2 * estimated_time  # 20% delay for high winds
            if avg_weather["precipitation"] > 20:
                weather_delay += 0.3 * estimated_time  # 30% delay for heavy precipitation
            if avg_weather["visibility"] < 5:
                weather_delay += 0.25 * estimated_time  # 25% delay for low visibility
            if avg_weather["temperature"] < 0 or avg_weather["temperature"] > 35:
                weather_delay += 0.1 * estimated_time  # 10% delay for extreme temperatures
                
        final_time = estimated_time + weather_delay
        
        terrain_challenges = self._get_terrain_challenges(start, end)
        
        path_data = {
            "start": start,
            "end": end,
            "difficulty": difficulty,
            "distance_km": round(distance, 2),
            "estimated_time_hours": round(final_time, 1),
            "base_time_hours": round(estimated_time, 1),
            "weather_delay_hours": round(weather_delay, 1),
            "waypoints": waypoints,
            "terrain_challenges": terrain_challenges,
            "recommended_equipment": self._recommend_equipment(terrain_challenges),
            "generated_timestamp": self._get_timestamp()
        }
        
        if include_weather:
            path_data["weather_conditions"] = {
                "start": start_weather,
                "end": end_weather,
                "average": avg_weather
            }
            path_data["weather_risks"] = self.weather_agent.assess_weather_risk(start)["risks"]
            
        return path_data
    
    def get_terrain_map(self, location, format="geojson", include_weather=True):
        """Get terrain map for a location in specified format with optional weather overlay"""
        if location not in self.current_analysis:
            self.analyze_terrain(location, include_weather=include_weather)
        
        if location not in self.obstacle_database:
            self.identify_obstacles(location, include_weather=include_weather)
            
        obstacles = self.obstacle_database[location]
        analysis = self.current_analysis[location]
        
        if format.lower() == "geojson":
            return self._generate_geojson(location, analysis, obstacles, include_weather)
        else:
            return {"error": f"Unsupported format: {format}"}
    
    def monitor_terrain_changes(self, location):
        """Monitor terrain for changes since last analysis"""
        if location not in self.current_analysis:
            return {
                "location": location,
                "error": "No prior analysis available",
                "recommendation": "Run terrain analysis first"
            }
            
        last_analysis = self.current_analysis[location]
        last_timestamp = last_analysis["analysis_timestamp"]
        
        current_weather = self.weather_agent.get_current_conditions(location)
        terrain_changes = []
        
        # If enough time has passed or weather has changed significantly, certain terrain features could be affected
        if "weather_conditions" in last_analysis:
            old_weather = last_analysis["weather_conditions"]
            
            # Check for rainfall increase (potential flooding)
            if current_weather.get("precipitation", 0) > old_weather.get("precipitation", 0) + 20:
                terrain_changes.append({
                    "type": "increased_water_levels",
                    "description": "Recent rainfall may have raised water levels",
                    "affected_areas": ["river banks", "low-lying areas"],
                    "severity": "medium"
                })
                
            # Check for wind increase (potential fallen trees/debris)
            if current_weather.get("wind_speed", 0) > old_weather.get("wind_speed", 0) + 15:
                if "forest" in last_analysis["terrain_types"]:
                    terrain_changes.append({
                        "type": "fallen_trees",
                        "description": "Increased winds may have caused tree falls",
                        "affected_areas": ["forested areas", "trails"],
                        "severity": "high"
                    })
                
            # Check for temperature changes (snow melt or freezing)
            if (old_weather.get("temperature", 0) < 0 and
                current_weather.get("temperature", 0) > 5):
                terrain_changes.append({
                    "type": "snow_melt",
                    "description": "Rising temperatures are causing snow and ice melt",
                    "affected_areas": ["slopes", "water crossings"],
                    "severity": "medium" 
                })
                
            elif (old_weather.get("temperature", 0) > 0 and
                  current_weather.get("temperature", 0) < 0):
                terrain_changes.append({
                    "type": "freezing_conditions",
                    "description": "Dropping temperatures are causing icy conditions",
                    "affected_areas": ["paths", "slopes", "water crossings"],
                    "severity": "high"
                })
                
        return {
            "location": location,
            "last_analysis": last_timestamp,
            "current_time": self._get_timestamp(),
            "detected_changes": terrain_changes,
            "requires_reanalysis": len(terrain_changes) > 0,
            "current_weather": current_weather
        }
    
    def evaluate_crossing_difficulty(self, location, obstacle_type):
        """Evaluate specific crossing difficulty considering terrain and weather"""
        if location not in self.current_analysis:
            self.analyze_terrain(location)
        
        if location not in self.obstacle_database:
            self.identify_obstacles(location)
            
        matching_obstacles = [o for o in self.obstacle_database[location] 
                            if o["type"] == obstacle_type]
        
        weather = self.weather_agent.get_current_conditions(location)
        
        if not matching_obstacles:
            return {
                "location": location,
                "obstacle_type": obstacle_type,
                "current_weather": weather,
                "error": f"No matching obstacles found", 
                "recommendation": "Run identify_obstacles to update obstacle database or try a different obstacle type"
            }
        
        base_difficulties = {
            "steep_slope": 3,
            "water_crossing": 4,
            "dense_vegetation": 2,
            "flash_flood": 5,
            "sandy_terrain": 2,
            "boggy_ground": 3,
            "low_visibility_area": 3,
            "wind_hazard": 2
        }
        
        results = []
        for obstacle in matching_obstacles:
            base_score = base_difficulties.get(obstacle_type, 3)
            weather_modifiers = 0
            
            if obstacle_type == "water_crossing":
                if weather.get("precipitation", 0) > 20:
                    weather_modifiers += 2  # Heavy rain makes crossings harder
                if weather.get("temperature", 20) < 5:
                    weather_modifiers += 1  # Cold temperatures make water crossings more dangerous
                    
            elif obstacle_type == "steep_slope":
                if weather.get("precipitation", 0) > 10:
                    weather_modifiers += 2  # Rain makes slopes slippery
                if weather.get("wind_speed", 0) > 30:
                    weather_modifiers += 1  # Wind makes balance harder
                    
            elif obstacle_type == "dense_vegetation":
                if weather.get("wind_speed", 0) > 20:
                    weather_modifiers += 1  # Wind causes branches to sway
                    
            if weather.get("visibility", 10) < 5:
                weather_modifiers += 1  # Low visibility always adds difficulty
                
            final_score = base_score + weather_modifiers
            difficulty_rating = self._score_to_difficulty(final_score)
            
            results.append({
                "obstacle_id": self.obstacle_database[location].index(obstacle),
                "coordinates": obstacle["coordinates"],
                "base_difficulty": base_score,
                "weather_modifier": weather_modifiers,
                "final_difficulty": final_score,
                "difficulty_rating": difficulty_rating,
                "crossing_recommendation": self._get_crossing_recommendation(
                    obstacle_type, 
                    difficulty_rating
                ),
                "estimated_crossing_time": self._estimate_crossing_time(
                    obstacle_type,
                    difficulty_rating,
                    obstacle
                )
            })
            
        return {
            "location": location,
            "obstacle_type": obstacle_type,
            "current_weather": weather,
            "evaluation_timestamp": self._get_timestamp(),
            "evaluations": results
        }
    
    def _score_to_difficulty(self, score):
        """Convert numeric difficulty score to rating"""
        if score <= 2:
            return "easy"
        elif score <= 4:
            return "moderate"
        elif score <= 6:
            return "difficult"
        else:
            return "extreme"
    
    def _get_crossing_recommendation(self, obstacle_type, difficulty):
        """Get recommendations for crossing a specific obstacle type"""
        recommendations = {
            "water_crossing": {
                "easy": "Safe to cross at marked points",
                "moderate": "Use walking stick for stability; consider water shoes",
                "difficult": "Use rope assist system; avoid crossing if alone",
                "extreme": "Do not attempt crossing; find alternate route"
            },
            "steep_slope": {
                "easy": "Use proper footwear with good traction",
                "moderate": "Use hiking poles; take breaks on ascent",
                "difficult": "Use climbing equipment; set safety lines",  
                "extreme": "Technical climbing skills required; consider alternate route"
            },
            "dense_vegetation": {
                "easy": "Follow established trails",
                "moderate": "Use protective clothing; bring machete for clearing",
                "difficult": "Seek animal trails; progress will be slow",
                "extreme": "Consider aerial extraction if available"
            },
            "flash_flood": {
                "easy": "Cross at shallow points; monitor upstream",
                "moderate": "Delay crossing if water rising; use walking stick",
                "difficult": "Find alternate route or wait for water to recede",
                "extreme": "Do not attempt crossing; seek higher ground"
            },
            "boggy_ground": {
                "easy": "Stay on marked trails",
                "moderate": "Test ground firmness before steps; use hiking poles",
                "difficult": "Use snowshoe-like platforms to distribute weight",
                "extreme": "Avoid area completely; significant risk of sinking"
            }
        }
        
        return recommendations.get(obstacle_type, {}).get(
            difficulty,
            f"Exercise caution appropriate to {difficulty} rating"
        )
    
    def _estimate_crossing_time(self, obstacle_type, difficulty, obstacle_details):
        """Estimate time to cross obstacle based on type and difficulty"""
        base_times = {
            "water_crossing": 5,
            "steep_slope": 15,
            "dense_vegetation": 10,
            "sandy_terrain": 7,
            "boggy_ground": 12,
            "flash_flood": 20,
            "low_visibility_area": 8,
            "wind_hazard": 5
        }
        
        multipliers = {
            "easy": 0.7,
            "moderate": 1.0,
            "difficult": 1.5,
            "extreme": 2.5
        }
        
        base_time = base_times.get(obstacle_type, 10)
        multiplier = multipliers.get(difficulty, 1.0)
        
        if obstacle_details.get("details"):
            details = obstacle_details["details"]
            
            if obstacle_type == "water_crossing" and "width_meters" in details:
                # Wider crossings take longer
                base_time = details["width_meters"] * 0.5  # 0.5 minutes per meter
                
            elif obstacle_type == "steep_slope" and "length_meters" in details:
                # Longer slopes take longer
                base_time = details["length_meters"] * 0.1  # 0.1 minutes per meter
                
            elif obstacle_type == "dense_vegetation" and "area_sq_meters" in details:
                # Larger areas take longer to traverse
                # Assuming roughly square shaped area, get average dimension
                avg_dimension = (details["area_sq_meters"] ** 0.5)
                base_time = avg_dimension * 0.2  # 0.2 minutes per meter
        
        return round(base_time * multiplier, 1)
    
    def _analyze_terrain_weather_interactions(self, terrain_analysis, weather_data):
        """Analyze how weather affects terrain conditions"""
        interactions = []
        
        if weather_data.get("precipitation", 0) > 10:
            if "mountain" in terrain_analysis["terrain_types"]:
                interactions.append({
                    "type": "increased_landslide_risk",
                    "description": "Rain increases the risk of landslides on steep slopes",
                    "severity": "high" if weather_data.get("precipitation", 0) > 30 else "medium"
                })
                
            if "river" in terrain_analysis["terrain_types"]:
                interactions.append({
                    "type": "rising_water_levels",
                    "description": "Rain may cause water levels to rise",
                    "severity": "high" if weather_data.get("precipitation", 0) > 40 else "medium"
                })
                
            if terrain_analysis.get("soil_type") == "clay":
                interactions.append({
                    "type": "slippery_ground",
                    "description": "Rain on clay soil creates slippery conditions",
                    "severity": "medium"
                })
                
        if weather_data.get("wind_speed", 0) > 30:
            if "forest" in terrain_analysis["terrain_types"]:
                interactions.append({
                    "type": "falling_branches",
                    "description": "High winds may cause branches or trees to fall",
                    "severity": "high"
                })
                
            if terrain_analysis.get("elevation", {}).get("max", 0) > 1000:
                interactions.append({
                    "type": "dangerous_ridgelines",
                    "description": "High winds on exposed ridgelines create hazardous conditions",
                    "severity": "high"
                })
                
        if weather_data.get("temperature", 20) < 0:
            if "river" in terrain_analysis["terrain_types"]:
                interactions.append({
                    "type": "ice_formation",
                    "description": "Freezing temperatures create ice on water crossings",
                    "severity": "medium"
                })
                
            interactions.append({
                "type": "slippery_surfaces",
                "description": "Freezing temperatures create icy surfaces",
                "severity": "high" if terrain_analysis.get("slope", 0) > 20 else "medium"
            })
            
        elif weather_data.get("temperature", 20) > 35:
            if "desert" in terrain_analysis["terrain_types"]:
                interactions.append({
                    "type": "extreme_heat_danger",
                    "description": "High temperatures increase risk of heat-related illness",
                    "severity": "extreme"
                })
                
        if weather_data.get("visibility", 10) < 5:
            interactions.append({
                "type": "reduced_visibility",
                "description": "Poor visibility increases risk of navigation errors",
                "severity": "high" if terrain_analysis.get("slope", 0) > 30 else "medium"
            })
            
        return interactions
    
    def _generate_geojson(self, location, analysis, obstacles, include_weather=True):
        """Generate GeoJSON representation of terrain and obstacles with optional weather overlay"""
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        
        center = self._parse_location_to_coordinates(location)
        geojson["features"].append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [center[0] - 0.05, center[1] - 0.05],
                    [center[0] + 0.05, center[1] - 0.05],
                    [center[0] + 0.05, center[1] + 0.05],
                    [center[0] - 0.05, center[1] + 0.05],
                    [center[0] - 0.05, center[1] - 0.05]
                ]]
            },
            "properties": {
                "name": f"Terrain area: {location}",
                "terrain_types": analysis["terrain_types"],
                "elevation_range": [analysis["elevation"]["min"], analysis["elevation"]["max"]],
                "vegetation_density": analysis["vegetation_density"],
                "soil_type": analysis.get("soil_type", "unknown")
            }
        })
        
        for idx, obstacle in enumerate(obstacles):
            properties = {
                "name": f"Obstacle {idx+1}",
                "type": obstacle["type"],
                "severity": obstacle["severity"]
            }
            
            if "details" in obstacle:
                for key, value in obstacle["details"].items():
                    properties[key] = value
                    
            geojson["features"].append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": obstacle["coordinates"]
                },
                "properties": properties
            })
        
        if include_weather and "weather_conditions" in analysis:
            weather = analysis["weather_conditions"]
            
            geojson["features"].append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": center
                },
                "properties": {
                    "name": "Weather Conditions",
                    "temperature": weather.get("temperature"),
                    "wind_speed": weather.get("wind_speed"),
                    "precipitation": weather.get("precipitation"),
                    "visibility": weather.get("visibility"),
                    "feature_type": "weather_marker"
                }
            })
            
            if "terrain_weather_interactions" in analysis:
                for idx, interaction in enumerate(analysis["terrain_weather_interactions"]):
                    # slight offset so points don't stack
                    offset_coords = [
                        center[0] + random.uniform(-0.02, 0.02),
                        center[1] + random.uniform(-0.02, 0.02)
                    ]
                    
                    geojson["features"].append({
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": offset_coords
                        },
                        "properties": {
                            "name": f"Weather Impact {idx+1}",
                            "type": interaction["type"],
                            "description": interaction["description"],
                            "severity": interaction["severity"],
                            "feature_type": "weather_impact"
                        }
                    })
        
        return geojson
    

    def _get_terrain_challenges(self, start, end):
        """Get terrain challenges between two points"""
        challenges = []
        
        all_obstacles = []
        if start in self.obstacle_database:
            all_obstacles.extend(self.obstacle_database[start])
        if end in self.obstacle_database:
            all_obstacles.extend(self.obstacle_database[end])
            
        if all_obstacles:
            num_challenges = min(len(all_obstacles), random.randint(1, 3))
            selected_obstacles = random.sample(all_obstacles, num_challenges)
            
            for obstacle in selected_obstacles:
                challenges.append({
                    "type": obstacle["type"],
                    "severity": obstacle["severity"],
                    "description": self._generate_challenge_description(obstacle["type"]),
                    "mitigation": self._generate_mitigation_strategy(obstacle["type"])
                })
        
        return challenges

    def _generate_challenge_description(self, obstacle_type):
        """Generate description for a terrain challenge"""
        descriptions = {
            "steep_slope": "Steep slope requiring technical climbing skills",
            "water_crossing": "Water crossing that may require equipment",
            "dense_vegetation": "Dense vegetation reducing visibility and speed",
            "sandy_terrain": "Soft sand terrain reducing mobility and increasing energy expenditure",
            "boggy_ground": "Boggy ground with risk of sinking or becoming stuck",
            "flash_flood": "Area at risk of flash flooding, potentially impassable",
            "low_visibility_area": "Area with reduced visibility due to environmental factors",
            "wind_hazard": "Area with high winds that may affect balance and equipment"
        }
        return descriptions.get(obstacle_type, "Challenging terrain feature")

    def _generate_mitigation_strategy(self, obstacle_type):
        """Generate mitigation strategy for a terrain challenge"""
        strategies = {
            "steep_slope": "Use climbing equipment and establish safety lines",
            "water_crossing": "Find narrowest point or use inflatable raft",
            "dense_vegetation": "Use machetes to clear path or find game trails",
            "sandy_terrain": "Use wide footwear or boards to distribute weight",
            "boggy_ground": "Probe ground before stepping, use walking sticks for stability",
            "flash_flood": "Monitor weather upstream and avoid known flood channels",
            "low_visibility_area": "Use GPS navigation and additional lighting",
            "wind_hazard": "Secure loose equipment and approach from sheltered direction"
        }
        return strategies.get(obstacle_type, "Proceed with caution")

    def _recommend_equipment(self, terrain_challenges):
        """Recommend equipment based on terrain challenges"""
        equipment = ["standard SAR kit", "communications equipment", "first aid supplies"]
        
        for challenge in terrain_challenges:
            if challenge["type"] == "steep_slope":
                equipment.extend(["climbing rope", "harnesses", "carabiners", "helmets"])
            elif challenge["type"] == "water_crossing":
                equipment.extend(["water-resistant boots", "trekking poles", "life vests"])
            elif challenge["type"] == "dense_vegetation":
                equipment.extend(["machetes", "heavy gloves", "protective clothing"])
            elif challenge["type"] == "sandy_terrain":
                equipment.extend(["gaiters", "wide-base footwear"])
            elif challenge["type"] == "boggy_ground":
                equipment.extend(["trekking poles", "mud boots", "extraction equipment"])
            elif challenge["type"] == "flash_flood":
                equipment.extend(["water-resistant gear", "emergency flotation devices"])
            elif challenge["type"] == "low_visibility_area":
                equipment.extend(["high-powered flashlights", "reflective markers"])
            elif challenge["type"] == "wind_hazard":
                equipment.extend(["wind-resistant clothing", "face protection"])
        
        unique_equipment = []
        for item in equipment:
            if item not in unique_equipment:
                unique_equipment.append(item)
        
        return unique_equipment

    def _generate_waypoints(self, start, end, num_waypoints):
        """Generate waypoints between start and end locations"""
        start_coords = self._parse_location_to_coordinates(start)
        end_coords = self._parse_location_to_coordinates(end)
        
        waypoints = []
        for i in range(1, num_waypoints + 1):
            # Linear interpolation with slight random variation
            ratio = i / (num_waypoints + 1)
            lon = start_coords[0] + (end_coords[0] - start_coords[0]) * ratio
            lat = start_coords[1] + (end_coords[1] - start_coords[1]) * ratio
            
            # Add some randomness to make path more realistic
            lon += random.uniform(-0.02, 0.02)
            lat += random.uniform(-0.02, 0.02)
            
            waypoints.append({
                "id": i,
                "coordinates": [round(lon, 6), round(lat, 6)],
                "estimated_time_from_previous": self._calculate_waypoint_time(i, waypoints, start_coords if i == 1 else None)
            })
        
        return waypoints

    def _calculate_waypoint_time(self, waypoint_id, waypoints, start_coords=None):
        """Calculate estimated time in minutes to reach this waypoint from the previous one"""
        if not waypoints or waypoint_id <= 0:
            return 15.0 
            
        if waypoint_id == 1 and start_coords:
            distance = self._calculate_distance_between_coordinates(
                start_coords, 
                waypoints[0]["coordinates"]
            )
        else:
            if waypoint_id == 1:
                return 15.0 
                
            if waypoint_id - 2 < 0 or waypoint_id - 1 >= len(waypoints):
                return 15.0  
                
            distance = self._calculate_distance_between_coordinates(
                waypoints[waypoint_id - 2]["coordinates"],
                waypoints[waypoint_id - 1]["coordinates"]
            )
        
        hours = distance / 3.0 # Assuming average speed of 3 km/h, idk if this is too much
        minutes = hours * 60
        
        return round(minutes, 1)

    def _calculate_distance_between_locations(self, location1, location2):
        """Calculate distance between two locations"""
        coords1 = self._parse_location_to_coordinates(location1)
        coords2 = self._parse_location_to_coordinates(location2)
        return self._calculate_distance_between_coordinates(coords1, coords2)

    def _calculate_distance_between_coordinates(self, coords1, coords2):
        """Calculate distance between coordinates using Haversine formula"""
        import math
        
        lat1 = math.radians(coords1[1])
        lon1 = math.radians(coords1[0])
        lat2 = math.radians(coords2[1])
        lon2 = math.radians(coords2[0])
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371 
        
        return c * r

    def _generate_random_coordinates(self, location):
        """Generate random coordinates near a location"""
        base_coords = self._parse_location_to_coordinates(location)
        lon = base_coords[0] + random.uniform(-0.05, 0.05)
        lat = base_coords[1] + random.uniform(-0.05, 0.05)
        return [round(lon, 6), round(lat, 6)]

    def _parse_location_to_coordinates(self, location):
        """Parse location string to coordinates"""
        # Random values, use geocoding in real system
        location_hash = hash(location) % 1000
        base_lat = 35.0 + (location_hash % 10)
        base_lon = -120.0 + (location_hash // 10)
        
        return [round(base_lon, 6), round(base_lat, 6)]

    def _get_timestamp(self):
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().isoformat()

    def update_status(self, status):
        """Update agent's mission status"""
        self.mission_status = status
        return {"status": "updated", "new_status": status}

    def get_status(self):
        """Return current status"""
        return self.mission_status