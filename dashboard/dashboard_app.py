"""
dashboard_app.py - Interactive Mutual Fund Analytics Dashboard
================================================================
4-page interactive dashboard built with Plotly Dash replicating
the Power BI dashboard requirements for the Bluestock Capstone Project.

Pages:
  1. Industry Overview — KPIs, AUM trends, AUM by AMC
  2. Fund Performance — Risk vs Return scatter, fund scorecard, NAV vs benchmark
  3. Investor Analytics — Transactions by state, SIP/Lumpsum split, age analysis
  4. SIP & Market Trends — SIP inflows vs Nifty, category heatmap

Author: Akash Kumar Pandit
Date: August 2026
"""

import dash
from dash import dcc, html, dash_table, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sqlite3
import os

# ── Load Data ──────────────────────────────────────────────────────
DB_PATH = 'data/processed/database.db' if os.path.exists('data/processed/database.db') else '../data/processed/database.db'
conn = sqlite3.connect(DB_PATH)

fund_master = pd.read_sql("SELECT * FROM fund_master", conn)
nav_history = pd.read_sql("SELECT * FROM nav_history", conn)
aum_by_fh = pd.read_sql("SELECT * FROM aum_by_fund_house", conn)
sip_inflows = pd.read_sql("SELECT * FROM monthly_sip_inflows", conn)
cat_inflows = pd.read_sql("SELECT * FROM category_inflows", conn)
folio_count = pd.read_sql("SELECT * FROM industry_folio_count", conn)
scheme_perf = pd.read_sql("SELECT * FROM scheme_performance", conn)
inv_txn = pd.read_sql("SELECT * FROM investor_transactions", conn)
holdings = pd.read_sql("SELECT * FROM portfolio_holdings", conn)
bench_idx = pd.read_sql("SELECT * FROM benchmark_indices", conn)
risk_metrics = pd.read_sql("SELECT * FROM risk_metrics", conn)
conn.close()

# Parse dates
nav_history['date'] = pd.to_datetime(nav_history['date'], errors='coerce')
bench_idx['date'] = pd.to_datetime(bench_idx['date'], errors='coerce')
inv_txn['transaction_date'] = pd.to_datetime(inv_txn['transaction_date'], errors='coerce')

# ── Color Theme ────────────────────────────────────────────────────
COLORS = {
    'bg': '#0a0a1a',
    'card': '#131328',
    'card_border': '#1e1e3f',
    'primary': '#4f6df5',
    'accent': '#00e5ff',
    'text': '#e0e0e0',
    'text_muted': '#888899',
    'success': '#4caf50',
    'warning': '#ff9800',
    'danger': '#f44336',
    'gradient_1': '#667eea',
    'gradient_2': '#764ba2',
}

# ── Helper: KPI Card ──────────────────────────────────────────────
def kpi_card(title, value, icon="📊", color=COLORS['accent']):
    return dbc.Col(
        dbc.Card([
            dbc.CardBody([
                html.Div(icon, style={'fontSize': '28px', 'marginBottom': '4px'}),
                html.H3(value, style={'color': color, 'fontWeight': '700', 'marginBottom': '2px', 'fontSize': '1.6rem'}),
                html.P(title, style={'color': COLORS['text_muted'], 'fontSize': '0.8rem', 'marginBottom': '0'}),
            ], style={'textAlign': 'center', 'padding': '16px 8px'})
        ], style={
            'backgroundColor': COLORS['card'],
            'border': f"1px solid {COLORS['card_border']}",
            'borderRadius': '12px',
            'boxShadow': '0 4px 20px rgba(0,0,0,0.3)',
        }),
        width=3, className='mb-3'
    )

# ── Helper: Section Title ─────────────────────────────────────────
def section_title(text):
    return html.H5(text, style={
        'color': COLORS['text'], 'fontWeight': '600',
        'borderLeft': f"4px solid {COLORS['accent']}",
        'paddingLeft': '12px', 'marginTop': '20px', 'marginBottom': '16px'
    })

