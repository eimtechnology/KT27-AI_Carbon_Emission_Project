"""
调试版本的重量检测系统
添加详细的调试信息来诊断显示问题
"""

from machine import Pin, SPI
from hx711_gpio import HX711
import time
import gc
import st7789
import vga1_16x32 as font

# =========================================
# HARDWARE CONFIGURATION
# =========================================

# HX711 Weight Sensor
PIN_DATA = 8      # HX711 data pin (DOUT)
PIN_CLOCK = 9     # HX711 clock pin (SCK)

# ST7789 Display Configuration
WIDTH, HEIGHT = 240, 240
SPI_NUM = 0       # SPI bus number
BACKLIGHT_PIN = 0 # Display backlight pin
RST_PIN = 13      # Display reset pin
DC_PIN = 12       # Display data/command pin
CS_PIN = 1        # Display chip select pin
SCK_PIN = 18      # SPI clock pin (SCL)
MOSI_PIN = 19     # SPI data pin (SDA)

# Sensor Configuration
CALIBRATION_FACTOR = 419.0  # Calibration factor (unit: LSB/g)
STABILITY_THRESHOLD = 5.0   # Weight stability threshold (grams)
RAPID_SAMPLE_COUNT = 5      # Number of rapid samples for stabilization
RAPID_SAMPLE_INTERVAL = 0.05  # Interval between rapid samples (seconds)
WARMUP_SAMPLES = 10         # Number of warmup samples during initialization

# Weight sending configuration
MIN_WEIGHT_THRESHOLD = 5.0  # Minimum weight to consider (grams)
WEIGHT_CHANGE_THRESHOLD = 2.0  # Minimum weight change to trigger new send (grams)
TIME_BETWEEN_SENDS = 5.0    # Minimum time between sends (seconds)

print("DEBUG: 初始化SPI和显示屏...")

# Initialize SPI and Display
spi = SPI(SPI_NUM, baudrate=31250000, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))
print("DEBUG: SPI初始化完成")

tft = st7789.ST7789(
    spi, WIDTH, HEIGHT,
    reset=Pin(RST_PIN, Pin.OUT),
    cs=Pin(CS_PIN, Pin.OUT),
    dc=Pin(DC_PIN, Pin.OUT),
    backlight=Pin(BACKLIGHT_PIN, Pin.OUT),
    rotation=0,
)
print("DEBUG: ST7789初始化完成")


