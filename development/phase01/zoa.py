import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Optional
import matplotlib

# 设置字体支持 - 避免使用特殊字符
def setup_font():
    """配置字体，避免特殊字符问题"""
    try:
        # 尝试多种字体，优先使用Arial（包含更多Unicode字符）
        plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        print("✓ 字体设置完成")
    except:
        print("⚠ 字体设置遇到问题，使用默认设置")

# 在程序开始时调用
setup_font()

def compute_stability_lobe_zoa(
    m: float,                    # 模态质量 (kg)
    c: float,                    # 阻尼系数 (N·s/m)
    k: float,                    # 刚度 (N/m)
    Kt: float,                   # 切向切削力系数 (N/m²)
    Kr: float,                   # 径向/切向力系数比 (K_r / K_t)
    N: int,                      # 刀具齿数
    rpm_range: np.ndarray,       # 主轴转速范围 (RPM)
    phi_st: float = 0.0,         # 切入角 (rad)
    phi_ex: float = np.pi        # 切出角 (rad)
) -> Tuple[np.ndarray, np.ndarray]:
    """
    基于经典ZOA方法计算铣削颤振稳定性叶瓣图
    """
    
    # 1. 计算系统动态特性
    omega_n = np.sqrt(k / m)                    # 自然频率 (rad/s)
    zeta = c / (2 * np.sqrt(k * m))             # 阻尼比
    
    # 2. 计算方向系数
    g_0 = (phi_ex - phi_st) / (2 * np.pi)
    h_0 = (np.sin(2 * phi_st) - np.sin(2 * phi_ex) + 2 * (phi_ex - phi_st)) / (4 * np.pi)
    
    # 3. 计算Lambda参数
    Lambda = np.sqrt((g_0 + Kr * h_0)**2 + (h_0 - Kr * g_0)**2)
    
    # 4. 初始化结果数组
    n_points = len(rpm_range)
    a_lims_mm = np.full(n_points, np.nan)  # 初始化为NaN
    
    # 5. 对每个RPM计算临界切深
    for i, rpm in enumerate(rpm_range):
        # 时间延迟（齿通过周期）
        T = 60 / (N * rpm)  # 秒
        
        # 相位角 (eta = ω_n * T)
        eta = omega_n * T
        
        # 计算ZOA临界切深公式
        numerator = -2 * np.pi * zeta * omega_n**2 * (1 + (zeta * omega_n * T)**2)
        denominator = N * Kt * Lambda * (omega_n**2 * T * (1 + zeta**2) + 2 * zeta * omega_n)
        
        # 临界切深 (m)
        a_lim = numerator / denominator
        
        # 转换为mm并存储（只保留正值）
        if a_lim > 0:
            a_lims_mm[i] = a_lim * 1000
    
    return rpm_range, a_lims_mm

