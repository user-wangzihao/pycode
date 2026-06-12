# 任务1：写一个函数，计算 BMI 并返回评级
# 函数签名：calc_bmi(weight, height, unit="kg")
#   - BMI=体重(kg)​ / 身高(m) * 身高(m)
#   - weight: 体重数值
#   - height: 身高（米）
#   - unit: 默认 "kg"，可以传 "lb"（磅，1磅=0.453592kg）
# 返回 tuple：(BMI值保留2位小数, 评级字符串)
#   - BMI < 18.5: "偏瘦"
#   - 18.5 <= BMI < 24: "正常"
#   - 24 <= BMI < 28: "偏胖"
#   - BMI >= 28: "肥胖"

def calc_bmi(weight, height, unit="kg"):
    # 实现
    # 判断传来的单位是否为 kg，计算前先统一计算单位
    if unit == "lb":
        weight = round(weight * 0.453592, 2)

    bmi = round(weight / (height * height), 2)
    level = ""
    if bmi < 18.5:
        level = "偏瘦"
    elif 18.5 <= bmi < 24:
        level = "正常"
    elif 24 <= bmi < 28:
        level = "偏胖"
    else:
        level = "肥胖"
    return bmi, level


if __name__ == "__main__":
    # 测试1：默认 kg
    bmi, level = calc_bmi(70, 1.75)
    print(f"70kg/1.75m → BMI={bmi}, 评级={level}")

    # 测试2：关键字参数顺序乱
    bmi, level = calc_bmi(height=1.80, weight=85)
    print(f"85kg/1.80m → BMI={bmi}, 评级={level}")

    # 测试3：使用磅
    bmi, level = calc_bmi(150, 1.70, unit="lb")
    print(f"150lb/1.70m → BMI={bmi}, 评级={level}")