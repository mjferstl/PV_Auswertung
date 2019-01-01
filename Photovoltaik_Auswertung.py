# Python-Skript zur grafischen Darstellung und Auswertung der Zaehlerstaende in den Unterordnern fuer alle Jahre und Monate
# -----------------------------------------------------
# Autor: mjferstl
# Datum: 2019-01-01
# -----------------------------------------------------
# INFO:
# Der erste Tag eines Jahres muss einen Wert enthalten
# -----------------------------------------------------

# Pakete laden
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages
import os.path
import numpy as np
from datetime import datetime
import pandas as pd

# Lists fuer die Jahre, Monate und die Anzahl der Tage
years = [2018,2017,2016,2015,2014,2013,2012]
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dez']
days = [31,28,31,30,31,30,31,31,30,31,30,31]

# Bezeichnugn der Monate fuer die Beschriftung der Plots
Monate = ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember']

# Leere Lists fuer die Zaehlerstaende und das jeweilige Datum
# Die Elemente der Lists enthatlen jeweils die Daten fuer ein ganzes Jahr
Total = [[] for i in range(len(years))]
Dates = [[] for i in range(len(years))]

# Lists fuer den Plot des Monats-Vergleichs
TotalCompare = [[] for i in range(len(years))]
DatesCompare = [[] for i in range(len(years))]

# Pandas-Element als Datenbank
data = pd.DataFrame(columns=['Datum','Zählerstand'])

# Hilfsvarible
n = 0

# Funktion zum Einlesen der Daten aus Txt-Files
# Parameter
# - y: das aktuell auszuwertende Jahr als int
# - m: den aktuell auszuwertenden Monat als fortlaufende Zahl von 0 bis 11
def readData(y,m):
	# Dateiname mit den Zaehlerstanden fuer aktuell auszuwertenden Monat
	filename = str(y) + '/' + str(y) + '_' + months[m] + '.txt'
	
	# Einlesen der Zeilen des Txt-Files
	with open(filename) as file:
		res = file.readlines()
		
	# In jeder Zeile '\n' und ' ' entfernen
	res = [res[i].rstrip('\n') for i in range(len(res))]
	res = [res[i].rstrip(' ') for i in range(len(res))]
	
	# Die Anzahl der Zeilen auf die Anzahl der Tage im aktuellen Monat reduzieren
	#res = [res[i]for i in range(days[m])]
	
	# Interpolation, falls eine Zeile keinen Wert enthaelt
	for i in range(len(res)):
		
		# Pruefen, ob die aktuelle Zeile einen Wert enthaelt
		if res[i] == '':
		
			# Wenn kein Wert enthalten ist, dann aus vorhandenen Werten interpolieren
			
			# Wenn eine Zeile davor und eine Zeile danach einen Wert enthaelt, 
			# dann kann mit den eingelesenen Daten interpoliert werden
			check = False
			for k in range(i+1,len(res)):
				if res[k] != '' and res[k] != ' ':
					try:
						a = int(res[k])
						check = True
					except ValueError:
						print('Fehler bei der Interpolation')
						
			if i > 0 and check:
				# im aktuellen Monat interpolieren
				
				n = 0
				# Zeile mit dem naechsten Eintrag finden
				for j in range(i+1,len(res)):					
					if res[j] != '' and res[j] != ' ':
						n = j-i
						break
				
				# Differenz von naechstem und letztem Wert
				diff = int(res[i+n]) - int(res[i-1])
				
				# Die Werte bis zum naechsten Eintrag durch Interpolation bestimmen
				# Eintrag in die List als String
				for j in range(i,i+n):
					res[j] = str(int(int(res[i-1]) + (diff/(n+1))*(j-i+1)))
			
			# wenn keine Interpolation innerhalb des Monats moeglich ist
			else:
				# ueber den Monat hinaus interpolieren
				
				# Wenn der erste Wert des Monats fehlt, dann mit Daten aus dem Vormonat interpolieren
				if res[0] == '' or res[0] == ' ':
				
					# finde den naechsten Eintrag im aktuellen Monat
					for j in range(len(res)):
						if res[j] != '' and res[j] != ' ':
							n = j							
							break
					
					# letzten Eintrag aus dem Vormonat zur Interpolation nutzen
					last = Total[yss][-1]
					
					# Differenz berechnen
					diff = int(res[j])-last
					
					# Bis zum naechsten Eintrag im aktuellen Monat interpolieren
					for j in range(n):
						res[j] = last + diff/(n+1)*(j+1)
				
				# Wenn der letzte Tag des Monats keinen Wert enthaelt, dann muss mit den Daten des folgenden Monats interpoliert werden
				else:
					# Wenn es nicht der letzte Tag im letzten Monat des Jahres ist, dann Daten des Folgemonats laden
					if m < (12-1):
						filename = str(y) + '/' + str(y) + '_' + months[m+1] + '.txt'
			
						# Daten des Folgemonats zeilenweise einlesen
						with open(filename) as file:
							resNext = file.readlines()

						# '\n' in jedem Element des Lists entfernen
						resNext = [resNext[i].rstrip('\n') for i in range(len(resNext))]
						
						# Suche den ersten Eintrag im Folgemonat
						for j in range(len(resNext)):
							if resNext[j] != '' and resNext[j] != ' ':
								# Anzahl der zu interpolierenden Daten bestimmen
								n = j + len([x for x in range(len(res)) if res[x] == '' or res[x] == ' '])
								break
								
						# Differenz berechnen
						diff = int(resNext[j]) - int(res[i-1])
						
						# Bis zum Monatsende interpolieren
						for j in range(i,len(res)):
							res[j] = int(res[i-1]) + diff/(n+1)*(j-i+1)
					
					# Wenn im aktuellen Jahr keine neuen Eintraege mehr enthalten sind, dann den letzten vorhandenen Wert in alle folgenden Elemente schreiben
					else:
						for j in range(i,len(res)):
							res[j] = res[i-1]
	
	# Ergebnisse sind noch als String in der Lists
	# Deshalb werden alle Elemente auf int formattiert
	res = list(map(int, res))

	return res
		

