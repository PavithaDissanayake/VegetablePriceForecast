import streamlit as st
import pandas as pd
import altair as alt
from streamlit_extras.mandatory_date_range import date_range_picker

# creating the suitable chart
def create_area_chart(data, start_date, end_date, markets, today, minValue, maxValue, vegetable, translations):

    Date = translations.get('Date', 'Date')
    Market = translations.get('Market', 'Market')
    Price = translations.get('Price', 'Price')
    Rs = translations.get('Rs.', 'Rs.')

    data = data.copy()
    data.rename(columns={'Date': Date}, inplace=True)

    area_data = data.melt(id_vars=[Date], value_vars=markets, var_name=Market, value_name=Price)

    past_data = area_data[area_data[Date] <= today.date()]
    future_data = area_data[area_data[Date] >= today.date()]

    past_chart = alt.Chart(past_data).mark_area(opacity=0.6).encode(
        x=f'{Date}:T',
        y=alt.Y(f'{Price}:Q', title=f'{Price} ({Rs})', stack=None, scale=alt.Scale(domain=[minValue, maxValue])),
        color=f'{Market}:N',
        tooltip=[f'{Date}:T', f'{Market}:N', f'{Price}:Q']
    ).properties(height=650)

    future_chart = alt.Chart(future_data).mark_area(opacity=0.3).encode(
        x=f'{Date}:T',
        y=alt.Y(f'{Price}:Q', stack=None, scale=alt.Scale(domain=[minValue, maxValue])),
        color=f'{Market}:N',
        tooltip=[f'{Date}:T', f'{Market}:N', f'{Price}:Q']
    ).properties(height=650)

    # Vertical line for today
    today_line = alt.Chart(pd.DataFrame({f'{Date}': [today.date()]})).mark_rule(
        color='gray', strokeDash=[5, 3]
    ).encode(x=f'{Date}:T', tooltip=[f'{Date}:T'])

    # Today label
    today_label = alt.Chart(pd.DataFrame({f'{Date}': [today.date()], 'label': [translations.get('Today', 'Today')]})).mark_text(
        align='left', dx=5, dy=-200, color='gray'
    ).encode(x=f'{Date}:T', text='label')

    if today < start_date or today > end_date:
        combined_chart = alt.layer(past_chart, future_chart).properties(
            title=f'{vegetable} {translations.get('price', 'price')}', height=650
        )
    else:
        combined_chart = alt.layer(past_chart, future_chart, today_line, today_label).properties(
            title=f'{vegetable} {translations.get('price', 'price')}', height=650
        )

    return combined_chart

def create_bar_chart(data, start_date, end_date, markets, today, vegetable, translations):
    
    Date = translations.get('Date', 'Date')
    Market = translations.get('Market', 'Market')
    Price = translations.get('Price', 'Price')
    Rs = translations.get('Rs.', 'Rs.')

    data = data.copy()
    data.rename(columns={'Date': Date}, inplace=True)

    area_data = data.melt(id_vars=[Date], value_vars=markets, var_name=Market, value_name=Price)

    past_data = area_data[area_data[Date] <= today.date()]
    future_data = area_data[area_data[Date] >= today.date()]

    num_days = (end_date - start_date).days
    bar_width = 3 / num_days if num_days > 0 else 3

    past_chart = alt.Chart(past_data).mark_bar(size=bar_width*100).encode(
        x=f'{Date}:T',
        y=alt.Y(f'{Price}:Q', title=f'{Price} ({Rs})'),
        color=f'{Market}:N',
        tooltip=[f'{Date}:T', f'{Market}:N', f'{Price}:Q']
    ).properties(height=650)

    future_chart = alt.Chart(future_data).mark_bar(opacity=0.5, size=bar_width*100).encode(
        x=f'{Date}:T',
        y=alt.Y(f'{Price}:Q'),
        color=f'{Market}:N',
        tooltip=[f'{Date}:T', f'{Market}:N', f'{Price}:Q']
    ).properties(height=650)

    # Vertical line for today
    today_line = alt.Chart(pd.DataFrame({f'{Date}': [today.date()]})).mark_rule(
        color='gray', strokeDash=[5, 3]
    ).encode(x=f'{Date}:T', tooltip=[f'{Date}:T'])

    # Today label
    today_label = alt.Chart(pd.DataFrame({f'{Date}': [today.date()], 'label': [translations.get('Today', 'Today')]})).mark_text(
        align='left', dx=5, dy=-200, color='gray'
    ).encode(x=f'{Date}:T', text='label')

    if today < start_date or today > end_date:
        combined_chart = alt.layer(past_chart, future_chart).properties(
            title=f'{vegetable} {translations.get('price', 'price')}', height=650
        )
    else:
        combined_chart = alt.layer(past_chart, future_chart, today_line, today_label).properties(
            title=f'{vegetable} {translations.get('price', 'price')}', height=650
        )

    return combined_chart

