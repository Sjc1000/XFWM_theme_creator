#!/usr/bin/env python3
"""theme_creator
A simple GUI for creating XFWM4 themes. Currently does not support any
themerc file styff. It is a planned feature.
"""

import math
import os
import subprocess
import json
import cairo
from collections import OrderedDict
from gi.repository import Gtk, Gdk
from gi.repository.GdkPixbuf import Pixbuf



names = ['bottom-active', 'bottom-inactive', 'bottom-left-active',
         'bottom-left-inactive', 'bottom-right-active',
         'bottom-right-inactive', 'close-active', 'close-inactive',
         'close-prelight', 'close-pressed', 'hide-active', 'hide-inactive',
         'hide-prelight', 'hide-pressed', 'left-active', 'left-inactive',
         'maximize-active', 'maximize-inactive', 'maximize-prelight',
         'maximize-pressed', 'maximize-toggled-active',
         'maximize-toggled-inactive', 'maximize-toggled-prelight',
         'maximize-toggled-pressed', 'menu-active', 'menu-inactive',
         'menu-prelight', 'menu-pressed', 'right-active', 'right-inactive',
         'shade-active', 'shade-inactive', 'shade-prelight', 'shade-pressed',
         'shade-toggled-active', 'shade-toggled-inactive',
         'shade-toggled-prelight', 'shade-toggled-pressed', 'stick-active',
         'stick-inactive', 'stick-prelight', 'stick-pressed',
         'stick-toggled-active', 'stick-toggled-inactive',
         'stick-toggled-prelight', 'stick-toggled-pressed', 'title-1-active',
         'title-1-inactive', 'title-2-active', 'title-2-inactive',
         'title-3-active', 'title-3-inactive', 'title-4-active',
         'title-4-inactive', 'title-5-active', 'title-5-inactive',
         'top-left-active', 'top-left-inactive', 'top-right-active',
         'top-right-inactive']

required = ['bottom-active', 'bottom-inactive', 'bottom-left-active',
         'bottom-left-inactive', 'bottom-right-active',
         'bottom-right-inactive', 'close-active', 'close-inactive',
         'hide-active', 'hide-inactive', 'left-active', 'left-inactive',
         'maximize-active', 'maximize-inactive', 'maximize-pressed',
         'menu-active', 'menu-inactive', 'menu-pressed', 'right-active',
         'right-inactive', 'shade-active', 'shade-inactive', 'stick-active',
         'stick-inactive', 'title-1-active', 'title-1-inactive',
         'title-2-active', 'title-2-inactive', 'title-3-active',
         'title-3-inactive', 'title-4-active', 'title-4-inactive',
         'title-5-active', 'title-5-inactive', 'top-left-active',
         'top-left-inactive', 'top-right-active', 'top-right-inactive']


files = OrderedDict()
for name in names:
    files.update({name: {'image': [[[None, None] for x in range(20)] for y in range(20)], 'size': [20, 20]}})