# counter for years since start
yss = -1

# load data
for year in years:
	
	# Zeilenindex hochzaehlen
	yss += 1

	# Umschalten bei einem Schaltjahr
	if year%4 == 0:
		days[1] = 29
	else:
		days[1] = 28

	# erster Wert des Jahres
	firstNum = np.loadtxt(str(year)+ '/' + str(year) + '_Jan.txt')[0]
		
	for m in range(12):
		content = readData(year,m)
		listen = []
		zeiten = []
		for d in range(len(content)):
			if content[d] == 0:
				if d > 0:
					Total[yss].append(Total[yss][-1])
				else:
					Total[yss].append(Total[yss][-1])
			else:
				Total[yss].append(content[d])
				
			TotalCompare[yss].append(Total[yss][-1]-firstNum)			

			Dates[yss].append(datetime(year,m+1,d+1))				
			DatesCompare[yss].append(datetime(2016,m+1,d+1).date())
			listen.append([Dates[yss][-1],Total[yss][-1]])

		newdata = pd.DataFrame(listen,columns=['Datum','Zählerstand'])
		data = data.append(newdata,ignore_index=True)

#
data['Datum'] = pd.to_datetime(data['Datum'], format='%Y.%m.%d') # format='%d%b%Y:%H:%M:%S.%f'
data['Tag'] = pd.DatetimeIndex(data['Datum']).day
data['Monat'] = pd.DatetimeIndex(data['Datum']).month
data['Jahr'] = pd.DatetimeIndex(data['Datum']).year
Jahre = len(data.Jahr.unique())

# PDF erstellen
pdf_filename = ('Photovoltaik_' + str(min(years)) + '_bis_' + str(max(years)) + '.pdf')
pdf = PdfPages(pdf_filename)
FigureSize = (16.3*2 / 2.58, 13.2*2 / 2.58)
PlotColors = ['tab:blue', 'tab:red', 'tab:green', 'tab:orange',
			  'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray',
			  'tab:olive', 'tab:cyan']
