"""Dashboard utilities."""

import ttkbootstrap as ttk


def build_scrollable_frame(f_parent: ttk.Frame, width=None, **kwargs) -> ttk.Frame:
    """Build and return a scrollable frame.

    Args:
        f_parent (Frame): Parent fram, master of the main frame.
        width (int): Minimum width for the scrollable frame.
        **kwargs: Keyword arguments to pass to scrollable frame when init.

    Returns:
        Frame: The scrollable frame.

    """
    f_main = ttk.Frame(f_parent)
    f_main.pack(fill="both", expand=True)

    canvas = ttk.Canvas(f_main)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(f_main, command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    f_scrollable = ttk.Frame(canvas, **kwargs)

    f_scrollable.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=f_scrollable, anchor="nw", width=width)
    canvas.configure(yscrollcommand=scrollbar.set)

    return f_scrollable