def create_line_chart(data, start_date, end_date, markets, today, minValue, maxValue, vegetable, translations):
    
    Date = translations.get('Date', 'Date')
    Market = translations.get('Market', 'Market')
    Price = translations.get('Price', 'Price')
    Rs = translations.get('Rs.', 'Rs.')

    data = data.copy()
    data.rename(columns={'Date': Date}, inplace=True)

    area_data = data.melt(id_vars=[Date], value_vars=markets, var_name=Market, value_name=Price)

    past_data = area_data[area_data[Date] <= today.date()]
    future_data = area_data[area_data[Date] >= today.date()]

    past_chart = alt.Chart(past_data).mark_line().encode(
        x=f'{Date}:T',
        y=alt.Y(f'{Price}:Q', title=f'{Price} ({Rs})', stack=None, scale=alt.Scale(domain=[minValue, maxValue])),
        color=f'{Market}:N',
        tooltip=[f'{Date}:T', f'{Market}:N', f'{Price}:Q']
    ).properties(height=650)

    future_chart = alt.Chart(future_data).mark_line(strokeDash=[5, 3]).encode(
        x=f'{Date}:T',
        y=alt.Y(f'{Price}:Q', stack=None, scale=alt.Scale(domain=[minValue, maxValue])),
        color=f'{Market}:N',
        tooltip=[f'{Date}:T', f'{Market}:N', f'{Price}:Q']
    ).properties(height=650)

    # Vertical line for today
    today_line = alt.Chart(pd.DataFrame({f'{Date}': [today.date()]})).mark_rule(
        color='gray', strokeDash=[5, 3]
    ).encode(x=f'{Date}:T', tooltip=[f'{Date}:T'])

    # Today label
    today_label = alt.Chart(pd.DataFrame({f'{Date}': [today.date()], 'label': [translations.get('Today', 'Today')]})).mark_text(
        align='left', dx=5, dy=-200, color='gray'
    ).encode(x=f'{Date}:T', text='label')

    if today < start_date or today > end_date:
        combined_chart = alt.layer(past_chart, future_chart).properties(
            title=f'{vegetable} {translations.get('price', 'price')}', height=650
        )
    else:
        combined_chart = alt.layer(past_chart, future_chart, today_line, today_label).properties(
            title=f'{vegetable} {translations.get('price', 'price')}', height=650
        )

    return combined_chart

def create_scatter_plot(data, start_date, end_date, markets, today, minValue, maxValue, vegetable, translations):
    
    Date = translations.get('Date', 'Date')
    Market = translations.get('Market', 'Market')
    Price = translations.get('Price', 'Price')
    Rs = translations.get('Rs.', 'Rs.')

    data = data.copy()
    data.rename(columns={'Date': Date}, inplace=True)

    area_data = data.melt(id_vars=[Date], value_vars=markets, var_name=Market, value_name=Price)

    past_data = area_data[area_data[Date] < today.date()]
    future_data = area_data[area_data[Date] >= today.date()]

    num_days = (end_date - start_date).days
    scatter_size = 100 / num_days if num_days > 0 else 100

    past_chart = alt.Chart(past_data).mark_circle(size=scatter_size*100).encode(
        x=f'{Date}:T',
        y=alt.Y(f'{Price}:Q', title=f'{Price} ({Rs})', stack=None, scale=alt.Scale(domain=[minValue, maxValue])),
        color=f'{Market}:N',
        tooltip=[f'{Date}:T', f'{Market}:N', f'{Price}:Q']
    ).properties(height=650)

    future_chart = alt.Chart(future_data).mark_circle(opacity=0.5, size=scatter_size*100).encode(
        x=f'{Date}:T',
        y=alt.Y(f'{Price}:Q', stack=None, scale=alt.Scale(domain=[minValue, maxValue])),
        color=f'{Market}:N',
        tooltip=[f'{Date}:T', f'{Market}:N', f'{Price}:Q']
    ).properties(height=650)

    # Vertical line for today
    today_line = alt.Chart(pd.DataFrame({f'{Date}': [today.date()]})).mark_rule(
        color='gray', strokeDash=[5, 3]
    ).encode(x=f'{Date}:T', tooltip=[f'{Date}:T'])

    # Today label
    today_label = alt.Chart(pd.DataFrame({f'{Date}': [today.date()], 'label': [translations.get('Today', 'Today')]})).mark_text(
        align='left', dx=5, dy=-200, color='gray'
    ).encode(x=f'{Date}:T', text='label')

    if today < start_date or today > end_date:
        combined_chart = alt.layer(past_chart, future_chart).properties(
            title=f'{vegetable} {translations.get('price', 'price')}', height=650
        )
    else:
        combined_chart = alt.layer(past_chart, future_chart, today_line, today_label).properties(
            title=f'{vegetable} {translations.get('price', 'price')}', height=650
        )

    return combined_chart

