import plotly.graph_objects as go

fig = go.Figure(data = [
    go.Bar(name= 'Category A', x=['Jan', 'Feb', 'Mar'], y=[20,14,23]),
    go.Bar(name= 'Category B', x=['Jan', 'Feb', 'Mar'], y=[21,12,20])

])

fig.update_layout(
    title = 'Simple bar chart',
    xaxis_title = 'Month',
    yaxis_title = 'Value',
    barmode = 'group'
)

fig.show()