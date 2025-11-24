"""
测试串口通信功能
验证PC端和Pico端的数据传输
"""

import time

class TestResultReceiver:
    """测试用的结果接收器"""
    
    def __init__(self):
        self.received_count = 0
        
    def process_serial_input(self, line):
        """处理接收到的串口数据"""
        try:
            line = line.strip()
            print(f"[RECEIVER] 收到数据: {line}")
            self.received_count += 1
            
            # 解析AI结果消息: AI_RESULT:food:confidence:weight:co2:impact
            if line.startswith("AI_RESULT:"):
                parts = line.split(":")
                if len(parts) >= 6:
                    _, food_name, confidence, weight, co2_grams, impact_level = parts[:6]
                    
                    print(f"[PARSED] 食物: {food_name}")
                    print(f"[PARSED] 置信度: {confidence}%")
                    print(f"[PARSED] 重量: {weight}g")
                    print(f"[PARSED] CO2: {co2_grams}g")
                    print(f"[PARSED] 影响: {impact_level}")
                    
                    return True
            
            return False
            
        except Exception as e:
            print(f"[ERROR] 数据处理错误: {e}")
            return False


def test_serial_input():
    """测试串口输入功能"""
    print("=== 串口通信测试 ===")
    print("这个测试将检查串口输入功能")
    print()
    
    receiver = TestResultReceiver()
    
    # 测试不同的输入方式
    print("1. 测试MicroPython风格的输入检查...")
    
    try:
        import sys
        
        # 检查MicroPython特有的方法
        if hasattr(sys.stdin, 'any'):
            print("✅ 检测到MicroPython环境")
            
            print("等待串口输入... (输入 'quit' 退出)")
            print("可以尝试输入: AI_RESULT:apple:85:125.5:75.3:LOW")
            print()
            
            timeout_counter = 0
            max_timeout = 100  # 10秒超时
            
            while timeout_counter < max_timeout:
                try:
                    if sys.stdin.any():
                        line = sys.stdin.readline().strip()
                        if line:
                            print(f"[INPUT] 接收: {line}")
                            
                            if line.lower() == 'quit':
                                break
                                
                            # 处理输入
                            success = receiver.process_serial_input(line)
                            if success:
                                print("✅ AI结果解析成功!")
                            else:
                                print("⚠️ 非AI结果数据")
                            print()
                    
                    time.sleep(0.1)
                    timeout_counter += 1
                    
                    # 每秒显示一次状态
                    if timeout_counter % 10 == 0:
                        print(f"[STATUS] 等待输入... ({timeout_counter//10}s)")
                        
                except KeyboardInterrupt:
                    print("\n用户中断")
                    break
                except Exception as e:
                    print(f"[ERROR] 输入处理错误: {e}")
                    break
        else:
            print("⚠️ 非MicroPython环境，使用标准方法测试")
            
            # 模拟一些测试数据
            test_data = [
                "AI_RESULT:apple:85:125.5:75.3:LOW",
                "AI_RESULT:banana:92:180.2:126.1:MEDIUM",
                "WEIGHT:125.5:STABLE",
                "STATUS:READY:MODE:REAL:WEIGHT:0.0"
            ]
            
            for data in test_data:
                print(f"[TEST] 测试数据: {data}")
                receiver.process_serial_input(data)
                print()
                time.sleep(1)
    
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
    
    print(f"测试完成. 总共处理了 {receiver.received_count} 条消息")


def test_output():
    """测试串口输出功能"""
    print("\n=== 串口输出测试 ===")
    
    # 模拟发送重量数据
    test_weights = [0.0, 25.5, 125.8, 250.3]
    
    for weight in test_weights:
        stability = "STABLE" if weight > 50 else "CHANGING"
        message = f"WEIGHT:{weight:.1f}:{stability}"
        
        print(message)  # 这会通过USB串口发送到PC
        time.sleep(1)
    
    # 发送状态消息
    status_message = "STATUS:READY:MODE:SIMULATION:WEIGHT:125.5"
    print(status_message)
    
    print("输出测试完成")


def test_bidirectional():
    """测试双向通信"""
    print("\n=== 双向通信测试 ===")
    
    receiver = TestResultReceiver()
    
    # 发送一些数据
    print("发送测试数据...")
    print("WEIGHT:123.5:STABLE")
    print("STATUS:READY:MODE:TEST:WEIGHT:123.5")
    
    # 等待响应
    print("\n等待PC端响应...")
    print("期望接收: AI_RESULT:food_name:confidence:weight:co2:impact")
    
    try:
        import sys
        timeout = 50  # 5秒超时
        
        while timeout > 0:
            if hasattr(sys.stdin, 'any') and sys.stdin.any():
                line = sys.stdin.readline().strip()
                if line:
                    print(f"[RESPONSE] 收到响应: {line}")
                    receiver.process_serial_input(line)
                    break
            
            time.sleep(0.1)
            timeout -= 1
            
            if timeout % 10 == 0:
                print(f"等待中... ({(50-timeout)//10}s)")
        
        if timeout <= 0:
            print("⚠️ 未收到PC端响应")
    
    except Exception as e:
        print(f"[ERROR] 双向通信测试失败: {e}")


if __name__ == "__main__":
    print("开始串口通信测试...")
    
    # 运行所有测试
    test_output()
    test_serial_input()
    test_bidirectional()
    
    print("\n🎉 所有测试完成!")
    print("如果看到正确的消息解析，说明串口通信正常")
