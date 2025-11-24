"""
简化的显示测试脚本 - 测试ST7789基本显示功能
"""

from machine import Pin, SPI
import time
import st7789
import vga1_16x32 as font

# 显示配置
WIDTH, HEIGHT = 240, 240
spi = SPI(0, baudrate=31250000, sck=Pin(18), mosi=Pin(19))

# 初始化显示屏
print("初始化ST7789显示屏...")
tft = st7789.ST7789(
    spi, WIDTH, HEIGHT,
    reset=Pin(13, Pin.OUT),
    cs=Pin(1, Pin.OUT),
    dc=Pin(12, Pin.OUT),
    backlight=Pin(0, Pin.OUT),
    rotation=0,
)

def test_basic_display():
    """基本显示测试"""
    print("开始基本显示测试...")
    
    # 测试1: 清屏和颜色填充
    print("测试1: 颜色填充")
    colors = [st7789.BLACK, st7789.RED, st7789.GREEN, st7789.BLUE, st7789.WHITE]
    names = ["黑色", "红色", "绿色", "蓝色", "白色"]
    
    for color, name in zip(colors, names):
        print(f"  填充{name}...")
        tft.fill(color)
        time.sleep(1)
    
    # 测试2: 文字显示
    print("测试2: 文字显示")
    tft.fill(st7789.BLACK)
    
    # 显示测试文字
    test_messages = [
        ("Display Test", 20, st7789.WHITE),
        ("ST7789 OK", 60, st7789.GREEN),
        ("Font Working", 100, st7789.YELLOW),
        ("All Good!", 140, st7789.CYAN),
    ]
    
    for text, y, color in test_messages:
        print(f"  显示: {text}")
        # 居中显示
        text_width = len(text) * 16
        x = max(0, (WIDTH - text_width) // 2)
        tft.text(font, text, x, y, color, st7789.BLACK)
        time.sleep(1)
    
    # 测试3: 矩形绘制
    print("测试3: 矩形绘制")
    time.sleep(2)
    tft.fill(st7789.BLACK)
    
    # 绘制彩色矩形
    rects = [
        (20, 20, 60, 40, st7789.RED),
        (100, 20, 60, 40, st7789.GREEN),
        (180, 20, 40, 40, st7789.BLUE),
        (20, 80, 200, 20, st7789.YELLOW),
    ]
    
    for x, y, w, h, color in rects:
        print(f"  绘制矩形 ({x},{y},{w},{h})")
        tft.fill_rect(x, y, w, h, color)
        time.sleep(0.5)
    
    print("基本显示测试完成!")

def test_weight_display():
    """模拟重量显示测试"""
    print("测试重量显示...")
    
    tft.fill(st7789.BLACK)
    
    # 显示标题
    tft.text(font, "Weight Monitor", 20, 20, st7789.WHITE, st7789.BLACK)
    
    # 模拟重量变化
    weights = [0.0, 25.5, 50.2, 125.8, 250.3, 500.1]
    
    for weight in weights:
        # 清除重量显示区域
        tft.fill_rect(0, 60, 240, 40, st7789.BLACK)
        
        # 显示重量
        if weight > 1000:
            weight_text = f"{weight/1000:.2f}kg"
        else:
            weight_text = f"{weight:.1f}g"
        
        # 根据重量选择颜色
        color = st7789.GREEN if weight > 100 else st7789.YELLOW if weight > 10 else st7789.RED
        
        # 居中显示重量
        text_width = len(weight_text) * 16
        x = max(0, (WIDTH - text_width) // 2)
        tft.text(font, weight_text, x, 80, color, st7789.BLACK)
        
        # 显示状态
        status = "STABLE" if weight > 50 else "MEASURING"
        status_color = st7789.GREEN if weight > 50 else st7789.YELLOW
        
        # 清除状态区域
        tft.fill_rect(0, 120, 240, 40, st7789.BLACK)
        
        # 显示状态
        text_width = len(status) * 16
        x = max(0, (WIDTH - text_width) // 2)
        tft.text(font, status, x, 140, status_color, st7789.BLACK)
        
        print(f"  显示重量: {weight_text} ({status})")
        time.sleep(1.5)
    
    print("重量显示测试完成!")

def test_analysis_result():
    """模拟AI分析结果显示"""
    print("测试AI分析结果显示...")
    
    # 清屏
    tft.fill(st7789.BLACK)
    
    # 标题
    tft.text(font, "Carbon Analysis", 10, 5, st7789.WHITE, st7789.BLACK)
    
    # 模拟分析结果
    food_name = "apple"
    confidence = 85
    weight = 125.5
    co2_grams = 75.3
    impact_level = "LOW"
    
    # 显示食物信息
    food_text = f"Food: {food_name}"
    tft.text(font, food_text, 5, 40, st7789.CYAN, st7789.BLACK)
    
    conf_text = f"Conf: {confidence}%"
    tft.text(font, conf_text, 5, 70, st7789.CYAN, st7789.BLACK)
    
    # 显示重量
    weight_text = f"Weight: {weight:.1f}g"
    tft.text(font, weight_text, 5, 105, st7789.YELLOW, st7789.BLACK)
    
    # 显示CO2
    co2_text = f"CO2: {co2_grams:.1f}g"
    co2_color = st7789.GREEN  # LOW impact = green
    tft.text(font, co2_text, 5, 140, co2_color, st7789.BLACK)
    
    # 显示影响等级
    impact_text = f"Impact: {impact_level}"
    tft.text(font, impact_text, 5, 175, co2_color, st7789.BLACK)
    
    # 显示完成状态
    tft.text(font, "Analysis Complete", 5, 210, st7789.GREEN, st7789.BLACK)
    
    print("AI分析结果显示完成!")

if __name__ == "__main__":
    print("=== ST7789显示屏测试程序 ===")
    
    try:
        # 基本显示测试
        test_basic_display()
        time.sleep(3)
        
        # 重量显示测试
        test_weight_display()
        time.sleep(3)
        
        # AI分析结果显示测试
        test_analysis_result()
        
        print("=== 所有测试完成! ===")
        print("如果你能看到显示屏上的内容，说明显示功能正常")
        
    except Exception as e:
        print(f"测试失败: {e}")
        print("可能的问题:")
        print("1. 检查接线")
        print("2. 检查电源")
        print("3. 检查模块安装")
