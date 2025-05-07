from ttkbootstrap import Style

def apply_hover_style(style: Style):
    style.configure("Hover.TButton",
        font=("Arial", 10),
        background="#f7f7f7",
        foreground="#222",
        borderwidth=1,
        relief="flat"
    )
    style.map("Hover.TButton",
        background=[("active", "#b91c1c")],  # Deep red
        foreground=[("active", "#ffffff")]
    )