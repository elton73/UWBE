import numpy as np
import math
xyz_Cam=np.array([0,2,0])
Cam_dist = np.array([3,5,2])
#camera angles should be in degrees, and then will get switched to radians
Cam_ang = np.array([[math.radians(0)],[math.radians(25)],[math.radians(45)]])
xRmat=np.array([[1,0,0],[0,math.cos(Cam_ang[0]),-math.sin(Cam_ang[0])],[0,math.sin(Cam_ang[0]),math.cos(Cam_ang[0])]])
yRmat=[[math.cos(Cam_ang[1]),0,math.sin(Cam_ang[1])],[0,1,0],[-math.sin(Cam_ang[1]),0,math.cos(Cam_ang[1])]]
zRmat=[[math.cos(Cam_ang[2]),-math.sin(Cam_ang[2]),0],[math.sin(Cam_ang[2]),math.cos(Cam_ang[2]),0],[0,0,1]]
Rotation_Matrix=xRmat@yRmat@zRmat
xyz_Origin=xyz@Rotation_Matrix+Cam_dist
print(xyz_Origin)