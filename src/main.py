from os import path, mkdir, environ
import subprocess
from kipy import KiCad
from kipy.board_types import BoardRectangle, BoardPolygon
from kipy.proto.board.board_types_pb2 import BoardLayer
from kipy.util.units import to_mm
from gui import App, Error
from typing import Dict
import xml.etree.ElementTree as etree
import cairosvg
from PIL import Image
from time import strftime
import shlex


def generate_png(settings: Dict) -> None:
    print(settings)
    kicad = KiCad()
    settings_dir = kicad.get_plugin_settings_path("com_github_tobiglaser_kipng")
    if not path.exists(settings_dir):
        mkdir(settings_dir)

    board = kicad.get_board()
    cli_path = kicad.get_kicad_binary_path("kicad-cli")
    print("cli_path: ", cli_path)

    exe = ""
    if cli_path.__contains__("/app/") and not environ.get("FLATPAK_ID"):
        # kicad in flatpak, but script external
        exe = "flatpak run --command=kicad-cli org.kicad.KiCad"
    elif cli_path.__contains__("kicad-nightly"):
        # suspecting copr nightly version
        cli_path = kicad.get_kicad_binary_path("kicad-cli-nightly")
        print("cli_path: ", cli_path)
        exe = cli_path
    else:
        exe = cli_path
    print("exec: ", exe)

    project_path = board.document.project.path
    board_path = path.join(project_path, board.document.board_filename)
    project_name = board.document.project.name

    cache_dir = path.join(project_path, "temp-KiPNG")
    if not path.exists(cache_dir):
        mkdir(cache_dir)
        note = open(path.join(cache_dir, "you_may_delete_this_directory.txt"), 'w')
        note.close()
        


    layer_list = settings["layers"]
    for layer in layer_list:
        print(layer)
    mirror = "--mirror" if settings["flip"] else ""
    mode = "--mode-single" if settings["keep_order"] else "--mode-multi"
    output_path = path.join(cache_dir, "one_file.svg") if settings["keep_order"] else cache_dir
    
    cmd = [
        exe,
        'pcb', 'export', 'svg',
        '--output', output_path,
        '--layers', ','.join(layer_list),
        *([mirror] if mirror else []),
        mode,
        board_path
    ]
    print(shlex.join(cmd))
    subprocess.run(cmd, check=True)
    
    svgs = [output_path] if settings["keep_order"] else [path.join(output_path, f"{project_name}-{l.replace('.', '_')}.svg") for l in layer_list]
    print(svgs)
    big_svg = etree.Element("{http://www.w3.org/2000/svg}svg", {"xmlns": "http://www.w3.org/2000/svg"})
    if not settings["antialiasing"]:
        big_svg.set('shape-rendering', 'crispEdges')
    svgs.reverse() # plot from bottom to top
    for i, svg in enumerate(svgs):
        tree = etree.parse(svg)
        root = tree.getroot()
        group = etree.Element("g", id=f"layer_{i}")
        for child in list(root):
            group.append(child)
        big_svg.append(group)
        if not big_svg.attrib.get("width"):
            big_svg.attrib["width"]   = root.attrib["width"]
            big_svg.attrib["height"]  = root.attrib["height"]
            big_svg.attrib["viewBox"] = root.attrib["viewBox"]

    #etree.ElementTree(big_svg).write(path.join(cache_dir, "big_svg.svg"), "utf-8", True)

    xmin = settings["xmin"]
    xmax = settings["xmax"]
    if settings["flip"]:
        w = float(big_svg.attrib["width"].removesuffix("mm"))
        b = (w / 2) - xmin
        c = xmax - (w / 2)
        xmin = (w / 2) - c
        xmax = (w / 2) + b

    ymin = settings["ymin"]
    ymax = settings["ymax"]

    x_dist = xmax - xmin
    y_dist = ymax - ymin

    x_pixels = settings["x_res"]
    y_pixels = settings["y_res"]
    dpi = settings["dpi"]
    CAIRO_MAX = 32000

    x_steps = (x_pixels / CAIRO_MAX).__ceil__()
    y_steps = (y_pixels / CAIRO_MAX).__ceil__()
    
    x_stride = x_dist / x_steps
    y_stride = y_dist / y_steps
    
    root = big_svg

    if x_steps > 1 or y_steps > 1:
        for xi in range(x_steps):
            for yi in range(y_steps):
                root.set('width', str(x_stride))
                root.set('height', str(y_stride))
                root.set('viewBox', f"{xmin + (xi * x_stride)} {ymin + (yi * y_stride)} {x_stride} {y_stride}")

                cairosvg.svg2png(bytestring=etree.tostring(root),
                    write_to=path.join(cache_dir,f"{xi}{yi}.png"),
                    dpi=dpi,
                    output_width=x_pixels / x_steps,
                    output_height=y_pixels / y_steps,
                    negate_colors=False,
                    )
        final_image = Image.new("RGBA", (x_pixels, y_pixels))
        for xi in range(x_steps):
            for yi in range(y_steps):
                image = Image.open(path.join(cache_dir, f"{xi}{yi}.png"))
                final_image.paste(image, (xi * image.width, yi * image.height))
        
        final_image.save(path.join(project_path, f"{strftime('%Y%m%d-%H%M%S')}.png"))
    
    else:
        root.set('width', str(x_stride))
        root.set('height', str(y_stride))
        root.set('viewBox', f"{xmin} {ymin} {x_stride} {y_stride}")

        cairosvg.svg2png(bytestring=etree.tostring(root),
            write_to=path.join(project_path, f"{strftime('%Y%m%d-%H%M%S')}.png"),
            dpi=dpi,
            output_width=x_pixels,
            output_height=y_pixels,
            negate_colors=False,
            )





if __name__ == "__main__":
    board = KiCad().get_board()
    layers = board.get_enabled_layers()
    layer_strings = [board.get_layer_name(layer) for layer in layers]
    n_copper_layers = board.get_copper_layer_count()
    print(n_copper_layers)
    for layer in layer_strings:
        print(layer)
    selected_items = board.get_selection()
    print(selected_items)
    if len(selected_items) == 1 and type(selected_items[0]) == BoardRectangle:
        rect = selected_items[0]
        viewport_x1 = to_mm(rect.top_left.x)
        viewport_x2 = to_mm(rect.bottom_right.x)
        viewport_y1 = to_mm(rect.top_left.y)
        viewport_y2 = to_mm(rect.bottom_right.y)
    elif len(selected_items) == 1 and type(selected_items[0]) == BoardPolygon and selected_items[0].layer == BoardLayer.BL_Edge_Cuts:
        bb = selected_items[0].bounding_box()
        viewport_x1 = to_mm(bb.pos.x)
        viewport_x2 = to_mm(bb.pos.x + bb.size.x)
        viewport_y1 = to_mm(bb.pos.y)
        viewport_y2 = to_mm(bb.pos.y + bb.size.y)
    else:
        Error("\nPlease select a Rectangle or the PCB edge polygon as Viewport.\n\n(Ideally on a Layer you don't want to plot.)\nRotation is currently not supported.")
        exit()
    del board

    app = App(redirect=False)
    app.set_layers(layer_strings)
    app.set_copper_count(n_copper_layers)
    app.set_viewport(viewport_x2, viewport_x1, viewport_y2, viewport_y1)
    app.set_callback(generate_png)
    app.run()











