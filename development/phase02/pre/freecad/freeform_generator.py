# generate_with_freecad.py
import FreeCAD
import Part
import math

def create_freeform_surface():
    """创建复杂的自由曲面"""
    doc = FreeCAD.newDocument("FreeformSurface")
    
    # 创建B样条曲面
    points = []
    for i in range(5):
        row = []
        for j in range(5):
            x = i * 10.0
            y = j * 10.0
            # 创建一些高度变化
            z = math.sin(i * 0.5) * math.cos(j * 0.5) * 5.0
            row.append(FreeCAD.Vector(x, y, z))
        points.append(row)
    
    # 创建B样条曲面
    bspline_surface = Part.BSplineSurface()
    bspline_surface.buildFromPolesMultsKnots(
        points,
        [4, 1, 4],  # u方向多重性
        [4, 1, 4],  # v方向多重性
        [0.0, 0.5, 1.0],  # u方向节点
        [0.0, 0.5, 1.0],  # v方向节点
        False, False,  # 周期性
        3, 3  # 度数
    )
    
    # 创建面
    face = Part.makeFilledFace(bspline_surface.toShape().Edges)
    
    # 添加到文档
    part_obj = doc.addObject("Part::Feature", "FreeformSurface")
    part_obj.Shape = face
    
    # 导出STEP文件
    Part.export([part_obj], "freeform_surface.step")
    print("Generated freeform_surface.step")
    
    return doc

def create_sculpted_surface():
    """创建雕刻曲面"""
    doc = FreeCAD.newDocument("SculptedSurface")
    
    # 使用多个贝塞尔曲面片拼接
    patches = []
    
    # 创建4个曲面片
    for patch_i in range(2):
        for patch_j in range(2):
            patch_points = []
            for i in range(4):
                row = []
                for j in range(4):
                    x = patch_i * 50.0 + i * 20.0
                    y = patch_j * 50.0 + j * 20.0
                    # 复杂的z函数
                    z = (math.sin(x/10.0) * math.cos(y/10.0) + 
                         0.3 * math.sin(x/5.0) * math.sin(y/5.0)) * 8.0
                    row.append(FreeCAD.Vector(x, y, z))
                patch_points.append(row)
            
            bspline = Part.BSplineSurface()
            bspline.buildFromPolesMultsKnots(
                patch_points,
                [4, 1, 1, 4],
                [4, 1, 1, 4],
                [0.0, 1/3.0, 2/3.0, 1.0],
                [0.0, 1/3.0, 2/3.0, 1.0],
                False, False,
                3, 3
            )
            patches.append(bspline.toShape())
    
    # 合并所有曲面片
    compound = Part.makeCompound(patches)
    
    part_obj = doc.addObject("Part::Feature", "SculptedSurface")
    part_obj.Shape = compound
    
    # 导出STEP
    Part.export([part_obj], "sculpted_surface.step")
    print("Generated sculpted_surface.step")
    
    return doc

if __name__ == "__main__":
    create_freeform_surface()
    # create_sculpted_surface()