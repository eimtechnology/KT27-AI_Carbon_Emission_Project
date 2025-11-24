# 🌍 Food Carbon Emission Detection System

<div align="center">

**An intelligent system that combines computer vision, AI, and hardware sensors to calculate the carbon footprint of food items in real-time.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux-lightgrey.svg)]()

</div>

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Hardware Setup](#-hardware-setup)
- [Usage](#-usage)
- [File Structure](#-file-structure)
- [Carbon Emission Database](#-carbon-emission-database)
- [Troubleshooting](#-troubleshooting)
- [Security](#-security)
- [Contributing](#-contributing)

---

## 🌟 Project Overview

This project is a complete **Food Carbon Emission Detection System** that combines:

- **🤖 AI-Powered Food Recognition** - Uses Google Gemini Vision API to identify food items
- **⚖️ Real-Time Weight Measurement** - Hardware scale with HX711 load cell sensor
- **🌱 Carbon Footprint Calculation** - Comprehensive database with emission factors from FAO, IPCC, and EPA
- **📺 Dual Display** - Results shown on both PC GUI and hardware display screen

### System Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   PC Application│◄───────►│ Raspberry Pi Pico│
│   (gui_main.py) │  Serial │  (Hardware Code) │
│                 │         │                  │
│  • Camera       │         │  • HX711 Sensor │
│  • AI Analysis  │         │  • ST7789 Display│
│  • Calculation  │         │  • Serial Comm  │
└─────────────────┘         └──────────────────┘
```

---

## ✨ Features

- 🎯 **Accurate Food Recognition** - Powered by Google Gemini Pro Vision API
- 📊 **Comprehensive Carbon Database** - 100+ food items with verified emission factors
- ⚖️ **Real-Time Weight Sensing** - Automatic weight detection and stability checking
- 📺 **Dual Display System** - Results on both PC screen and hardware display
- 🎨 **Modern GUI** - Intuitive interface with live camera feed
- 🔄 **Auto-Detection** - Automatic hardware port detection
- 📈 **Environmental Impact Analysis** - Shows equivalents (car km, tree absorption, etc.)
- 🌍 **Multi-Platform** - Works on Windows, Mac, and Linux

---

## 🔄 How It Works

1. **📷 Image Capture**: PC camera captures an image of the food item
2. **🤖 AI Recognition**: Image is sent to Google Gemini API for food identification
3. **⚖️ Weight Measurement**: Food is placed on hardware scale, weight data sent to PC
4. **🧮 Carbon Calculation**: System calculates: `Carbon Emission = Weight (kg) × Emission Factor`
5. **📊 Result Display**: Results shown on PC GUI and sent to hardware display screen

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))
- Raspberry Pi Pico (for hardware features)

### One-Click Launch

**Windows:**
```bash
# Just double-click run_app.bat
# Or run from command line:
run_app.bat
```

**Mac/Linux:**
```bash
# Make executable and run:
chmod +x run_app.sh
./run_app.sh
```

The script will automatically:
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Launch the application

---

## 📦 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/Carbon_Emission_Calculation.git
cd Carbon_Emission_Calculation
```

### Step 2: Set Up Python Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Configure API Key

⚠️ **IMPORTANT**: You must configure your Google Gemini API key before running.

**Option 1: Environment Variable (Recommended)**

Windows PowerShell:
```powershell
$env:GOOGLE_API_KEY="your-api-key-here"
python gui_main.py
```

Windows CMD:
```cmd
set GOOGLE_API_KEY=your-api-key-here
python gui_main.py
```

Mac/Linux:
```bash
export GOOGLE_API_KEY="your-api-key-here"
python3 gui_main.py
```

**Option 2: Edit Config File**

1. Open `config/system_config.py`
2. Find: `GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")`
3. Replace with: `GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "your-api-key-here")`
4. ⚠️ **Never commit this file with your API key!**

### Step 4: Run Application

```bash
python gui_main.py
```

---

## 🔧 Hardware Setup

### Required Components

- **Raspberry Pi Pico** (or Pico W)
- **HX711 Load Cell Amplifier** + Strain Gauge
- **ST7789 Display** (240x240 pixels)
- **USB Cable** for Pico connection
- **Breadboard & Jumper Wires** for connections

### Wiring Diagram

```
HX711 Weight Sensor:
├── DOUT → GPIO 8 (Pico)
├── SCK  → GPIO 9 (Pico)
├── VCC  → 5V
└── GND  → GND

ST7789 Display:
├── SCL  → GPIO 18 (SPI Clock)
├── SDA  → GPIO 19 (SPI MOSI)
├── CS   → GPIO 1  (Chip Select)
├── DC   → GPIO 12 (Data/Command)
├── RST  → GPIO 13 (Reset)
├── BL   → GPIO 0  (Backlight)
├── VCC  → 3.3V
└── GND  → GND
```

### Upload Code to Pico

1. **Install Thonny IDE**: Download from [thonny.org](https://thonny.org/)

2. **Connect Pico**: Plug Pico into PC via USB

3. **Upload Libraries**:
   - Upload `hx711_gpio.py` to Pico
   - Upload `st7789.py` to Pico
   - Upload `vga1_16x32.py` to Pico

4. **Upload Main Code**:
   - Upload `carbon_emissions_HX711.py` to Pico
   - (Optional) Rename to `main.py` for auto-run on boot

5. **Run Code**: Click "Run" in Thonny or restart Pico

---

## 💻 Usage

### Basic Workflow

1. **Connect Hardware**
   - Plug Raspberry Pi Pico into PC via USB
   - Application will auto-detect the serial port

2. **Launch Application**
   - Windows: Double-click `run_app.bat`
   - Mac/Linux: Run `./run_app.sh`

3. **Analyze Food**
   - Place food under camera
   - Click **"🔍 ANALYZE FOOD"** button or press **Space**
   - Wait for AI recognition (2-5 seconds)

4. **Measure Weight**
   - Place food on hardware scale
   - System automatically detects stable weight
   - Carbon footprint is calculated instantly

5. **View Results**
   - Results displayed on PC screen
   - Results also sent to hardware display
   - View environmental impact and equivalents

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Space` | Analyze food |
| `F11` | Toggle fullscreen |
| `F5` | Center window |
| `Ctrl+R` | Reset system |
| `Ctrl+D` | Send results to hardware display |
| `Ctrl+T` | Send test data to display |

### GUI Features

- **📷 Live Camera Feed** - Real-time preview with target frame
- **📁 Upload Image** - Analyze from image file instead of camera
- **📊 Analysis Results** - Detailed carbon footprint breakdown
- **⚖️ Weight Display** - Real-time weight monitoring
- **🔗 Hardware Status** - Connection status and port information

---

## 📂 File Structure

```
Carbon_Emission_Calculation/
│
├── 📄 gui_main.py                 # Main PC application (GUI)
├── 📄 carbon_emissions_HX711.py   # Hardware code for Raspberry Pi Pico
├── 📄 requirements.txt            # Python dependencies
├── 📄 run_app.bat                 # Windows launcher script
├── 📄 run_app.sh                  # Mac/Linux launcher script
├── 📄 README.md                   # This file
│
├── 📁 modules/                    # Core application modules
│   ├── __init__.py
│   ├── vision_ai.py              # AI vision recognition (Google Gemini)
│   └── carbon_calculator.py      # Carbon emission calculation engine
│
├── 📁 config/                     # Configuration files
│   ├── __init__.py
│   └── system_config.py           # System configuration (API keys, settings)
│
└── 📁 Hardware Libraries/        # Required libraries for Pico
    ├── hx711_gpio.py             # HX711 weight sensor driver
    ├── st7789.py                 # ST7789 display driver
    └── vga1_16x32.py             # Font file for display
```

---

## 🔬 Carbon Emission Database

### Data Sources

The system uses a comprehensive carbon emission factor database based on:

- **FAO** (Food and Agriculture Organization) - Global food production data
- **IPCC** (Intergovernmental Panel on Climate Change) - Climate change standards
- **EPA** (Environmental Protection Agency) - Environmental impact guidelines

### Sample Emission Factors

| Food Category | Example | Emission Factor (kg CO₂/kg) | Impact Level |
|--------------|---------|----------------------------|--------------|
| **Meat** | Beef | ~60.0 | 🔴 Very High |
| **Meat** | Chicken | ~6.9 | 🟡 Medium |
| **Seafood** | Salmon | ~11.9 | 🟠 High |
| **Dairy** | Cheese | ~21.2 | 🟠 High |
| **Vegetables** | Carrots | ~0.4 | 🟢 Low |
| **Fruits** | Apples | ~0.6 | 🟢 Low |
| **Grains** | Rice | ~4.0 | 🟡 Medium |

### Calculation Formula

```
Carbon Emission (kg CO₂) = Weight (kg) × Emission Factor (kg CO₂/kg)
```

### Environmental Equivalents

The system also calculates:
- **Car Driving Distance**: Equivalent km driven
- **Tree Absorption**: Months of CO₂ absorption by a tree
- **Phone Charges**: Equivalent number of phone charging cycles

---

## ⚠️ Troubleshooting

### Software Issues

#### Camera Not Working
- ✅ Check if another application is using the webcam
- ✅ Verify camera permissions in system settings
- ✅ Try restarting the application
- ✅ On Windows: Check Device Manager for camera issues
- ✅ Try different camera index in code (0 or 1)

#### Hardware Not Found
- ✅ Check USB cable connection
- ✅ Ensure Pico is not "busy" in Thonny (close Thonny)
- ✅ Try reconnecting the USB cable
- ✅ Check COM port:
  - Windows: Device Manager → Ports (COM & LPT)
  - Mac/Linux: `ls /dev/tty*` or `ls /dev/cu.*`
- ✅ Application auto-detects port, but you can manually specify in code

#### AI Recognition Error
- ✅ Check internet connection
- ✅ Verify API key is correctly set
- ✅ Check API quota/limits on [Google AI Studio](https://makersuite.google.com/app/apikey)
- ✅ Ensure API key has access to Gemini Pro Vision model
- ✅ Check console for detailed error messages

#### Import Errors
- ✅ Ensure virtual environment is activated
- ✅ Run `pip install -r requirements.txt` again
- ✅ Check Python version: `python --version` (requires 3.8+)
- ✅ Verify all files are in correct directories

### Hardware Issues

#### Weight Sensor Not Responding
- ✅ Check HX711 wiring (DOUT → GPIO 8, SCK → GPIO 9)
- ✅ Verify power supply to HX711 (5V)
- ✅ Calibrate sensor (code includes calibration routine)
- ✅ Check serial communication baud rate (115200)
- ✅ Ensure `hx711_gpio.py` is uploaded to Pico

#### Display Not Showing
- ✅ Check ST7789 wiring (see Hardware Wiring section)
- ✅ Verify display power (3.3V) and backlight
- ✅ Ensure `st7789.py` and `vga1_16x32.py` are uploaded to Pico
- ✅ Check display rotation settings in code
- ✅ Verify SPI pins are correct

#### Serial Communication Issues
- ✅ Ensure Pico code is running (check Thonny console)
- ✅ Verify baud rate matches (115200)
- ✅ Close other serial programs (Thonny, Arduino IDE, etc.)
- ✅ Try different USB port
- ✅ Check USB cable (data cable, not just charging cable)

---

## 🔒 Security

### API Key Security

⚠️ **CRITICAL**: Never commit API keys to version control!

**Best Practices:**
1. ✅ Use environment variables for API keys
2. ✅ Add `config/system_config.py` to `.gitignore` if it contains keys
3. ✅ Use `.env` files with `python-dotenv` for local development
4. ✅ Rotate API keys regularly
5. ✅ Set API key restrictions in Google Cloud Console

**Example `.gitignore`:**
```
# API Keys
config/system_config.py
.env
*.key
```

---

## 📝 Dependencies

### Python Packages

- `google-generativeai` - Google Gemini API client
- `opencv-python` - Computer vision and image processing
- `Pillow` - Image manipulation
- `numpy` - Numerical computing
- `pyserial` - Serial communication with hardware

See `requirements.txt` for complete list and versions.

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Code Style**: Follow PEP 8 Python style guide
2. **Language**: All code comments and documentation must be in English
3. **Testing**: Test on both Windows and Mac/Linux if possible
4. **Documentation**: Update README.md if adding new features
5. **Commits**: Write clear commit messages

### Contribution Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License & Credits

### Technologies Used

- **Google Gemini API** - Food recognition
- **OpenCV** - Image processing
- **PySerial** - Hardware communication
- **Tkinter** - GUI framework
- **MicroPython** - Pico firmware

### Data Sources

- **FAO** - Food and Agriculture Organization
- **IPCC** - Intergovernmental Panel on Climate Change
- **EPA** - Environmental Protection Agency

### Acknowledgments

- Carbon emission data sourced from verified scientific databases
- Hardware drivers based on open-source MicroPython libraries

---

## 📧 Support & Contact

### Getting Help

1. 📖 Check the [Troubleshooting](#-troubleshooting) section
2. 🔍 Review error messages in console output
3. 📋 Check GitHub Issues for similar problems
4. 💬 Open a new issue with detailed error information

### Reporting Issues

When reporting issues, please include:
- Operating System (Windows/Mac/Linux)
- Python version
- Error messages from console
- Steps to reproduce the issue
- Hardware setup (if applicable)

---

## 🎯 Future Enhancements

Potential features for future versions:

- [ ] Support for multiple food items in one image
- [ ] Meal-level carbon footprint calculation
- [ ] Historical data tracking and analytics
- [ ] Export results to CSV/PDF
- [ ] Mobile app companion
- [ ] Cloud database synchronization
- [ ] Multi-language support

---

<div align="center">

**Version**: 1.0.0  
**Last Updated**: 2024

Made with ❤️ for environmental awareness

</div>
