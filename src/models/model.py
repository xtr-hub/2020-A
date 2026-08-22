import numpy as np


class model:
    """回焊炉温度模型：炉内空气温度沿炉长方向分段稳态分布，
    焊接区域沿厚度方向做一维非稳态导热，两侧表面与空气对流换热。"""

    def __init__(self, dt, dx, dz, temperature_zone, end_time, v, a, k,
                 air_init_temperature=25, front_power=1.0):
        self.dt = dt
        self.dx = dx
        self.dz = dz  # 厚度方向
        self.l = 435.5
        self.d = 0.15
        self.x_len = int(self.l / dx) + 1
        self.z_len = int(round(self.d / dz)) + 1
        self.air_init_temperature = air_init_temperature
        self.front_power = front_power  # 炉前区域温度分布幂指数
        self.temperature_zone = temperature_zone
        self.end_time = end_time
        self.end_time_idx = int(round(end_time / dt)) + 1
        self.air_temperature = np.empty(self.x_len)  # 稳态空气温度沿炉长的分布
        self.v = v / 60  # cm/min -> cm/s
        self.center_temperature = np.empty(self.end_time_idx)
        self.a = a  # 热扩散率 mm^2/s
        self.k = np.atleast_1d(k).astype(float)  # 等效换热系数，1/mm
        self.time_axis = np.arange(self.end_time_idx) * dt

    @staticmethod
    def LERP(T1, T2, L, x):
        return T1 + ((T2 - T1) / L) * x

    def _build_air_temperature(self):
        """空气在指定位置的温度，由于炉内空气温度为稳态，同一位置温度不随时间变化"""
        eps = 1e-9
        for x_idx in range(self.x_len):
            x = x_idx * self.dx
            if x >= 410.5 - eps:
                # 炉后区域
                self.air_temperature[x_idx] = 25
            elif x < 25:
                # 炉前区域按幂次分布过渡
                self.air_temperature[x_idx] = 25 + (self.temperature_zone[0] - 25) * (x / 25) ** self.front_power
            else:
                s = x - 25
                zidx = min(int(s // 35.5), 10)
                pos = s - zidx * 35.5
                if pos <= 30.5:
                    # 小温区内部
                    self.air_temperature[x_idx] = self.temperature_zone[zidx]
                else:
                    # 温区间隙线性过渡
                    self.air_temperature[x_idx] = self.LERP(
                        self.temperature_zone[zidx],
                        self.temperature_zone[min(zidx + 1, 10)], 5, pos - 30.5)

    def implicit_Euler_method(self):
        """隐式欧拉格式求解厚度方向一维导热方程，边界为对流 Robin 条件"""
        n = self.z_len
        r = self.a * self.dt / self.dz ** 2

        # 换热系数按功能温区分段：1~5 / 6~9 / 10~11
        if len(self.k) == 3:
            region_of_x = lambda x: 0 if x < 205 else (1 if x < 342 else 2)
        else:
            region_of_x = lambda x: 0

        Ainvs = []
        for kval in self.k:
            c = kval * self.dz
            A = np.zeros((n, n))
            for j in range(1, n - 1):
                A[j, j - 1] = -r
                A[j, j] = 1 + 2 * r
                A[j, j + 1] = -r
            # 两侧表面对流边界
            A[0, 0] = 1 + c
            A[0, 1] = -1
            A[n - 1, n - 2] = -1
            A[n - 1, n - 1] = 1 + c
            Ainvs.append(np.linalg.inv(A))  # 只求逆一次

        xgrid = np.arange(self.x_len) * self.dx
        T = np.full(n, float(self.air_init_temperature))
        mid = (n - 1) / 2
        lo, hi = int(np.floor(mid)), int(np.ceil(mid))
        for i in range(self.end_time_idx):
            x = min(self.v * self.time_axis[i], self.l)  # 追踪电路板中心位置
            reg = region_of_x(x)
            c = self.k[reg] * self.dz
            t_air = np.interp(x, xgrid, self.air_temperature)
            rhs = T.copy()
            rhs[0] = c * t_air
            rhs[n - 1] = c * t_air
            T = Ainvs[reg] @ rhs
            self.center_temperature[i] = (T[lo] + T[hi]) / 2

    def run(self):
        """火炉开始运行，空气被加热至稳态，同时传送带启动"""
        self._build_air_temperature()
        self.implicit_Euler_method()
        return self.center_temperature

    def temperature_at_position(self, x):
        """电路板中心经过炉长 x(cm) 处时的中心温度"""
        return float(np.interp(x / self.v, self.time_axis, self.center_temperature))

    def _cross_times(self, level):
        """中心温度穿越 level 的时刻（线性插值）"""
        T = self.center_temperature
        s = T - level
        idx = np.where(s[:-1] * s[1:] < 0)[0]
        return self.time_axis[idx] + (level - T[idx]) * self.dt / (T[idx + 1] - T[idx])

    def metrics(self):
        """制程界限指标：上升/下降斜率极值、150~190升温时间、217以上时间、峰值温度"""
        T = self.center_temperature
        peak_idx = int(np.argmax(T))
        slope = np.diff(T) / self.dt
        c150, c190, c217 = self._cross_times(150), self._cross_times(190), self._cross_times(217)
        return {
            "slope_up": float(np.max(slope[:peak_idx])) if peak_idx > 0 else 0.0,
            "slope_down": float(np.min(slope[peak_idx:])) if peak_idx < len(slope) else 0.0,
            "t150_190": float(c190[0] - c150[0]) if len(c150) and len(c190) else 0.0,
            "t217": float(c217[-1] - c217[0]) if len(c217) >= 2 else 0.0,
            "peak": float(T[peak_idx]),
        }

    def area_above(self, level=217):
        """炉温曲线超过 level 部分所覆盖的面积"""
        return float(np.sum(np.clip(self.center_temperature - level, 0, None)) * self.dt)

    def symmetry_index(self, level=217):
        """以峰值为中心线，两侧超过 level 部分面积的对称度，0 表示完全对称"""
        T = self.center_temperature
        peak_idx = int(np.argmax(T))
        left = float(np.sum(np.clip(T[:peak_idx + 1] - level, 0, None)) * self.dt)
        right = float(np.sum(np.clip(T[peak_idx:] - level, 0, None)) * self.dt)
        if left + right == 0:
            return 1.0
        return abs(left - right) / (left + right)
