"""How plot windows reach the screen from inside PyMOL."""
import warnings

import matplotlib.pyplot as plt


def show(fig) -> None:
    """Display a figure without blocking PyMOL, regardless of what ran before it."""
    plt.ion()
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="FigureCanvasAgg is non-interactive")
        fig.show()