FontSize = 8
params = []
mpl.rcParams['axes.linewidth'] = 0.7
mpl.rcParams['xtick.labelsize'] = 8
mpl.rcParams['ytick.labelsize'] = 8

# Den Verlauf des Zaehlerstands plotten
fig, ax = plt.subplots()
for i in range(len(years)):
	ax.plot(Dates[i],Total[i],label=str(years[i]))

ax.legend(loc='upper left')
plt.grid()
plt.xlim((Dates[-1][0], Dates[0][-1]))
plt.xlabel('Tag')
plt.ylabel('Zählerstand in kWh')
plt.xticks(rotation=45)
plt.title('Stromproduktion der Photovoltaikanlage')
fig.tight_layout()
pdf.savefig()
fig.clf()

# Einen Vergleich der ausgewaehlten Jahre plotten
yIndex = pd.DatetimeIndex(data['Datum']).year

plotdata = [[] for i in range(Jahre)]
date = [[] for i in range(Jahre)]

for i in range(Jahre):
	plotdata[i] = [data['Zählerstand'][k] for k in range(len(data['Datum'])) if (yIndex[k] == years[i])]
	plotdata[i] = [plotdata[i][m]-plotdata[i][0] for m in range(len(plotdata[i]))]
	date[i] = [DatesCompare[i][k] for k in range(len(DatesCompare[i]))]  

fig, ax = plt.subplots()
for i in range(len(years)):
	ax.plot(date[i],plotdata[i],label=str(years[i]))

ax.legend(loc='upper left')
plt.grid()
myFmt = mdates.DateFormatter('%m-%d')
ax.xaxis.set_major_formatter(myFmt)
plt.xlim((date[-1][0], date[-1][-1]))
plt.xlabel('Monat-Tag')
ax.set_ylim(bottom=0)
plt.ylabel('Strompoduktion seit Jahresbeginn in kWh')
plt.xticks(rotation=45)
plt.title('Vergleich der Stromproduktion im Jahresverlauf')
fig.tight_layout()
pdf.savefig()
fig.clf()

# Monate vergleichen
plotdata = [[] for i in range(len(Monate))]
date = [[] for i in range(len(Monate))]
mIndex = pd.DatetimeIndex(data['Datum']).month
yIndex = pd.DatetimeIndex(data['Datum']).year

for i in range(len(Monate)):
	plotdata[i] = [[] for k in range(Jahre)]
	date[i] = [[] for k in range(Jahre)]	
	
	for j in range(Jahre):
		date[i][j] = [data['Tag'][k] for k in range(len(mIndex)) if (mIndex[k] == i+1 and yIndex[k] == years[j])]
		plotdata[i][j] = [data['Zählerstand'][k] for k in range(len(mIndex)) if (mIndex[k] == i+1 and yIndex[k] == years[j])]
		# korrigeren
		if i > 0:
			tmp = [data['Zählerstand'][k] for k in range(len(mIndex)) if (mIndex[k] == i and yIndex[k] == years[j])]
			endLastMonth = tmp[-1]
		else:
			if j < Jahre-1:
				tmp = [data['Zählerstand'][k] for k in range(len(mIndex)) if (mIndex[k] == 12 and yIndex[k] == years[j+1])]
				endLastMonth = tmp[-1]
			else:
				endLastMonth = plotdata[i][j][0]
				
		plotdata[i][j] = [plotdata[i][j][m]-endLastMonth for m in range(len(plotdata[i][j]))]

for i in range(len(Monate)):
	fig, ax = plt.subplots()
	for j in range(Jahre):
		ax.plot(date[i][j],plotdata[i][j],label=str(years[j]))

	ax.legend(loc='upper left')	
	plt.grid()
	
	plt.xlim((1, max(max(date[i]))))
	plt.xlabel('Tag')
	ax.set_ylim(bottom=0)
	plt.ylabel('Strompoduktion seit Monatsbeginn in kWh')
	plt.title('Vergleich der Stromproduktion im Monat ' + Monate[i])
	fig.tight_layout()
	pdf.savefig()
	fig.clf()

pdf.close()
print('PDF mit Ergebnissen wurde erstellt!')
print(pdf_filename  + '\n')
