from flask import Flask, render_template, request, jsonify
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import folium
from logger_config import get_logger

app = Flask(__name__)
logger = get_logger(__name__)

# Sensor configuration
class SensorManager:
    def __init__(self):
        self.sensors = [
            {"id": "D1", "coords": (28.6139, 77.2090)},
            {"id": "D2", "coords": (28.7041, 77.1025)},
            {"id": "D3", "coords": (28.5355, 77.3910)},
            {"id": "D4", "coords": (28.4089, 77.3178)},
            {"id": "D5", "coords": (28.4595, 77.0266)},
        ]
        logger.info("SensorManager initialized with sensor data")

    def convert_to_xy(self):
        """Convert latitude/longitude to Cartesian coordinates."""
        logger.info("Converting sensor coordinates to XY format.")
        try:
            R = 6371000  # Earth's radius in meters
            lat0, lon0 = self.sensors[0]["coords"]
            xy_positions = []
            for sensor in self.sensors:
                lat, lon = sensor["coords"]
                x = R * np.radians(lon - lon0) * np.cos(np.radians(lat0))
                y = R * np.radians(lat - lat0)
                xy_positions.append((x, y))
            logger.debug(f"Converted XY positions: {xy_positions}")
            return xy_positions
        except Exception as e:
            logger.error(f"Error converting coordinates: {e}", exc_info=True)
            raise


# Crack location calculator
class CrackLocator:
    def __init__(self, sensor_positions, vibration_speed, time_differences):
        self.sensor_positions = sensor_positions
        self.vibration_speed = vibration_speed
        self.time_differences = time_differences
        logger.info("CrackLocator initialized.")
        
    def calculate_location(self):
        """Use TDoA and optimization to calculate the crack location."""
        logger.info("Starting crack location calculation.")
        try:
            def objective_function(crack_position):
                total_error = 0
                for i, (x, y) in enumerate(self.sensor_positions):
                    estimated_distance = np.sqrt((crack_position[0] - x) ** 2 + (crack_position[1] - y) ** 2)
                    actual_distance = self.vibration_speed * self.time_differences[i]
                    total_error += (estimated_distance - actual_distance) ** 2
                return total_error

            initial_guess = [0, 0]  # Start with the origin
            result = minimize(objective_function, initial_guess, method="L-BFGS-B")
            logger.debug(f"Optimization result: {result}")
            return result.x
        except Exception as e:
            logger.error(f"Error during crack location calculation: {e}", exc_info=True)
            raise

# Visualization class
class Visualization:
    @staticmethod
    def plot_graph(sensor_positions, crack_position):
        """Plot the sensor and crack positions."""
        logger.info("Generating crack location graph.")
        try:
            x_sensors, y_sensors = zip(*sensor_positions)
            fig, ax = plt.subplots()
            ax.scatter(x_sensors, y_sensors, label="Sensors", color="blue")
            ax.scatter(crack_position[0], crack_position[1], label="Crack", color="red")
            ax.legend()
            ax.set_title("Crack Location")
            ax.set_xlabel("X (meters)")
            ax.set_ylabel("Y (meters)")
            ax.grid()

            # Save plot to a string
            buffer = BytesIO()
            plt.savefig(buffer, format="png")
            buffer.seek(0)
            plot_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
            buffer.close()
            logger.info("Graph generated successfully.")
            return plot_data
        except Exception as e:
            logger.error(f"Error generating graph: {e}", exc_info=True)
            raise

    @staticmethod
    def create_map(crack_coords):
        """Create a folium map showing the crack location."""
        logger.info("Creating map for crack location.")
        try:
            crack_map = folium.Map(location=crack_coords, zoom_start=12)
            folium.Marker(crack_coords, popup="Crack Location", icon=folium.Icon(color="red")).add_to(crack_map)
            logger.info("Map generated successfully.")
            return crack_map._repr_html_()
        except Exception as e:
            logger.error(f"Error creating map: {e}", exc_info=True)
            raise
@app.route("/", methods=["GET", "POST"])
def index():
    logger.info("Processing request on '/' route.")
    sensor_manager = SensorManager()
    sensor_positions = sensor_manager.convert_to_xy()

    # Initialize variables to hold results
    crack_coords = None
    plot_data = None
    map_data = None
    error = None

    if request.method == "POST":
        try:
            # Get user input only from the form
            vibration_speed = request.form.get("vibration_speed")
            time_differences = [
                request.form.get(f"time_{sensor['id']}") for sensor in sensor_manager.sensors
            ]

            # Check if the required data is provided
            if vibration_speed and all(time_differences):
                vibration_speed = float(vibration_speed)
                time_differences = [float(t) for t in time_differences]
                logger.debug(f"Received vibration speed: {vibration_speed}")
                logger.debug(f"Received time differences: {time_differences}")

                # Normalize time differences relative to the first sensor
                time_differences = [t - time_differences[0] for t in time_differences]
                logger.debug(f"Normalized time differences: {time_differences}")

                # Calculate crack location
                locator = CrackLocator(sensor_positions, vibration_speed, time_differences)
                crack_xy = locator.calculate_location()
                logger.info(f"Calculated crack XY location: {crack_xy}")

                # Convert XY to lat/lon
                R = 6371000  # Earth's radius in meters
                lat0, lon0 = sensor_manager.sensors[0]["coords"]
                lat = lat0 + np.degrees(crack_xy[1] / R)
                lon = lon0 + np.degrees(crack_xy[0] / (R * np.cos(np.radians(lat0))))
                crack_coords = (lat, lon)
                logger.info(f"Crack location in lat/lon: {crack_coords}")

                # Generate visualizations
                plot_data = Visualization.plot_graph(sensor_positions, crack_xy)
                map_data = Visualization.create_map(crack_coords)
            else:
                error = "Please provide both vibration speed and time differences for calculation."
                logger.warning(f"Missing input: Vibration speed or time differences not provided.")

        except Exception as e:
            error = "Invalid input. Please check your values and try again."
            logger.error(f"Error processing POST request: {e}", exc_info=True)

    # Render the template with data
    return render_template(
        "index.html",
        crack_coords=crack_coords,
        plot_data=plot_data,
        map_data=map_data,
        sensors=sensor_manager.sensors,
        error=error,
    )

if __name__ == "__main__":
    logger.info("Starting Flask application.")
    app.run(debug=True)