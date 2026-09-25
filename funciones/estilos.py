"""Paleta y estilos visuales de la aplicación."""
from tkinter import ttk

BG_PRIMARY = "#F8F9FA"
BG_SECONDARY = "#FFFFFF" 
BG_CARD = "#F1F5F9"
BORDER_COLOR = "#D1D5DB"
TEXT_PRIMARY = "#1F2937"
TEXT_SECONDARY = "#6B7280"
ACCENT_BLUE = "#3B82F6"
ACCENT_GREEN = "#10B981"
ACCENT_RED = "#EF4444"
ACCENT_PURPLE = "#8B5CF6"
ACCENT_ORANGE = "#F59E0B"
ACCENT_TEAL = "#14B8A6"

def configurar_estilos(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TLabel", background=BG_PRIMARY, foreground=TEXT_PRIMARY, font=("Segoe UI", 9))
    style.configure("TFrame", background=BG_PRIMARY)

    # Estilo para títulos de sección
    style.configure("SectionTitle.TLabel", font=("Segoe UI", 11, "bold"), foreground=TEXT_PRIMARY, background=BG_PRIMARY)

    # Estilo para texto secundario
    style.configure("Secondary.TLabel", font=("Segoe UI", 8), foreground=TEXT_SECONDARY, background=BG_PRIMARY)

    # Botones con estilo corporativo moderno
    style.configure("Minimal.TButton", 
                    font=("Segoe UI", 9), 
                    padding=(8, 4), 
                    background=BG_SECONDARY, 
                    borderwidth=1, 
                    relief="solid",
                    bordercolor=BORDER_COLOR)
    style.map("Minimal.TButton", 
              background=[("active", BG_CARD), ("pressed", "#E2E8F0")])

    # Botón de añadir con color distintivo
    style.configure("Add.TButton", 
                    font=("Segoe UI", 9), 
                    padding=(8, 4), 
                    background=ACCENT_TEAL, 
                    foreground="white",
                    borderwidth=0, 
                    relief="flat")
    style.map("Add.TButton", 
              background=[("active", "#0F766E"), ("pressed", "#0D9488")])

    # Botón de acción principal compacto
    style.configure("CompactPrimary.TButton", 
                    font=("Segoe UI", 9, "bold"), 
                    padding=(10, 5),
                    background=ACCENT_BLUE, 
                    foreground="white", 
                    borderwidth=0,
                    relief="flat")
    style.map("CompactPrimary.TButton", 
              background=[("active", "#2563EB"), ("disabled", "#9CA3AF")])

    # Botón de peligro sutil
    style.configure("DangerMinimal.TButton", 
                    font=("Segoe UI", 9), 
                    padding=(6, 4),
                    background=BG_SECONDARY, 
                    foreground=ACCENT_RED, 
                    borderwidth=1, 
                    relief="solid",
                    bordercolor="#FCA5A5")
    style.map("DangerMinimal.TButton", 
              background=[("active", "#FEF2F2")])

    # Radiobuttons personalizados
    style.configure("Minimal.TRadiobutton", 
                    background=BG_PRIMARY, 
                    foreground=TEXT_PRIMARY,
                    font=("Segoe UI", 9))

    # Botón de configuración compacto
    style.configure("Config.TButton", 
                    font=("Segoe UI", 9), 
                    padding=(4, 4), 
                    background=ACCENT_PURPLE, 
                    foreground="white",
                    borderwidth=0, 
                    relief="flat")
    style.map("Config.TButton", 
              background=[("active", "#7C3AED"), ("pressed", "#6D28D9")])

    # Botón primario para configuración
    style.configure("Primary.TButton", 
                    font=("Segoe UI", 9, "bold"), 
                    padding=(10, 6), 
                    background=ACCENT_BLUE, 
                    foreground="white",
                    borderwidth=0, 
                    relief="flat")
    style.map("Primary.TButton", 
              background=[("active", "#2563EB"), ("pressed", "#1D4ED8")])

    # Entradas de texto limpias
    style.configure("TEntry", 
                    borderwidth=1, 
                    relief="solid", 
                    bordercolor=BORDER_COLOR,
                    font=("Segoe UI", 9))
    return style
