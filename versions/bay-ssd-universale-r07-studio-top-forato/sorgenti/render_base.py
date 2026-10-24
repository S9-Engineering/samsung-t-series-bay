from pathlib import Path
import json
import numpy as np
import trimesh
import vtk
from vtk.util.numpy_support import numpy_to_vtk
from PIL import Image,ImageDraw,ImageFont
import genera as g
ROOT=g.ROOT
BG="#f2f4f6";INK="#26343e";MUTED="#65737c"
FONT="/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD="/System/Library/Fonts/Supplemental/Arial Bold.ttf"
def font(size,bold=False):return ImageFont.truetype(BOLD if bold else FONT,size)

def actor(mesh,color,metal=False):
    points=vtk.vtkPoints();points.SetData(numpy_to_vtk(np.ascontiguousarray(mesh.vertices),deep=True))
    data=vtk.vtkPolyData();data.SetPoints(points);cells=vtk.vtkCellArray()
    for triangle in mesh.faces:
        cells.InsertNextCell(3)
        for i in triangle:cells.InsertCellPoint(int(i))
    data.SetPolys(cells)
    normals=vtk.vtkPolyDataNormals();normals.SetInputData(data)
    normals.SetFeatureAngle(28);normals.SplittingOn();normals.Update()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
    item=vtk.vtkActor();item.SetMapper(mapper)
    prop=item.GetProperty()
    prop.SetColor(*[int(color[i:i+2],16)/255 for i in (1,3,5)])
    prop.SetInterpolationToPhong();prop.SetAmbient(.28);prop.SetDiffuse(.7)
    prop.SetSpecular(.30 if not metal else .4);prop.SetSpecularPower(45)
    return item

def render(rows,palette,view,output):
    renderer=vtk.vtkRenderer();renderer.SetBackground(242/255,244/255,246/255)
    for row,mesh in rows:
        kind=row["kind"]
        color=palette["tetto"] if kind=="coperchio" else palette["scocca"]
        if kind in ("gabarit_ssd","silicone_commerciale","ferramenta_commerciale"):color=row["color"]
        item=actor(mesh,color,kind=="ferramenta_commerciale")
        if row.get("opacity") is not None:item.GetProperty().SetOpacity(row["opacity"])
        if row.get("color_override"):item.GetProperty().SetColor(*[int(row["color_override"][i:i+2],16)/255 for i in (1,3,5)])
        renderer.AddActor(item)
    camera=renderer.GetActiveCamera()
    target=view.get("target",(45,50.5,41))
    camera.SetFocalPoint(*target);camera.SetPosition(*view["camera"])
    camera.SetViewUp(*view.get("up",(0,0,1)));camera.ParallelProjectionOn()
    camera.SetParallelScale(view.get("scale",82))
    for pos,power in [((-170,-240,320),.75),((260,80,240),.45),((40,330,280),.3),
                       (view["camera"],.32)]:
        light=vtk.vtkLight();light.SetPosition(*pos);light.SetFocalPoint(*target)
        light.SetIntensity(power);renderer.AddLight(light)
    if view["camera"][2]<0:
        light=vtk.vtkLight();light.SetPosition(-90,-100,-220);light.SetFocalPoint(*target)
        light.SetIntensity(.75);renderer.AddLight(light)
    # Occlusione ambientale per leggere bordi, fuga del tetto e tasche poco profonde.
    passes=vtk.vtkRenderStepsPass();ao=vtk.vtkSSAOPass();ao.SetDelegatePass(passes)
    ao.SetRadius(3);ao.SetBias(.03);ao.SetKernelSize(96)
    renderer.SetPass(ao);renderer.UseFXAAOn()
    window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1080,850)
    window.SetMultiSamples(0);window.AddRenderer(renderer);renderer.ResetCameraClippingRange()
    window.Render()
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(window)
    capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff();capture.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(output))
    writer.SetInputConnection(capture.GetOutputPort());writer.Write();window.Finalize()
    return Image.open(output).convert("RGB")
