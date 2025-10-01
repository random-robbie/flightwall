# FlightWall

A CircuitPython-powered flight tracking display for Adafruit Matrix Portal M4 that shows overhead aircraft information on a 32x32 RGB LED matrix.

![FlightWall Demo](demo.gif)

## Features

- **Live Aircraft Tracking**: Displays real-time overhead aircraft information
- **Scrolling Text**: Aircraft descriptions scroll smoothly for full visibility
- **Boot Animation**: Aircraft bitmap flies across screen during startup
- **Auto-Refresh**: Cycles through 5 aircraft every 10 seconds, refreshes data every 50 seconds
- **WiFi Status**: Visual feedback for connection status and errors
- **Compact Display**: Optimized for 32x32 LED matrix with 3 lines of information:
  - Line 1: Airline/Operator (Green)
  - Line 2: Aircraft Type (Yellow, scrolls if long)
  - Line 3: Flight Callsign + Route (Blue, scrolls if long)

## Hardware Required

### Core Components
- [Adafruit Matrix Portal M4](https://thepihut.com/products/adafruit-matrix-portal-m4) - Main controller board
- [32x32 RGB LED Matrix Panel - 4mm Pitch](https://thepihut.com/products/32x32-rgb-led-matrix-panel-4mm-pitch) - Display panel
- [USB-C Cable](https://thepihut.com/products/usb-c-cable-usb-2-0-type-a-to-type-c-1-meter) - For programming and power

### Optional Accessories
- [Acrylic Diffusion Panel](https://thepihut.com/products/rgb-matrix-panel-diffusion-acrylic) - Softens LED appearance
- [Matrix Portal Case](https://thepihut.com/products/adafruit-matrix-portal-case) - Protective enclosure

## Flight Data Source

This project requires a local flight data API endpoint that provides aircraft information in JSON format. The display fetches data from:

```
http://YOUR_LOCAL_IP/api/flight_data/sign.php
```

Expected JSON structure:
```json
{
  "aircraft": [
    {
      "flight": "EZY65FJ",
      "desc": "AIRBUS A-319",
      "ownOp": "easyJet",
      "route": "LGW-EDI",
      "alt_baro": 22625
    }
  ]
}
```

i currently supply planefinder and use the client web ui to the flight data with a mixture of two other apis to get operator and destinations.

## Installation

### 1. Prepare Hardware
- Connect the LED matrix to Matrix Portal M4 following [Adafruit's guide](https://learn.adafruit.com/adafruit-matrixportal-m4)
- Connect USB-C cable to Matrix Portal M4

### 2. Install CircuitPython
1. Download [CircuitPython for Matrix Portal M4](https://circuitpython.org/board/matrixportal_m4/)
2. Flash CircuitPython to the board following [Adafruit's instructions](https://learn.adafruit.com/adafruit-matrixportal-m4/install-circuitpython)

### 3. Install FlightWall
1. Clone this repository:
   ```bash
   git clone https://github.com/random-robbie/flightwall.git
   ```

2. Copy files to your Matrix Portal M4 (appears as CIRCUITPY drive):
   ```bash
   cp flightwall/code.py /Volumes/CIRCUITPY/
   cp -r flightwall/lib/* /Volumes/CIRCUITPY/lib/
   ```

3. Configure WiFi settings:
   ```bash
   cp flightwall/settings.toml.example /Volumes/CIRCUITPY/settings.toml
   ```

   Edit `settings.toml` with your WiFi credentials:
   ```toml
   CIRCUITPY_WIFI_SSID = "your_network_name"
   CIRCUITPY_WIFI_PASSWORD = "your_network_password"
   timezone = "Europe/London"
   ```

### 4. Update Flight Data URL
Edit `code.py` line 146 to point to your flight data API:
```python
response = network.fetch("http://YOUR_LOCAL_IP/api/flight_data/sign.php")
```

## Usage

1. Power on the Matrix Portal M4
2. Watch the boot animation as it connects to WiFi
3. The display will show overhead aircraft information:
   - Each aircraft displays for 10 seconds
   - Cycles through up to 5 aircraft
   - Refreshes data every 50 seconds
   - Long text scrolls automatically

## Console Output

The device outputs detailed information to the serial console:
```
Connecting to WiFi and fetching flight data...
Found 5 aircraft (showing first 5)
--- Aircraft 1/5 ---
Operator: easyJet
Aircraft: AIRBUS A-319
Flight:   EZY65FJ LGW-EDI
```

## Troubleshooting

### Connection Issues
- **"CONNECTING RETRY..."**: Check WiFi credentials in `settings.toml`
- **"NETWORK ERROR"**: Verify flight data API is accessible
- **"NO AIRCRAFT"**: API returned empty aircraft list

### Display Issues
- **Blank screen**: Check power connections and CircuitPython installation
- **Garbled text**: Verify all required libraries are in `/lib` folder

### API Issues
- **"JSON ERROR"**: Check API response format matches expected structure
- **"BAD RESPONSE"**: API endpoint may be down or unreachable

## Configuration

### Display Timing
```python
AIRCRAFT_DISPLAY_TIME = 10  # Seconds each aircraft is shown
SCROLL_SPEED = 0.5         # Seconds between scroll updates
```

### Colors
```python
# Line colors (RGB hex)
text1.color = 0x00FF00  # Green (Operator)
text2.color = 0xFFFF00  # Yellow (Aircraft)
text3.color = 0x0000FF  # Blue (Flight/Route)
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by [smartbutnot/flightportal](https://github.com/smartbutnot/flightportal)
- Built with [Adafruit CircuitPython](https://circuitpython.org/)
- Hardware from [The Pi Hut](https://thepihut.com/)

## Support

For issues and questions:
- Open an [issue](https://github.com/random-robbie/flightwall/issues)
- Check [Adafruit's learning guides](https://learn.adafruit.com/adafruit-matrixportal-m4)
