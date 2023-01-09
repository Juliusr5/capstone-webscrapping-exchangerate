from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('table')

# Mencari semua baris di tabel (tr atau table row) dengan for loop
data_rows = table.find_all('tr')
rows = []
for row in data_rows:
    value = row.find_all('td')
    beautified_value = [ele.text.strip() for ele in value]
    # Remove data arrays that are empty
    if len(beautified_value) == 0:
        continue
    rows.append(beautified_value)

##Menukar posisi atau urutan data (bagian bawah menjadi atas)
rows = rows[::-1]
#change into dataframe
df = pd.DataFrame(rows, columns = ['Tanggal','Hari','Harga_Harian','Keterangan'])


#insert data wrangling here
df['Tanggal'] = pd.to_datetime(df['Tanggal'])
df['Harga_Harian'] = df['Harga_Harian'].str.replace('IDR', '')
df['Harga_Harian'] = df['Harga_Harian'].str.replace(',', '')
df['Harga_Harian'] = df['Harga_Harian'].astype(float)
rupiah=df.loc[:, ['Tanggal','Harga_Harian']]

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{rupiah["Harga_Harian"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = rupiah.plot('Tanggal','Harga_Harian',figsize=(20,9),title='Indonesian Rupiahs(IDR) per US Dollar(USD)',xlabel='Tanggal',ylabel='Harga Harian(IDR)')
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)