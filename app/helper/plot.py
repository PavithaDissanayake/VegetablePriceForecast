from helper.Apex import apex_chart

def forecastPlot(df, columns, topic, chartType, today):
    xaxis = [str(date) for date in df['Date']]
    lines = {}
    for col in columns:
        lines[col] = list(df[col])
    forecastChart = apex_chart(f'{topic} price forecast', chartType.lower(), 'smooth', xaxis, lines, 400, highlightPoint=str(today.date()))
    return forecastChart

def insightPlot(df, columns):
    xaxis = [str(date) for date in df['Date']]
    lines = {}
    for col in columns:
        lines[col] = list(df[col])
    insightChart = apex_chart(f'Vegetable price forecast for next month', 'line', 'smooth', xaxis, lines, 400)
    return insightChart

def historicalPlot(df, columns, topic):
    xaxis = [str(date) for date in df['Date']]
    lines = {}
    for col in columns:
        lines[col] = list(df[col])
    historicalChart = apex_chart(topic, 'bar', 'stepline', xaxis, lines, 400)
    return historicalChart

def trendPlot(df, title):
    xaxis = [str(date) for date in df['Date']]
    lines = {'Rolling Mean': list(df['Rolling Mean'])}
    trendChart = apex_chart(title, 'area', 'smooth', xaxis, lines, 400)
    return trendChart