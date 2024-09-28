CRIME_WEIGHT = 0.9
ROAD_WEIGHT = 0.6
LIGHT_WEIGHT = 0.6

def calculate_weightings(crimes: list[int], roads: list[int], lights: int) -> int:
    return CRIME_WEIGHT * sum(crimes) + ROAD_WEIGHT * sum([(100 - r) for r in roads]) + LIGHT_WEIGHT * lights
