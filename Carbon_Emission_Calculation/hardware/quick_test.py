"""
快速测试修复后的主程序
"""

# 测试导入
try:
    print("测试导入模块...")
    from machine import Pin, SPI
    import st7789
    import vga1_16x32 as font
    print("✅ 所有模块导入成功")
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    exit(1)

# 测试显示初始化
try:
    print("测试显示初始化...")
    
    # 初始化SPI和显示
    spi = SPI(0, baudrate=31250000, sck=Pin(18), mosi=Pin(19))
    tft = st7789.ST7789(
        spi, 240, 240,
        reset=Pin(13, Pin.OUT),
        cs=Pin(1, Pin.OUT),
        dc=Pin(12, Pin.OUT),
        backlight=Pin(0, Pin.OUT),
        rotation=0,
    )
    
    print("✅ 显示初始化成功")
    
    # 测试显示内容
    tft.fill(st7789.BLACK)
    tft.text(font, "Quick Test OK", 50, 100, st7789.GREEN, st7789.BLACK)
    
    print("✅ 显示内容测试成功")
    
except Exception as e:
    print(f"❌ 显示测试失败: {e}")
    exit(1)

# 测试主程序导入
try:
    print("测试主程序导入...")
    import simple_weight_system
    print("✅ 主程序导入成功")
    
    # 测试DisplayManager类
    display = simple_weight_system.DisplayManager(tft)
    print("✅ DisplayManager创建成功")
    
    # 测试重量显示
    display.update_weight(123.5, True)
    print("✅ 重量显示测试成功")
    
except Exception as e:
    print(f"❌ 主程序测试失败: {e}")
    exit(1)

print("🎉 所有测试通过！主程序应该能正常工作了。")
