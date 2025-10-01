import time
import board
import displayio
import terminalio
import adafruit_display_text.label
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix
import adafruit_requests as requests
import json
from adafruit_bitmap_font import bitmap_font

# Initialize network and display
matrix = Matrix()
display = matrix.display
network = Network(status_neopixel=board.NEOPIXEL, debug=False)

# Create display group
group = displayio.Group()

# Try to use a smaller font, fallback to terminalio
try:
    small_font = bitmap_font.load_font("/fonts/helvR08.bdf")
except:
    small_font = terminalio.FONT

# Line 1: Operator (Green) - Y=6
text1 = adafruit_display_text.label.Label(
    small_font,
    text="",
    color=0x00FF00
)
text1.x = 1
text1.y = 6
group.append(text1)

# Line 2: Aircraft Description (Yellow) - Y=6+8+3=17 (8px font height + 3px gap)
text2 = adafruit_display_text.label.Label(
    small_font,
    text="",
    color=0xFFFF00
)
text2.x = 1
text2.y = 17
group.append(text2)

# Line 3: Route (Blue) - Y=17+8+3=28 (8px font height + 3px gap)
text3 = adafruit_display_text.label.Label(
    small_font,
    text="",
    color=0x0000FF
)
text3.x = 1
text3.y = 28
group.append(text3)



display.root_group = group

# Boot animation - aircraft bitmap moving across screen
def boot_animation():
    # Create 12x12 bitmap for plane (like flightportal repo)
    plane_bmp = displayio.Bitmap(12, 12, 2)
    plane_palette = displayio.Palette(2)
    plane_palette[1] = 0x00FF00  # Green aircraft
    plane_palette[0] = 0x000000  # Black background

    # Exact aircraft bitmap from smartbutnot/flightportal repo
    plane_bmp[6,0] = plane_bmp[6,1] = plane_bmp[5,1] = plane_bmp[4,2] = plane_bmp[5,2] = plane_bmp[6,2] = 1
    plane_bmp[9,3] = plane_bmp[5,3] = plane_bmp[4,3] = plane_bmp[3,3] = 1
    plane_bmp[1,4] = plane_bmp[2,4] = plane_bmp[3,4] = plane_bmp[4,4] = plane_bmp[5,4] = plane_bmp[6,4] = plane_bmp[7,4] = plane_bmp[8,4] = plane_bmp[9,4] = 1
    plane_bmp[1,5] = plane_bmp[2,5] = plane_bmp[3,5] = plane_bmp[4,5] = plane_bmp[5,5] = plane_bmp[6,5] = plane_bmp[7,5] = plane_bmp[8,5] = plane_bmp[9,5] = 1
    plane_bmp[9,6] = plane_bmp[5,6] = plane_bmp[4,6] = plane_bmp[3,6] = 1
    plane_bmp[6,9] = plane_bmp[6,8] = plane_bmp[5,8] = plane_bmp[4,7] = plane_bmp[5,7] = plane_bmp[6,7] = 1

    # Create display objects for plane
    plane_tg = displayio.TileGrid(plane_bmp, pixel_shader=plane_palette)
    plane_group = displayio.Group(x=display.width + 12, y=10)
    plane_group.append(plane_tg)

    # Show plane animation
    display.root_group = plane_group

    # Move aircraft across screen (right to left like flightportal)
    for x in range(display.width + 12, -12, -1):
        plane_group.x = x
        time.sleep(0.04)  # Same speed as flightportal

    # Restore original display group
    display.root_group = group

print("Connecting to WiFi and fetching flight data...")
boot_animation()

last_flight_check = None
current_aircraft_index = 0
aircraft_data = []
current_aircraft = None
last_aircraft_switch = 0
AIRCRAFT_DISPLAY_TIME = 10
scroll_offset = 0
last_scroll_update = 0
SCROLL_SPEED = 0.5

def get_route_destination(route_str):
    if route_str and "-" in route_str:
        parts = route_str.split("-")
        return parts[-1] if len(parts) > 1 else "N/A"
    return "N/A"

def format_operator(aircraft):
    operator = aircraft.get("ownOp", "")

    if operator:
        return operator
    else:
        callsign = aircraft.get("callsign", aircraft.get("flight", ""))
        return callsign if callsign else "UNKNOWN"

def scroll_text_if_long(text, max_chars=8):
    global scroll_offset, last_scroll_update

    if len(text) <= max_chars:
        return text

    # Update scroll position
    current_time = time.monotonic()
    if current_time - last_scroll_update > SCROLL_SPEED:
        scroll_offset += 1
        last_scroll_update = current_time

        # Reset scroll when we reach the end
        if scroll_offset > len(text) - max_chars:
            scroll_offset = 0

    # Return scrolled substring
    return text[scroll_offset:scroll_offset + max_chars]