def create_step_chart(data, start_date, end_date, markets, today, minValue, maxValue, vegetable, translations):
    
    Date = translations.get('Date', 'Date')
    Market = translations.get('Market', 'Market')
    Price = translations.get('Price', 'Price')
    Rs = translations.get('Rs.', 'Rs.')

    data = data.copy()
    data.rename(columns={'Date': Date}, inplace=True)

    area_data = data.melt(id_vars=[Date], value_vars=markets, var_name=Market, value_name=Price)

    past_data = area_data[area_data[Date] <= today.date()]
    future_data = area_data[area_data[Date] >= today.date()]

    past_chart = alt.Chart(past_data).mark_line(interpolate='step-after').encode(
        x=f'{Date}:T',
        y=alt.Y(f'{Price}:Q', title=f'{Price} ({Rs})', stack=None, scale=alt.Scale(domain=[minValue, maxValue])),
        color=f'{Market}:N',
        tooltip=[f'{Date}:T', f'{Market}:N', f'{Price}:Q']
    ).properties(height=650)

    future_chart = alt.Chart(future_data).mark_line(interpolate='step-after', strokeDash=[5, 3]).encode(
        x=f'{Date}:T',
        y=alt.Y(f'{Price}:Q', stack=None, scale=alt.Scale(domain=[minValue, maxValue])),
        color=f'{Market}:N',
        tooltip=[f'{Date}:T', f'{Market}:N', f'{Price}:Q']
    ).properties(height=650)

    # Vertical line for today
    today_line = alt.Chart(pd.DataFrame({f'{Date}': [today.date()]})).mark_rule(
        color='gray', strokeDash=[5, 3]
    ).encode(x=f'{Date}:T', tooltip=[f'{Date}:T'])

    # Today label
    today_label = alt.Chart(pd.DataFrame({f'{Date}': [today.date()], 'label': [translations.get('Today', 'Today')]})).mark_text(
        align='left', dx=5, dy=-200, color='gray'
    ).encode(x=f'{Date}:T', text='label')

    if today < start_date or today > end_date:
        combined_chart = alt.layer(past_chart, future_chart).properties(
            title=f'{vegetable} {translations.get('price', 'price')}', height=650
        )
    else:
        combined_chart = alt.layer(past_chart, future_chart, today_line, today_label).properties(
            title=f'{vegetable} {translations.get('price', 'price')}', height=650
        )

    return combined_chart

def show_raw_data(data, markets, today, primaryColor, translations):
    
    selected_columns = ['Date'] + markets
    final_data = data[selected_columns]

    Date = translations.get('Date', 'Date')
    final_data.rename(columns={'Date': Date}, inplace=True)

    def highlight(row):
        return [f'background-color: {primaryColor}' if row[Date] == today.date() else f'color: grey' if row[Date] > today.date() else '' for _ in row]
    
    final_data = final_data.style.apply(highlight, axis=1)

    format_dict = {column: lambda x: translations.get('Rs.', 'Rs.')+f' {x:.2f}' if pd.notnull(x) else 'N/A' for column in final_data.columns[1:]}
    
    final_data = final_data.format(format_dict)

    return final_data

