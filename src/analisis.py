import pandas as pd

# Cargar dataset
file_path = "data/Online Retail.xlsx"
df = pd.read_excel(file_path)

# Vista general
print("Dimensión del dataset:", df.shape)
print("\nPrimeras filas:")
print(df.head())

print("\nInformación general:")
print(df.info())

print("\nValores nulos por columna:")
print(df.isnull().sum())

# Copia para limpieza
df_clean = df.copy()

df_clean = df_clean.dropna(subset=['CustomerID'])


df_clean = df_clean[df_clean['Quantity'] > 0]


df_clean['TotalPrice'] = df_clean['Quantity'] * df_clean['UnitPrice']


print("Dimensión después de limpieza:", df_clean.shape)
print(df_clean.head())

# Métricas principales
total_revenue = df_clean['TotalPrice'].sum()
total_orders = df_clean['InvoiceNo'].nunique()
total_customers = df_clean['CustomerID'].nunique()

print(f"Ingresos totales: £{total_revenue:,.2f}")
print(f"Total de órdenes: {total_orders}")
print(f"Total de clientes únicos: {total_customers}")

import matplotlib.pyplot as plt

# Crear columna Año-Mes
df_clean['YearMonth'] = df_clean['InvoiceDate'].dt.to_period('M')

# Agrupar ventas por mes
monthly_sales = df_clean.groupby('YearMonth')['TotalPrice'].sum()

plt.figure(figsize=(12,6))
monthly_sales.plot()
plt.title("Ventas mensuales (£)")
plt.xlabel("Mes")
plt.ylabel("Ingresos")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

top_products = df_clean.groupby('Description')['TotalPrice'].sum().sort_values(ascending=False).head(10)

plt.figure(figsize=(10,6))
top_products.plot(kind='barh')
plt.title("Top 10 productos por ingresos")
plt.xlabel("Ingresos (£)")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()

top_customers = df_clean.groupby('CustomerID')['TotalPrice'].sum().sort_values(ascending=False).head(10)

plt.figure(figsize=(10,6))
top_customers.plot(kind='bar')
plt.title("Top 10 clientes por ingresos")
plt.xlabel("Cliente ID")
plt.ylabel("Ingresos (£)")
plt.tight_layout()
plt.show()


import datetime as dt

# Fecha de referencia (última fecha + 1 día)
snapshot_date = df_clean['InvoiceDate'].max() + dt.timedelta(days=1)

# Crear tabla RFM
rfm = df_clean.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (snapshot_date - x.max()).days,  # Recency
    'InvoiceNo': 'nunique',  # Frequency
    'TotalPrice': 'sum'      # Monetary
})

rfm.columns = ['Recency', 'Frequency', 'Monetary']

print(rfm.head())

# Crear score RFM
rfm['R_rank'] = pd.qcut(rfm['Recency'], 4, labels=[4,3,2,1], duplicates='drop')
rfm['F_rank'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1,2,3,4])
rfm['M_rank'] = pd.qcut(rfm['Monetary'], 4, labels=[1,2,3,4], duplicates='drop')

rfm['RFM_Score'] = rfm[['R_rank','F_rank','M_rank']].astype(int).sum(axis=1)

print(rfm.head())

segment_distribution = rfm['RFM_Score'].value_counts().sort_index()

plt.figure(figsize=(10,5))
segment_distribution.plot(kind='bar')
plt.title("Distribución de clientes por RFM Score")
plt.xlabel("RFM Score")
plt.ylabel("Cantidad de clientes")
plt.tight_layout()
plt.show()