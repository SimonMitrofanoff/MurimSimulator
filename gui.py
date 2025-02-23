import tkinter as tk
from tkinter import font
from character import create_random_character, trait_stat_relationships, negative_trait_stat_relationships, secret_bodies
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import os  # Import os for handling relative paths
from PIL import Image, ImageTk  # Import PIL for image handling

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None

        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip:
            return

        # Position the tooltip near the widget
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)  # Remove window decorations
        self.tooltip.wm_geometry(f"+{x}+{y}")

        # Modern tooltip style
        frame = tk.Frame(self.tooltip, bg="#e3f2fd", relief="solid", borderwidth=1)
        frame.pack()
        label = tk.Label(frame, text=self.text, font=("Arial", 10), bg="#e3f2fd", fg="#333", wraplength=200, justify="left")
        label.pack(padx=5, pady=5)

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


def add_tooltip(widget, text):
    Tooltip(widget, text)


def format_bonuses(traits_list):
    """
    Format the bonuses/maluses of a list of traits into a readable tooltip format.
    """
    if not traits_list:
        return ""

    tooltip_text = ""
    for trait in traits_list:
        bonuses = trait_stat_relationships.get(trait, negative_trait_stat_relationships.get(trait, None))
        if bonuses:
            formatted_bonuses = "\n".join([f"{key}: {value}" for key, value in bonuses.items()])
            tooltip_text += f"{trait}\n{'-' * len(trait)}\n{formatted_bonuses}\n\n"

    return tooltip_text.strip()

def draw_radar_chart(primary_stats):
    categories = list(primary_stats.keys())
    values = list(primary_stats.values())
    values += values[:1]  # Loop back to close the chart

    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(2.5, 2.5), subplot_kw=dict(polar=True))

    # Match GUI background color
    background_color = "#f4f4f4"
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)

    # Set max value for the chart (20)
    max_value = 20
    ax.set_ylim(0, max_value)

    ax.fill(angles, values, color="blue", alpha=0.2)
    ax.plot(angles, values, color="blue", linewidth=1.5)
    ax.set_yticks([5, 10, 15, 20])
    ax.set_yticklabels([])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=8)

    fig.tight_layout(pad=0)
    return fig


