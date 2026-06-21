import pandas as pd
from typing import Dict, Any

class ChartRenderer:
    def __init__(self):
        try:
            import plotly.express as px
            import plotly.graph_objects as go
            self.px = px
            self.go = go
            self.available = True
        except ImportError:
            self.available = False

    def render(self, spec: Dict[str, Any], data: list) -> Any:
        if not self.available or spec.get("chart_type") == "table":
            return None
            
        df = pd.DataFrame(data)
        if df.empty:
            return None
            
        chart_type = spec.get("chart_type")
        x = spec.get("x")
        y = spec.get("y")
        color = spec.get("color")
        title = spec.get("title")
        
        fig = None
        
        if chart_type == "bar":
            fig = self.px.bar(df, x=x, y=y, title=title, color=color, barmode='group')
        elif chart_type == "horizontal_bar":
            fig = self.px.bar(df, x=x, y=y, title=title, color=color, orientation='h')
        elif chart_type == "grouped_bar":
            fig = self.px.bar(df, x=x, y=y, color=color, barmode='group', title=title)
        elif chart_type == "stacked_bar":
            fig = self.px.bar(df, x=x, y=y, color=color, barmode='stack', title=title)
        elif chart_type == "line":
            fig = self.px.line(df, x=x, y=y, color=color, title=title)
        elif chart_type == "pie":
            fig = self.px.pie(df, names=x, values=y, title=title)
            
        if fig and spec.get("unit"):
            fig.update_layout(yaxis_title=f"{y} ({spec['unit']})" if chart_type != "horizontal_bar" else y)
            
        return fig
