import numpy as np
class model:
    def __init__(self,dt,dx,dz,l,d,temperature_zone,end_time,v,k,air_temperature = 25):
        self.dt = dt
        self.dx = dx
        self.dz = dz # 厚度方向
        self.l = l
        self.d = d
        self.x_len = int(l / dx)
        self.z_len = int(d / dz)
        self.temperature_zone = temperature_zone
        self.end_time = end_time
        self.air_temperature = air_temperature
        self.end_time_idx = int(end_time / dt)
        self.air_temperature_distribution = np.empty((self.x_len, self.z_len, self.end_time_idx))
        self.v = v
        self.k = k # 板厚
        self.center_temperature = np.empty((self.end_time_idx))

    def run(self):
        """火炉开始运行，空气被加热，同时传送带启动"""
        for x_idx in range(0, self.x_len + 1, self.v*self.dt):#追踪中心
            

            



        