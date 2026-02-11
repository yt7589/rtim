// generate_test_surface.cpp
#include <BRepPrimAPI_MakeBox.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <Geom_BSplineSurface.hxx>
#include <TColgp_Array2OfPnt.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>
#include <STEPControl_Writer.hxx>
#include <Interface_Static.hxx>
#include <TopoDS_Face.hxx>
#include <gp_Pnt.hxx>
#include <iostream>

void CreateSaddleSurface() {
    std::cout << "Creating saddle surface..." << std::endl;
    
    // 创建双曲抛物面控制点 (4x4网格)
    TColgp_Array2OfPnt points(1, 4, 1, 4);
    
    for (int i = 1; i <= 4; i++) {
        for (int j = 1; j <= 4; j++) {
            double u = (i - 1) / 3.0;
            double v = (j - 1) / 3.0;
            
            // 双曲抛物面: z = x^2 - y^2
            double x = -1.0 + 2.0 * u;
            double y = -1.0 + 2.0 * v;
            double z = x * x - y * y;
            
            // 缩放并偏移
            points.SetValue(i, j, gp_Pnt(x * 50, y * 50, z * 20));
        }
    }
    
    // 节点向量
    TColStd_Array1OfReal knots(1, 2);
    knots.SetValue(1, 0.0);
    knots.SetValue(2, 1.0);
    
    // 多重性
    TColStd_Array1OfInteger mults(1, 2);
    mults.SetValue(1, 4);
    mults.SetValue(2, 4);
    
    // 创建B样条曲面
    Handle(Geom_BSplineSurface) surface = 
        new Geom_BSplineSurface(points, knots, knots, mults, mults, 3, 3);
    
    // 创建面
    TopoDS_Face face = BRepBuilderAPI_MakeFace(surface, 1e-6);
    
    // 写入STEP文件
    STEPControl_Writer writer;
    Interface_Static::SetCVal("write.step.schema", "AP203");
    
    writer.Transfer(face, STEPControl_AsIs);
    IFSelect_ReturnStatus status = writer.Write("saddle_surface.step");
    
    if (status == IFSelect_RetDone) {
        std::cout << "Successfully created saddle_surface.step" << std::endl;
    } else {
        std::cerr << "Failed to create STEP file" << std::endl;
    }
}

void CreateWaveSurface() {
    std::cout << "Creating wave surface..." << std::endl;
    
    // 创建正弦波曲面控制点 (6x6网格)
    TColgp_Array2OfPnt points(1, 6, 1, 6);
    
    for (int i = 1; i <= 6; i++) {
        for (int j = 1; j <= 6; j++) {
            double u = (i - 1) / 5.0;
            double v = (j - 1) / 5.0;
            
            double x = u * 100.0;
            double y = v * 100.0;
            double z = 10.0 * sin(2 * M_PI * u) * cos(2 * M_PI * v);
            
            points.SetValue(i, j, gp_Pnt(x, y, z));
        }
    }
    
    // 节点向量 (6个控制点，3次B样条需要10个节点)
    TColStd_Array1OfReal uknots(1, 4);
    TColStd_Array1OfReal vknots(1, 4);
    for (int i = 1; i <= 4; i++) {
        uknots.SetValue(i, (i-1) / 3.0);
        vknots.SetValue(i, (i-1) / 3.0);
    }
    
    // 多重性
    TColStd_Array1OfInteger umults(1, 4);
    TColStd_Array1OfInteger vmults(1, 4);
    for (int i = 1; i <= 4; i++) {
        umults.SetValue(i, 1);
        vmults.SetValue(i, 1);
    }
    umults.SetValue(1, 4);
    umults.SetValue(4, 4);
    vmults.SetValue(1, 4);
    vmults.SetValue(4, 4);
    
    // 创建B样条曲面
    Handle(Geom_BSplineSurface) surface = 
        new Geom_BSplineSurface(points, uknots, vknots, umults, vmults, 3, 3);
    
    // 创建面
    TopoDS_Face face = BRepBuilderAPI_MakeFace(surface, 1e-6);
    
    // 写入STEP文件
    STEPControl_Writer writer;
    Interface_Static::SetCVal("write.step.schema", "AP203");
    
    writer.Transfer(face, STEPControl_AsIs);
    IFSelect_ReturnStatus status = writer.Write("wave_surface.step");
    
    if (status == IFSelect_RetDone) {
        std::cout << "Successfully created wave_surface.step" << std::endl;
    } else {
        std::cerr << "Failed to create STEP file" << std::endl;
    }
}

