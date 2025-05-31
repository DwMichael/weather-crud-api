import pandas as pd

def process_simulation_data(results, chart_mode='static'):
    df = pd.DataFrame(results)
    df['date'] = pd.to_datetime(df['date'])

    df_long = df.melt(
        id_vars='date',
        value_vars=['water_amount', 'pumped_up_water', 'pumped_out_water', 'saved_water'],
        var_name='type',
        value_name='value'
    )
    if chart_mode == 'static':
        df_long.loc[df_long['type'] == 'pumped_out_water', 'value'] *= -1

    translation_map = {
        'water_amount': 'Poziom wody [L]',
        'pumped_up_water': 'Wpompowana woda [L]',
        'pumped_out_water': 'Zużyta woda [L]',
        'saved_water': 'Zaoszczędzona woda [L]'
    }

    df_long['type'] = df_long['type'].map(translation_map)

    return df, df_long