class FileSelecter(Gtk.ScrolledWindow):
    """FileSelecter
    A list of all the files in the theme.
    If you leave these blank and it is not in the required list my program
    will not export it to a file.
    If it is in required it will export a transparent image.
    """
    icon = 'image-x-generic'
    active = None
    copy_data = None

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.view = Gtk.IconView()
        self.list = Gtk.ListStore(Pixbuf, str)
        self.view.set_model(self.list)
        self.view.set_pixbuf_column(0)
        self.view.set_text_column(1)
        self.view.set_activate_on_single_click(True)
        self.view.set_item_width(100)

        self.menu = Gtk.Menu()
        copy = Gtk.MenuItem('Copy')
        copy.connect('activate', self.copy)
        paste = Gtk.MenuItem('Paste')
        paste.connect('activate', self.paste)
        self.menu.append(copy)
        self.menu.append(paste)

        self.view.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.view.connect('button-press-event', self.show_menu)

        self.view.set_vexpand(True)
        self.view.set_hexpand(True)
        self.add(self.view)
        self.view.connect('item-activated', self.row_activated)

    def clean(self):
        """clean
        Clears the current file list.
        """
        self.list.clear()
        return None

    def populate(self):
        """populate
        Populates the file list with data from the global var 'files'.
        It reads in their image data and gives them an icon from that.
        """
        main_window = self.get_toplevel()

        for name in files:
            image = files[name]['image']
            pix_width = len(image[0])
            pix_height = len(image)
            if pix_width < 6:
                pix_width = 6
            if pix_height < 6:
                pix_height = 6
            pix_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pix_width,
                                             pix_height)
            pix_context = cairo.Context(pix_surface)
            pix_context.set_source_rgba(*main_window.paint_background.get_rgba())

            for yi, yv in enumerate(image):
                for xi, xv in enumerate(yv):
                    rgb, var = xv
                    if rgb is not None:
                        pix_context.set_source_rgba(*rgb)
                        pix_context.rectangle(xi, yi, 1, 1)
                        pix_context.fill()
            pixbuf = Gdk.pixbuf_get_from_surface(pix_surface, 0, 0, pix_width,
                                                 pix_height)

            icon = Gtk.IconTheme.get_default().load_icon('image-x-generic', 40, 0)
            self.list.append([pixbuf, name])
        return None

    def show_menu(self, widget, event):
        """show_menu
        Shows the right click menu of the current item.
        """
        button = event.button
        if button == 3 and self.active != None:
            self.menu.show_all()
            self.menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())
        return None

    def copy(self, *_):
        """copy
        Called when you click the copy menu
        """
        self.copy_data = self.active
        return None

    def paste(self, *_):
        """paste
        Called when you click the paste menu
        This will automatically reload the image to the pasted image.
        """
        file_data = files[self.copy_data]
        files[self.active]['size'] = file_data['size']
        width, height = files[self.active]['size']
        files[self.active]['image'] = [[[None, None] for x in range(width)] for y in range(height)]
        for yi, y in enumerate(file_data['image']):
            for xi, x in enumerate(y):
                files[self.active]['image'][yi][xi] = x
        main_window = self.get_toplevel()
        main_window.paint_area.reload_image()
        return None

    def row_activated(self, widget, path):
        """row_activated
        Called when the user clicks on a file.
        """
        file_data = files[self.list[path][1]]
        self.active = self.list[path][1]
        size = file_data['size']
        image = file_data['image']
        main_window = self.get_toplevel()
        main_window.paint_area.set_image(image)
        main_window.paint_area.view.queue_draw()
        main_window.size.set_size(*size)
        return None


