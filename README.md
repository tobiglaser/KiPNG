# KiPNG - Export PNGs right from KiCads PCB-Editor

This KiCad Plugin uses KiCads built in SVG export functionality
and combines it with `cairosvg` rasterized it into a `.png`-Image.
So the output is visually similar to the SVGs, but converted hastle free in one click.
Settings include
  - the resolution in dots per inch (DPI),
  - whether edges should have a clear cut or be smoothed over, creating a gradient,
  - flipping the PCB to look at it from behind and of course
  - which layers to export and in what order.

Since the SVG export targets the file, the output will only include saved changes.

Very large resolutions may currently overwhelm your RAM.
