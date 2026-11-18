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

Tested on Linux and Windows. If you are able to provide feedback on macOS, please do so.

## Usage

1. Viewport selection:
   - By default, the Edge.Cuts shapes define the viewport.
   - Select any other shape or shapes to specify their combined bounding box as a viewport.
2. Open KiPNG
3. Select any layers you want to export by moving them to the right column. Some presets are available on the bottom.
4. Adjust the layer order with the buttons below the right column.
5. Specify a resolution in Dots per Inch.
6. Adjust the other settings to your liking:
   - Flip & Mirror: Makes it, so the picture is looking at the back of the board.
   - Use KiCad ordering: Forces KiCads native layer order like when exporting other formats.
   - Anti-Aliasing: Smooths jagged edges, creating a better looking picture.
7. Do it, click the big button.
8. Open the project folder to find the exported PNG named with the timestamp
   or double-click the status bar to open the image directly.  
   (Note that pictures are not shown in the file tree of the KiCad launcher.)
