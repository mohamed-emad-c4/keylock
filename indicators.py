import tkinter as tk

def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius=10, **kwargs):
    """Draw a rounded rectangle on the canvas"""
    # Draw corner arcs
    canvas.create_arc(x1, y1, x1 + 2*radius, y1 + 2*radius, 
                      start=90, extent=90, style="pieslice", **kwargs)
    canvas.create_arc(x2 - 2*radius, y1, x2, y1 + 2*radius, 
                      start=0, extent=90, style="pieslice", **kwargs)
    canvas.create_arc(x1, y2 - 2*radius, x1 + 2*radius, y2, 
                      start=180, extent=90, style="pieslice", **kwargs)
    canvas.create_arc(x2 - 2*radius, y2 - 2*radius, x2, y2, 
                      start=270, extent=90, style="pieslice", **kwargs)
    
    # Draw connecting rectangles
    canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)
    canvas.create_rectangle(x1, y1 + radius, x1 + radius, y2 - radius, **kwargs)
    canvas.create_rectangle(x2 - radius, y1 + radius, x2, y2 - radius, **kwargs)

def draw_keyboard_indicator(canvas, colors, locked=False):
    """Draw a keyboard indicator on a canvas"""
    try:
        # Clear existing items
        canvas.delete("all")
        
        width = int(canvas.cget("width"))
        height = int(canvas.cget("height"))
        
        # Calculate dimensions for centered keyboard
        kb_width = width * 0.8
        kb_height = height * 0.6
        key_spacing = kb_width / 12
        
        kb_left = (width - kb_width) / 2
        kb_top = (height - kb_height) / 2
        kb_right = kb_left + kb_width
        kb_bottom = kb_top + kb_height
        
        # Draw keyboard base with rounded corners
        draw_rounded_rectangle(
            canvas,
            kb_left, kb_top, kb_right, kb_bottom,
            radius=5,
            fill=colors["glass_highlight"] if not locked else "#263238",
            outline=colors["foreground"],
            width=2
        )
        
        # Draw keyboard keys
        key_rows = [10, 12, 9]  # Number of keys in each row
        key_height = kb_height / (len(key_rows) + 1)
        
        for row, num_keys in enumerate(key_rows):
            key_width = (kb_width - ((num_keys + 1) * 2)) / num_keys
            y_top = kb_top + (row + 0.5) * key_height
            y_bottom = y_top + key_height * 0.7
            
            for key in range(num_keys):
                x_left = kb_left + 2 + key * (key_width + 2)
                x_right = x_left + key_width
                
                # Draw individual keys
                draw_rounded_rectangle(
                    canvas,
                    x_left, y_top, x_right, y_bottom,
                    radius=2,
                    fill=colors["surface"] if not locked else "#455A64",
                    outline=colors["foreground"],
                    width=1
                )
        
        # Draw space bar
        space_width = kb_width * 0.5
        space_left = kb_left + (kb_width - space_width) / 2
        space_right = space_left + space_width
        space_top = kb_top + 3.5 * key_height
        space_bottom = space_top + key_height * 0.7
        
        draw_rounded_rectangle(
            canvas,
            space_left, space_top, space_right, space_bottom,
            radius=2,
            fill=colors["surface"] if not locked else "#455A64",
            outline=colors["foreground"],
            width=1
        )
        
        # Draw lock indicator
        indicator_size = 20
        indicator_x = kb_right + 5
        indicator_y = kb_top
        
        if locked:
            # Draw locked indicator (closed padlock)
            canvas.create_oval(
                indicator_x - indicator_size/2, 
                indicator_y - indicator_size/2,
                indicator_x + indicator_size/2, 
                indicator_y + indicator_size/2,
                fill="#FF5252",
                outline=colors["foreground"],
                width=1
            )
            
            # Draw lock symbol
            icon_size = indicator_size * 0.6
            canvas.create_rectangle(
                indicator_x - icon_size/3,
                indicator_y - icon_size/4,
                indicator_x + icon_size/3,
                indicator_y + icon_size/2,
                fill="#FFFFFF",
                outline=""
            )
            canvas.create_arc(
                indicator_x - icon_size/2,
                indicator_y - icon_size/2,
                indicator_x + icon_size/2,
                indicator_y,
                start=0,
                extent=180,
                style="arc",
                outline="#FFFFFF",
                width=2
            )
            
        else:
            # Draw unlocked indicator (green circle)
            canvas.create_oval(
                indicator_x - indicator_size/2, 
                indicator_y - indicator_size/2,
                indicator_x + indicator_size/2, 
                indicator_y + indicator_size/2,
                fill="#4CAF50",
                outline=colors["foreground"],
                width=1
            )
            
            # Draw unlock symbol (checkmark)
            canvas.create_line(
                indicator_x - indicator_size/3,
                indicator_y,
                indicator_x - indicator_size/9,
                indicator_y + indicator_size/3,
                indicator_x + indicator_size/3,
                indicator_y - indicator_size/3,
                fill="#FFFFFF",
                width=2,
                smooth=True,
                capstyle="round",
                joinstyle="round"
            )
            
        return canvas
        
    except Exception as e:
        print(f"Error drawing keyboard indicator: {e}")
        return canvas


