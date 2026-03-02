import numpy as np


def latlon_to_cartesian(lat_deg, lon_deg, R):
    """将经纬度（度）转换为三维直角坐标"""
    lat = np.radians(lat_deg)
    lon = np.radians(lon_deg)
    x = R * np.cos(lat) * np.cos(lon)
    y = R * np.cos(lat) * np.sin(lon)
    z = R * np.sin(lat)
    return np.array([x, y, z])


def perpendicular_distance_to_chord(lat1, lon1, lat2, lon2, R=6371.0):
    """
    计算地心到地表两点所连线段（弦）的垂线段长度。

    参数:
        lat1, lon1: 第一个点的纬度和经度（度）
        lat2, lon2: 第二个点的纬度和经度（度）
        R: 地球半径（km），默认 6371 km

    返回:
        地心到该弦的垂直距离（km）

    原理:
        线段参数方程: P(t) = P1 + t·(P2 - P1),  t ∈ [0, 1]
        令 d = P2 - P1，最近点参数: t* = -P1·d / |d|²
        由于 |P1| = |P2| = R，可以证明 t* 恒等于 0.5，
        即垂足总在弦的中点（球心到等长弦的垂线平分该弦）。
        因此距离 = |(P1 + P2) / 2| = R·cos(θ/2)，其中 θ 为圆心角。
    """
    P1 = latlon_to_cartesian(lat1, lon1, R)
    P2 = latlon_to_cartesian(lat2, lon2, R)

    d = P2 - P1
    d_dot_d = np.dot(d, d)

    # 两点重合时，弦退化为一个点，距离即为 R
    if d_dot_d < 1e-12:
        return R

    # 求原点到直线最近点的参数 t，并限制在 [0,1] 内（线段范围）
    t = -np.dot(P1, d) / d_dot_d
    t = np.clip(t, 0.0, 1.0)

    # 线段上离原点最近的点
    closest_point = P1 + t * d
    distance = np.linalg.norm(closest_point)

    return distance


# ===================== 示例与验证 =====================
if __name__ == "__main__":

    R = 6371.0  # 地球平均半径 (km)
    _targets = {
        'ETR':'AEG',
        'TER':'EAE',
        'TIN':'ERE',
        'ETE':'REA',
        'TEM':'TNG',
        'TEE':'FTI',
        'TAO':'FTE',
        'NER':'ERM',
        'THE':'TEN',
        'ANG':'THH'
    }
    new_targets = """圣罗莎国际机场	-3.441986	-79.996957	Heard It in the Morning	巴东石林潘	1.4001	99.430496
拉杰斯机场	38.761799	-27.090799	Death's End	思沃机场	-17.0903	168.3430023
廷杜夫机场	27.7003994	-8.167099953	The Three-Body Problem	埃拉夫机场	-6.606463154	143.9002132
米提玛	12.93299961	36.16699982	For the Benefit of Mankind	雷奥机场	-18.46652	-136.43855
特莫拉机场	-34.421398	147.511993	The Wandering Earth	伯克哈勒夫机场	35.731741	-5.921459
泰贝萨机场	35.43159866	8.12071991	Of Ants and Dinosaurs	费图伊塔机场	-14.216131	-169.423771
青岛国际机场	36.361953	120.088171	End of the Microcosmos	埃尔卡拉法特机场	-50.2803	-72.053101
内尤格里机场	56.91389847	124.9140015	Sea of Dreams	科曼达恩特克拉莫机场	-27.663614	-52.271489
特雷西纳机场	-5.06025	-42.823712	The Messenger	铜仁凤凰机场	27.883333	109.308889
布里查姆普尼厄斯机场	45.729198	0.221456	The Thinker	塔哈罗阿机场	-38.18109894	174.7079926"""
    d_list = []
    for line in new_targets.split('\n'):
        parts = line.strip().split('\t')
        key = parts[0]
        lat1 = float(parts[1])
        lon1 = float(parts[2])
        value = parts[4]
        lat2 = float(parts[5])
        lon2 = float(parts[6])
        d = perpendicular_distance_to_chord(lat1, lon1, lat2, lon2, R)
        d /= 100
        d_list.append(d)
        print(f"{key} → {value}:  垂线段长度 = {d:.4f} (100000 m)")
    for d in d_list:
        d = int(round(d, 0))
        print(chr(d+ord('A')-1),end='')
    # --- 示例 1：北京 → 上海 ---
    # beijing = (39.9042, 116.4074)
    # shanghai = (31.2304, 121.4737)
    # d1 = perpendicular_distance_to_chord(*beijing, *shanghai, R)
    # print(f"北京 → 上海:  垂线段长度 = {d1:.4f} km")

    # # --- 示例 2：对径点（北极 → 南极），弦穿过球心，距离应为 0 ---
    # d2 = perpendicular_distance_to_chord(90, 0, -90, 0, R)
    # print(f"北极 → 南极:  垂线段长度 = {d2:.4f} km  (理论值 0)")

    # # --- 示例 3：同一点，距离应为 R ---
    # d3 = perpendicular_distance_to_chord(40, 116, 40, 116, R)
    # print(f"同一点:       垂线段长度 = {d3:.4f} km  (理论值 {R})")

    # # --- 示例 4：赤道上相隔 90°，理论值 R·cos(45°) ---
    # d4 = perpendicular_distance_to_chord(0, 0, 0, 90, R)
    # theory4 = R * np.cos(np.radians(45))
    # print(f"赤道 0° → 90°: 垂线段长度 = {d4:.4f} km  (理论值 {theory4:.4f})")

    # # --- 示例 5：赤道上相隔 180°（对径），距离应为 0 ---
    # d5 = perpendicular_distance_to_chord(0, 0, 0, 180, R)
    # print(f"赤道 0° → 180°: 垂线段长度 = {d5:.4f} km  (理论值 0)")

    # # --- 通用公式验证：距离 = R·cos(θ/2) ---
    # print("\n--- 通用公式验证: d = R·cos(θ/2) ---")
    # for angle in [30, 60, 90, 120, 150, 180]:
    #     d = perpendicular_distance_to_chord(0, 0, 0, angle, R)
    #     theory = R * np.cos(np.radians(angle / 2))
    #     print(f"  圆心角 {angle:>3}°:  计算值 = {d:.4f} km,  理论值 = {theory:.4f} km,  误差 = {abs(d - theory):.2e} km")