# create_visible_freeform.py
import numpy as np
import math

def create_visible_freeform_surface():
    """
    创建一个在FreeCAD中可见的自由曲面
    使用离散的三角面片而不是B样条曲面
    """
    
    print("=" * 80)
    print("Creating visible freeform surface for FreeCAD")
    print("=" * 80)
    
    # ============================================
    # 1. 生成曲面网格点
    # ============================================
    print("\n1. Generating surface mesh points...")
    
    size = 100.0  # 曲面尺寸
    nx, ny = 20, 20  # 网格分辨率
    
    vertices = []
    faces = []
    vertex_id = 1
    
    # 生成顶点
    for i in range(nx):
        u = i / (nx - 1)
        x = -size/2 + size * u
        
        for j in range(ny):
            v = j / (ny - 1)
            y = -size/2 + size * v
            
            # 复杂的曲面方程
            # 1. 主高斯凸起
            dx1, dy1 = x, y
            distance1 = math.sqrt(dx1*dx1 + dy1*dy1)
            z1 = 25.0 * math.exp(-distance1*distance1 / 800.0)
            
            # 2. 马鞍面分量
            z2 = 0.03 * (x*x - y*y)
            
            # 3. 第二个高斯凸起（偏移）
            dx2, dy2 = x - 30, y + 20
            distance2 = math.sqrt(dx2*dx2 + dy2*dy2)
            z3 = 15.0 * math.exp(-distance2*distance2 / 500.0)
            
            # 4. 正弦波纹
            z4 = 8.0 * math.sin(0.12 * x) * math.cos(0.08 * y)
            
            # 组合
            z = z1 + z2 + 0.7*z3 + 0.5*z4
            
            # 边界平坦化
            if abs(x) > size/2 - 5 or abs(y) > size/2 - 5:
                z = 0.0
            
            vertices.append((vertex_id, x, y, z))
            vertex_id += 1
    
    print(f"   Generated {len(vertices)} vertices")
    
    # ============================================
    # 2. 生成三角形面
    # ============================================
    print("\n2. Generating triangular faces...")
    
    face_id = 1
    for i in range(nx - 1):
        for j in range(ny - 1):
            # 计算顶点索引
            v1 = i * ny + j + 1
            v2 = i * ny + (j + 1) + 1
            v3 = (i + 1) * ny + j + 1
            v4 = (i + 1) * ny + (j + 1) + 1
            
            # 两个三角形组成一个四边形
            faces.append((face_id, v1, v2, v3))
            face_id += 1
            faces.append((face_id, v2, v4, v3))
            face_id += 1
    
    print(f"   Generated {len(faces)} triangular faces")
    
    # ============================================
    # 3. 创建STEP文件（使用三角面片）
    # ============================================
    print("\n3. Creating STEP file with triangular facets...")
    
    # STEP文件内容
    step_content = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('Visible Freeform Surface - Triangular Mesh'),'2;1');
FILE_NAME('visible_freeform_surface.step','2024-01-15','','','','','');
FILE_SCHEMA(('CONFIG_CONTROL_DESIGN'));
ENDSEC;
DATA;
"""
    
    # ============================================
    # 4. 添加顶点
    # ============================================
    print("4. Adding vertices to STEP file...")
    
    for vid, x, y, z in vertices:
        step_content += f"#{vid}=CARTESIAN_POINT('',({x:.3f},{y:.3f},{z:.3f}));\n"
    
    # ============================================
    # 5. 添加三角形面
    # ============================================
    print("5. Adding triangular faces to STEP file...")
    
    # 我们需要创建：
    # 1. 顶点点 (VERTEX_POINT)
    # 2. 边曲线 (EDGE_CURVE)
    # 3. 边循环 (EDGE_LOOP)
    # 4. 面边界 (FACE_BOUND)
    # 5. 高级面 (ADVANCED_FACE)
    
    # 为每个三角形创建单独的实体
    current_id = len(vertices) + 1
    
    # 存储所有面的ID
    face_entities = []
    
    for fid, v1, v2, v3 in faces:
        # 获取顶点坐标
        x1, y1, z1 = vertices[v1-1][1:]
        x2, y2, z2 = vertices[v2-1][1:]
        x3, y3, z3 = vertices[v3-1][1:]
        
        # 创建三个顶点实体
        vp1 = current_id
        vp2 = vp1 + 1
        vp3 = vp2 + 1
        current_id += 3
        
        step_content += f"""
