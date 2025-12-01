import tempfile, webbrowser
import plotly.io as pio
from PySide6.QtWidgets import QLabel

def plotly_to_qwebengine(fig):
    html = pio.to_html(fig, full_html=True, include_plotlyjs='cdn')
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    tmp.write(html.encode())
    tmp.close()
    webbrowser.open(tmp.name)
    return QLabel("Plot opened in browser")
