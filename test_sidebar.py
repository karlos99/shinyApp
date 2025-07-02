try:
    from mtss.sidebar import app_sidebar, organized_cols, baseColumns
    print('Import successful')
    print(f'app_sidebar type: {type(app_sidebar)}')
    print(f'organized_cols type: {type(organized_cols)}')
    print(f'baseColumns type: {type(baseColumns)}')
except Exception as e:
    print(f'Error: {e}')