void CreateSimpleTestSurface() {
    std::cout << "Creating simple test surface..." << std::endl;
    
    // 创建简单的3x3控制点网格
    TColgp_Array2OfPnt points(1, 3, 1, 3);
    
    // 第一行
    points.SetValue(1, 1, gp_Pnt(0, 0, 0));
    points.SetValue(1, 2, gp_Pnt(50, 0, 20));
    points.SetValue(1, 3, gp_Pnt(100, 0, 0));
    
    // 第二行
    points.SetValue(2, 1, gp_Pnt(0, 50, 15));
    points.SetValue(2, 2, gp_Pnt(50, 50, 40));  // 中心高点
    points.SetValue(2, 3, gp_Pnt(100, 50, 15));
    
    // 第三行
    points.SetValue(3, 1, gp_Pnt(0, 100, 0));
    points.SetValue(3, 2, gp_Pnt(50, 100, 20));
    points.SetValue(3, 3, gp_Pnt(100, 100, 0));
    
    // 节点向量
    TColStd_Array1OfReal knots(1, 2);
    knots.SetValue(1, 0.0);
    knots.SetValue(2, 1.0);
    
    // 多重性
    TColStd_Array1OfInteger mults(1, 2);
    mults.SetValue(1, 3);
    mults.SetValue(2, 3);
    
    // 创建B样条曲面（2次）
    Handle(Geom_BSplineSurface) surface = 
        new Geom_BSplineSurface(points, knots, knots, mults, mults, 2, 2);
    
    // 创建面
    TopoDS_Face face = BRepBuilderAPI_MakeFace(surface, 1e-6);
    
    // 写入STEP文件
    STEPControl_Writer writer;
    Interface_Static::SetCVal("write.step.schema", "AP203");
    
    writer.Transfer(face, STEPControl_AsIs);
    IFSelect_ReturnStatus status = writer.Write("test_surface.step");
    
    if (status == IFSelect_RetDone) {
        std::cout << "Successfully created test_surface.step" << std::endl;
        
        // 输出一些信息供测试
        std::cout << "\nSurface information:" << std::endl;
        std::cout << "  Control points: 3x3" << std::endl;
        std::cout << "  Degree: 2x2" << std::endl;
        std::cout << "  Range: X[0, 100], Y[0, 100], Z[0, 40]" << std::endl;
        std::cout << "\nExpected curvatures:" << std::endl;
        std::cout << "  Center (50,50): Maximum curvature (convex)" << std::endl;
        std::cout << "  Corners: Minimum curvature (saddle-like)" << std::endl;
    } else {
        std::cerr << "Failed to create STEP file" << std::endl;
    }
}

int main() {
    std::cout << "Generating test STEP files for geometry feature extraction..." << std::endl;
    std::cout << "======================================================" << std::endl;
    
    CreateSimpleTestSurface();
    std::cout << std::endl;
    
    CreateSaddleSurface();
    std::cout << std::endl;
    
    CreateWaveSurface();
    
    std::cout << "\n======================================================" << std::endl;
    std::cout << "All test surfaces generated successfully!" << std::endl;
    std::cout << "\nFiles created:" << std::endl;
    std::cout << "  1. test_surface.step - Simple 3x3 B-spline (good for initial testing)" << std::endl;
    std::cout << "  2. saddle_surface.step - Hyperbolic paraboloid" << std::endl;
    std::cout << "  3. wave_surface.step - Sinusoidal wave surface" << std::endl;
    
    return 0;
}