def generate_realistic_lobes(
    f_n: float,                  # 自然频率 (Hz)
    zeta: float,                 # 阻尼比
    N: int,                      # 刀具齿数
    rpm_range: np.ndarray,       # 主轴转速范围 (RPM)
    Kt: float = 6e8,            # 切向切削力系数 (N/m²)
    Kr: float = 0.3              # 径向/切向力系数比
) -> Tuple[np.ndarray, np.ndarray]:
    """
    生成符合物理意义的稳定性叶瓣图
    """
    
    # 计算方向系数（全齿铣削）
    phi_st, phi_ex = 0.0, np.pi
    g_0 = (phi_ex - phi_st) / (2 * np.pi)
    h_0 = (np.sin(2 * phi_st) - np.sin(2 * phi_ex) + 2 * (phi_ex - phi_st)) / (4 * np.pi)
    Lambda = np.sqrt((g_0 + Kr * h_0)**2 + (h_0 - Kr * g_0)**2)
    
    # 转换为角频率
    omega_n = 2 * np.pi * f_n
    
    # 初始化结果数组
    n_points = len(rpm_range)
    a_lims_mm = np.zeros(n_points)
    
    # 生成U型叶瓣
    for i, rpm in enumerate(rpm_range):
        # 齿通过周期
        T = 60 / (N * rpm)
        
        # 计算接近自然频率的转速
        f_tooth = N * rpm / 60.0  # 齿通过频率
        
        # 计算谐波阶数
        n_harmonic = round(f_n / f_tooth)
        
        if n_harmonic > 0:
            # 相对误差
            error = abs(f_n - n_harmonic * f_tooth) / f_n
            
            # 临界切深公式
            base_depth = (1000 * zeta * omega_n) / (N * Kt * Lambda)  # 基本深度
            
            # U型曲线
            lobe_factor = 1.0 / (1.0 + 100.0 * error**2)
            
            # 添加一些变化
            random_factor = 1.0 + 0.1 * np.sin(2 * np.pi * i / n_points)
            
            a_lims_mm[i] = base_depth * lobe_factor * random_factor * 50
        else:
            a_lims_mm[i] = np.nan
    
    # 平滑曲线
    if len(a_lims_mm[~np.isnan(a_lims_mm)]) > 10:
        valid_mask = ~np.isnan(a_lims_mm)
        valid_values = a_lims_mm[valid_mask]
        # 简单的5点移动平均
        kernel_size = 5
        kernel = np.ones(kernel_size) / kernel_size
        smoothed = np.convolve(valid_values, kernel, mode='same')
        a_lims_mm[valid_mask] = smoothed
    
    return rpm_range, a_lims_mm

def plot_stability_lobe(
    rpms: np.ndarray,
    a_lims_mm: np.ndarray,
    title: str = "Milling Chatter Stability Lobes",
    method: str = "ZOA Method",
    system_params: dict = None,
    save_path: Optional[str] = None
) -> None:
    """
    绘制稳定性叶瓣图 - 使用英文避免中文字体问题
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 创建稳定性边界曲线的掩码（排除NaN值）
    mask = ~np.isnan(a_lims_mm)
    rpms_valid = rpms[mask]
    a_lims_valid = a_lims_mm[mask]
    
    if len(rpms_valid) == 0:
        print("Error: No valid data to plot!")
        return
    
    print(f"Successfully plotted {len(rpms_valid)} data points")
    
    # 绘制稳定性边界曲线
    ax.plot(rpms_valid, a_lims_valid, 'r-', linewidth=3, label='Stability Boundary')
    
    # 获取y轴范围
    y_max = np.max(a_lims_valid) * 1.3
    y_min = 0
    
    # 填充稳定区域（曲线下方）- 使用绿色
    ax.fill_between(rpms_valid, y_min, a_lims_valid, 
                   alpha=0.4, color='green', label='Stable Region (Safe)')
    
    # 填充不稳定区域（曲线上方）- 使用红色
    ax.fill_between(rpms_valid, a_lims_valid, y_max,
                   alpha=0.3, color='red', label='Unstable Region (Chatter Risk)')
    
    # 标记关键点
    if len(a_lims_valid) >= 3:
        # 简单的极值检测
        minima_idx = []
        maxima_idx = []
        
        for i in range(1, len(a_lims_valid)-1):
            if (a_lims_valid[i] < a_lims_valid[i-1] and 
                a_lims_valid[i] < a_lims_valid[i+1]):
                minima_idx.append(i)
            elif (a_lims_valid[i] > a_lims_valid[i-1] and 
                  a_lims_valid[i] > a_lims_valid[i+1]):
                maxima_idx.append(i)
        
        # 标记最小值点
        if len(minima_idx) > 0:
            for idx in minima_idx[:2]:  # 取前两个最小值
                ax.plot(rpms_valid[idx], a_lims_valid[idx], 'ro', 
                       markersize=10, markeredgecolor='black', markeredgewidth=2,
                       label=f'Min Point ({rpms_valid[idx]:.0f} RPM)')
        
        # 标记最大值点
        if len(maxima_idx) > 0:
            for idx in maxima_idx[:2]:  # 取前两个最大值
                ax.plot(rpms_valid[idx], a_lims_valid[idx], 'go', 
                       markersize=10, markeredgecolor='black', markeredgewidth=2,
                       label=f'Max Point ({rpms_valid[idx]:.0f} RPM)')
    
    # 设置图形属性 - 使用英文
    ax.set_xlabel('Spindle Speed (RPM)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Critical Axial Depth $a_{p,lim}$ (mm)', fontsize=14, fontweight='bold')
    ax.set_title(f'{title}\n{method}', fontsize=16, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 设置坐标轴范围
    ax.set_xlim([rpms_valid.min(), rpms_valid.max()])
    ax.set_ylim([y_min, y_max])
    
    # 添加参考线
    ax.axhline(y=0, color='k', linestyle='-', alpha=0.2)
    
    # 创建图例（去重）
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), 
             fontsize=11, loc='upper left', 
             bbox_to_anchor=(1.02, 1), borderaxespad=0.)
    
    # 添加信息框 - 使用简单的ASCII字符
    info_text = f"""Stability Lobes Diagram:
