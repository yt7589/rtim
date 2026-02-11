# Freeform Surface Analysis for Chatter Research
# Generated: 2024-01-15

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Control points from STEP file
control_points = np.array([    [[-50.000, -50.000, 0.000], [-50.000, -35.714, 0.000], [-50.000, -21.429, 0.000], [-50.000, -7.143, 0.000], [-50.000, 7.143, 0.000], [-50.000, 21.429, 0.000], [-50.000, 35.714, 0.000], [-50.000, 50.000, 0.000]],
    [[-35.714, -50.000, 0.000], [-35.714, -35.714, -1.874], [-35.714, -21.429, 17.457], [-35.714, -7.143, 31.669], [-35.714, 7.143, 31.668], [-35.714, 21.429, 17.455], [-35.714, 35.714, -1.876], [-35.714, 50.000, 0.000]],
    [[-21.429, -50.000, 0.000], [-21.429, -35.714, -13.699], [-21.429, -21.429, 7.828], [-21.429, -7.143, 21.633], [-21.429, 7.143, 21.607], [-21.429, 21.429, 7.777], [-21.429, 35.714, -13.731], [-21.429, 50.000, 0.000]],
    [[-7.143, -50.000, 0.000], [-7.143, -35.714, -16.130], [-7.143, -21.429, 7.612], [-7.143, -7.143, 19.831], [-7.143, 7.143, 19.505], [-7.143, 21.429, 6.971], [-7.143, 35.714, -16.534], [-7.143, 50.000, 0.000]],
    [[7.143, -50.000, 0.000], [7.143, -35.714, -20.666], [7.143, -21.429, 6.826], [7.143, -7.143, 27.313], [7.143, 7.143, 25.506], [7.143, 21.429, 3.267], [7.143, 35.714, -22.912], [7.143, 50.000, 0.000]],
    [[21.429, -50.000, 0.000], [21.429, -35.714, -7.671], [21.429, -21.429, 17.118], [21.429, -7.143, 27.669], [21.429, 7.143, 23.233], [21.429, 21.429, 8.382], [21.429, 35.714, -13.185], [21.429, 50.000, 0.000]],
    [[35.714, -50.000, 0.000], [35.714, -35.714, 9.939], [35.714, -21.429, 30.713], [35.714, -7.143, 33.904], [35.714, 7.143, 29.090], [35.714, 21.429, 21.234], [35.714, 35.714, 3.957], [35.714, 50.000, 0.000]],
    [[50.000, -50.000, 0.000], [50.000, -35.714, 0.000], [50.000, -21.429, 0.000], [50.000, -7.143, 0.000], [50.000, 7.143, 0.000], [50.000, 21.429, 0.000], [50.000, 35.714, 0.000], [50.000, 50.000, 0.000]]
])

def analyze_surface():
    """分析曲面特征"""
    print("Surface Analysis")
    print("=" * 50)
    
    # 提取所有Z值
    all_z = control_points[:,:,2].flatten()
    
    print(f"Control points: {nx} x {ny}")
    print(f"Max height: {np.max(all_z):.2f} mm")
    print(f"Min height: {np.min(all_z):.2f} mm")
    print(f"Height range: {np.max(all_z)-np.min(all_z):.2f} mm")
    print(f"Avg height: {np.mean(all_z):.2f} mm")
    
    # 曲率估算（简化）
    print("\nEstimated curvature regions:")
    
    # 中心区域
    center_z = control_points[nx//2, ny//2, 2]
    print(f"  Center (0,0): Height = {center_z:.1f} mm")
    
    # 最高点
    max_idx = np.unravel_index(np.argmax(control_points[:,:,2]), (nx, ny))
    max_x, max_y, max_z = control_points[max_idx]
    print(f"  Highest point: ({max_x:.1f}, {max_y:.1f}) = {max_z:.1f} mm")
    
    # 最低点
    min_idx = np.unravel_index(np.argmin(control_points[:,:,2]), (nx, ny))
    min_x, min_y, min_z = control_points[min_idx]
    print(f"  Lowest point: ({min_x:.1f}, {min_y:.1f}) = {min_z:.1f} mm")
    
    # 颤振风险评估
    print("\nChatter risk assessment:")
    
    test_points = [
        (0, 0, "Center"),
        (max_x, max_y, "Highest point"),
        (min_x, min_y, "Lowest point"),
        (30, 20, "Gaussian bump"),
        (-30, -20, "Saddle region")
    ]
    
    for x, y, desc in test_points:
        # 找到最近的控制点
        u = (x + size/2) / size
        v = (y + size/2) / size
        i = int(u * (nx - 1))
        j = int(v * (ny - 1))
        
        z = control_points[i, j, 2]
        
        # 简化曲率估算：使用相邻点的高度差
        if i > 0 and i < nx-1 and j > 0 and j < ny-1:
            curvature = abs(control_points[i+1, j, 2] - 2*z + control_points[i-1, j, 2]) +                        abs(control_points[i, j+1, 2] - 2*z + control_points[i, j-1, 2])
        else:
            curvature = 0
        
        if curvature > 10:
            risk = "HIGH"
            suggestion = "Reduce depth of cut significantly"
        elif curvature > 5:
            risk = "MEDIUM"
            suggestion = "Use adaptive toolpath"
        else:
            risk = "LOW"
            suggestion = "Standard parameters OK"
        
        print(f"  {desc}:")
        print(f"    Position: ({x:.1f}, {y:.1f}), Height: {z:.1f} mm")
        print(f"    Curvature index: {curvature:.2f}")
        print(f"    Chatter risk: {risk}")
        print(f"    Suggestion: {suggestion}")

def plot_surface():
    """绘制曲面"""
    fig = plt.figure(figsize=(12, 8))
    
    # 3D曲面图
    ax1 = fig.add_subplot(121, projection='3d')
    
    X = control_points[:,:,0]
    Y = control_points[:,:,1]
    Z = control_points[:,:,2]
    
    ax1.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.set_zlabel('Z (mm)')
    ax1.set_title('Freeform Surface for Chatter Analysis')
    
    # 2D等高线图
    ax2 = fig.add_subplot(122)
    contour = ax2.contourf(X, Y, Z, 20, cmap='viridis')
    plt.colorbar(contour, ax=ax2, label='Height (mm)')
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.set_title('Height Contour (Chatter Risk Map)')
    
    # 标记关键点
    key_points = [
        (0, 0, 'Center'),
        (control_points[nx//2, ny//2, 0], control_points[nx//2, ny//2, 1], 'Max'),
        (control_points[nx//4, ny//4, 0], control_points[nx//4, ny//4, 1], 'Saddle')
    ]
    
    for x, y, label in key_points:
        ax2.plot(x, y, 'ro', markersize=8)
        ax2.text(x, y, f' {label}', fontsize=10, color='red')
    
    plt.tight_layout()
    plt.savefig('surface_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("\nSaved plot to 'surface_analysis.png'")

if __name__ == "__main__":
    analyze_surface()
    plot_surface()