class PaintArea(Gtk.ScrolledWindow):
    """PaintArea
    A custom widget that allows the user to paint in a pixel style area.
    """
    x = 0
    y = 0
    width = 0
    height = 0
    original_width = 0
    original_height = 0
    zoomed = False
    square = False
    fill = False
    last = None
    image = None
    background_color = (0, 0, 0)
    get_color = False

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.view = Gtk.DrawingArea()
        self.view.set_hexpand(True)
        self.view.set_vexpand(True)
        self.view.set_events(Gdk.EventMask.BUTTON_PRESS_MASK
                             | Gdk.EventMask.KEY_PRESS_MASK
                             | Gdk.EventType.MOTION_NOTIFY
                             | Gdk.EventMask.POINTER_MOTION_MASK)
        self.view.connect('draw', self.draw)
        self.view.connect('button-press-event', self.press)
        self.view.connect('motion-notify-event', self.motion)
        self.add(self.view)

    def reload_image(self):
        """reload_image
        Reloads the current image and then queues the paint area for a
        re-draw.
        """
        main_window = self.get_toplevel()
        active_image = main_window.file_selecter.active
        self.image = files[active_image]['image']
        self.view.queue_draw()
        return None

    def motion(self, widget, event):
        """motion
        Called whenever the user hovers over the paint area.
        I make sure there is an active image and that the mouse
        is in the images width / height before doing any hover stuff.
        """
        if self.image is None:
            return None
        image_width = len(self.image[0])
        image_height = len(self.image)
        x = math.floor((event.x)/self.scale)
        y = math.floor((event.y)/self.scale)
        if x+1 > image_width or y+1 > image_height or x < 0 or y < 0:
            self.view.set_tooltip_text(None)
            return None
        data = self.image[y][x][1]
        if data is not None:
            self.view.set_tooltip_text(data)
        else:
            self.view.set_tooltip_text(None)
        return None

    def zoom_in(self):
        """zoom_in
        Called when the user presses Ctrl and =
        """
        self.width += 50
        self.height += 50
        if self.width != self.original_width or self.height != self.original_height:
            self.zoomed = True
        else:
            self.zoomed = False
        self.view.set_size_request(self.width, self.height)
        self.view.queue_draw()
        return None

    def zoom_out(self):
        """zoom_out
        Called when the user presses Ctrl and -
        """
        self.width -= 50
        self.height -= 50
        if self.width != self.original_width or self.height != self.original_height:
            self.zoomed = True
        else:
            self.zoomed = False
        self.view.set_size_request(self.width, self.height)
        self.view.queue_draw()
        return None

    def press(self, widget, event):
        """press
        Called when the user presses a mouse button.
        Left click: Paint the currently active foreground color.
        Right Click: Remove the pixel under the mouse.
        Middle Click: Fill with the active foreground color.
        """
        if self.image is None:
            return None
        main_window = self.get_toplevel()
        var_name = main_window.var_list.active
        image_width = len(self.image[0])
        image_height = len(self.image)
        x = math.floor((event.x)/self.scale)
        y = math.floor((event.y)/self.scale)
        if x+1 > image_width or y+1 > image_height or x < 0 or y < 0:
            return None

        if event.button == 2:
            r, g, b, a = main_window.paint_color.get_rgba()
            color = [Gdk.RGBA(r, g, b), var_name]
            original = self.image[y][x]
            for yi, y in enumerate(self.image):
                for xi, x in enumerate(y):
                    if str(self.image[yi][xi]) != str(original):
                        continue
                    self.image[yi][xi] = color
            self.view.queue_draw()
            return None

        elif event.button == 1 and self.get_color:
            color = self.image[y][x]
            main_window.var_list.active = None
            main_window.paint_color.set_rgba(color[0])
            for index, item in enumerate(main_window.var_list.list):
                path = Gtk.TreePath().new_from_string(str(index))
                if item[0] == color[1]:
                    item[1] = True
                    main_window.var_list.active = item[0]
                else:
                    item[1] = False

            return None
        if event.button == 1:
            color = main_window.paint_color.get_rgba()
        elif event.button == 3:
            color = None

        if self.last is not None and self.square:
            lx, ly = self.last
            for xi in range(image_width):
                for yi in range(image_height):
                    if ((x > lx and lx <= xi <= x or x < lx and lx >= xi >= x)
                            and (y > ly and ly <= yi <= y or y < ly
                            and ly >= yi >= y)):
                        self.image[yi][xi] = [color, var_name]
        else:
            self.image[y][x] = [color, var_name]
            self.last = [x, y]
        self.view.queue_draw()
        return None

    def set_image(self, image):
        self.image = image
        main_window = self.get_toplevel()
        active_image = main_window.file_selecter.active
        files[active_image]['image'] = image
        files[active_image]['size'] = [len(image[0]), len(image)]
        return None

    def draw(self, widget, context):
        if self.image is None:
            return None
        main_window = self.get_toplevel()
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()

        self.width = width
        self.height = height

        if not self.zoomed:
            self.original_width = width
            self.original_height = height
            self.view.set_size_request(-1, -1)

        context.set_source_rgba(*main_window.paint_background.get_rgba())
        context.paint()

        image_width = len(self.image[0])
        image_height = len(self.image)

        if image_width < width:
            scale_width = width / image_width
        else:
            scale_width = image_width / width

        if image_height < height:
            scale_height = height / image_height
        else:
            scale_height = image_height / height

        if scale_height < scale_width:
            scale = scale_height
        else:
            scale = scale_width

        scale = scale
        self.scale = scale

        cx = 0
        cy = 0

        context.set_line_width(3)
        context.set_source_rgb(1, 0, 0)
        context.rectangle(0, 0, image_width*scale, image_height*scale)
        context.stroke()

        context.set_line_width(1)

        pix_width = len(self.image[0])
        pix_height = len(self.image)
        if pix_width < 6:
            pix_width = 6
        if pix_height < 6:
            pix_height = 6
        pix_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pix_width,
                                         pix_height)
        pix_context = cairo.Context(pix_surface)
        pix_context.set_source_rgba(*main_window.paint_background.get_rgba())

        for yi, yv in enumerate(self.image):
            for xi, xv in enumerate(yv):
                rgb, var = xv
                if rgb is not None:
                    context.set_source_rgba(*rgb)
                    context.rectangle(cx-0.25, cy-0.25, scale+0.75, scale+0.75)
                    context.fill()

                    pix_context.set_source_rgba(*rgb)
                    pix_context.rectangle(xi, yi, 1, 1)
                    pix_context.fill()
                if var is not None:
                    context.set_source_rgb(1, 0, 0)
                    context.rectangle(cx-0.25, cy-0.25, scale+0.75, scale+0.75)
                    context.stroke()
                cx += scale
            cx = 0
            cy += scale

        pixbuf = Gdk.pixbuf_get_from_surface(pix_surface, 0, 0, pix_width,
                                             pix_height)
        file_selecter = main_window.file_selecter
        for index, item in enumerate(file_selecter.list):
            if item[1] == file_selecter.active:
                file_selecter.list[index][0] = pixbuf
        return None


