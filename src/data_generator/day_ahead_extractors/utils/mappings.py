FORECAST_MAPPING = {
    'Krajowe zapotrzebowanie na moc': 'load_forecast',
    'Suma zdolności wytwórczych JWCD': 'capacity_jwcd_forecast',
    'Suma zdolności wytwórczych nJWCD': 'capacity_njwcd_forecast',
    'Generacja JWCD': 'generation_jwcd_forecast',
    'Generacja nJWCD': 'generation_njwcd_forecast',
    'Generacja źródeł wiatrowych': 'generation_wind_forecast',
    'Generacja źródeł fotowoltaicznych': 'generation_solar_forecast',
    'Wymagana rezerwa mocy ponad zapotrzebowanie': 'reserve1_forecast',
    'Wymagana rezerwa mocy poniżej zapotrzebowania': 'reserve2_forecast',
}

ACTUAL_MAPPING = {
    'Krajowe zapotrzebowanie na moc': 'load_actual',
    'Sumaryczna generacja JWCD': 'generation_jwcd_actual',
    'Sumaryczna generacja nJWCD': 'generation_njwcd_actual',
    'Generacja PI': 'generation_pi_actual',
    'Generacja IRZ': 'generation_irz_actual',
    'Generacja źródeł wiatrowych': 'generation_wind_actual',
    'Generacja źródeł fotowoltaicznych': 'generation_solar_actual',
    'Krajowe saldo wymiany międzysystemowej równoległej': 'crossborder_sync_balance_actual',
    'Krajowe saldo wymiany międzysystemowej nierównoległej': 'crossborder_async_balance_actual',
    'RCCO2 [zł/Mg CO2]': 'co2_price_pln_actual',
    'RCCO2 [EUR/Mg CO2]': 'co2_price_eur_actual',
}
