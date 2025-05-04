import pygame
import os
import json
import math

class Globemap:
    def __init__(self):
        pygame.init()
        global center_x, center_y, width, height, geojson_data, radius, country_border_data
        width = 800
        height = 800
        self.screen = pygame.display.set_mode( (width, height), pygame.SCALED | pygame.FULLSCREEN |  pygame.HWSURFACE | pygame.DOUBLEBUF )

        # Globe settings
        radius = 400  # Radius of the globe
        center_x = width // 2
        center_y = height // 2
        print(os.path.join(os.path.dirname(__file__), "coastlines_geo.json"))

        # Load the JSON file using os.path.join directly
        with open(os.path.join(os.path.dirname(__file__), "coastlines_geo.json"), "r") as file:
            geojson_data = json.load(file)
        with open(os.path.join(os.path.dirname(__file__), "country_borders_geo.json"), "r") as file:
            country_border_data = json.load(file)


    # Orthographic projection: Converts lat/lon to screen x, y
    def lat_lon_to_xy(self, lat, lon, radius, center_x, center_y, lon_center, lat_center):
        lat_r = math.radians(lat)
        lon_r = math.radians(lon)
        lon_center_r = math.radians(lon_center)
        lat_center_r = math.radians(lat_center)

        # Check if the point is on the visible hemisphere (front side of the globe)
        cos_c = math.sin(lat_center_r) * math.sin(lat_r) + math.cos(lat_center_r) * math.cos(lat_r) * math.cos(lon_r - lon_center_r)
        if cos_c < 0:  # If cos_c < 0, the point is on the back of the globe
            return None

        # Orthographic projection formula
        x = radius * math.cos(lat_r) * math.sin(lon_r - lon_center_r)
        y = radius * (math.cos(lat_center_r) * math.sin(lat_r) -
                      math.sin(lat_center_r) * math.cos(lat_r) * math.cos(lon_r - lon_center_r))

        return int(center_x + x), int(center_y - y)

    # Check if a point is within the screen boundaries
    def is_point_on_screen(self, x, y, width, height):
        return 0 <= x < width and 0 <= y < height

    # Draw GeoJSON features (polygons, multi-polygons, lines)
    def draw_geojson_coastlines(self, lon_center, lat_center, color):
        self.color = color
        if not geojson_data:  # Handle empty or invalid GeoJSON
            return
        for feature in geojson_data["features"]:
            geometry = feature["geometry"]
            if geometry["type"] == "Polygon":
                for polygon in geometry["coordinates"]:
                    self.draw_polygon(polygon, radius, center_x, center_y, lon_center, lat_center)
            elif geometry["type"] == "MultiPolygon":
                for polygons in geometry["coordinates"]:
                    for polygon in polygons:
                        self.draw_polygon(polygon, radius, center_x, center_y, lon_center, lat_center)
            elif geometry["type"] == "LineString":
                self.draw_linestring(geometry["coordinates"], radius, center_x, center_y, lon_center, lat_center)

    # Draw GeoJSON features (polygons, multi-polygons, lines)
    def draw_geojson_country_borders(self, lon_center, lat_center, color):
        self.color = color
        if not country_border_data:  # Handle empty or invalid GeoJSON
            return

        for feature in country_border_data["features"]:
            geometry = feature["geometry"]
            if geometry["type"] == "Polygon":
                for polygon in geometry["coordinates"]:
                    self.draw_polygon(polygon, radius, center_x, center_y, lon_center, lat_center)
            elif geometry["type"] == "MultiPolygon":
                for polygons in geometry["coordinates"]:
                    for polygon in polygons:
                        self.draw_polygon(polygon, radius, center_x, center_y, lon_center, lat_center)
            elif geometry["type"] == "LineString":
                self.draw_linestring(geometry["coordinates"], radius, center_x, center_y, lon_center, lat_center)

    # Draw a polygon feature
    def draw_polygon(self, polygon, radius, center_x, center_y, lon_center, lat_center):
        projected_points = [
            self.lat_lon_to_xy(coord[1], coord[0], radius, center_x, center_y, lon_center, lat_center)
            for coord in polygon
        ]
        # Filter valid and on-screen points
        projected_points = [
            point for point in projected_points if point and self.is_point_on_screen(point[0], point[1], width, height)
        ]
        if len(projected_points) > 1:
            pygame.draw.polygon(self.screen, self.color, projected_points, 0)

    # Draw a line feature
    def draw_linestring(self, coordinates, radius, center_x, center_y, lon_center, lat_center):
        projected_points = [
            self.lat_lon_to_xy(coord[1], coord[0], radius, center_x, center_y, lon_center, lat_center)
            for coord in coordinates
        ]
        # Filter valid and on-screen points
        projected_points = [
            point for point in projected_points if point and self.is_point_on_screen(point[0], point[1], width, height)
        ]
        if len(projected_points) > 1:
            pygame.draw.lines(self.screen, self.color, False, projected_points, 1)