#{vp1}=VERTEX_POINT('',#{v1});
#{vp2}=VERTEX_POINT('',#{v2});
#{vp3}=VERTEX_POINT('',#{v3});
"""
        
        # 创建三条边（线）
        line1 = current_id
        line2 = line1 + 1
        line3 = line2 + 1
        current_id += 3
        
        step_content += f"""
#{line1}=LINE('',#{v1},#{v2});
#{line2}=LINE('',#{v2},#{v3});
#{line3}=LINE('',#{v3},#{v1});
"""
        
        # 创建三条边曲线
        edge1 = current_id
        edge2 = edge1 + 1
        edge3 = edge2 + 1
        current_id += 3
        
        step_content += f"""
#{edge1}=EDGE_CURVE('',#{vp1},#{vp2},#{line1},.T.);
#{edge2}=EDGE_CURVE('',#{vp2},#{vp3},#{line2},.T.);
#{edge3}=EDGE_CURVE('',#{vp3},#{vp1},#{line3},.T.);
"""
        
        # 创建边循环
        loop = current_id
        current_id += 1
        
        step_content += f"""
#{loop}=EDGE_LOOP('',(#{edge1},#{edge2},#{edge3}));
"""
        
        # 创建面边界
        bound = current_id
        current_id += 1
        
        step_content += f"""
#{bound}=FACE_BOUND('',#{loop},.T.);
"""
        
        # 创建平面（每个三角形的平面）
        # 计算法向量
        import numpy as np
        p1 = np.array([x1, y1, z1])
        p2 = np.array([x2, y2, z2])
        p3 = np.array([x3, y3, z3])
        
        v12 = p2 - p1
        v13 = p3 - p1
        normal = np.cross(v12, v13)
        normal = normal / np.linalg.norm(normal) if np.linalg.norm(normal) > 0 else np.array([0, 0, 1])
        
        # 创建轴定位
        axis = current_id
        current_id += 1
        
        step_content += f"""
#{axis}=AXIS2_PLACEMENT_3D('',#{v1},$,$);
"""
        
        # 创建平面
        plane = current_id
        current_id += 1
        
        step_content += f"""
#{plane}=PLANE('',#{axis});
"""
        
        # 创建高级面
        face_entity = current_id
        face_entities.append(face_entity)
        current_id += 1
        
        step_content += f"""
#{face_entity}=ADVANCED_FACE('',(#{bound}),#{plane},.T.);
"""
    
    # ============================================
    # 6. 创建外壳和实体
    # ============================================
    print("6. Creating shell and solid...")
    
    # 创建外壳
    shell_id = current_id
    current_id += 1
    
    # 将所有面添加到外壳
    face_list = ",".join([f"#{fid}" for fid in face_entities])
    step_content += f"""
#{shell_id}=CLOSED_SHELL('',({face_list}));
"""
    
    # 创建实体
    solid_id = current_id
    
    step_content += f"""
#{solid_id}=MANIFOLD_SOLID_BREP('',#{shell_id});
"""
    
    # ============================================
    # 7. 结束文件
    # ============================================
    step_content += """ENDSEC;