def show_character():
    character = create_random_character()

    tooltips_data = {**trait_stat_relationships, **negative_trait_stat_relationships, **secret_bodies}

    primary_stats = {
        "Strength": character["Strength"],
        "Dexterity": character["Dexterity"],
        "Intellect": character["Intellect"],
        "Perception": character["Perception"],
        "Luck": character["Luck"],
        "Agility": character["Agility"],
        "Resilience": character["Resilience"],
        "Social": character["Social"],
    }
    secondary_stats = character["Secondary Stats"]

    # 🟢 CLEAR ALL FRAMES BEFORE UPDATING
    for frame in [details_frame, primary_stats_frame, secondary_stats_frame]:
        for widget in frame.winfo_children():
            widget.destroy()

    # 🟢 CHARACTER DETAILS (Grid Row 0)
    details_labels = [
        ("Name", character["Name"]), ("Sex", character["Sex"]), ("Age", character["Age"]),
        ("Background", character["Background"]), ("Affiliation", character["Affiliation"] or "None"),
        ("Secret Body", character["Secret Body"] if character["Secret Body"] != "None" else "None"),
        ("QI", character["QI"]), ("Lifespan", character["Lifespan"])
    ]

    row_num = 0
    for label_text, value in details_labels:
        tk.Label(details_frame, text=f"{label_text}: {value}", font=body_font, bg="#f4f4f4", fg="#333", anchor="w").grid(
            row=row_num, column=0, padx=10, pady=3, sticky="w")
        row_num += 1

    # 🟢 TRAITS & FLAWS
    traits_labels = [
        ("Native Traits", character["Secret Talents (Native)"]),
        ("Acquired Traits", character["Acquired Talents"]),
        ("Flaws", character["Negative Traits (Native)"]),
        ("Acquired Flaws", character["Acquired Negative Traits"])
    ]

    for label_text, traits in traits_labels:
        row_num += 1
        text = f"{label_text}: {', '.join(traits) if traits else 'None'}"
        tk.Label(details_frame, text=text, font=body_font, bg="#f4f4f4", fg="#333", anchor="w").grid(
            row=row_num, column=0, padx=10, pady=3, sticky="w")

        # "?" Tooltip for bonuses/maluses
        if traits:
            tooltip_text = format_bonuses(traits)
            if tooltip_text:
                tooltip_label = tk.Label(details_frame, text="?", font=("Arial", 12, "bold"), bg="#f4f4f4", fg="#007ACC")
                tooltip_label.grid(row=row_num, column=1, padx=5)
                add_tooltip(tooltip_label, tooltip_text)

    # 🟢 PRIMARY STATS, CHART, AND IMAGE (Grid Row 1)
    chart_frame = tk.Frame(primary_stats_frame, bg="#f4f4f4")
    chart_frame.grid(row=0, column=0, padx=10, pady=5)

    fig = draw_radar_chart(primary_stats)
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()
    plt.close(fig)

    stats_frame = tk.Frame(primary_stats_frame, bg="#f4f4f4")
    stats_frame.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(stats_frame, text="Primary Stats", font=body_font, bg="#f4f4f4", fg="#333").pack(pady=5)

    for stat, base_value in character["Base Stats"].items():
        final_value = character[stat]
        bonus = final_value - base_value
        stat_display = f"{stat}: {final_value} ({'+' if bonus > 0 else ''}{bonus})" if bonus else f"{stat}: {final_value}"
        tk.Label(stats_frame, text=stat_display, font=body_font, bg="#f4f4f4", fg="#333", anchor="w").pack(anchor="w")

    # 🟢 CHARACTER IMAGE ON RIGHT (Fixed Position)
    try:
        image_filename = "Female Char 1.png" if character["Sex"] == "Female" else "Male Char 1.png"
        image_path = os.path.join(os.path.dirname(__file__), "assets", image_filename)

        img = Image.open(image_path)
        img = img.resize((200, 300), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        image_label = tk.Label(primary_stats_frame, image=img_tk, bg="#f4f4f4")
        image_label.image = img_tk  # Keep reference
        image_label.grid(row=0, column=2, padx=20, pady=10)
    except FileNotFoundError:
        print(f"Error: Image not found at {image_path}. Ensure the 'assets/' folder contains the images.")

    # 🟢 SECONDARY STATS (Grid Row 2) - CENTERED
    tk.Label(secondary_stats_frame, text="Secondary Stats", font=body_font, bg="#f4f4f4", fg="#333").grid(
        row=0, column=0, columnspan=4, pady=5)

    stats_per_row = 4
    row, col = 1, 0

    for stat, value in secondary_stats.items():
        if not isinstance(value, dict):
            label = tk.Label(secondary_stats_frame, text=f"{stat}: {value}", font=("Arial", 12), bg="#f4f4f4", fg="#333")
            label.grid(row=row, column=col, padx=10, pady=3, sticky="w")
            col += 1
            if col >= stats_per_row:
                col = 0
                row += 1

    # 🟢 SECONDARY STATS WITH SUBCATEGORIES
    for stat, value in secondary_stats.items():
        if isinstance(value, dict):
            tk.Label(secondary_stats_frame, text=f"{stat}:", font=("Arial", 12, "bold"), bg="#f4f4f4", fg="#333").grid(
                row=row, column=0, columnspan=4, sticky="w", pady=5)
            row += 1
            sub_col = 0
            for sub_stat, sub_value in value.items():
                label = tk.Label(secondary_stats_frame, text=f"{sub_stat}: {sub_value}", font=("Arial", 12),
                                 bg="#f4f4f4", fg="#333")
                label.grid(row=row, column=sub_col, padx=10, pady=3, sticky="w")
                sub_col += 1
                if sub_col >= stats_per_row:
                    sub_col = 0
                    row += 1
            row += 1




def run_gui():
    global details_frame, primary_stats_frame, secondary_stats_frame, body_font

    window = tk.Tk()
    window.title("Murim Adventure V.0 Character Randomizer")
    window.geometry("750x1100")
    window.configure(bg="#f4f4f4")

    header_font = font.Font(family="Helvetica", size=18, weight="bold")
    body_font = font.Font(family="Helvetica", size=12)

    header_label = tk.Label(window, text="MURIM ADVENTURE V.0\nCHARACTER RANDOMIZER", bg="#f4f4f4", fg="#333", font=header_font)
    header_label.pack(pady=10)

    details_frame = tk.Frame(window, bg="#f4f4f4")
    details_frame.pack(pady=10, fill="x")

    primary_stats_frame = tk.Frame(window, bg="#f4f4f4")
    primary_stats_frame.pack(pady=10, fill="x")

    secondary_stats_frame = tk.Frame(window, bg="#f4f4f4")
    secondary_stats_frame.pack(pady=10, fill="x")

    randomize_button = tk.Button(window, text="Randomize Character", command=show_character, bg="#4CAF50", fg="white", font=body_font, relief="raised", padx=20, pady=10)
    randomize_button.pack(pady=20)

    show_character()

    window.mainloop()