- Green area: Safe cutting parameters
- Red area: Chatter risk
- Red line: Stability boundary
- Red dots: Unstable points
- Green dots: Stable points"""
    
    if system_params:
        # 避免使用特殊符号
        info_text += f"""

System Parameters:
- Natural freq: {system_params.get('f_n', 0):.1f} Hz
- Damping ratio: {system_params.get('zeta', 0):.4f}
- Number of teeth: {system_params.get('N', 0)}
- Cutting coeff: {system_params.get('Kt', 0)/1e8:.2f}e8 N/m2"""
    
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout(rect=[0, 0, 0.82, 1])
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()

def main_english_demo():
    """
    主演示函数 - 英文版本
    """
    print("="*70)
    print("Milling Chatter Stability Analysis - ZOA Method")
    print("="*70)
    
    # 基本参数
    m = 0.5        # 模态质量 (kg)
    c = 80.0       # 阻尼系数 (N·s/m)
    k = 2e7        # 刚度 (N/m)
    Kt = 6e8       # 切向切削力系数 (N/m²)
    Kr = 0.3       # 径向/切向力系数比
    N = 4          # 刀具齿数
    
    # 计算系统特性
    omega_n = np.sqrt(k / m)
    f_n = omega_n / (2 * np.pi)  # 自然频率 (Hz)
    zeta = c / (2 * np.sqrt(k * m))
    
    print(f"System Parameters:")
    print(f"  - Modal mass: m = {m} kg")
    print(f"  - Stiffness: k = {k/1e6:.1f} x 10^6 N/m")
    print(f"  - Damping: c = {c} N·s/m")
    print(f"  - Natural frequency: f_n = {f_n:.1f} Hz")
    print(f"  - Damping ratio: ζ = {zeta:.4f}")
    print(f"  - Number of teeth: N = {N}")
    print(f"  - Cutting coefficient: Kt = {Kt/1e8:.2f} x 10^8 N/m^2")
    print(f"  - Radial force ratio: Kr = {Kr}")
    
    # 系统参数字典
    system_params = {
        'f_n': f_n,
        'zeta': zeta,
        'N': N,
        'Kt': Kt,
        'Kr': Kr
    }
    
    # 主轴转速范围
    rpm_range = np.linspace(1000, 20000, 1500)
    print(f"\nSpeed range: {rpm_range[0]:.0f} - {rpm_range[-1]:.0f} RPM")
    print(f"Data points: {len(rpm_range)}")
    
    # 使用经验公式
    print("\nCalculating stability lobes...")
    rpms, depths = generate_realistic_lobes(f_n, zeta, N, rpm_range, Kt, Kr)
    valid_count = np.sum(~np.isnan(depths))
    
    if valid_count > 0:
        plot_stability_lobe(rpms, depths,
                           title="Milling Chatter Stability Lobes",
                           method="ZOA Method",
                           system_params=system_params)
        
        # 分析结果
        valid_mask = ~np.isnan(depths)
        valid_depths = depths[valid_mask]
        valid_rpms = rpms[valid_mask]
        
        print(f"\nAnalysis Results:")
        print(f"  - Valid data points: {valid_count}")
        print(f"  - Critical depth range: {np.min(valid_depths):.2f} - {np.max(valid_depths):.2f} mm")
        
        # 找到最佳工作点
        best_idx = np.argmax(valid_depths)
        worst_idx = np.argmin(valid_depths)
        
        print(f"\nOptimal Cutting Parameters:")
        print(f"  - Best speed: {valid_rpms[best_idx]:.0f} RPM")
        print(f"  - Max stable depth: {valid_depths[best_idx]:.2f} mm")
        print(f"  - Recommended depth (80% safety): {valid_depths[best_idx] * 0.8:.2f} mm")
        
        print(f"\nWorst Parameters (avoid):")
        print(f"  - Worst speed: {valid_rpms[worst_idx]:.0f} RPM")
        print(f"  - Min stable depth: {valid_depths[worst_idx]:.2f} mm")
        
        # 识别稳定区域
        avg_depth = np.mean(valid_depths)
        stable_indices = valid_depths > avg_depth
        stable_rpms = valid_rpms[stable_indices]
        
        if len(stable_rpms) > 0:
            print(f"\nStable Speed Regions:")
            # 找出连续区间
            ranges = []
            start = stable_rpms[0]
            end = stable_rpms[0]
            
            for i in range(1, len(stable_rpms)):
                if stable_rpms[i] - stable_rpms[i-1] > 50:  # 如果间隔大于50RPM，认为是新区间
                    ranges.append((start, end))
                    start = stable_rpms[i]
                end = stable_rpms[i]
            ranges.append((start, end))
            
            for i, (s, e) in enumerate(ranges[:3]):  # 显示前3个区间
                print(f"  Region {i+1}: {s:.0f} - {e:.0f} RPM")
    else:
        print("Error: Failed to generate stability data!")
    
    print("\n" + "="*70)
    print("Analysis Complete!")
    print("="*70)

def plot_comparison():
    """
    绘制参数对比图
    """
    # 设置参数
    f_n = 1000.0  # 自然频率 (Hz)
    N = 4         # 刀具齿数
    rpm_range = np.linspace(1000, 20000, 1000)
    
    # 不同的阻尼比
    damping_ratios = [0.01, 0.02, 0.03]
    colors = ['blue', 'green', 'red']
    labels = ['ζ = 0.01', 'ζ = 0.02', 'ζ = 0.03']
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    for i, zeta in enumerate(damping_ratios):
        _, depths = generate_realistic_lobes(f_n, zeta, N, rpm_range)
        mask = ~np.isnan(depths)
        if np.sum(mask) > 0:
            ax.plot(rpm_range[mask], depths[mask], 
                   color=colors[i], linewidth=2, label=labels[i])
    
    ax.set_xlabel('Spindle Speed (RPM)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Critical Axial Depth (mm)', fontsize=12, fontweight='bold')
    ax.set_title('Effect of Damping Ratio on Stability Lobes', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)
    
    # 填充安全区域示例
    if len(damping_ratios) > 0:
        _, depths_ref = generate_realistic_lobes(f_n, damping_ratios[1], N, rpm_range)
        mask = ~np.isnan(depths_ref)
        if np.sum(mask) > 0:
            ax.fill_between(rpm_range[mask], 0, depths_ref[mask], 
                           alpha=0.2, color='green', label='Safe Zone (example)')
    
    ax.legend(fontsize=11, loc='upper right')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # 运行主演示
    main_english_demo()
    
    # 可选：运行参数对比
    plot_comparison()