# ── PAGE 1: Industry Overview ─────────────────────────────────────
def page_industry():
    # KPIs
    total_aum = aum_by_fh['aum_lakh_crore'].sum() if 'aum_lakh_crore' in aum_by_fh.columns else aum_by_fh.iloc[:, 1].sum()
    total_sip = sip_inflows.iloc[:, 1].iloc[-1] if len(sip_inflows) > 0 else 0
    total_folios = folio_count['total_folios_crore'].iloc[-1] if 'total_folios_crore' in folio_count.columns else 0
    total_schemes = len(fund_master)

    # AUM by Fund House chart
    aum_col = [c for c in aum_by_fh.columns if 'aum' in c.lower() and 'fund' not in c.lower()][0]
    fh_col = [c for c in aum_by_fh.columns if 'fund' in c.lower() or 'house' in c.lower() or 'amc' in c.lower()][0]
    aum_sorted = aum_by_fh.sort_values(aum_col, ascending=True)

    fig_aum_bar = px.bar(
        aum_sorted, x=aum_col, y=fh_col, orientation='h',
        color=aum_col, color_continuous_scale=['#1a237e', '#4f6df5', '#00e5ff'],
        labels={aum_col: 'AUM', fh_col: 'Fund House'}
    )
    fig_aum_bar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color=COLORS['text'], showlegend=False, coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10), height=350,
        xaxis=dict(gridcolor='#1e1e3f'), yaxis=dict(gridcolor='#1e1e3f'),
    )

    # SIP inflow trend
    month_col = sip_inflows.columns[0]
    sip_col = sip_inflows.columns[1]
    fig_sip_trend = px.line(
        sip_inflows, x=month_col, y=sip_col,
        markers=True, labels={month_col: 'Month', sip_col: 'SIP Inflow (₹ Cr)'}
    )
    fig_sip_trend.update_traces(line_color=COLORS['accent'], marker_color=COLORS['primary'])
    fig_sip_trend.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color=COLORS['text'], margin=dict(l=10, r=10, t=10, b=10), height=350,
        xaxis=dict(gridcolor='#1e1e3f', tickangle=-45), yaxis=dict(gridcolor='#1e1e3f'),
    )

    # Folio trend
    fig_folio = px.area(
        folio_count, x=folio_count.columns[0], y='total_folios_crore',
        labels={folio_count.columns[0]: 'Month', 'total_folios_crore': 'Total Folios (Crore)'}
    )
    fig_folio.update_traces(fill='tozeroy', line_color=COLORS['primary'], fillcolor='rgba(79,109,245,0.2)')
    fig_folio.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color=COLORS['text'], margin=dict(l=10, r=10, t=10, b=10), height=300,
        xaxis=dict(gridcolor='#1e1e3f', tickangle=-45), yaxis=dict(gridcolor='#1e1e3f'),
    )

    return html.Div([
        dbc.Row([
            kpi_card("Total AUM", f"₹{total_aum:.1f}L Cr", "💰", COLORS['accent']),
            kpi_card("SIP Inflows/Mo", f"₹{total_sip:,.0f} Cr", "📈", COLORS['success']),
            kpi_card("Total Folios", f"{total_folios:.2f} Cr", "👥", COLORS['warning']),
            kpi_card("Schemes Analyzed", str(total_schemes), "📋", COLORS['primary']),
        ], className='mb-2'),
        dbc.Row([
            dbc.Col([
                section_title("AUM by Fund House"),
                dbc.Card(dcc.Graph(figure=fig_aum_bar, config={'displayModeBar': False}),
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '12px', 'border': f"1px solid {COLORS['card_border']}"}),
            ], width=6),
            dbc.Col([
                section_title("Monthly SIP Inflow Trend"),
                dbc.Card(dcc.Graph(figure=fig_sip_trend, config={'displayModeBar': False}),
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '12px', 'border': f"1px solid {COLORS['card_border']}"}),
            ], width=6),
        ], className='mb-3'),
        dbc.Row([
            dbc.Col([
                section_title("Industry Folio Growth"),
                dbc.Card(dcc.Graph(figure=fig_folio, config={'displayModeBar': False}),
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '12px', 'border': f"1px solid {COLORS['card_border']}"}),
            ], width=12),
        ]),
    ])

