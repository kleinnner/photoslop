# Adobo PhotoSlop - A fun drawing toy like Photoshop!
# Made with love for doodling and drawing!
# MIT License (shortened for space)
# Copyright (c) 2025 xAI (inspired by Grok)
# Permission is hereby granted, free of charge, to use, modify, and distribute.

import pygame
import os
import sys
import colorsys

# Start the toy machine
pygame.init()

# Make a screen (like a big paper) - Enable resizable window
WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Adobo PhotoSlop")
icon = pygame.Surface((32, 32))
icon.fill((60, 100, 170))  # A cool blue color
pygame.display.set_icon(icon)

# Colors (like crayons!)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
UI_BG = (30, 30, 40)  # Dark background
UI_ACCENT = (60, 100, 170)  # Button color
UI_HIGHLIGHT = (80, 120, 200)  # Hover color
UI_TEXT = (240, 240, 240)  # Text color
UI_BUTTON = (50, 60, 80)  # Button background
UI_BUTTON_HOVER = (70, 80, 100)  # Button hover color
UI_PANEL = (40, 45, 55)  # Panel color
UI_BORDER = (80, 85, 95)  # Border color

# Layout constants
SIDEBAR_WIDTH = 280
TOOLBAR_HEIGHT = 50
BOTTOM_HEIGHT = 70
PADDING = 10
BUTTON_WIDTH, BUTTON_HEIGHT = 120, 30
SMALL_BUTTON_WIDTH, SMALL_BUTTON_HEIGHT = 60, 25
WINDOW_BUTTON_WIDTH, WINDOW_BUTTON_HEIGHT = 30, 30  # For minimize/maximize/close buttons
COLOR_PANEL_HEIGHT = 180  # Defined early

# Set up the drawing area (canvas)
canvas_size = (WIDTH - SIDEBAR_WIDTH - 20, HEIGHT - TOOLBAR_HEIGHT - BOTTOM_HEIGHT - 20)
canvas = pygame.Surface(canvas_size, pygame.SRCALPHA)
canvas.fill(WHITE)
current_color = BLACK
brush_size = 5
opacity = 255
tool = "brush"  # Start with brush tool

# Layers for drawing
layers = [canvas.copy()]
current_layer = 0

# Fonts
font = pygame.font.SysFont("Arial", 16, bold=True)
small_font = pygame.font.SysFont("Arial", 12)
title_font = pygame.font.SysFont("Arial", 18, bold=True)

