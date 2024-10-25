from helper.Apex import apex_chart

def forecastPlot(df, columns, topic, chartType, today, language):
    # Create x-axis from 'Date' column and prepare line data
    xaxis = [str(date) for date in df['Date']]
    lines = {}
    for col in columns:
        lines[language.get(col, col)] = list(df[col])
    
    # Generate the forecast chart using the apex_chart function
    forecastChart = apex_chart(f'{language.get(topic, topic)} {language.get('price forecast', 'price forecast')}', chartType.lower(), 'smooth', xaxis, lines, 400, highlightPoint=str(today.date()))
    return forecastChart

def insightPlot(df, columns, language):
    # Create x-axis from 'Date' column and prepare line data for insights
    xaxis = [str(date) for date in df['Date']]
    lines = {}
    for col in columns:
        lines[language.get(col, col)] = list(df[col])
    
    # Generate the insight chart using the apex_chart function
    insightChart = apex_chart(language.get('Vegetable price forecast for next month', 'Vegetable price forecast for next month'), 'line', 'smooth', xaxis, lines, 400)
    return insightChart

def historicalPlot(df, columns, topic, language):
    # Create x-axis from 'Date' column and prepare line data for historical data
    xaxis = [str(date) for date in df['Date']]
    lines = {}
    for col in columns:
        lines[language.get(col, col)] = list(df[col])
    
    # Generate the historical chart using the apex_chart function
    historicalChart = apex_chart(topic, 'bar', 'stepline', xaxis, lines, 400)
    return historicalChart

def trendPlot(df, title, language):
    # Create x-axis from 'Date' column and prepare line data for trend analysis
    xaxis = [str(date) for date in df['Date']]
    lines = {language.get('Rolling Mean', 'Rolling Mean'): list(df['Rolling Mean'])}
    
    # Generate the trend chart using the apex_chart function
    trendChart = apex_chart(title, 'area', 'smooth', xaxis, lines, 400)
    return trendChart