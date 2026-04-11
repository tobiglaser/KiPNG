import wx
from math import ceil
from os import path
from typing import Callable, Dict


def Error(message: str):
    app = wx.App()
    dialog = wx.MessageDialog(None, message, caption="Error")
    dialog.ShowModal()
    app.MainLoop()


class App(wx.App):
    def OnInit(self):
        self.frame = wx.Frame(parent=None, title='KiPNG')
        
        script_dir = path.dirname(path.abspath(__file__))
        png_path = path.join(script_dir, 'icons', 'icon.png')
        if not path.exists(png_path):
            png_path = path.join(script_dir, '..', 'resources', 'icon.png')

        bmp = wx.Bitmap(png_path, wx.BITMAP_TYPE_PNG)
        icon = wx.Icon(bmp)

        self.frame.SetIcon(icon)

        self.panel = wx.Panel(self.frame)

        self.layer_list = wx.ListBox(self.panel, choices=[])
        self.frontside_button = wx.Button(self.panel, label="Front")
        self.frontside_button.Bind(wx.EVT_BUTTON, self.preset_front)
        self.backside_button = wx.Button(self.panel, label="Back")
        self.backside_button.Bind(wx.EVT_BUTTON, self.preset_back)
        self.copper_button = wx.Button(self.panel, label="Copper")
        self.copper_button.Bind(wx.EVT_BUTTON, self.preset_copper)

        preset_sizer = wx.BoxSizer(wx.HORIZONTAL)
        preset_sizer.Add(self.frontside_button, 1)
        preset_sizer.AddSpacer(10)
        preset_sizer.Add(self.backside_button, 1)
        preset_sizer.AddSpacer(10)
        preset_sizer.Add(self.copper_button, 1)
        
        sel_list_sizer = wx.BoxSizer(wx.VERTICAL)
        sel_list_sizer.Add(self.layer_list, 1, wx.EXPAND | wx.ALL, 10)
        sel_list_sizer.Add(preset_sizer, 0, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, 10)
        
        left_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self.panel, "Layer Selection:")
        left_sizer.Add(sel_list_sizer, 1, wx.EXPAND)
        addsub_sizer = wx.BoxSizer(wx.VERTICAL)
        addsub_sizer.AddStretchSpacer(4)
        right_button = wx.Button(self.panel, label="->")
        right_button.Bind(wx.EVT_BUTTON, self.on_right)
        addsub_sizer.Add(right_button)
        addsub_sizer.AddStretchSpacer(1)
        left_button = wx.Button(self.panel, label="<-")
        left_button.Bind(wx.EVT_BUTTON, self.on_left)
        addsub_sizer.Add(left_button)
        addsub_sizer.AddStretchSpacer(4)
        left_sizer.Add(addsub_sizer, 0, wx.EXPAND)

        lr_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lr_sizer.Add(left_sizer, 2, wx.EXPAND | wx.ALL, 5)

        self.plot_list = wx.ListBox(self.panel, choices=[])
        plot_sizer = wx.BoxSizer(wx.VERTICAL)
        plot_sizer.Add(self.plot_list, 1, wx.EXPAND | wx.ALL, 10)
        ud_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.down_button = wx.Button(self.panel, label="Down")
        self.down_button.Bind(wx.EVT_BUTTON, self.on_down)
        self.up_button = wx.Button(self.panel, label="Up")
        self.up_button.Bind(wx.EVT_BUTTON, self.on_up)
        ud_sizer.Add(self.up_button, 1)
        ud_sizer.AddSpacer(10)
        ud_sizer.Add(self.down_button, 1)
        plot_sizer.Add(ud_sizer, 0, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, 10)
        left_sizer.Add(plot_sizer, 1, wx.EXPAND)

        right_sizer = wx.StaticBoxSizer(wx.VERTICAL, self.panel, "Configuration:")
        dpi_label = wx.StaticText(self.panel, label="DPI:")
        right_sizer.Add(dpi_label, 0, wx.ALL, 10)
        self.dpi_box = wx.SpinCtrl(self.panel, initial=300, min=1, max=10000)
        self.dpi_box.Bind(wx.EVT_SPINCTRL, self.on_dpi_change)
        right_sizer.Add(self.dpi_box, 0, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, 10)

        result_label = wx.StaticText(self.panel, label="Resulting Resolution:")
        right_sizer.Add(result_label, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 10)
        self.resolution_label_xy = wx.StaticText(self.panel, label="\t0x0")
        right_sizer.Add(self.resolution_label_xy, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 10)
        self.resolution_label_mp = wx.StaticText(self.panel, label="\t0x0")
        right_sizer.Add(self.resolution_label_mp, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 10)

        self.flip_flag = wx.CheckBox(self.panel, label="Flip && Mirror")
        self.flip_flag.Value = False
        self.flip_flag.Bind(wx.EVT_CHECKBOX, self.on_flip_flag)
        right_sizer.Add(self.flip_flag, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 10)
        self.order_flag = wx.CheckBox(self.panel, label="Use KiCad ordering")
        self.order_flag.Value = True
        self.order_flag.Bind(wx.EVT_CHECKBOX, self.on_order_flag)
        right_sizer.Add(self.order_flag, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 10)
        self.aa_flag = wx.CheckBox(self.panel, label="Anti-Aliasing")
        self.aa_flag.Value = False
        right_sizer.Add(self.aa_flag, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 10)

        right_sizer.AddStretchSpacer(1)

        self.shoot_button = wx.Button(self.panel, label="📸 Generate PNG")
        self.shoot_button.Bind(wx.EVT_BUTTON, self.on_shoot)
        right_sizer.Add(self.shoot_button, 1, wx.EXPAND | wx.ALL, 10)

        lr_sizer.Add(right_sizer, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizer(lr_sizer)

        self.frame.SetSizeHints(wx.Size(900, 400))

        return True

    def run(self):
        self.on_dpi_change(None)
        self.on_order_flag(None)
        self.frame.Show()
        self.MainLoop()
        pass

    def set_layers(self, layers: list) -> None:
        self.layer_list.Set(layers)
        self.original_list = layers

    def set_copper_count(self, n_layers: int = 2) -> None:
        self.n_copper_layers = n_layers

    def set_viewport(self, xmax, xmin, ymax, ymin) -> None:
        self.x_min = xmin
        self.x_max = xmax
        self.y_min = ymin
        self.y_max = ymax
        self.x = xmax - xmin
        self.y = ymax - ymin

    def reset_plot_list(self):
        while self.plot_list.GetCount():
            self.plot_list.SetSelection(0)
            self.on_left(None)

    def set_plot_list(self, layers: list):
        for layer in layers:
            for i, name in enumerate(self.layer_list.GetStrings()):
                if name == layer:
                    self.layer_list.SetSelection(i)
                    self.on_right(None)

    def preset_front(self, event) -> None:
        self.reset_plot_list()
        self.flip_flag.Value = False
        self.on_flip_flag(None)
        new_layers = [
            "Edge.Cuts",
            "F.Paste",
            "F.Mask",
            "F.Silkscreen",
            "F.Cu",
        ]
        copper = self.n_copper_layers
        for i in range (1, copper // 2):
            new_layers.append(f"In{i}.Cu")
        print(new_layers)
        self.set_plot_list(new_layers)

    def preset_back(self, event) -> None:
        self.reset_plot_list()
        self.flip_flag.Value = True
        self.on_flip_flag(None)
        new_layers = [
            "Edge.Cuts",
            "B.Paste",
            "B.Mask",
            "B.Silkscreen",
            "B.Cu",
        ]
        copper = self.n_copper_layers
        for i in range(copper // 2, copper - 1):
            new_layers.append(f"In{i}.Cu")
        print(new_layers)
        self.set_plot_list(new_layers)

    def preset_copper(self, event) -> None:
        self.reset_plot_list()
        self.flip_flag.Value = False
        self.on_flip_flag(None)
        new_layers = ["F.Cu"]
        copper = self.n_copper_layers
        for i in range (1, copper - 1):
            new_layers.append(f"In{i}.Cu")
        new_layers.append("B.Cu")
        print(new_layers)
        self.set_plot_list(new_layers)
        

    def on_right(self, event) -> None:
        all = self.layer_list.GetStrings()
        selections = self.layer_list.GetSelections()
        
        new = self.plot_list.GetStrings()
        for item in selections:
            new.append(all[item])
        self.plot_list.Set(new)
        
        for item in reversed(selections):
            all.remove(all[item])
        self.layer_list.Set(all)

    def on_left(self, event) -> None:
        all = self.plot_list.GetStrings()
        selections = self.plot_list.GetSelections()

        new = self.layer_list.GetStrings()
        for item in selections:
            new.append(all[item])
        
        def find_index(layer: str) -> int:
            for i, entry in enumerate(self.original_list):
                if entry == layer:
                    return i
            return -1
        new.sort(key=find_index)
        self.layer_list.Set(new)
        
        for item in reversed(selections):
            all.remove(all[item])
        self.plot_list.Set(all)

    def on_up(self, event) -> None:
        index = self.plot_list.GetSelection()
        if index == 0:
            return
        
        strings = self.plot_list.GetStrings()
        entry = strings[index]
        above_entry = strings[index - 1]

        strings[index] = above_entry
        strings[index - 1] = entry

        self.plot_list.Set(strings)
        self.plot_list.SetSelection(index - 1)


    def on_down(self, event):
        index = self.plot_list.GetSelection()
        strings = self.plot_list.GetStrings()
        if index == len(strings) - 1:
            return
        
        entry = strings[index]
        below_entry = strings[index + 1]

        strings[index] = below_entry
        strings[index + 1] = entry

        self.plot_list.Set(strings)
        self.plot_list.SetSelection(index + 1)

    def on_flip_flag(self, event) -> None:
        list = self.plot_list.GetStrings()
        list.reverse()
        self.plot_list.Set(list)

    def on_order_flag(self, event) -> None:
        if self.order_flag.Value:
            self.up_button.Disable()
            self.down_button.Disable()
        else:
            self.up_button.Enable()
            self.down_button.Enable()


    def on_dpi_change(self, event) -> None:
        INCH = 25.4#mm
        self.res_x = ceil(self.dpi_box.Value * self.x / INCH)
        self.res_y = ceil(self.dpi_box.Value * self.y / INCH)
        self.resolution_label_xy.LabelText = f"\t{self.res_x}x{self.res_y}"
        pixels = self.res_x * self.res_y / 1e6
        self.resolution_label_mp.LabelText = f"\t {pixels:.2f} MP"

    def on_shoot(self, event) -> None:
        settings = {}
        settings["layers"] = self.plot_list.GetStrings()
        settings["dpi"] = self.dpi_box.Value
        settings["x_res"] = self.res_x
        settings["y_res"] = self.res_y
        settings["xmin"] = self.x_min
        settings["xmax"] = self.x_max
        settings["ymin"] = self.y_min
        settings["ymax"] = self.y_max
        settings["flip"] = self.flip_flag.Value
        settings["keep_order"] = self.order_flag.Value
        settings["antialiasing"] = self.aa_flag.Value
        if self.shoot_callback:
            self.shoot_callback(settings)
    
    def set_callback(self, func: Callable) -> None:
        self.shoot_callback = func




if __name__ == "__main__":
    app = App()
    app.set_viewport(25.4, 0, 50.8, 0)
    app.set_layers(["a","b","c","d","e", "f", "g", "h", "i", "j", "k", "l"])
    def print_dict(dict: Dict) -> None:
        print(dict)
    app.set_callback(print_dict)
    app.run()