# UI Elements
def update_ui_elements():
    global canvas_view_rect, sidebar_rect, toolbar_rect, bottom_rect, color_panel_rect, color_picker, color_preview, tools_panel, toolbar_buttons, page_info_rect
    canvas_view_rect = pygame.Rect(SIDEBAR_WIDTH + 10, TOOLBAR_HEIGHT + 10,
                                   WIDTH - SIDEBAR_WIDTH - 20, HEIGHT - TOOLBAR_HEIGHT - BOTTOM_HEIGHT - 20)
    sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, HEIGHT)
    toolbar_rect = pygame.Rect(SIDEBAR_WIDTH, 0, WIDTH - SIDEBAR_WIDTH, TOOLBAR_HEIGHT)
    bottom_rect = pygame.Rect(0, HEIGHT - BOTTOM_HEIGHT, WIDTH, BOTTOM_HEIGHT)

    # Color picker
    color_panel_rect = pygame.Rect(PADDING, PADDING, SIDEBAR_WIDTH - 2 * PADDING, COLOR_PANEL_HEIGHT)
    color_picker = pygame.Rect(PADDING * 2, PADDING * 3 + 30, SIDEBAR_WIDTH - 4 * PADDING, 120)
    color_preview = pygame.Rect(PADDING * 2, PADDING * 4 + 160, 40, 40)

    # Tool panel
    tools_panel["rect"] = pygame.Rect(PADDING, COLOR_PANEL_HEIGHT + PADDING * 2 + 30, SIDEBAR_WIDTH - 2 * PADDING, 120)

    # Toolbar buttons (for opening, saving, and window controls)
    button_spacing = (WIDTH - SIDEBAR_WIDTH - (2 * BUTTON_WIDTH + 3 * WINDOW_BUTTON_WIDTH)) // 5
    toolbar_buttons = {
        "open": pygame.Rect(SIDEBAR_WIDTH + button_spacing, PADDING, BUTTON_WIDTH, BUTTON_HEIGHT),
        "save": pygame.Rect(SIDEBAR_WIDTH + button_spacing * 2 + BUTTON_WIDTH, PADDING, BUTTON_WIDTH, BUTTON_HEIGHT),
        "minimize": pygame.Rect(WIDTH - 3 * WINDOW_BUTTON_WIDTH - PADDING, PADDING, WINDOW_BUTTON_WIDTH, WINDOW_BUTTON_HEIGHT),
        "maximize": pygame.Rect(WIDTH - 2 * WINDOW_BUTTON_WIDTH - PADDING, PADDING, WINDOW_BUTTON_WIDTH, WINDOW_BUTTON_HEIGHT),
        "close": pygame.Rect(WIDTH - WINDOW_BUTTON_WIDTH - PADDING, PADDING, WINDOW_BUTTON_WIDTH, WINDOW_BUTTON_HEIGHT),
    }

    # Bottom bar - layer info
    page_info_rect = pygame.Rect(PADDING, HEIGHT - BOTTOM_HEIGHT + PADDING, SMALL_BUTTON_WIDTH * 2, SMALL_BUTTON_HEIGHT)

    # Reinitialize tool buttons to adjust positions
    init_button_rects()

# Tool panel
tools_panel = {
    "rect": pygame.Rect(PADDING, COLOR_PANEL_HEIGHT + PADDING * 2 + 30, SIDEBAR_WIDTH - 2 * PADDING, 120),
    "title": "Tools",
    "buttons": {}
}

# Tool buttons
tool_buttons = {
    "brush": {"panel": "tools", "row": 0, "col": 0, "text": "Brush"},
    "erase": {"panel": "tools", "row": 0, "col": 1, "text": "Erase"},
    "fill": {"panel": "tools", "row": 1, "col": 0, "text": "Fill"},
    "clear": {"panel": "tools", "row": 1, "col": 1, "text": "Clear"}
}

# Bottom bar - layer info
page_info_rect = pygame.Rect(PADDING, HEIGHT - BOTTOM_HEIGHT + PADDING, SMALL_BUTTON_WIDTH * 2, SMALL_BUTTON_HEIGHT)

# Toolbar buttons (for opening, saving, and window controls)
button_spacing = (WIDTH - SIDEBAR_WIDTH - (2 * BUTTON_WIDTH + 3 * WINDOW_BUTTON_WIDTH)) // 5
toolbar_buttons = {
    "open": pygame.Rect(SIDEBAR_WIDTH + button_spacing, PADDING, BUTTON_WIDTH, BUTTON_HEIGHT),
    "save": pygame.Rect(SIDEBAR_WIDTH + button_spacing * 2 + BUTTON_WIDTH, PADDING, BUTTON_WIDTH, BUTTON_HEIGHT),
    "minimize": pygame.Rect(WIDTH - 3 * WINDOW_BUTTON_WIDTH - PADDING, PADDING, WINDOW_BUTTON_WIDTH, WINDOW_BUTTON_HEIGHT),
    "maximize": pygame.Rect(WIDTH - 2 * WINDOW_BUTTON_WIDTH - PADDING, PADDING, WINDOW_BUTTON_WIDTH, WINDOW_BUTTON_HEIGHT),
    "close": pygame.Rect(WIDTH - WINDOW_BUTTON_WIDTH - PADDING, PADDING, WINDOW_BUTTON_WIDTH, WINDOW_BUTTON_HEIGHT),
}