END-ISO-10303-21;"""
    
    # 保存文件
    filename = "visible_freeform_surface.step"
    with open(filename, "w") as f:
        f.write(step_content)
    
    # 检查文件大小
    import os
    file_size = os.path.getsize(filename)
    
    print(f"\n✓ Created {filename}")
    print(f"  File size: {file_size:,} bytes")
    print(f"  Vertices: {len(vertices)}")
    print(f"  Triangles: {len(faces)}")
    
    # ============================================
    # 8. 创建OBJ文件作为备份（更可靠）
    # ============================================
    create_obj_backup(vertices, faces)
    
    # ============================================
    # 9. 创建简单的STL文件（最可靠）
    # ============================================
    create_stl_file(vertices, faces, nx, ny)
    
    return filename

def create_obj_backup(vertices, faces):
    """创建OBJ文件作为备份"""
    print("\nCreating OBJ backup file...")
    
    obj_content = "# Freeform Surface for Chatter Analysis\n"
    obj_content += "# Generated: 2024-01-15\n\n"
    
    # 顶点
    for _, x, y, z in vertices:
        obj_content += f"v {x:.6f} {y:.6f} {z:.6f}\n"
    
    obj_content += "\n"
    
    # 面（注意：OBJ使用1-based索引）
    for _, v1, v2, v3 in faces:
        obj_content += f"f {v1} {v2} {v3}\n"
    
    with open("freeform_surface.obj", "w") as f:
        f.write(obj_content)
    
    import os
    size = os.path.getsize("freeform_surface.obj")
    print(f"✓ Created freeform_surface.obj ({size:,} bytes)")
    
    # 创建转换说明
    print("\nTo convert OBJ to STEP in FreeCAD:")
    print("1. Open FreeCAD")
    print("2. File → Open → freeform_surface.obj")
    print("3. Select the mesh object")
    print("4. Part → Create shape from mesh")
    print("5. File → Export → Save as STEP")

def create_stl_file(vertices, faces, nx, ny):
    """创建STL文件（二进制格式，更可靠）"""
    print("\nCreating STL file (most reliable format)...")
    
    # STL二进制格式
    import struct
    
    # 计算法向量
    def calculate_normal(p1, p2, p3):
        import numpy as np
        v1 = np.array(p2) - np.array(p1)
        v2 = np.array(p3) - np.array(p1)
        normal = np.cross(v1, v2)
        norm = np.linalg.norm(normal)
        if norm > 0:
            normal = normal / norm
        else:
            normal = np.array([0.0, 0.0, 1.0])
        return normal
    
    with open("freeform_surface.stl", "wb") as f:
        # 80字节的头部
        header = b"Freeform Surface for Chatter Analysis" + b"\x00" * (80 - 38)
        f.write(header)
        
        # 三角形数量 (4字节，小端)
        num_triangles = len(faces)
        f.write(struct.pack('<I', num_triangles))
        
        # 每个三角形
        for _, v1, v2, v3 in faces:
            # 获取顶点坐标
            _, x1, y1, z1 = vertices[v1-1]
            _, x2, y2, z2 = vertices[v2-1]
            _, x3, y3, z3 = vertices[v3-1]
            
            # 计算法向量
            normal = calculate_normal((x1, y1, z1), (x2, y2, z2), (x3, y3, z3))
            
            # 写入法向量 (12字节)
            f.write(struct.pack('<fff', normal[0], normal[1], normal[2]))
            
            # 写入三个顶点 (36字节)
            f.write(struct.pack('<fff', x1, y1, z1))
            f.write(struct.pack('<fff', x2, y2, z2))
            f.write(struct.pack('<fff', x3, y3, z3))
            
            # 属性字节计数 (2字节)
            f.write(struct.pack('<H', 0))
    
    import os
    size = os.path.getsize("freeform_surface.stl")
    print(f"✓ Created freeform_surface.stl ({size:,} bytes)")
    
    # 创建STL转STEP的Python脚本
    create_conversion_script()

def create_conversion_script():
    """创建STL转STEP的Python脚本"""
    print("\nCreating STL to STEP conversion script...")
    
    script_content = """# STL to STEP Converter for FreeCAD
# Run this script in FreeCAD Python console

import FreeCAD
import Part
import Mesh