# ── PAGE 2: Fund Performance ──────────────────────────────────────
def page_performance():
    # Merge scheme performance with risk metrics
    merged = scheme_perf.merge(risk_metrics[['amfi_code', 'annualized_std_dev', 'alpha', 'beta', 'risk_profile']],
                                on='amfi_code', how='left')

    # Scatter plot: Return vs Risk
    fig_scatter = px.scatter(
        merged, x='return_3yr_pct', y='annualized_std_dev',
        size='aum_crore', color='risk_profile',
        hover_name='scheme_name', hover_data=['fund_house', 'alpha', 'beta'],
        color_discrete_map={'Low Risk': '#4caf50', 'Medium Risk': '#ff9800', 'High Risk': '#f44336'},
        labels={'return_3yr_pct': '3-Year Return (%)', 'annualized_std_dev': 'Volatility (Ann. Std Dev)',
                'aum_crore': 'AUM (₹Cr)', 'risk_profile': 'Risk Profile'},
    )
    fig_scatter.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color=COLORS['text'], margin=dict(l=10, r=10, t=30, b=10), height=420,
        xaxis=dict(gridcolor='#1e1e3f'), yaxis=dict(gridcolor='#1e1e3f'),
        legend=dict(bgcolor='rgba(0,0,0,0)'),
    )

    # Fund scorecard table
    scorecard_cols = ['scheme_name', 'fund_house', 'category', 'return_1yr_pct', 'return_3yr_pct',
                      'sharpe_ratio', 'morningstar_rating', 'risk_grade']
    available_cols = [c for c in scorecard_cols if c in merged.columns]
    scorecard_df = merged[available_cols].sort_values('return_3yr_pct', ascending=False).head(15)

    table = dash_table.DataTable(
        data=scorecard_df.to_dict('records'),
        columns=[{'name': c.replace('_', ' ').title(), 'id': c} for c in available_cols],
        sort_action='native',
        style_header={
            'backgroundColor': COLORS['primary'], 'color': 'white',
            'fontWeight': 'bold', 'fontSize': '11px', 'border': 'none',
        },
        style_cell={
            'backgroundColor': COLORS['card'], 'color': COLORS['text'],
            'fontSize': '11px', 'border': f"1px solid {COLORS['card_border']}",
            'textAlign': 'left', 'padding': '6px 10px', 'maxWidth': '180px',
            'overflow': 'hidden', 'textOverflow': 'ellipsis',
        },
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#0d0d20'},
        ],
        page_size=10,
    )

    return html.Div([
        dbc.Row([
            dbc.Col([
                section_title("Return vs Risk — Bubble Chart (Size = AUM)"),
                dbc.Card(dcc.Graph(figure=fig_scatter, config={'displayModeBar': False}),
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '12px', 'border': f"1px solid {COLORS['card_border']}"}),
            ], width=12),
        ], className='mb-3'),
        dbc.Row([
            dbc.Col([
                section_title("Fund Scorecard (Sortable)"),
                dbc.Card(html.Div(table, style={'padding': '8px'}),
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '12px', 'border': f"1px solid {COLORS['card_border']}"}),
            ], width=12),
        ]),
    ])