class BackgroundColor(Gtk.ColorButton):
    def __init__(self):
        Gtk.ColorButton.__init__(self)
        self.set_rgba(Gdk.RGBA(0, 0, 0, 1))
        self.connect('color-set', self.color_set)

    def color_set(self, *_):
        main_window = self.get_toplevel()
        main_window.paint_area.view.queue_draw()
        return None


class PaintColor(Gtk.ColorButton):
    def __init__(self):
        Gtk.ColorButton.__init__(self)
        self.set_rgba(Gdk.RGBA(1, 1, 1, 1))
        self.connect('color-set', self.color_set)

    def color_set(self, *_):
        main_window = self.get_toplevel()
        main_window.paint_area.view.queue_draw()
        return None


class Size(Gtk.HBox):

    default = [20, 20]

    def __init__(self):
        Gtk.HBox.__init__(self)
        title = Gtk.Label('Size:')
        self.width = Gtk.Entry()
        self.height = Gtk.Entry()
        text = Gtk.Label('x')
        okay = Gtk.Button('Okay')
        okay.connect('clicked', self.clicked)

        self.pack_start(title, True, True, 10)
        self.pack_start(self.width, True, True, 0)
        self.pack_start(text, True, True, 0)
        self.pack_start(self.height, True, True, 0)
        self.pack_start(okay, True, True, 0)
        self.set_size(*self.default)

    def clicked(self, widget):
        main_window = self.get_toplevel()
        size = self.get_size()
        paint_area = main_window.paint_area
        paint_area.set_image([[[None, None] for x in range(size[0])] for y in range(size[1])])
        paint_area.view.queue_draw()
        return None

    def set_size(self, width, height):
        width_buffer = self.width.get_buffer()
        height_buffer = self.height.get_buffer()
        width_buffer.set_text(str(width), -1)
        height_buffer.set_text(str(height), -1)
        return None

    def get_size(self):
        width_buffer = self.width.get_buffer()
        height_buffer = self.height.get_buffer()
        width = int(width_buffer.get_text())
        height = int(height_buffer.get_text())
        return width, height