def draw_mouse_indicator(canvas, colors, locked=False):
    """Draw a mouse indicator on a canvas"""
    try:
        # Clear existing items
        canvas.delete("all")
        
        width = int(canvas.cget("width"))
        height = int(canvas.cget("height"))
        
        # Calculate dimensions for centered mouse
        mouse_width = width * 0.4
        mouse_height = height * 0.7
        
        mouse_left = (width - mouse_width) / 2
        mouse_top = (height - mouse_height) / 2
        mouse_right = mouse_left + mouse_width
        mouse_bottom = mouse_top + mouse_height
        
        # Draw mouse body with rounded corners
        draw_rounded_rectangle(
            canvas,
            mouse_left, mouse_top, mouse_right, mouse_bottom,
            radius=mouse_width/2,
            fill=colors["glass_highlight"] if not locked else "#263238",
            outline=colors["foreground"],
            width=2
        )
        
        # Draw mouse wheel
        wheel_width = mouse_width * 0.2
        wheel_height = mouse_height * 0.15
        wheel_left = mouse_left + (mouse_width - wheel_width) / 2
        wheel_top = mouse_top + mouse_height * 0.3
        wheel_right = wheel_left + wheel_width
        wheel_bottom = wheel_top + wheel_height
        
        canvas.create_rectangle(
            wheel_left, wheel_top, wheel_right, wheel_bottom,
            fill=colors["surface"] if not locked else "#455A64",
            outline=colors["foreground"],
            width=1
        )
        
        # Draw mouse buttons
        btn_height = mouse_height * 0.25
        btn_top = mouse_top + mouse_height * 0.05
        btn_bottom = btn_top + btn_height
        btn_mid = mouse_left + mouse_width / 2
        
        # Left button
        canvas.create_line(
            btn_mid, btn_top, btn_mid, btn_bottom,
            fill=colors["foreground"],
            width=1
        )
        
        # Cable
        cable_width = mouse_width * 0.2
        cable_top = mouse_top - mouse_height * 0.1
        
        canvas.create_line(
            mouse_left + mouse_width/2, cable_top,
            mouse_left + mouse_width/2, mouse_top,
            fill=colors["foreground"],
            width=2
        )
        
        # Draw lock indicator
        indicator_size = 20
        indicator_x = mouse_right + 5
        indicator_y = mouse_top
        
        if locked:
            # Draw locked indicator (red circle)
            canvas.create_oval(
                indicator_x - indicator_size/2, 
                indicator_y - indicator_size/2,
                indicator_x + indicator_size/2, 
                indicator_y + indicator_size/2,
                fill="#FF5252",
                outline=colors["foreground"],
                width=1
            )
            
            # Draw lock symbol
            icon_size = indicator_size * 0.6
            canvas.create_rectangle(
                indicator_x - icon_size/3,
                indicator_y - icon_size/4,
                indicator_x + icon_size/3,
                indicator_y + icon_size/2,
                fill="#FFFFFF",
                outline=""
            )
            canvas.create_arc(
                indicator_x - icon_size/2,
                indicator_y - icon_size/2,
                indicator_x + icon_size/2,
                indicator_y,
                start=0,
                extent=180,
                style="arc",
                outline="#FFFFFF",
                width=2
            )
            
        else:
            # Draw unlocked indicator (green circle)
            canvas.create_oval(
                indicator_x - indicator_size/2, 
                indicator_y - indicator_size/2,
                indicator_x + indicator_size/2, 
                indicator_y + indicator_size/2,
                fill="#4CAF50",
                outline=colors["foreground"],
                width=1
            )
            
            # Draw unlock symbol (checkmark)
            canvas.create_line(
                indicator_x - indicator_size/3,
                indicator_y,
                indicator_x - indicator_size/9,
                indicator_y + indicator_size/3,
                indicator_x + indicator_size/3,
                indicator_y - indicator_size/3,
                fill="#FFFFFF",
                width=2,
                smooth=True,
                capstyle="round",
                joinstyle="round"
            )
            
        return canvas
        
    except Exception as e:
        print(f"Error drawing mouse indicator: {e}")
        return canvas 