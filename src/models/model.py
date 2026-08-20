import numpy as np
from functools import cache
class model:
    def __init__(self,dt,dx,dz,temperature_zone,end_time,v,air_init_temperature = 25,center_temperature=30):
        self.dt = dt
        self.dx = dx
        self.dz = dz # 厚度方向
        self.l = 435.5
        self.d = 0.15
        self.x_len = int(self.l / dx) + 1
        self.z_len = int(self.d / dz) + 1
        self.air_init_temperature = air_init_temperature
        self.temperature_zone = temperature_zone
        self.end_time = end_time
        self.end_time_idx = int(end_time / dt)
        self.air_temperature = np.empty((self.x_len)) # 空气在指定位置的表面温度，由于题目的空气温度为稳态，所以同一位置表面的温度不变
        self.v = v
        self.center_temperature = np.full((self.end_time_idx),center_temperature)

    @cache
    def LERP(self,T1,T2,L,x):
        return T1 + ((T2 - T1)/L)*x
    def run(self):
        """火炉开始运行，空气被加热至稳态，同时传送带启动"""
        dx = self.dx
        # 计算在一瞬间被加热到的稳态温度
        for x_idx in range(self.x_len):
            x = int(x_idx*dx)
            if x > 415.5:
                # 炉后区域直接为25，因为左右都是25
                self.air_temperature[x_idx] = 25
            elif x < 25:
                # 炉前区域线性插值
                self.air_temperature[x_idx] = self.LERP(25, self.temperature_zone[0], 25, x)
            elif (x - 25)%35.5 <= 30.5:
                # 小温区区域直接认为温度为加热温度
                self.air_temperature[x_idx] = self.temperature_zone[(x - 25)//35.5]
            else:
                # 间隔线性插值
                left_idx = (x - 25)//35.5
                self.air_temperature[x_idx] = self.LERP(self.temperature_zone[left_idx],self.temperature_zone[left_idx+1],5,(x - 25)%35.5-30.5)

        for x_idx in range(0, self.x_len, self.v*self.dt):#追踪中心
            
             

            



        