# ── PAGE 3: Investor Analytics ────────────────────────────────────
def page_investors():
    # Transaction amount by state
    state_txn = inv_txn.groupby('state')['amount_inr'].sum().reset_index().sort_values('amount_inr', ascending=True).tail(15)
    fig_state = px.bar(
        state_txn, x='amount_inr', y='state', orientation='h',
        color='amount_inr', color_continuous_scale=['#1a237e', '#4f6df5', '#00e5ff'],
        labels={'amount_inr': 'Total Amount (₹)', 'state': 'State'},
    )
    fig_state.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color=COLORS['text'], showlegend=False, coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10), height=380,
        xaxis=dict(gridcolor='#1e1e3f'), yaxis=dict(gridcolor='#1e1e3f'),
    )

    # Transaction type split (Donut)
    type_split = inv_txn.groupby('transaction_type')['amount_inr'].sum().reset_index()
    fig_donut = px.pie(
        type_split, values='amount_inr', names='transaction_type', hole=0.55,
        color_discrete_sequence=['#4f6df5', '#00e5ff', '#ff9800', '#f44336', '#4caf50'],
    )
    fig_donut.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', font_color=COLORS['text'],
        margin=dict(l=10, r=10, t=10, b=10), height=320,
        legend=dict(bgcolor='rgba(0,0,0,0)'),
    )

    # Age group analysis
    age_data = inv_txn.groupby('age_group')['amount_inr'].mean().reset_index().sort_values('amount_inr')
    fig_age = px.bar(
        age_data, x='age_group', y='amount_inr',
        color='amount_inr', color_continuous_scale=['#764ba2', '#667eea', '#00e5ff'],
        labels={'age_group': 'Age Group', 'amount_inr': 'Avg Transaction (₹)'},
    )
    fig_age.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color=COLORS['text'], showlegend=False, coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10), height=320,
        xaxis=dict(gridcolor='#1e1e3f'), yaxis=dict(gridcolor='#1e1e3f'),
    )

    # Monthly transaction volume
    monthly_vol = inv_txn.set_index('transaction_date').resample('M')['amount_inr'].count().reset_index()
    monthly_vol.columns = ['month', 'count']
    fig_vol = px.line(
        monthly_vol, x='month', y='count', markers=True,
        labels={'month': 'Month', 'count': 'Transaction Count'},
    )
    fig_vol.update_traces(line_color=COLORS['accent'], marker_color=COLORS['primary'])
    fig_vol.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color=COLORS['text'], margin=dict(l=10, r=10, t=10, b=10), height=320,
        xaxis=dict(gridcolor='#1e1e3f'), yaxis=dict(gridcolor='#1e1e3f'),
    )

    return html.Div([
        dbc.Row([
            dbc.Col([
                section_title("Transaction Amount by State (Top 15)"),
                dbc.Card(dcc.Graph(figure=fig_state, config={'displayModeBar': False}),
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '12px', 'border': f"1px solid {COLORS['card_border']}"}),
            ], width=7),
            dbc.Col([
                section_title("SIP / Lumpsum / Redemption Split"),
                dbc.Card(dcc.Graph(figure=fig_donut, config={'displayModeBar': False}),
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '12px', 'border': f"1px solid {COLORS['card_border']}"}),
            ], width=5),
        ], className='mb-3'),
        dbc.Row([
            dbc.Col([
                section_title("Average Transaction by Age Group"),
                dbc.Card(dcc.Graph(figure=fig_age, config={'displayModeBar': False}),
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '12px', 'border': f"1px solid {COLORS['card_border']}"}),
            ], width=6),
            dbc.Col([
                section_title("Monthly Transaction Volume"),
                dbc.Card(dcc.Graph(figure=fig_vol, config={'displayModeBar': False}),
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '12px', 'border': f"1px solid {COLORS['card_border']}"}),
            ], width=6),
        ]),
    ])

# ── PAGE 4: SIP & Market Trends ──────────────────────────────────
def page_sip_trends():
    # Dual axis: SIP Inflows + Nifty 50
    nifty = bench_idx[bench_idx['index_name'].str.contains('NIFTY', case=False, na=False)]
    nifty_monthly = nifty.set_index('date').resample('M')['close_value'].last().reset_index()

    fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
    
    sip_month_col = sip_inflows.columns[0]
    sip_val_col = sip_inflows.columns[1]
    
    fig_dual.add_trace(
        go.Bar(x=sip_inflows[sip_month_col], y=sip_inflows[sip_val_col],
               name='SIP Inflow (₹ Cr)', marker_color=COLORS['primary'], opacity=0.8),
        secondary_y=False,
    )
    fig_dual.add_trace(
        go.Scatter(x=nifty_monthly['date'], y=nifty_monthly['close_value'],
                   name='Nifty 50', line=dict(color=COLORS['accent'], width=2), mode='lines'),
        secondary_y=True,
    )
    fig_dual.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color=COLORS['text'], margin=dict(l=10, r=10, t=30, b=10), height=400,
        legend=dict(bgcolor='rgba(0,0,0,0)', x=0.01, y=0.99),
        xaxis=dict(gridcolor='#1e1e3f'),
    )
    fig_dual.update_yaxes(title_text="SIP Inflow (₹ Cr)", secondary_y=False, gridcolor='#1e1e3f')
    fig_dual.update_yaxes(title_text="Nifty 50", secondary_y=True, gridcolor='#1e1e3f')

    # Category inflow heatmap
    cat_cols = [c for c in cat_inflows.columns if c not in ['month', 'quarter', 'year', 'date', 'period']]
    date_col = cat_inflows.columns[0]
    
    if len(cat_cols) > 1:
        cat_melted = cat_inflows.melt(id_vars=[date_col], value_vars=cat_cols,
                                       var_name='category', value_name='inflow')
        fig_heatmap = px.density_heatmap(
            cat_melted, x=date_col, y='category', z='inflow',
            color_continuous_scale=['#0a0a1a', '#1a237e', '#4f6df5', '#00e5ff'],
            labels={date_col: 'Period', 'category': 'Category', 'inflow': 'Inflow (₹ Cr)'},
        )
    else:
        fig_heatmap = px.bar(cat_inflows, x=date_col, y=cat_cols[0] if cat_cols else cat_inflows.columns[1])

    fig_heatmap.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color=COLORS['text'], margin=dict(l=10, r=10, t=10, b=10), height=380,
        xaxis=dict(gridcolor='#1e1e3f', tickangle=-45), yaxis=dict(gridcolor='#1e1e3f'),
    )

    # Risk profile distribution
    risk_dist = risk_metrics['risk_profile'].value_counts().reset_index()
    risk_dist.columns = ['risk_profile', 'count']
    fig_risk = px.pie(
        risk_dist, values='count', names='risk_profile', hole=0.5,
        color='risk_profile',
        color_discrete_map={'Low Risk': '#4caf50', 'Medium Risk': '#ff9800', 'High Risk': '#f44336'},
    )
    fig_risk.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', font_color=COLORS['text'],
        margin=dict(l=10, r=10, t=10, b=10), height=300,
        legend=dict(bgcolor='rgba(0,0,0,0)'),
    )

    return html.Div([
        dbc.Row([
            dbc.Col([
                section_title("SIP Inflows vs Nifty 50 (Dual Axis)"),
                dbc.Card(dcc.Graph(figure=fig_dual, config={'displayModeBar': False}),
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '12px', 'border': f"1px solid {COLORS['card_border']}"}),
            ], width=12),
        ], className='mb-3'),
        dbc.Row([
            dbc.Col([
                section_title("Category Inflow Heatmap"),
                dbc.Card(dcc.Graph(figure=fig_heatmap, config={'displayModeBar': False}),
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '12px', 'border': f"1px solid {COLORS['card_border']}"}),
            ], width=8),
            dbc.Col([
                section_title("Fund Risk Profile Distribution"),
                dbc.Card(dcc.Graph(figure=fig_risk, config={'displayModeBar': False}),
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '12px', 'border': f"1px solid {COLORS['card_border']}"}),
            ], width=4),
        ]),
    ])

