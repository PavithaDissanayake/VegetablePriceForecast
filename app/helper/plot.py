from helper.Apex import apex_chart

def forecastPlot(df, columns, topic, chartType, today, language):
    xaxis = [str(date) for date in df['Date']]
    lines = {}
    for col in columns:
        lines[language.get(col, col)] = list(df[col])
    forecastChart = apex_chart(f'{language.get(topic, topic)} {language.get('price forecast', 'price forecast')}', chartType.lower(), 'smooth', xaxis, lines, 400, highlightPoint=str(today.date()))
    return forecastChart

def insightPlot(df, columns, language):
    xaxis = [str(date) for date in df['Date']]
    lines = {}
    for col in columns:
        lines[language.get(col, col)] = list(df[col])
    insightChart = apex_chart(language.get('Vegetable price forecast for next month', 'Vegetable price forecast for next month'), 'line', 'smooth', xaxis, lines, 400)
    return insightChart

def historicalPlot(df, columns, topic, language):
    xaxis = [str(date) for date in df['Date']]
    lines = {}
    for col in columns:
        lines[language.get(col, col)] = list(df[col])
    historicalChart = apex_chart(topic, 'bar', 'stepline', xaxis, lines, 400)
    return historicalChart

def trendPlot(df, title, language):
    xaxis = [str(date) for date in df['Date']]
    lines = {language.get('Rolling Mean', 'Rolling Mean'): list(df['Rolling Mean'])}
    trendChart = apex_chart(title, 'area', 'smooth', xaxis, lines, 400)
    return trendChart