while True:
    current_monotonic = time.monotonic()

    # Fetch flight data every 50 seconds (5 aircraft * 10 seconds each)
    if last_flight_check is None or current_monotonic > last_flight_check + 50:
        try:
            print("Fetching flight data...")
            response = network.fetch("http://192.168.1.71/api/flight_data/sign.php")

            if response is None:
                print("Network fetch returned None - retrying in 10 seconds")
                text1.text = "CONNECTING"
                text2.text = "RETRY..."
                text3.text = ""
                last_flight_check = current_monotonic - 40  # Retry in 10 seconds instead of 50
                continue

            print("Response received, parsing JSON...")

            # Check if response has json method before calling it
            if not hasattr(response, 'json'):
                print("Response object has no json method")
                text1.text = "BAD RESPONSE"
                text2.text = "RETRY..."
                text3.text = ""
                last_flight_check = current_monotonic - 40
                continue

            flight_json = response.json()

            if flight_json is None:
                print("JSON parsing returned None")
                text1.text = "JSON ERROR"
                text2.text = ""
                text3.text = ""
                last_flight_check = current_monotonic - 40  # Retry in 10 seconds
                continue

            if "aircraft" not in flight_json:
                print("No aircraft key in JSON")
                text1.text = "NO DATA"
                text2.text = ""
                text3.text = ""
                last_flight_check = current_monotonic - 40  # Retry in 10 seconds
                continue

            all_aircraft = flight_json["aircraft"]

            # Take only first 5 aircraft to save memory
            aircraft_data = all_aircraft[:5]

            if aircraft_data:
                print(f"Found {len(aircraft_data)} aircraft (showing first 5)")

                # Show aircraft animation when we first get data
                if current_aircraft is None:  # First time getting data
                    boot_animation()

                current_aircraft_index = 0
                last_flight_check = current_monotonic
                last_aircraft_switch = 0  # Reset aircraft switching cycle
            else:
                print("Aircraft list is empty")
                text1.text = "NO AIRCRAFT"
                text2.text = ""
                text3.text = ""
                last_flight_check = current_monotonic - 40  # Retry in 10 seconds

        except Exception as e:
            print("Exception fetching flight data:", e)
            text1.text = "NETWORK"
            text2.text = "ERROR"
            text3.text = "RETRY..."
            last_flight_check = current_monotonic - 40  # Retry in 10 seconds instead of 50


    # Switch aircraft every 10 seconds
    if aircraft_data and (last_aircraft_switch == 0 or current_monotonic > last_aircraft_switch + AIRCRAFT_DISPLAY_TIME):
        current_aircraft = aircraft_data[current_aircraft_index]
        last_aircraft_switch = current_monotonic
        scroll_offset = 0  # Reset scroll for new aircraft

        # Console output matching screen display
        operator = format_operator(current_aircraft)
        desc = current_aircraft.get("desc", "UNKNOWN TYPE")
        route = current_aircraft.get("route")
        flight = current_aircraft.get("flight", "")

        # Combine callsign and route for line 3
        if route is not None and route != "":
            # Both callsign and route available
            combined_route = f"{flight} {route}"
        elif flight:
            # Only callsign available
            combined_route = flight
        else:
            # Nothing available
            combined_route = "LOCAL"

        route = combined_route

        print(f"--- Aircraft {current_aircraft_index + 1}/{len(aircraft_data)} ---")
        print(f"Operator: {operator}")
        print(f"Aircraft: {desc}")
        print(f"Flight:   {route}")
        print()

        # Move to next aircraft
        current_aircraft_index = (current_aircraft_index + 1) % len(aircraft_data)

    # Display current aircraft data with scrolling
    if current_aircraft:
        operator = format_operator(current_aircraft)
        desc = current_aircraft.get("desc", "UNKNOWN TYPE")
        route = current_aircraft.get("route")

        # If no route (null in JSON becomes None), use flight callsign
        if route is None or route == "":
            flight = current_aircraft.get("flight", "")
            if flight:
                route = flight
            else:
                route = "LOCAL"


        # Update display - scroll aircraft description and route if long
        text1.text = operator[:12] if len(operator) <= 12 else operator[:12]
        text2.text = scroll_text_if_long(desc, 12)  # Aircraft type scrolls
        text3.text = scroll_text_if_long(route, 12)  # Route + callsign scrolls

    time.sleep(0.1)