# ── App Layout ─────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    title="Mutual Fund Analytics | Bluestock Fintech"
)

navbar = dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col(html.Div([
                html.Span("📊 ", style={'fontSize': '24px'}),
                html.Span("Mutual Fund Analytics", style={
                    'fontSize': '18px', 'fontWeight': '700', 'color': 'white',
                    'background': f'linear-gradient(135deg, {COLORS["gradient_1"]}, {COLORS["accent"]})',
                    '-webkit-background-clip': 'text', '-webkit-text-fill-color': 'transparent',
                }),
                html.Span("  |  Bluestock Fintech", style={
                    'fontSize': '12px', 'color': COLORS['text_muted'], 'marginLeft': '8px'
                }),
            ]), width='auto'),
        ], align='center'),
        dbc.Nav([
            dbc.NavItem(dbc.NavLink("Industry Overview", href="/", active='exact',
                                     style={'color': COLORS['text'], 'fontSize': '13px'})),
            dbc.NavItem(dbc.NavLink("Fund Performance", href="/performance", active='exact',
                                     style={'color': COLORS['text'], 'fontSize': '13px'})),
            dbc.NavItem(dbc.NavLink("Investor Analytics", href="/investors", active='exact',
                                     style={'color': COLORS['text'], 'fontSize': '13px'})),
            dbc.NavItem(dbc.NavLink("SIP & Market Trends", href="/sip-trends", active='exact',
                                     style={'color': COLORS['text'], 'fontSize': '13px'})),
        ], navbar=True, className='ms-auto'),
    ], fluid=True),
    color=COLORS['card'], dark=True,
    style={'borderBottom': f"2px solid {COLORS['primary']}", 'padding': '4px 0'},
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    dbc.Container(id='page-content', fluid=True, style={'padding': '20px 24px'}),
], style={'backgroundColor': COLORS['bg'], 'minHeight': '100vh'})

@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/performance':
        return page_performance()
    elif pathname == '/investors':
        return page_investors()
    elif pathname == '/sip-trends':
        return page_sip_trends()
    else:
        return page_industry()

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  BLUESTOCK MF ANALYTICS DASHBOARD")
    print("  Open in browser: http://127.0.0.1:8050")
    print("=" * 50 + "\n")
    app.run(debug=False, port=8050)
