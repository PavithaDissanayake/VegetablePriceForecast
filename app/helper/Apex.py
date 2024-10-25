def darken_color(color, factor=0.5):
    # Convert hex color to RGB, darken it by the specified factor
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    
    # Apply factor to darken the color, ensuring values don't go below 0
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))

    return f'#{r:02x}{g:02x}{b:02x}'

def apex_chart(title, type, curve, xaxis, lines, height, highlightPoint=None, hightlightSeries=None, minValue=None, maxValue=None):
    
    # Downsample x-axis and lines if too many data points
    if len(xaxis) > 100:
        xaxis = xaxis[::10]
        for name, data in lines.items():
            lines[name] = data[::10]

    colors = ['#008ffb', '#00e396', '#feb019', '#ff4560', '#775dd0', '#546E7A', '#26a69a', '#D10CE8', '#FFD700', '#FF6347']

    def get_series(lines):
        # Generate series data for the chart
        series = ''
        for i, (name, data) in enumerate(lines.items()):
            strData = ','.join(str(d) for d in data)
            color = colors[i % len(colors)]
            series += (f"""{{
                'name': '{name}',
                'data': [{strData}],
                'color': '{color}'
            }},""")
        series = series[:-1]  # Remove trailing comma
        return series
    
    strXAxis = ','.join(f"'{x}'" for x in xaxis)
    if len(lines) > 0:
        data_length = max(len(data) for data in lines.values())
    else:
        data_length = 0
    no_data_warning = data_length < 50  # Check if there is enough data

    plot_options = ""
    if type == 'bar':
        # Set bar chart specific options
        plot_options = f"""
        plotOptions: {{
          bar: {{
            borderRadius: 100/{data_length},
            borderRadiusApplication: 'end',
            dataLabels: {{
              position: 'top'
            }}
          }}
        }},
        """
    
    markers = ""
    discrete_markers = []

    # Add highlight markers for specific points
    if highlightPoint and highlightPoint in xaxis:
        index = xaxis.index(highlightPoint)
        for i in range(len(lines)):  # Loop through each series
            original_color = colors[i % len(colors)]
            discrete_markers.append(f"""{{
                seriesIndex: {i},
                dataPointIndex: {index},
                fillColor: '{darken_color(original_color)}',
                strokeColor: '#fff',
                size: 8
            }}""")

    # Add markers for min and max values if specified
    if minValue:
        index = xaxis.index(minValue[0])

        discrete_markers.append(f"""{{
            seriesIndex: {minValue[1]},
            dataPointIndex: {index},
            fillColor: '#FF0000',
            strokeColor: '#fff',
            size: 8
        }}""")

    if maxValue:
        index = xaxis.index(maxValue[0])

        discrete_markers.append(f"""{{
            seriesIndex: {maxValue[1]},
            dataPointIndex: {index},
            fillColor: '#00FF00',
            strokeColor: '#fff',
            size: 8
        }}""")

    markers = f"""
        markers: {{
            discrete: [{', '.join(discrete_markers)}]
        }},
        """        
    
    # Create the ApexCharts HTML template
    apex_chart = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    </head>
    <body>
      <div id="chart"></div>
      <script>
        var options = {{
          chart: {{
            type: '{type}',
            height: {height},
            animations: {{
              enabled: {str(no_data_warning).lower()}
            }}
          }},
          {plot_options}
          series: [{get_series(lines)}],
          xaxis: {{
            categories: [{strXAxis}]
          }},
          stroke: {{
            curve: '{curve}'
          }},
          title: {{
            text: '{title}'
          }},
          noData: {{
            text: 'Please fill all boxes to view the chart',
            align: 'center',
            verticalAlign: 'middle',
            style: {{
              color: '#000',
              fontSize: '16px'
            }}
          }},
          {markers}
        }};

        var chart = new ApexCharts(document.querySelector("#chart"), options);
        chart.render();
      </script>
    </body>
    </html>        
    """

    return apex_chart