class VariableList(Gtk.ScrolledWindow):

    active = None

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.list = Gtk.ListStore(str, bool)
        self.view = Gtk.TreeView(self.list)
        self.view.set_hexpand(True)
        text_renderer = Gtk.CellRendererText()
        check_renderer = Gtk.CellRendererToggle()
        name_column = Gtk.TreeViewColumn('Gtk color list', text_renderer, text=0)
        check_column = Gtk.TreeViewColumn('', check_renderer, active=1)
        self.view.append_column(check_column)
        self.view.append_column(name_column)
        self.view.connect('row-activated', self.row_activated)
        self.add(self.view)

        names = ['active_text_color', 'inactive_text_color',
                 'active_text_shadow_color', 'inactive_text_shadow_color',
                 'active_border_color', 'inactive_border_color',
                 'active_color_1', 'active_color_2', 'active_highlight_1',
                 'active_highlight_2', 'active_mid_1', 'active_mid_2',
                 'active_shadow_1', 'active_shadow_2', 'inactive_color_1',
                 'inactive_color_2', 'inactive_highlight_1',
                 'inactive_highlight_2', 'inactive_mid_1', 'inactive_mid_2',
                 'inactive_shadow_1', 'inactive_shadow_2']
        for name in names:
            self.list.append([name, False])

    def row_activated(self, widget, path, column):
        for item in self.list:
            if item[1] == True and item[0] != self.list[path][0]:
                item[1] = False
        self.active = self.list[path][0]
        self.list[path][1] = not self.list[path][1]
        if self.list[path][1] == False:
            self.active = None
        return None


