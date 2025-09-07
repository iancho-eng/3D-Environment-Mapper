import serial
import numpy as np
import open3d as o3d
import math

NUM_POINTS = 32
NUM_STEPS = 3

distances = [0] * NUM_POINTS
x_coords = [[] for _ in range(NUM_POINTS)]
z_coords = [[] for _ in range(NUM_POINTS)]

ser = serial.Serial('COM5', 115200, timeout=10)
print("Opening: " + ser.name)
ser.reset_output_buffer()
ser.reset_input_buffer()
input("Press Enter to start communication...")
ser.write('s'.encode())

with open("tof_radar.txt", "w") as file:
    for i in range(NUM_STEPS):
        print("The PCD array for step", i, ":")
        for j in range(NUM_POINTS):
            z_coords[j].clear()
            while True:
                r = ser.read()
                if r == b'\n':
                    break
                z_coords[j].append(r.decode())
            
            x_coords[j] = "".join(z_coords[j]).split(", ")
            distances[j] = int(x_coords[j][0])
            print(j, ") Measured Coords:", distances)
            z = distances[j] * math.cos((2 / NUM_POINTS * (j + 1)) * math.pi)
            y = distances[j] * math.sin((2 / NUM_POINTS * (j + 1)) * math.pi)
            x = i * 100  
            file.write('{} {} {}\n'.format(x, y, z))

ser.close()

pcd = o3d.io.read_point_cloud("tof_radar.txt", format='xyz')
print(pcd)
print(np.asarray(pcd.points))

lines = []
for i in range(NUM_POINTS):
    if i != NUM_POINTS - 1:
        lines.append([i, i + 1])
    else:
        lines.append([i, 0])

line_set = o3d.geometry.LineSet(points=o3d.utility.Vector3dVector(np.asarray(pcd.points)), lines=o3d.utility.Vector2iVector(lines))
o3d.visualization.draw_geometries([line_set])
