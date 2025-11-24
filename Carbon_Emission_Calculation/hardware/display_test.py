"""
ST7789 Display Test Script - 诊断显示问题
测试显示屏是否正常工作
"""

from machine import Pin, SPI
import time
import st7789
import vga1_16x32 as font

# ST7789 Display Configuration
WIDTH, HEIGHT = 240, 240
SPI_NUM = 0
BACKLIGHT_PIN = 0
RST_PIN = 13
DC_PIN = 12
CS_PIN = 1
SCK_PIN = 18
MOSI_PIN = 19

def test_display():
    """测试ST7789显示屏基本功能"""
    print("=== ST7789 Display Test ===")
    
    try:
        # Initialize SPI
        print("1. Initializing SPI...")
        spi = SPI(SPI_NUM, baudrate=31250000, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))
        print("   SPI initialized successfully")
        
        # Initialize Display
        print("2. Initializing ST7789...")
        tft = st7789.ST7789(
            spi, WIDTH, HEIGHT,
            reset=Pin(RST_PIN, Pin.OUT),
            cs=Pin(CS_PIN, Pin.OUT),
            dc=Pin(DC_PIN, Pin.OUT),
            backlight=Pin(BACKLIGHT_PIN, Pin.OUT),
            rotation=0,
        )
        print("   ST7789 initialized successfully")
        
        # Test 1: Fill screen with colors
        print("3. Testing color fill...")
        colors = [st7789.RED, st7789.GREEN, st7789.BLUE, st7789.WHITE, st7789.BLACK]
        color_names = ["RED", "GREEN", "BLUE", "WHITE", "BLACK"]
        
        for i, (color, name) in enumerate(zip(colors, color_names)):
            print(f"   Filling with {name}...")
            tft.fill(color)
            time.sleep(1)
        
        # Test 2: Draw text
        print("4. Testing text display...")
        tft.fill(st7789.BLACK)
        
        # Test different positions and colors
        test_texts = [
            ("Display Test", 10, st7789.WHITE),
            ("Line 2", 50, st7789.RED),
            ("Line 3", 90, st7789.GREEN),
            ("Line 4", 130, st7789.BLUE),
            ("Line 5", 170, st7789.YELLOW),
        ]
        
        for text, y, color in test_texts:
            print(f"   Drawing: {text}")
            # Calculate center position
            text_width = len(text) * 16  # Approximate width
            x = max(0, (WIDTH - text_width) // 2)
            tft.text(font, text, x, y, color, st7789.BLACK)
            time.sleep(0.5)
        
        # Test 3: Draw rectangles
        print("5. Testing rectangle drawing...")
        time.sleep(2)
        tft.fill(st7789.BLACK)
        
        # Draw colored rectangles
        rectangles = [
            (10, 10, 50, 30, st7789.RED),
            (70, 10, 50, 30, st7789.GREEN),
            (130, 10, 50, 30, st7789.BLUE),
            (190, 10, 40, 30, st7789.YELLOW),
        ]
        
        for x, y, w, h, color in rectangles:
            print(f"   Drawing rectangle at ({x},{y})")
            tft.fill_rect(x, y, w, h, color)
            time.sleep(0.5)
        
        # Test 4: Final message
        print("6. Displaying final message...")
        time.sleep(2)
        tft.fill(st7789.BLACK)
        
        final_messages = [
            ("ST7789 Display", 60, st7789.WHITE),
            ("Test Complete", 100, st7789.GREEN),
            ("All Functions", 140, st7789.CYAN),
            ("Working OK!", 180, st7789.YELLOW),
        ]
        
        for text, y, color in final_messages:
            text_width = len(text) * 16
            x = max(0, (WIDTH - text_width) // 2)
            tft.text(font, text, x, y, color, st7789.BLACK)
            time.sleep(0.5)
        
        print("=== Display Test Completed Successfully! ===")
        return True
        
    except Exception as e:
        print(f"ERROR: Display test failed: {e}")
        print("Possible issues:")
        print("- Check wiring connections")
        print("- Verify power supply")
        print("- Check SPI pins configuration")
        print("- Ensure st7789 and font modules are installed")
        return False

def diagnose_display_issues():
    """诊断显示问题"""
    print("=== Display Issues Diagnosis ===")
    
    # Check 1: Pin configuration
    print("1. Checking pin configuration...")
    pin_config = {
        "BACKLIGHT": BACKLIGHT_PIN,
        "RESET": RST_PIN,
        "DC": DC_PIN,
        "CS": CS_PIN,
        "SCK": SCK_PIN,
        "MOSI": MOSI_PIN,
    }
    
    for name, pin_num in pin_config.items():
        try:
            pin = Pin(pin_num, Pin.OUT)
            print(f"   {name} (Pin {pin_num}): OK")
        except Exception as e:
            print(f"   {name} (Pin {pin_num}): ERROR - {e}")
    
    # Check 2: SPI initialization
    print("2. Checking SPI initialization...")
    try:
        spi = SPI(SPI_NUM, baudrate=31250000, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))
        print("   SPI: OK")
    except Exception as e:
        print(f"   SPI: ERROR - {e}")
    
    # Check 3: Font module
    print("3. Checking font module...")
    try:
        import vga1_16x32 as font
        print("   Font module: OK")
    except Exception as e:
        print(f"   Font module: ERROR - {e}")
    
    # Check 4: ST7789 module
    print("4. Checking ST7789 module...")
    try:
        import st7789
        print("   ST7789 module: OK")
    except Exception as e:
        print(f"   ST7789 module: ERROR - {e}")

if __name__ == "__main__":
    print("Starting display diagnostics...")
    diagnose_display_issues()
    print()
    print("Starting display test...")
    test_display()
