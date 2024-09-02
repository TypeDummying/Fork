
import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
import math
import json
import os

class Pearl2DCustomTool:
    def __init__(self, master):
        self.master = master
        self.master.title("Pearl 2D Custom Modeling Tool")
        self.master.geometry("1200x800")

        # Initialize variables
        self.current_tool = "select"
        self.current_color = "black"
        self.current_fill = ""
        self.stroke_width = 2
        self.shapes = []
        self.selected_shape = None
        self.start_x = None
        self.start_y = None

        self.create_widgets()
        self.create_canvas()
        self.create_toolbar()
        self.create_color_panel()
        self.create_layer_panel()
        self.bind_events()

    def create_widgets(self):
        """Create main application widgets"""
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_panel = ttk.Frame(self.main_frame, width=200)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)

        self.right_panel = ttk.Frame(self.main_frame)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def create_canvas(self):
        """Create drawing canvas"""
        self.canvas_frame = ttk.Frame(self.right_panel)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def create_toolbar(self):
        """Create toolbar with drawing tools"""
        self.toolbar = ttk.Frame(self.left_panel)
        self.toolbar.pack(fill=tk.X, padx=5, pady=5)

        tools = [
            ("Select", "select"),
            ("Line", "line"),
            ("Rectangle", "rectangle"),
            ("Ellipse", "ellipse"),
            ("Polygon", "polygon"),
            ("Text", "text")
        ]

        for text, mode in tools:
            btn = ttk.Button(self.toolbar, text=text, command=lambda m=mode: self.set_tool(m))
            btn.pack(side=tk.TOP, padx=2, pady=2)

    def create_color_panel(self):
        """Create color selection panel"""
        self.color_panel = ttk.Frame(self.left_panel)
        self.color_panel.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(self.color_panel, text="Stroke Color:").pack()
        self.stroke_color_btn = ttk.Button(self.color_panel, text="Choose Color", command=self.choose_stroke_color)
        self.stroke_color_btn.pack(fill=tk.X)

        ttk.Label(self.color_panel, text="Fill Color:").pack()
        self.fill_color_btn = ttk.Button(self.color_panel, text="Choose Color", command=self.choose_fill_color)
        self.fill_color_btn.pack(fill=tk.X)

        ttk.Label(self.color_panel, text="Stroke Width:").pack()
        self.stroke_width_var = tk.StringVar(value="2")
        self.stroke_width_entry = ttk.Entry(self.color_panel, textvariable=self.stroke_width_var)
        self.stroke_width_entry.pack(fill=tk.X)
        self.stroke_width_entry.bind("<FocusOut>", self.update_stroke_width)

    def create_layer_panel(self):
        """Create layer management panel"""
        self.layer_panel = ttk.Frame(self.left_panel)
        self.layer_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(self.layer_panel, text="Layers:").pack()
        self.layer_listbox = tk.Listbox(self.layer_panel)
        self.layer_listbox.pack(fill=tk.BOTH, expand=True)

        layer_btn_frame = ttk.Frame(self.layer_panel)
        layer_btn_frame.pack(fill=tk.X)

        ttk.Button(layer_btn_frame, text="Add Layer", command=self.add_layer).pack(side=tk.LEFT)
        ttk.Button(layer_btn_frame, text="Remove Layer", command=self.remove_layer).pack(side=tk.LEFT)
        ttk.Button(layer_btn_frame, text="Move Up", command=self.move_layer_up).pack(side=tk.LEFT)
        ttk.Button(layer_btn_frame, text="Move Down", command=self.move_layer_down).pack(side=tk.LEFT)

    def bind_events(self):
        """Bind mouse events to canvas"""
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def set_tool(self, tool):
        """Set the current drawing tool"""
        self.current_tool = tool

    def choose_stroke_color(self):
        """Open color chooser for stroke color"""
        color = colorchooser.askcolor(self.current_color)[1]
        if color:
            self.current_color = color
            self.stroke_color_btn.configure(text=color)

    def choose_fill_color(self):
        """Open color chooser for fill color"""
        color = colorchooser.askcolor(self.current_fill)[1]
        if color:
            self.current_fill = color
            self.fill_color_btn.configure(text=color)

    def update_stroke_width(self, event):
        """Update stroke width based on user input"""
        try:
            self.stroke_width = int(self.stroke_width_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer for stroke width.")
            self.stroke_width_var.set(str(self.stroke_width))

    def on_press(self, event):
        """Handle mouse press event"""
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        if self.current_tool == "select":
            self.select_shape(event)
        elif self.current_tool == "text":
            self.create_text(event)

    def on_drag(self, event):
        """Handle mouse drag event"""
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        if self.current_tool == "select" and self.selected_shape:
            self.move_shape(cur_x, cur_y)
        elif self.current_tool in ["line", "rectangle", "ellipse"]:
            self.draw_shape(cur_x, cur_y)

    def on_release(self, event):
        """Handle mouse release event"""
        if self.current_tool in ["line", "rectangle", "ellipse", "polygon"]:
            self.finalize_shape()

        self.start_x = None
        self.start_y = None

    def select_shape(self, event):
        """Select a shape on the canvas"""
        clicked = self.canvas.find_withtag("current")
        if clicked:
            self.selected_shape = clicked[0]
            self.canvas.itemconfig(self.selected_shape, width=self.stroke_width + 2)
        else:
            if self.selected_shape:
                self.canvas.itemconfig(self.selected_shape, width=self.stroke_width)
            self.selected_shape = None

    def move_shape(self, x, y):
        """Move the selected shape"""
        dx = x - self.start_x
        dy = y - self.start_y
        self.canvas.move(self.selected_shape, dx, dy)
        self.start_x = x
        self.start_y = y

    def draw_shape(self, x, y):
        """Draw temporary shape while dragging"""
        self.canvas.delete("temp_shape")
        if self.current_tool == "line":
            self.canvas.create_line(self.start_x, self.start_y, x, y, fill=self.current_color, width=self.stroke_width, tags="temp_shape")
        elif self.current_tool == "rectangle":
            self.canvas.create_rectangle(self.start_x, self.start_y, x, y, outline=self.current_color, fill=self.current_fill, width=self.stroke_width, tags="temp_shape")
        elif self.current_tool == "ellipse":
            self.canvas.create_oval(self.start_x, self.start_y, x, y, outline=self.current_color, fill=self.current_fill, width=self.stroke_width, tags="temp_shape")

    def finalize_shape(self):
        """Finalize the drawn shape"""
        temp_shape = self.canvas.find_withtag("temp_shape")
        if temp_shape:
            shape_type = self.current_tool
            coords = self.canvas.coords(temp_shape)
            self.canvas.delete("temp_shape")
            self.create_permanent_shape(shape_type, coords)

    def create_permanent_shape(self, shape_type, coords):
        """Create a permanent shape on the canvas"""
        if shape_type == "line":
            shape = self.canvas.create_line(*coords, fill=self.current_color, width=self.stroke_width)
        elif shape_type == "rectangle":
            shape = self.canvas.create_rectangle(*coords, outline=self.current_color, fill=self.current_fill, width=self.stroke_width)
        elif shape_type == "ellipse":
            shape = self.canvas.create_oval(*coords, outline=self.current_color, fill=self.current_fill, width=self.stroke_width)
        elif shape_type == "polygon":
            shape = self.canvas.create_polygon(*coords, outline=self.current_color, fill=self.current_fill, width=self.stroke_width)

        self.shapes.append({
            "type": shape_type,
            "id": shape,
            "coords": coords,
            "color": self.current_color,
            "fill": self.current_fill,
            "width": self.stroke_width
        })

        self.update_layer_listbox()

    def create_text(self, event):
        """Create text on the canvas"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        text = tk.simpledialog.askstring("Input", "Enter text:")
        if text:
            shape = self.canvas.create_text(x, y, text=text, fill=self.current_color, font=("Arial", 12))
            self.shapes.append({
                "type": "text",
                "id": shape,
                "coords": (x, y),
                "color": self.current_color,
                "text": text
            })
            self.update_layer_listbox()

    def update_layer_listbox(self):
        """Update the layer listbox"""
        self.layer_listbox.delete(0, tk.END)
        for i, shape in enumerate(self.shapes):
            self.layer_listbox.insert(tk.END, f"Shape {i+1}: {shape['type']}")

    def add_layer(self):
        """Add a new empty layer"""
        self.shapes.append({"type": "layer", "items": []})
        self.update_layer_listbox()

    def remove_layer(self):
        """Remove the selected layer"""
        selected = self.layer_listbox.curselection()
        if selected:
            index = selected[0]
            removed_shape = self.shapes.pop(index)
            if removed_shape["type"] != "layer":
                self.canvas.delete(removed_shape["id"])
            self.update_layer_listbox()

    def move_layer_up(self):
        """Move the selected layer up"""
        selected = self.layer_listbox.curselection()
        if selected and selected[0] > 0:
            index = selected[0]
            self.shapes[index], self.shapes[index-1] = self.shapes[index-1], self.shapes[index]
            self.update_layer_listbox()
            self.layer_listbox.selection_set(index-1)

    def move_layer_down(self):
        """Move the selected layer down"""
        selected = self.layer_listbox.curselection()
        if selected and selected[0] < len(self.shapes) - 1:
            index = selected[0]
            self.shapes[index], self.shapes[index+1] = self.shapes[index+1], self.shapes[index]
            self.update_layer_listbox()
            self.layer_listbox.selection_set(index+1)

    def save_project(self):
        """Save the current project to a file"""
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            project_data = {
                "shapes": self.shapes,
                "canvas_size": (self.canvas.winfo_width(), self.canvas.winfo_height())
            }
            with open(file_path, "w") as f:
                json.dump(project_data, f)

    def load_project(self):
        """Load a project from a file"""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "r") as f:
                project_data = json.load(f)

            self.canvas.delete("all")
            self.shapes = []

            for shape in project_data["shapes"]:
                if shape["type"] == "layer":
                    self.shapes.append(shape)
                else:
                    self.create_shape_from_data(shape)

            self.update_layer_listbox()

    def create_shape_from_data(self, shape_data):
        """Create a shape on the canvas from loaded data"""
        shape_type = shape_data["type"]
        coords = shape_data["coords"]
        color = shape_data["color"]
        fill = shape_data.get("fill", "")
        width = shape_data.get("width", 2)

        if shape_type == "line":
            shape = self.canvas.create_line(*coords, fill=color, width=width)
        elif shape_type == "rectangle":
            shape = self.canvas.create_rectangle(*coords, outline=color, fill=fill, width=width)
        elif shape_type == "ellipse":
            shape = self.canvas.create_oval(*coords, outline=color, fill=fill, width=width)
        elif shape_type == "polygon":
            shape = self.canvas.create_polygon(*coords, outline=color, fill=fill, width=width)
        elif shape_type == "text":
            shape = self.canvas.create_text(*coords, text=shape_data["text"], fill=color, font=("Arial", 12))

        self.shapes.append({
            "type": shape_type,
            "id": shape,
            "coords": coords,
        })