class MainWindow(Gtk.Window):

    can_zoom = False

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_size_request(400, 400)
        self.set_title('XFWM Theme Creator')
        self.connect('delete-event', Gtk.main_quit)
        self.connect('key-press-event', self.key_press)
        self.connect('key-release-event', self.key_release)
        self.create_widgets()
        self.show_all()
        self.file_selecter.populate()

    def key_release(self, widget, event):
        keyval = event.keyval
        if keyval == 65505:
            self.paint_area.square = False
        elif keyval == 65507:
            self.can_zoom = False
            self.paint_area.get_color = False
        elif keyval == 65513:
            self.paint_area.fill = False
        return None

    def key_press(self, widget, event):
        keyval = event.keyval
        if keyval == 45 and self.can_zoom:
            self.paint_area.zoom_out()
        elif keyval == 61 and self.can_zoom:
            self.paint_area.zoom_in()
        elif keyval == 65505:
            self.paint_area.square = True
        elif keyval == 65513:
            self.paint_area.fill = True
        elif keyval == 65507:
            self.can_zoom = True
            self.paint_area.get_color = True
        return None

    def create_widgets(self):
        self.grid = Gtk.Grid()
        self.file_selecter = FileSelecter()
        self.paint_area = PaintArea()
        self.paint_background = BackgroundColor()
        self.paint_color = PaintColor()
        self.size = Size()
        self.var_list = VariableList()

        self.name = Gtk.Entry()
        self.name.get_buffer().set_text('MyTheme', -1)

        export = Gtk.Button('Export')
        export.connect('clicked', self.export)

        load = Gtk.Button('Load')
        load.connect('clicked', self.load)


        paned2 = Gtk.Paned()
        paned2.set_position(200)
        paned2.add1(self.paint_area)
        paned2.add2(self.var_list)

        paned = Gtk.Paned()
        paned.set_position(200)
        paned.add1(self.file_selecter)
        paned.add2(paned2)


        self.grid.attach(paned, 0, 0, 10, 10)
        self.grid.attach(self.paint_background, 1, 10, 1, 1)
        self.grid.attach(self.paint_color, 2, 10, 1, 1)
        self.grid.attach(self.size, 3, 10, 1, 1)
        self.grid.attach(export, 8, 10, 1, 1)
        self.grid.attach(load, 9, 10, 1, 1)
        self.grid.attach(self.name, 7, 10, 1, 1)
        self.add(self.grid)
        return None

    def load(self, *_):
        chooser = Gtk.FileChooserDialog('Please select a xfwm4 folder.', self,
            Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = chooser.run()
        if response == Gtk.ResponseType.OK:
            self.file_selecter.clean()
            folder = chooser.get_filename()
            self.load_files(folder)
            self.file_selecter.populate()
        chooser.destroy()
        return None

    def load_files(self, folder):
        global files
        new_files = OrderedDict()
        image_files = sorted(os.listdir(folder))
        if 'xfwm4' in image_files:
            self.load_files(folder + '/xfwm4')
            return None
        for name in image_files:
            if name == 'themerc':
                # I might build in themerc support.
                # for now, I skip this.
                continue
            if not name.endswith('.xpm'):
                continue
            with open('{}/{}'.format(folder, name), 'r') as f:
                data = f.read().replace('\n', '')
            content = data.split('{')[1]
            content = content.strip('{};').split(',')
            chars = {}

            # Parse the width / height / number of colors
            width, height, colors, _ = content[0].strip('"').split(' ')
            width = int(width)
            height = int(height)
            for i in range(int(colors)):
                color_info = content[i+1].strip('"')
                char, color = color_info.split('c', 1)
                char = char[0]
                if 's' in color:
                    color, var = color.split('s', 1)
                else:
                    var = None
                color = color.strip()
                if color.lower() == 'none':
                    color = None
                if var is not None:
                    var = var.strip()
                if color is not None:
                    color = color.lstrip('#')
                    color = Gdk.RGBA(*(x/255 for x in bytes.fromhex(color)))
                chars[char] = [color, var]
            image = [[[None, None] for x in range(width)] for y in range(height)]
            for yi, y in enumerate(content[len(chars)+1:]):
                for xi, x in enumerate(y.strip('"')):
                    image[yi][xi] = chars[x]
            filename = name.split('.')[0]
            new_files.update({filename: {'image': image,
                         'size': [width, height]}})
        for name in names:
            if name not in image_files:
                files.update({name: {'image': [[[None, None]]], 'size': [1, 1]}})

        for name in sorted(new_files):
            files.update({name: new_files[name]})

        self.file_selecter.active = None
        return None

    def export(self, *_):
        dirname = self.name.get_buffer().get_text()
        if not os.path.exists('{}/'.format(dirname)):
            os.mkdir('{}/'.format(dirname))
        if not os.path.exists('{}/xfwm4/'.format(dirname)):
            os.mkdir('{}/xfwm4/'.format(dirname))
        for name in files:
            data = files[name]
            colors = []
            image = data['image']
            width = len(image[0])
            height = len(image)
            new_image = [[[None, None] for x in range(width)] for y in range(height)]
            for yi, yv in enumerate(image):
                for xi, x in enumerate(yv):
                    if x[0] is not None:
                        r, g, b, a = x[0]
                        color = '#%02x%02x%02x' % (r*255,g*255,b*255), x[1]
                    else:
                        color = [None, None]
                    new_image[yi][xi] = color
                    if color not in colors:
                        colors.append(color)

            if colors[0] == [None, None] and len(colors) == 1 and name not in required:
                continue

            output = '/* XPM */\nstatic char * {}[] = '.format(name)
            output += '{\n'
            output += '"{} {} {} {}",\n'.format(width, height, len(colors), 1)
            char = 32
            chars = []
            for color in colors:
                chars.append(chr(char))
                if color[1] is not None:
                    var = ' s ' + color[1]
                else:
                    var = ''
                output += '"{}\tc {}{}",\n'.format(chr(char), color[0], var)
                char += 1

            for y in new_image:
                output += '"'
                for x in y:
                    char = chars[colors.index(x)]
                    output += char
                output += '",\n'

            output = output[:-2] + '};\n'

            with open('{}/xfwm4/{}.xpm'.format(dirname, name), 'w') as f:
                f.write(output)

        with open('{}/xfwm4/themerc'.format(dirname), 'w') as f:
            f.write('')

        subprocess.call(['tar', '-czvf', '{}.tar.gz'.format(dirname),
                         '{}/xfwm4'.format(dirname)])
        subprocess.call(['rm', '-r', dirname])
        return None


def main():
    window = MainWindow()
    Gtk.main()
    return None


if __name__ == '__main__':
    main()