@st.fragment
def vegetableVsMarket(today, defaultStart, defaultEnd, vegetables, dataframes, primaryColor, translations):

    data, plot = st.columns([2, 3])

    # choose a vegetable
    vegetable = data.selectbox(translations.get('Select the vegetable', 'Select the vegetable'), options=vegetables)
    df = dataframes[vegetable]

    markets = sorted(df.drop(columns='Date').columns)

    # create metrics for the following week
    filtered = df[(df['Date'] >= today.date()) & (df['Date'] <= today.date() + pd.Timedelta(days=6))]

    def calculate_metrics(dataframe, today):
        metrics = {}
        for market in dataframe.columns[1:]:
            today_data = dataframe.loc[dataframe['Date'] == today.date()]
            today_value = today_data[market].values[0] if not today_data.empty else 0.00

            yesterday_data = dataframe.loc[dataframe['Date'] == today.date() - pd.Timedelta(days=1)]
            yesterday_value = yesterday_data[market].values[0] if not yesterday_data.empty else 0.00

            change_from_yesterday = today_value - yesterday_value
            metrics[market] = (today_value, change_from_yesterday)

        return metrics

    metrics = calculate_metrics(df, today)
    maxMarkets = []
    minMarkets = []
    max_value, min_value = 0, 0

    if len(metrics) >= 3:
        noColumns = 3
    else:
        noColumns = len(metrics)
    
    if len(metrics) >= 4:
        max_value = max(metrics.values(), key=lambda x: x[0])
        min_value = min(metrics.values(), key=lambda x: x[0])
        maxMarkets = [k for k, v in metrics.items() if v == max_value]
        minMarkets = [k for k, v in metrics.items() if v == min_value]

    metric = data.columns(noColumns)

    # show metrics and data for the week
    for i, m in enumerate(markets):
        with metric[i % noColumns].container():
            st.html(f'<span class="metricsDiv"></span>')
            if max_value != min_value:
                if m in maxMarkets:
                    st.html(f'<span class="max"></span>')
                elif m in minMarkets:
                    st.html(f'<span class="min"></span>')
            st.metric(label=m, label_visibility='visible', value=translations.get('Rs.', 'Rs.')+' {:.2f}'.format(metrics[m][0]), delta=round(metrics[m][1], 2), delta_color='inverse' if metrics[m][1] != 0 else 'off')
            with st.container():
                with st.expander(translations.get('Coming week', 'Coming week')):
                    for index, day in filtered.iterrows():
                        if day['Date'] != today.date():
                            month = translations.get(day['Date'].strftime('%B'), day['Date'].strftime('%B'))
                            date = day['Date'].strftime('%d')
                            st.write(f"{month} {date} - {translations.get('Rs.', 'Rs.')} {day[m]:.2f}")

    # start and end dates for the chart
    start, end = plot.columns([1, 1])
    with start.container():
        date_range = date_range_picker(title=translations.get("Select date range", "Select date range"), default_start=max(defaultStart, df['Date'].min()), default_end=min(defaultEnd, df['Date'].max()), min_date=df['Date'].min(), max_date=df['Date'].max())
    
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])

    # market selection
    market = end.multiselect(translations.get('Select market', 'Select market'), options=list(markets), default=list(markets))

    filtered_table = df[(df['Date'] >= start_date.date()) & (df['Date'] <= end_date.date())]

    # Choose the chart type
    chart_type = start.selectbox(translations.get("Select chart type", "Select chart type"), index=2, options=[translations.get(chart, chart) for chart in ["Area Chart", "Bar Chart", "Line Chart", "Scatter Plot", "Step Chart", "Raw Data"]])
    
    if len(market) == 0:
        minValue = 0
        maxValue = 100
    else:
        minValue = max(filtered_table[market].min().min()-10, 0)
        maxValue = filtered_table[market].max().max()+10

    combined_chart = None
    if chart_type == translations.get("Area Chart", "Area Chart"):
        combined_chart = create_area_chart(filtered_table, start_date, end_date, market, today, minValue, maxValue, vegetable, translations)
    elif chart_type == translations.get("Bar Chart", "Bar Chart"):
        combined_chart = create_bar_chart(filtered_table, start_date, end_date, market, today, vegetable, translations)
    elif chart_type == translations.get("Line Chart", "Line Chart"):
        combined_chart = create_line_chart(filtered_table, start_date, end_date, market, today, minValue, maxValue, vegetable, translations)
    elif chart_type == translations.get("Scatter Plot", "Scatter Plot"):
        combined_chart = create_scatter_plot(filtered_table, start_date, end_date, market, today, minValue, maxValue, vegetable, translations)
    elif chart_type == translations.get("Step Chart", "Step Chart"):
        combined_chart = create_step_chart(filtered_table, start_date, end_date, market, today, minValue, maxValue, vegetable, translations)
    else:
        num_days = (end_date - start_date).days
        if num_days >= 16:
            height = 650
        else:
            height = 55 + (num_days+1)*35
        plot.dataframe(show_raw_data(filtered_table, market, today, primaryColor, translations), use_container_width=True, height=height, hide_index=True, column_order=[translations.get('Date', 'Date')]+sorted(filtered_table.columns[1:]))

    if combined_chart is not None:
        with plot.container():
            st.html(f'<span class="chartDiv"></span>')
            st.altair_chart(combined_chart, use_container_width=True)
