import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def generate_graph(state):
    electricity_prices = [float(item['price']) for item in state['energy_prices_per_hour']]
    weather_forecast = [item['temperature'] for item in state['weather_forecast']]
    setpoints = [item['setpoint'] for item in state['setpoints']]
    bandwidth = state['bandwidth']
    temperature_setpoint = state['temperature_setpoint']

    hours = np.arange(24)
    min_setpoint = temperature_setpoint - bandwidth / 2
    max_setpoint = temperature_setpoint + bandwidth / 2

    data = pd.DataFrame({
        'Hour': hours,
        'Setpoints': setpoints,
        'Weather forecast': weather_forecast,
        'Electricity prices (Scaled)': np.interp(electricity_prices, (min(electricity_prices), max(electricity_prices)), (min_setpoint, max_setpoint))
    })

    plt.figure(figsize=(16, 9))
    sns.set_theme(style="darkgrid")

    sns.lineplot(x='Hour', y='Setpoints', data=data, marker='o', color='#0077b6', linewidth=2, label='Setpoints')
    sns.lineplot(x='Hour', y='Weather forecast', data=data, marker='s', color='#52b788', linestyle='--', linewidth=2, label='Weather forecast')
    sns.lineplot(x='Hour', y='Electricity prices (Scaled)', data=data, marker='d', color='#f4a261', linestyle='-.', linewidth=2, label='Electricity Prices (Scaled)')
    plt.axhline(y=temperature_setpoint, color='#e63946', linestyle='-', linewidth=2, label='Baseline temperature')
    plt.fill_between(hours, min_setpoint, max_setpoint, color='#ffcb77', alpha=0.3, label='Bandwidth range')

    plt.xlabel('Hour of the day', fontsize=14, fontweight='bold', labelpad=15)
    plt.ylabel('Value', fontsize=14, fontweight='bold', labelpad=15)
    plt.title('Temperature setpoints, Weather forecast, and Electricity prices', fontsize=18, fontweight='bold', pad=20)
    plt.legend(loc='lower right', fontsize=12)
    plt.xticks(hours, fontsize=12)
    plt.yticks(fontsize=12)

    plt.xlim(-0.5, 23.5)

    plt.savefig('setpoints.png', dpi=300, bbox_inches='tight')
    plt.show()
