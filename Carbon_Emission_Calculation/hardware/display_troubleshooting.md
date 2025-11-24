# ST7789显示屏故障排除指南

## 🚨 问题：屏幕上没有任何显示

### 📋 检查清单

#### 1. **硬件连接检查**
```
ST7789 -> Raspberry Pi Pico
VCC    -> 3.3V 或 VBUS
GND    -> GND
SCL    -> GPIO 18 (SCK)
SDA    -> GPIO 19 (MOSI)
RES    -> GPIO 13 (RESET)
DC     -> GPIO 12 (DATA/COMMAND)
CS     -> GPIO 1  (CHIP SELECT)
BLK    -> GPIO 0  (BACKLIGHT)
```

#### 2. **电源检查**
- ✅ 确保Pico通过USB供电
- ✅ 检查3.3V电压是否稳定
- ✅ 确保显示屏背光引脚连接正确

#### 3. **软件检查**
- ✅ 确保已安装 `st7789` 模块
- ✅ 确保已安装 `vga1_16x32` 字体模块
- ✅ 检查引脚配置是否正确

## 🔧 修复步骤

### 步骤1: 运行基本显示测试
```bash
# 上传并运行简单测试脚本
python hardware/simple_display_test.py
```

### 步骤2: 检查系统初始化
确保 `SimpleWeightSystem` 正确初始化了显示管理器：
```python
# 在 __init__ 方法中应该有：
self.display = DisplayManager(tft)
```

### 步骤3: 验证主循环更新
确保主循环中调用了显示更新：
```python
# 在 run() 方法中应该有：
self.display.update_weight(weight, is_stable)
```

## 🐛 常见问题和解决方案

### 问题1: 显示屏完全黑屏
**可能原因:**
- 背光未连接或损坏
- 电源不足
- 接线错误

**解决方案:**
1. 检查背光引脚连接
2. 使用万用表测试电压
3. 重新检查所有接线

### 问题2: 显示屏有背光但无内容
**可能原因:**
- SPI通信问题
- 引脚配置错误
- 软件初始化失败

**解决方案:**
1. 检查SPI引脚连接
2. 验证引脚配置
3. 运行诊断脚本

### 问题3: 显示内容不正确
**可能原因:**
- 字体模块问题
- 坐标计算错误
- 颜色配置问题

**解决方案:**
1. 重新安装字体模块
2. 检查文本绘制逻辑
3. 验证颜色定义

## 🔍 诊断命令

### 1. 检查模块安装
```python
try:
    import st7789
    print("ST7789模块: OK")
except ImportError:
    print("ST7789模块: 未安装")

try:
    import vga1_16x32
    print("字体模块: OK")
except ImportError:
    print("字体模块: 未安装")
```

### 2. 测试SPI通信
```python
from machine import Pin, SPI
spi = SPI(0, baudrate=31250000, sck=Pin(18), mosi=Pin(19))
print("SPI初始化成功")
```

### 3. 测试引脚
```python
from machine import Pin

pins = {
    "BACKLIGHT": 0, "RESET": 13, "DC": 12, 
    "CS": 1, "SCK": 18, "MOSI": 19
}

for name, pin_num in pins.items():
    try:
        pin = Pin(pin_num, Pin.OUT)
        print(f"{name} (GPIO{pin_num}): OK")
    except Exception as e:
        print(f"{name} (GPIO{pin_num}): 错误 - {e}")
```

## 📊 测试脚本使用

### 运行完整诊断
```bash
python hardware/display_test.py
```

### 运行简化测试
```bash
python hardware/simple_display_test.py
```

## ⚡ 快速修复

如果你的显示屏仍然没有显示，尝试以下快速修复：

1. **重启Pico**
   - 断开USB连接
   - 等待5秒
   - 重新连接

2. **检查接线**
   - 确保所有连接牢固
   - 检查是否有短路

3. **降低SPI速度**
   ```python
   spi = SPI(0, baudrate=10000000, sck=Pin(18), mosi=Pin(19))  # 降低到10MHz
   ```

4. **手动控制背光**
   ```python
   backlight = Pin(0, Pin.OUT)
   backlight.value(1)  # 打开背光
   ```

## 🎯 验证修复

修复后，你应该能看到：

1. **初始化时**: 欢迎信息显示
2. **重量检测时**: 实时重量数据
3. **AI分析时**: 完整的分析结果

如果问题仍然存在，请检查硬件连接或尝试更换显示屏模块。