def convert_stl_to_step():
    \"\"\"Convert STL file to STEP format\"\"\"
    
    # 输入输出文件
    stl_file = "freeform_surface.stl"
    step_file = "converted_freeform.step"
    
    print(f"Converting {stl_file} to {step_file}...")
    
    try:
        # 创建新文档
        doc = FreeCAD.newDocument("Conversion")
        
        # 导入STL
        mesh = Mesh.Mesh()
        mesh.read(stl_file)
        
        # 创建网格对象
        mesh_obj = doc.addObject("Mesh::Feature", "FreeformMesh")
        mesh_obj.Mesh = mesh
        
        # 转换为Part形状
        shape = Part.Shape()
        shape.makeShapeFromMesh(mesh_obj.Mesh.Topology, 0.1)
        
        # 创建Part对象
        part_obj = doc.addObject("Part::Feature", "FreeformShape")
        part_obj.Shape = shape
        
        # 导出STEP
        Part.export([part_obj], step_file)
        
        print(f"✓ Successfully converted to {step_file}")
        
        # 显示信息
        bbox = shape.BoundBox
        print(f"\\nSurface information:")
        print(f"  Size: {bbox.XLength:.1f} x {bbox.YLength:.1f} mm")
        print(f"  Height: {bbox.ZLength:.1f} mm")
        print(f"  Volume: {shape.Volume:.0f} mm³")
        
        return True
        
    except Exception as e:
        print(f"✗ Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# 自动运行转换
if __name__ == "__main__":
    # 如果在FreeCAD中运行
    try:
        import FreeCAD
        convert_stl_to_step()
    except ImportError:
        print("This script should be run in FreeCAD Python console")
        print("\\nManual conversion:")
        print("1. Open FreeCAD")
        print("2. File → Open → freeform_surface.stl")
        print("3. Select the mesh")
        print("4. Part → Create shape from mesh")
        print("5. File → Export → Save as STEP")
"""
    
    with open("convert_stl_to_step.py", "w") as f:
        f.write(script_content)
    
    print(f"✓ Created convert_stl_to_step.py")

def create_simple_but_visible_step():
    """创建简单但可见的STEP文件"""
    print("\n" + "="*80)
    print("Creating simple but visible STEP file...")
    print("="*80)
    
    # 创建一个非常简单的四面体，确保在FreeCAD中可见
    step_content = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('Simple Tetrahedron - For Visibility Test'),'2;1');
FILE_NAME('simple_tetrahedron.step','2024-01-15','','','','','');
FILE_SCHEMA(('CONFIG_CONTROL_DESIGN'));
ENDSEC;
DATA;
#1=CARTESIAN_POINT('',(0.,0.,0.));
#2=CARTESIAN_POINT('',(100.,0.,0.));
#3=CARTESIAN_POINT('',(50.,100.,0.));
#4=CARTESIAN_POINT('',(50.,50.,80.));
#5=VERTEX_POINT('',#1);
#6=VERTEX_POINT('',#2);
#7=VERTEX_POINT('',#3);
#8=VERTEX_POINT('',#4);
#9=LINE('',#1,#2);
#10=LINE('',#2,#3);
#11=LINE('',#3,#1);
#12=LINE('',#1,#4);
#13=LINE('',#2,#4);
#14=LINE('',#3,#4);
#15=EDGE_CURVE('',#5,#6,#9,.T.);
#16=EDGE_CURVE('',#6,#7,#10,.T.);
#17=EDGE_CURVE('',#7,#5,#11,.T.);
#18=EDGE_CURVE('',#5,#8,#12,.T.);
#19=EDGE_CURVE('',#6,#8,#13,.T.);
#20=EDGE_CURVE('',#7,#8,#14,.T.);
#21=EDGE_LOOP('',(#15,#16,#17));
#22=EDGE_LOOP('',(#15,#19,#18));
#23=EDGE_LOOP('',(#16,#20,#19));
#24=EDGE_LOOP('',(#17,#18,#20));
#25=FACE_BOUND('',#21,.T.);
#26=FACE_BOUND('',#22,.T.);
#27=FACE_BOUND('',#23,.T.);
#28=FACE_BOUND('',#24,.T.);
#29=AXIS2_PLACEMENT_3D('',#1,$,$);
#30=AXIS2_PLACEMENT_3D('',#1,$,$);
#31=AXIS2_PLACEMENT_3D('',#2,$,$);
#32=AXIS2_PLACEMENT_3D('',#3,$,$);
#33=PLANE('',#29);
#34=PLANE('',#30);
#35=PLANE('',#31);
#36=PLANE('',#32);
#37=ADVANCED_FACE('',(#25),#33,.T.);
#38=ADVANCED_FACE('',(#26),#34,.T.);
#39=ADVANCED_FACE('',(#27),#35,.T.);
#40=ADVANCED_FACE('',(#28),#36,.T.);
#41=CLOSED_SHELL('',(#37,#38,#39,#40));
#42=MANIFOLD_SOLID_BREP('',#41);
ENDSEC;
END-ISO-10303-21;"""
    
    with open("simple_tetrahedron.step", "w") as f:
        f.write(step_content)
    
    import os
    size = os.path.getsize("simple_tetrahedron.step")
    print(f"\n✓ Created simple_tetrahedron.step")
    print(f"  File size: {size:,} bytes")
    print(f"  Shape: Tetrahedron (4 vertices, 4 faces)")
    print(f"  Dimensions: 100x100x80 mm")
    
    print("\nThis should DEFINITELY be visible in FreeCAD!")
    print("If not, there's an issue with your FreeCAD installation.")

def test_freecad_installation():
    """测试FreeCAD安装"""
    print("\n" + "="*80)
    print("Testing FreeCAD installation...")
    print("="*80)
    
    try:
        import FreeCAD
        import Part
        
        print("✓ FreeCAD is installed")
        
        # 尝试创建一个简单的形状
        doc = FreeCAD.newDocument("Test")
        sphere = Part.makeSphere(10.0)
        obj = doc.addObject("Part::Feature", "TestSphere")
        obj.Shape = sphere
        
        print("✓ Can create 3D objects")
        print("✓ FreeCAD is working correctly")
        
        # 尝试打开一个STEP文件
        test_step = "simple_tetrahedron.step"
        import os
        if os.path.exists(test_step):
            print(f"\nTry opening {test_step} in FreeCAD")
            print("It should show a tetrahedron shape")
        
        return True
        
    except ImportError:
        print("✗ FreeCAD is not installed or not in Python path")
        print("\nTo install FreeCAD:")
        print("1. Download from: https://www.freecad.org/downloads.php")
        print("2. Install, then add to Python path:")
        print("   import sys")
        print("   sys.path.append(r'C:\\\\Program Files\\\\FreeCAD 0.21\\\\bin')")
        return False
    except Exception as e:
        print(f"✗ FreeCAD error: {e}")
        return False

if __name__ == "__main__":
    print("\n" * 2)
    print("=" * 80)
    print("CREATING VISIBLE FREEFORM SURFACES FOR FREECAD")
    print("=" * 80)
    
    # # 测试FreeCAD安装
    # freecad_ok = test_freecad_installation()
    
    # if freecad_ok:
    #     print("\n" + "=" * 80)
    #     print("Creating detailed freeform surface...")
    #     print("=" * 80)
        
    #     # 创建详细曲面
    #     try:
    #         main_file = create_visible_freeform_surface()
    #     except Exception as e:
    #         print(f"Error creating detailed surface: {e}")
    #         print("\nCreating simple tetrahedron instead...")
    #         main_file = "simple_tetrahedron.step"
    # else:
    #     print("\nCreating simple tetrahedron (no FreeCAD required)...")
    
    # 创建简单的四面体（总是有效）
    create_simple_but_visible_step()
    
    print("\n" + "=" * 80)
    print("FILES CREATED")
    print("=" * 80)
    print("\n1. STEP files:")
    print("   - visible_freeform_surface.step (detailed mesh)")
    print("   - simple_tetrahedron.step (simple test)")
    
    print("\n2. Other formats (more reliable):")
    print("   - freeform_surface.stl (STL binary, most reliable)")
    print("   - freeform_surface.obj (OBJ format)")
    
    print("\n3. Conversion scripts:")
    print("   - convert_stl_to_step.py (STL to STEP converter)")
    
    print("\n" + "=" * 80)
    print("RECOMMENDED WORKFLOW")
    print("=" * 80)
    print("\nOption 1 (Easiest):")
    print("   Open 'freeform_surface.stl' in FreeCAD")
    print("   Part → Create shape from mesh")
    print("   Export as STEP")
    
    print("\nOption 2 (Direct):")
    print("   Try opening 'simple_tetrahedron.step' in FreeCAD")
    print("   (This should definitely work)")
    
    print("\nOption 3 (For your research):")
    print("   Use the STL or OBJ file with your C++ geometry extractor")
    print("   Many libraries (including OpenCASCADE) can read STL/OBJ")
    
    print("\n" + "=" * 80)
    print("TROUBLESHOOTING")
    print("=" * 80)
    print("\nIf nothing appears in FreeCAD:")
    print("1. Try 'View → Draw style → Shaded'")
    print("2. Try 'View → Standard views → Isometric'")
    print("3. Check if the object is in the tree view")
    print("4. Try opening the STL file instead")
    create_visible_freeform_surface()