# Initialize button rects for tools
def init_button_rects():
    for panel_name, panel_info in {"tools": tools_panel}.items():
        panel_rect = panel_info["rect"]
        button_width = (panel_rect.width - PADDING * 4) // 2  # 2 columns
        button_height = 40
        button_dict = tool_buttons

        for button_name, button_info in button_dict.items():
            if button_info["panel"] == panel_name:
                row, col = button_info["row"], button_info["col"]
                x = panel_rect.x + PADDING + col * (button_width + PADDING)
                y = panel_rect.y + PADDING * 2 + 20 + row * (button_height + PADDING)
                button_dict[button_name]["rect"] = pygame.Rect(x, y, button_width, button_height)
                print(f"Tool {button_name} button at: {button_dict[button_name]['rect']}")  # Debug

init_button_rects()

# Call update_ui_elements() to initialize UI elements before the main loop
update_ui_elements()

# Draw a rounded rectangle
def draw_rounded_rect(surface, rect, color, radius=10, border=0, border_color=None):
    if border_color is None:
        border_color = color
    if border > 0:
        pygame.draw.rect(surface, border_color, rect, border_radius=radius)
        inner_rect = pygame.Rect(rect.x + border, rect.y + border, rect.width - 2*border, rect.height - 2*border)
        pygame.draw.rect(surface, color, inner_rect, border_radius=radius-border)
    else:
        pygame.draw.rect(surface, color, rect, border_radius=radius)

# Save the canvas
def save_canvas(filename):
    pygame.image.save(layers[current_layer], filename)
    print(f"Saved to {filename}!")

# Main toy loop
running = True
drawing = False
last_pos = None
is_maximized = False  # Track window state

