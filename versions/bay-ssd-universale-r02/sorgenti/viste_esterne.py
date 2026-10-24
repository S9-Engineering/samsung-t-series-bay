"""Tre proiezioni ortogonali della R02 chiusa, dalle mesh di assemblaggio."""
import hashlib
import json

from PIL import Image, ImageDraw
import trimesh
import vtk

from anteprime import ROOT, MAN, actor, font


BG = "#f2f4f6"
INK = "#24323d"
MUTED = "#63717a"
EXCLUDED = {"gabarit_cavo", "gabarit_connettore_non_rilevato"}
VIEWS = [
    dict(key="FRONTE", title="Davanti", position=(45, -300, 40.5),
         target=(45, 50.5, 40.5), up=(0, 0, 1),
         dimensions="90 mm larghezza  /  91 mm altezza", orientation=""),
    dict(key="LATO_DESTRO", title="Di lato", position=(350, 50.5, 40.5),
         target=(45, 50.5, 40.5), up=(0, 0, 1),
         dimensions="101 mm profondità  /  91 mm altezza",
         orientation="FRONTE                                               RETRO"),
    dict(key="ALTO", title="Dall’alto", position=(45, 50.5, 350),
         target=(45, 50.5, 40.5), up=(0, 1, 0),
         dimensions="90 mm larghezza  /  101 mm profondità",
         orientation="Retro in alto · fronte in basso"),
]


def render_view(view, meshes, output):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(242 / 255, 244 / 255, 246 / 255)
    for row, mesh in meshes:
        item = actor(mesh, row["color"])
        # Evita riflessi interpolati attraverso i grandi triangoli del tetto.
        item.GetProperty().SetInterpolationToFlat()
        item.GetProperty().SetAmbient(.32)
        item.GetProperty().SetDiffuse(.65)
        item.GetProperty().SetSpecular(.08)
        renderer.AddActor(item)
    camera = renderer.GetActiveCamera()
    camera.SetFocalPoint(*view["target"])
    camera.SetPosition(*view["position"])
    camera.SetViewUp(*view["up"])
    camera.ParallelProjectionOn()
    camera.SetParallelScale(62)
    for position, power in [((-100, -200, 400), .8),
                             ((250, 50, 300), .55),
                             ((30, 400, 240), .4)]:
        light = vtk.vtkLight()
        light.SetPosition(*position)
        light.SetFocalPoint(*view["target"])
        light.SetIntensity(power)
        renderer.AddLight(light)
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(840, 900)
    window.SetMultiSamples(8)
    window.AddRenderer(renderer)
    renderer.ResetCameraClippingRange()
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetInputBufferTypeToRGB()
    capture.ReadFrontBufferOff()
    capture.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(output))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()


def main():
    meshes = [(row, trimesh.load_mesh(ROOT / row["mesh"], process=False))
              for row in MAN["display"] if row["kind"] not in EXCLUDED]
    board = Image.new("RGB", (2700, 1330), BG)
    draw = ImageDraw.Draw(board)
    draw.text((60, 38), "R02 / scocca chiusa", font=font(50, True), fill=INK)
    draw.text((62, 108), "Tre viste del CAD attuale, alla stessa scala", font=font(27), fill=MUTED)
    outputs = []
    for i, view in enumerate(VIEWS):
        output = ROOT / "anteprime" / f"{7+i:02d}_R02_{view['key']}.png"
        render_view(view, meshes, output)
        raw = Image.open(output).convert("RGB")
        panel = Image.new("RGB", (900, 1130), BG)
        d = ImageDraw.Draw(panel)
        d.text((60, 25), view["title"], font=font(34, True), fill=INK)
        panel.paste(raw, (30, 95))
        d.text((60, 1005), view["dimensions"], font=font(24), fill=INK)
        if view["orientation"]:
            d.text((60, 1055), view["orientation"], font=font(20), fill=MUTED)
        panel.save(output)
        board.paste(panel, (i * 900, 185))
        outputs.append(str(output.relative_to(ROOT)))
    draw.text((62, 1280), "Coperchio e fissaggi montati · cavi e spine omessi · SSD nominali · colore indicativo · quote della scocca, piedini inclusi",
              font=font(22), fill=MUTED)
    overview = ROOT / "anteprime/06_R02_VISTE_ESTERNE.png"
    board.save(overview)
    outputs.append(str(overview.relative_to(ROOT)))
    report = dict(
        revision="R02", geometry_changed=False,
        projection="orthographic", parallel_scale_mm=62,
        views=VIEWS, hidden_kinds=sorted(EXCLUDED),
        manifest_sha256=hashlib.sha256((ROOT / "verifiche/manifest.json").read_bytes()).hexdigest(),
        meshes=[dict(name=row["name"], mesh=row["mesh"],
                     sha256=hashlib.sha256((ROOT / row["mesh"]).read_bytes()).hexdigest())
                for row, _ in meshes],
        outputs={name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                 for name in outputs},
    )
    (ROOT / "verifiche/viste_esterne.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps(dict(views=len(VIEWS), visible_solids=len(meshes), output=str(overview))))


if __name__ == "__main__":
    main()
