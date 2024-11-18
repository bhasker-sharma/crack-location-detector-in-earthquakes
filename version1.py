import re
import numpy as np
from scipy.optimize import minimize


class CrackLocator:
    def __init__(self):
        # Predefined sensor positions in DMS (as strings)
        self.sensors = [
            {"id": "D1", "coords": "28°07′12″N 77°12′32″E"},  # Example: Delhi
            {"id": "D2", "coords": "30°42′30″N 78°06′09″E"},  # Example: North Delhi
            {"id": "D3", "coords": "35°32′08″N 80°23′28″E"},  # Example: Noida
            {"id": "D4", "coords": "44°24′32″N 90°19′04″E"},  # Example: Gurgaon
            {"id": "D5", "coords": "50°27′34″N 85°01′36″E"},  # Example: Faridabad
        ]

        # Convert DMS coordinates to decimal degrees
        self.sensor_positions = self._convert_to_xy()

    @staticmethod
    def dms_to_decimal(dms):
        """Convert DMS (Degrees, Minutes, Seconds) format to decimal degrees."""
        match = re.match(r"(\d+)°(\d+)′(\d+(\.\d+)?)″([NSEW])", dms)
        if not match:
            raise ValueError(f"Invalid DMS format for '{dms}'. Expected format like '28°07′12″N'.")
        degrees, minutes, seconds, _, direction = match.groups()
        decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
        if direction in "SW":  # South and West are negative
            decimal = -decimal
        return decimal

    def _convert_to_xy(self):
        """Convert sensor positions in DMS to XY positions (in meters)."""
        R = 6371000  # Earth's radius in meters
        ref_lat, ref_lon = map(self.dms_to_decimal, self.sensors[0]["coords"].split())
        
        xy_positions = []
        for sensor in self.sensors:
            lat, lon = map(self.dms_to_decimal, sensor["coords"].split())
            x = R * np.radians(lon - ref_lon) * np.cos(np.radians(ref_lat))
            y = R * np.radians(lat - ref_lat)
            xy_positions.append([x, y])

        return xy_positions

    def calculate_crack_location(self, time_differences, vibration_speed):
        """Find the crack location using TDoA and optimization."""
        def objective_function(guess):
            """Calculate the error based on predicted and observed time differences."""
            error = 0
            for i, pos_i in enumerate(self.sensor_positions):
                for j, pos_j in enumerate(self.sensor_positions[i + 1:], i + 1):
                    distance_i = np.linalg.norm(np.array(guess) - np.array(pos_i))
                    distance_j = np.linalg.norm(np.array(guess) - np.array(pos_j))
                    predicted_delta_t = (distance_j - distance_i) / vibration_speed
                    observed_delta_t = time_differences[j] - time_differences[i]
                    error += (predicted_delta_t - observed_delta_t) ** 2
            return error

        # Initial guess: Mean of sensor positions
        initial_guess = np.mean(self.sensor_positions, axis=0).tolist()

        # Dynamically compute bounds (add a buffer for uncertainty)
        x_coords, y_coords = zip(*self.sensor_positions)
        buffer = 1e4  # Buffer of 10 km
        bounds = [
            (min(x_coords) - buffer, max(x_coords) + buffer),
            (min(y_coords) - buffer, max(y_coords) + buffer),
        ]

        # Optimization using L-BFGS-B
        result = minimize(
            objective_function,
            initial_guess,
            bounds=bounds,
            method="L-BFGS-B",
            options={"disp": False, "ftol": 1e-9}
        )

        if not result.success:
            print(f"Optimization failed: {result.message}")
            return None

        crack_xy = result.x
        return self._convert_to_dms(self._convert_to_lat_lon(crack_xy))

    def _convert_to_lat_lon(self, xy):
        """Convert XY back to latitude and longitude."""
        R = 6371000  # Earth's radius in meters
        ref_lat, ref_lon = map(self.dms_to_decimal, self.sensors[0]["coords"].split())
        
        x, y = xy
        lat = ref_lat + np.degrees(y / R)
        lon = ref_lon + np.degrees(x / (R * np.cos(np.radians(ref_lat))))
        return lat, lon

    @staticmethod
    def decimal_to_dms(decimal, is_latitude):
        """Convert decimal degrees to DMS format."""
        degrees = int(decimal)
        minutes = int((abs(decimal) - abs(degrees)) * 60)
        seconds = (abs(decimal) - abs(degrees) - minutes / 60) * 3600
        direction = (
            "N" if is_latitude and decimal >= 0 else
            "S" if is_latitude else
            "E" if decimal >= 0 else "W"
        )
        return f"{abs(degrees)}°{minutes}′{seconds:.2f}″{direction}"

    @staticmethod
    def _convert_to_dms(decimal_coords):
        """Convert decimal coordinates (lat, lon) to DMS format."""
        lat, lon = decimal_coords
        return CrackLocator.decimal_to_dms(lat, True), CrackLocator.decimal_to_dms(lon, False)


def main():
    print("=== Crack Location Detection System ===")

    locator = CrackLocator()
    print("\nAvailable Sensors (ID and Coordinates in DMS):")
    for sensor in locator.sensors:
        print(f"{sensor['id']}: {sensor['coords']}")

    try:
        # Input for vibration speed
        while True:
            try:
                vibration_speed = float(input("\nEnter the vibration propagation speed (m/s): "))
                if vibration_speed <= 0:
                    raise ValueError("Speed must be positive.")
                break
            except ValueError as e:
                print(f"Invalid input: {e}. Please enter a valid speed.")

        # Input for time differences
        print("Enter the time differences for each sensor relative to D1 (in seconds):")
        time_differences = []
        for sensor in locator.sensors:
            while True:
                try:
                    t = float(input(f"  Time for {sensor['id']}: "))
                    time_differences.append(t)
                    break
                except ValueError:
                    print("Invalid input. Please enter a valid time.")

        # Calculate crack location
        crack_location = locator.calculate_crack_location(time_differences, vibration_speed)
        if crack_location:
            print("\n=== Results ===")
            print(f"Estimated Crack Location (DMS Format): {crack_location}")
        else:
            print("Could not determine crack location due to optimization failure.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