while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle window resize
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.size
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            canvas_size = (WIDTH - SIDEBAR_WIDTH - 20, HEIGHT - TOOLBAR_HEIGHT - BOTTOM_HEIGHT - 20)
            canvas = pygame.Surface(canvas_size, pygame.SRCALPHA)
            canvas.fill(WHITE)
            layers = [canvas.copy()]  # Reset layers to new size
            current_layer = 0
            update_ui_elements()  # Update UI elements to new window size
            print(f"Resized to: {WIDTH}x{HEIGHT}")

        # Mouse button down
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check color picker
            if color_picker.collidepoint(mouse_pos):
                print("Clicked color picker")
                rel_x = mouse_pos[0] - color_picker.x
                rel_y = mouse_pos[1] - color_picker.y
                hue = rel_x / color_picker.width
                sat = 1 - rel_y / color_picker.height
                rgb = colorsys.hsv_to_rgb(hue, sat, 1)
                current_color = tuple(int(c * 255) for c in rgb)
                print(f"New color: {current_color}")

            # Check tool buttons
            for name, info in tool_buttons.items():
                if "rect" in info and info["rect"].collidepoint(mouse_pos):
                    tool = name
                    print(f"Selected tool: {tool}")
                    if tool == "clear":
                        layers[current_layer].fill(WHITE)
                        print("Cleared canvas")

            # Toolbar buttons (open, save, minimize, maximize, close)
            for name, rect in toolbar_buttons.items():
                if rect.collidepoint(mouse_pos):
                    if name == "open":
                        print("Open clicked (placeholder)")
                    elif name == "save":
                        save_canvas("output.png")
                    elif name == "minimize":
                        pygame.display.iconify()  # Minimize the window
                        print("Minimized window")
                    elif name == "maximize":
                        if is_maximized:
                            # Restore to default size
                            WIDTH, HEIGHT = 1200, 900
                            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                            is_maximized = False
                            print("Restored window")
                        else:
                            # Maximize to screen size
                            info = pygame.display.Info()
                            WIDTH, HEIGHT = info.current_w, info.current_h
                            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                            is_maximized = True
                            print("Maximized window")
                        # Update canvas and UI after resizing
                        canvas_size = (WIDTH - SIDEBAR_WIDTH - 20, HEIGHT - TOOLBAR_HEIGHT - BOTTOM_HEIGHT - 20)
                        canvas = pygame.Surface(canvas_size, pygame.SRCALPHA)
                        canvas.fill(WHITE)
                        layers = [canvas.copy()]
                        current_layer = 0
                        update_ui_elements()
                    elif name == "close":
                        running = False
                        print("Closing window")

            # Start drawing on canvas
            if canvas_view_rect.collidepoint(mouse_pos):
                canvas_x = mouse_pos[0] - canvas_view_rect.x
                canvas_y = mouse_pos[1] - canvas_view_rect.y
                canvas_pos = (int(canvas_x), int(canvas_y))
                if 0 <= canvas_x < canvas_size[0] and 0 <= canvas_y < canvas_size[1]:
                    if event.button == 1:
                        if tool == "brush":
                            drawing = True
                            last_pos = canvas_pos
                        elif tool == "erase":
                            drawing = True
                            last_pos = canvas_pos
                        elif tool == "fill":
                            pygame.draw.rect(layers[current_layer], current_color, (canvas_x, canvas_y, 50, 50))

        # Mouse button up
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                drawing = False

        # Mouse movement
        elif event.type == pygame.MOUSEMOTION and drawing:
            mouse_x, mouse_y = mouse_pos
            canvas_x = mouse_x - canvas_view_rect.x
            canvas_y = mouse_y - canvas_view_rect.y
            current_pos = (int(canvas_x), int(canvas_y))
            if 0 <= canvas_x < canvas_size[0] and 0 <= canvas_y < canvas_size[1]:
                if tool == "brush":
                    pygame.draw.line(layers[current_layer], current_color, last_pos, current_pos, brush_size)
                elif tool == "erase":
                    pygame.draw.line(layers[current_layer], WHITE, last_pos, current_pos, brush_size)
                last_pos = current_pos

        # Hover detection
        elif event.type == pygame.MOUSEMOTION:
            hover_button = None
            for name, rect in toolbar_buttons.items():
                if rect.collidepoint(mouse_pos):
                    hover_button = name
                    break
            for name, info in tool_buttons.items():
                if "rect" in info and info["rect"].collidepoint(mouse_pos):
                    hover_button = name
                    break

    # Draw the screen
    screen.fill(UI_BG)

    # Draw the canvas with layers
    composite = pygame.Surface(canvas_size, pygame.SRCALPHA)
    for layer in layers:
        composite.blit(layer, (0, 0))
    screen.blit(composite, (canvas_view_rect.x, canvas_view_rect.y))
    pygame.draw.rect(screen, UI_BORDER, canvas_view_rect, 1)

    # Draw sidebar
    pygame.draw.rect(screen, UI_PANEL, sidebar_rect)
    pygame.draw.line(screen, UI_BORDER, (sidebar_rect.right, 0), (sidebar_rect.right, HEIGHT), 1)

    # Draw toolbar
    pygame.draw.rect(screen, UI_PANEL, toolbar_rect)
    pygame.draw.line(screen, UI_BORDER, (toolbar_rect.left, toolbar_rect.bottom), (WIDTH, toolbar_rect.bottom), 1)

    # Draw bottom bar
    pygame.draw.rect(screen, UI_PANEL, bottom_rect)
    pygame.draw.line(screen, UI_BORDER, (0, bottom_rect.top), (WIDTH, bottom_rect.top), 1)

    # Draw color panel
    pygame.draw.rect(screen, UI_BG, color_panel_rect, border_radius=5)
    pygame.draw.rect(screen, UI_BORDER, color_panel_rect, 1, border_radius=5)
    color_title = title_font.render("Color Picker", True, UI_TEXT)
    screen.blit(color_title, (color_panel_rect.x + 10, color_panel_rect.y + 5))

    # Draw color picker gradient
    for x in range(color_picker.width):
        for y in range(color_picker.height):
            hue = x / color_picker.width
            sat = 1 - y / color_picker.height
            rgb = colorsys.hsv_to_rgb(hue, sat, 1)
            color = tuple(int(c * 255) for c in rgb)
            screen.set_at((color_picker.x + x, color_picker.y + y), color)
    pygame.draw.rect(screen, UI_BORDER, color_picker, 1, border_radius=3)

    # Color preview
    pygame.draw.rect(screen, current_color, color_preview)
    pygame.draw.rect(screen, UI_BORDER, color_preview, 1)

    # Draw tools panel
    panel_rect = tools_panel["rect"]
    pygame.draw.rect(screen, UI_BG, panel_rect, border_radius=5)
    pygame.draw.rect(screen, UI_BORDER, panel_rect, 1, border_radius=5)
    panel_title = title_font.render(tools_panel["title"], True, UI_TEXT)
    screen.blit(panel_title, (panel_rect.x + 10, panel_rect.y + 5))

    # Draw tool buttons
    for name, info in tool_buttons.items():
        if "rect" in info:
            button_color = UI_ACCENT if tool == name else UI_BUTTON
            if info["rect"].collidepoint(mouse_pos):
                button_color = UI_HIGHLIGHT
            draw_rounded_rect(screen, info["rect"], button_color, radius=5)
            pygame.draw.rect(screen, UI_BORDER, info["rect"], 1, border_radius=5)
            text = small_font.render(info["text"], True, UI_TEXT)
            text_pos = (info["rect"].x + (info["rect"].width - text.get_width()) // 2,
                        info["rect"].y + (info["rect"].height - text.get_height()) // 2)
            screen.blit(text, text_pos)

    # Draw toolbar buttons (including window controls)
    for name, rect in toolbar_buttons.items():
        button_color = UI_BUTTON
        if rect.collidepoint(mouse_pos):
            button_color = UI_HIGHLIGHT
        draw_rounded_rect(screen, rect, button_color, radius=5)
        pygame.draw.rect(screen, UI_BORDER, rect, 1, border_radius=5)
        if name in ["minimize", "maximize", "close"]:
            # Draw symbols for window controls
            if name == "minimize":
                pygame.draw.line(screen, UI_TEXT, (rect.x + 10, rect.y + rect.height - 10),
                                 (rect.x + rect.width - 10, rect.y + rect.height - 10), 2)
            elif name == "maximize":
                pygame.draw.rect(screen, UI_TEXT, (rect.x + 10, rect.y + 10, rect.width - 20, rect.height - 20), 2)
            elif name == "close":
                # Split start_pos and end_pos into separate tuples for both lines of the "X"
                pygame.draw.line(screen, UI_TEXT, (rect.x + 10, rect.y + 10),
                                 (rect.x + rect.width - 10, rect.y + rect.height - 10), 2)
                pygame.draw.line(screen, UI_TEXT, (rect.x + 10, rect.y + rect.height - 10),
                                 (rect.x + rect.width - 10, rect.y + 10), 2)
        else:
            text = small_font.render(name.capitalize(), True, UI_TEXT)
            text_pos = (rect.x + (rect.width - text.get_width()) // 2,
                        rect.y + (rect.height - text.get_height()) // 2)
            screen.blit(text, text_pos)

    # Draw layer info
    layer_text = f"Layer: {current_layer + 1}/{len(layers)}"
    page_info = small_font.render(layer_text, True, UI_TEXT)
    screen.blit(page_info, (page_info_rect.x, page_info_rect.y))

    # Status bar
    status_text = f"Tool: {tool.capitalize()}"
    status = small_font.render(status_text, True, UI_TEXT)
    screen.blit(status, (WIDTH - status.get_width() - PADDING, HEIGHT - status.get_height() - PADDING))

    # Tool info
    tool_info = ""
    if tool == "brush":
        tool_info = "Click and drag to draw."
    elif tool == "erase":
        tool_info = "Click and drag to erase."
    elif tool == "fill":
        tool_info = "Click to fill with color."
    info_text = small_font.render(tool_info, True, UI_TEXT)
    screen.blit(info_text, (SIDEBAR_WIDTH + PADDING, HEIGHT - info_text.get_height() - PADDING))

    pygame.display.flip()

# Turn off the toy
pygame.quit()
sys.exit()