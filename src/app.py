import pandas as pd
import plotly.graph_objects as go


def plot(border_df, inner_df):
    fig = go.Figure()

    # Grid data points (to divide whole area in small boxes in grid format)
    fig.add_trace(go.Scattermapbox(
        lat=border_df['lat'],
        lon=border_df['lon'],
        mode='markers',
        showlegend=False,
        name='Grid point',
        marker=go.scattermapbox.Marker(
            size=10,
            color='red'
        ),
        hovertext=border_df['name']
    ))

    # Actual rainfall data points (one for each grid box)
    # The size of the markers depend on the amount of rainfall
    # Larger the size, more the rainfall and vice-versa
    fig.add_trace(go.Scattermapbox(
        lat=inner_df['lat'],
        lon=inner_df['lon'],
        mode='markers',
        name='July 2022 Rainfall (mm)',
        marker=go.scattermapbox.Marker(
            size=inner_df['rainfall'],
            sizemode='diameter',
            sizemin=10,
            sizeref=3,
            color='blue'
        ),
        hovertext=inner_df['rainfall'],
    ))

    fig.update_layout(
        mapbox=dict(
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=border_df['lat'].mean(),
                lon=border_df['lon'].mean()
            ),
            pitch=0,
            zoom=7,
            style="open-street-map"
        )
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()


if __name__ == '__main__':
    
    # Grid data points
    border_df = pd.read_csv("resources\datasets\grid_points.csv")

    # Actual rainfall data points
    inner_df = pd.read_csv("resources\datasets\\actual_points.csv")

    plot(border_df, inner_df)