class DebugDisplayManager:
    """
    调试版本的显示管理器
    """
    
    def __init__(self, tft_display):
        """Initialize display manager"""
        print("DEBUG: 初始化DisplayManager...")
        self.tft = tft_display
        self.font = font
        
        # Display areas layout (240x240 pixels)
        self.header_area = (0, 0, 240, 40)      # System title
        self.weight_area = (0, 45, 240, 80)     # Weight display  
        self.food_area = (0, 90, 240, 130)      # Food name
        self.carbon_area = (0, 135, 240, 175)   # Carbon footprint
        self.status_area = (0, 180, 240, 220)   # System status
        self.footer_area = (0, 225, 240, 240)   # Time/info
        
        # Colors
        self.BLACK = st7789.BLACK
        self.WHITE = st7789.WHITE
        self.RED = st7789.RED
        self.GREEN = st7789.GREEN
        self.BLUE = st7789.BLUE
        self.YELLOW = st7789.YELLOW
        self.CYAN = st7789.CYAN
        self.MAGENTA = st7789.MAGENTA
        
        # Current display state
        self.current_weight = 0.0
        self.current_food = ""
        self.current_carbon = 0.0
        self.current_status = "Initializing..."
        self.ai_result_received = False
        
        # Initialize display
        self.init_display()
        print("DEBUG: DisplayManager初始化完成")
    
    def init_display(self):
        """Initialize display with welcome screen"""
        print("DEBUG: 初始化显示屏内容...")
        
        try:
            # Clear screen
            print("DEBUG: 清屏...")
            self.tft.fill(self.BLACK)
            
            # Display welcome message
            print("DEBUG: 显示欢迎信息...")
            self.draw_text_centered("DEBUG MODE", 20, self.WHITE)
            self.draw_text_centered("Weight System", 50, self.CYAN)
            self.draw_text_centered("Starting...", 80, self.YELLOW)
            
            print("DEBUG: 显示初始化成功")
            
        except Exception as e:
            print(f"DEBUG ERROR: 显示初始化失败: {e}")
    
    def draw_text_centered(self, text, y, color):
        """Draw text centered horizontally at given y position"""
        try:
            print(f"DEBUG: 绘制居中文本: '{text}' at y={y}")
            # Calculate approximate text width (16 pixels per character for this font)
            text_width = len(text) * 16
            x = max(0, (WIDTH - text_width) // 2)
            self.tft.text(self.font, text, x, y, color, self.BLACK)
            print(f"DEBUG: 文本绘制成功 at ({x}, {y})")
        except Exception as e:
            print(f"DEBUG ERROR: 文本绘制失败: {e}")
    
    def update_weight(self, weight, is_stable=False):
        """Update weight display with debug info"""
        print(f"DEBUG: 更新重量显示: {weight:.1f}g, 稳定={is_stable}")
        
        try:
            self.current_weight = weight
            
            # Choose color based on stability
            color = self.GREEN if is_stable else self.YELLOW
            
            # Format weight text
            if weight > 1000:
                weight_text = f"{weight/1000:.2f}kg"
            else:
                weight_text = f"{weight:.1f}g"
            
            print(f"DEBUG: 格式化重量文本: '{weight_text}'")
            
            # Clear weight area
            print("DEBUG: 清除重量显示区域...")
            self.tft.fill_rect(0, 45, 240, 35, self.BLACK)
            
            # Draw weight text
            text_width = len(weight_text) * 16
            x = max(0, (WIDTH - text_width) // 2)
            print(f"DEBUG: 绘制重量文本 at ({x}, 60)")
            self.tft.text(self.font, weight_text, x, 60, color, self.BLACK)
            
            # Update status indicator
            status_text = "STABLE" if is_stable else "MEASURING"
            status_color = self.GREEN if is_stable else self.YELLOW
            print(f"DEBUG: 更新状态指示器: {status_text}")
            self.tft.fill_rect(200, 45, 40, 35, status_color)
            
            print("DEBUG: 重量显示更新完成")
            
        except Exception as e:
            print(f"DEBUG ERROR: 重量显示更新失败: {e}")
    
    def show_debug_info(self, loop_count, weight, is_stable):
        """显示调试信息"""
        try:
            # Clear debug area
            self.tft.fill_rect(0, 120, 240, 100, self.BLACK)
            
            # Show loop count
            loop_text = f"Loop: {loop_count}"
            self.tft.text(self.font, loop_text, 5, 130, self.WHITE, self.BLACK)
            
            # Show weight info
            weight_info = f"W: {weight:.1f}g"
            self.tft.text(self.font, weight_info, 5, 150, self.CYAN, self.BLACK)
            
            # Show stability
            stable_text = f"S: {'YES' if is_stable else 'NO'}"
            stable_color = self.GREEN if is_stable else self.RED
            self.tft.text(self.font, stable_text, 5, 170, stable_color, self.BLACK)
            
            # Show timestamp
            time_text = f"T: {time.time():.1f}"
            self.tft.text(self.font, time_text, 5, 190, self.YELLOW, self.BLACK)
            
        except Exception as e:
            print(f"DEBUG ERROR: 调试信息显示失败: {e}")


class DebugWeightSensor:
    """
    调试版本的重量传感器 - 使用模拟数据
    """
    
    def __init__(self):
        print("DEBUG: 初始化调试重量传感器...")
        self._sim_weight = 0.0
        self._last_stable_weight = 0.0
        self._is_initialized = True
        self._simulation_mode = True
        print("DEBUG: 重量传感器初始化完成 (模拟模式)")
    
    def calibrate_zero(self):
        """模拟校准"""
        print("DEBUG: 模拟重量传感器校准...")
        time.sleep(1)
        print("DEBUG: 校准完成")
    
    def get_weight_fast(self):
        """获取模拟重量数据"""
        try:
            # 模拟重量变化
            cycle_time = int(time.time()) % 30  # 30秒周期
            
            if cycle_time < 5:
                self._sim_weight = 0.0  # 空秤
            elif cycle_time < 15:
                self._sim_weight = 125.0 + (cycle_time % 3) * 2  # 稳定重量
            else:
                self._sim_weight = 80.0 + cycle_time  # 变化重量
            
            # 模拟稳定性
            weight_change = abs(self._sim_weight - self._last_stable_weight)
            is_stable = weight_change < STABILITY_THRESHOLD and self._sim_weight > MIN_WEIGHT_THRESHOLD
            
            if is_stable:
                self._last_stable_weight = self._sim_weight
            
            print(f"DEBUG: 模拟重量: {self._sim_weight:.1f}g, 稳定: {is_stable}")
            return self._sim_weight, is_stable
            
        except Exception as e:
            print(f"DEBUG ERROR: 获取重量失败: {e}")
            return 0.0, False


class DebugWeightSystem:
    """
    调试版本的重量系统
    """
    
    def __init__(self):
        print("DEBUG: 初始化调试重量系统...")
        
        # Initialize display manager
        self.display = DebugDisplayManager(tft)
        
        # Initialize weight sensor
        self.weight_sensor = DebugWeightSensor()
        
        # System state
        self.last_sent_weight = 0.0
        self.last_sent_time = 0
        
        print("DEBUG: 系统初始化完成")
    
    def initialize(self):
        """初始化系统"""
        try:
            print("DEBUG: 开始系统初始化...")
            
            # Calibrate weight sensor
            self.weight_sensor.calibrate_zero()
            
            # Update display
            self.display.draw_text_centered("System Ready", 110, self.display.GREEN)
            
            print("DEBUG: 系统初始化完成")
            
        except Exception as e:
            print(f"DEBUG ERROR: 系统初始化失败: {e}")
    
    def run(self):
        """主循环 - 带调试信息"""
        print("DEBUG: 开始主循环...")
        
        loop_counter = 0
        
        try:
            while True:
                loop_counter += 1
                
                print(f"DEBUG: 循环 #{loop_counter}")
                
                try:
                    # Get current weight
                    weight, is_stable = self.weight_sensor.get_weight_fast()
                    
                    print(f"DEBUG: 获取重量: {weight:.1f}g, 稳定: {is_stable}")
                    
                    # Update display with current weight
                    print("DEBUG: 调用显示更新...")
                    self.display.update_weight(weight, is_stable)
                    
                    # Show debug info on screen
                    if loop_counter % 5 == 0:  # 每5次循环更新一次调试信息
                        self.display.show_debug_info(loop_counter, weight, is_stable)
                    
                    # Send weight message if significant
                    if weight > MIN_WEIGHT_THRESHOLD and is_stable:
                        weight_diff = abs(weight - self.last_sent_weight)
                        if weight_diff > WEIGHT_CHANGE_THRESHOLD or self.last_sent_weight == 0:
                            print(f"WEIGHT:{weight:.1f}:STABLE")
                            self.last_sent_weight = weight
                            self.last_sent_time = time.time()
                    
                    # Memory management
                    if loop_counter % 50 == 0:
                        print("DEBUG: 内存清理...")
                        gc.collect()
                    
                    # Delay
                    time.sleep(0.5)  # 较慢的更新频率便于调试
                    
                except Exception as e:
                    print(f"DEBUG ERROR: 循环内部错误: {e}")
                    time.sleep(1)
                
        except KeyboardInterrupt:
            print("DEBUG: 用户停止程序")
        except Exception as e:
            print(f"DEBUG ERROR: 主循环错误: {e}")


def main():
    """主程序入口"""
    print("=== 调试版重量检测系统 ===")
    
    try:
        # Create and initialize system
        system = DebugWeightSystem()
        system.initialize()
        
        print("DEBUG: 等待3秒后开始主循环...")
        time.sleep(3)
        
        # Run main loop
        system.run()
        
    except Exception as e:
        print(f"DEBUG ERROR: 致命错误: {e}")


if __name__ == "__main__":
    main()
