# test_click_speed.py
import pyautogui
import time

def test_raw_click():
    print("Тестируем скорость чистого pyautogui.click()...")
    
    x, y = 500, 300
    times = []
    
    for i in range(20):
        start = time.perf_counter()
        pyautogui.click(x, y)
        end = time.perf_counter()
        elapsed = end - start
        times.append(elapsed)
        
        if i < 5:  # покажем первые 5
            print(f"  Клик {i+1}: {elapsed*1000:.1f} мс")
    
    avg = sum(times) / len(times)
    print(f"\n✅ Среднее время клика: {avg*1000:.1f} мс")
    print(f"   Теоретический максимум: {1/avg:.0f} кликов/сек")
    return avg

def test_click_with_move():
    print("\nТестируем клик с перемещением курсора...")
    
    x, y = 500, 300
    times = []
    
    # Перемещаем курсор далеко
    pyautogui.moveTo(100, 100)
    
    for i in range(5):
        start = time.perf_counter()
        pyautogui.click(x, y)  # клик должен переместить курсор
        end = time.perf_counter()
        elapsed = end - start
        times.append(elapsed)
        print(f"  Клик {i+1}: {elapsed*1000:.1f} мс")
    
    avg = sum(times) / len(times)
    print(f"✅ Среднее время с перемещением: {avg*1000:.1f} мс")
    return avg

if __name__ == "__main__":
    raw_speed = test_raw_click()
    move_speed = test_click_with_move()
    
    print(f"\n📊 Разница: {move_speed/raw_speed:.1f}x медленнее с перемещением")