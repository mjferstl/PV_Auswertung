# Python-Skript zur grafischen Darstellung und Auswertung der Zaehlerstaende in den Unterordnern fuer alle Jahre und Monate
# -----------------------------------------------------
# Autor: mjferstl
# Datum: 2019-01-01
# Aenderungen: 2019-08-15
# -----------------------------------------------------
# INFO:
# Der erste Tag eines Jahres muss einen Wert enthalten
# -----------------------------------------------------

# Pakete laden
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages
import os, sys, re
import numpy as np
from datetime import datetime
import pandas as pd

# Eigene Skripte
from uty_DataDir import checkDataDir, DATA_DIR, getDataFiles, findValidDataFiles

# Variablen
monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dez']
daysPerMonth = [31,28,31,30,31,30,31,31,30,31,30,31]
COL_DATE = 'Datum'
COL_VALUES = 'Zaehlerstand'

# Bezeichnung der Monate fuer die Beschriftung der Plots
Monatsnamen = ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember']


# Pruefung, ob Daten vorhanden sind
check = checkDataDir()
dirIsOk, yearDirs = check[0], check[1]
if dirIsOk:
	print('Überprüfung, ob Daten vorhanden sind, war erfolgreich.')
else:
	sys.exit()

# Jahreszahlen absteigend sortieren
years = [int(year) for year in yearDirs]
years.sort()

# Prüfen, ob die Jahreszahlen direkt aufeinander folgen
# Falls nicht, dann wird eine Warnung ausgegeben
for y in range(len(years)-1):
	if years[y+1] - years[y] != 1:
		print('\n** Zwischen den Jahren ' + str(years[y]) + ' und ' + str(years[y+1]) + ' sind keine Daten vorhanden!\n')


# Leere Lists fuer die Zaehlerstaende und das jeweilige Datum
# Die Elemente der Lists enthatlen jeweils die Daten fuer ein ganzes Jahr
ZaehlerstaendeAbsolut = [[] for i in range(len(years))]
Datum = [[] for i in range(len(years))]

# Lists fuer den Plot des Monats-Vergleichs
ZaehlerstaendeMonate = [[] for i in range(len(years))]
DatumMonat = [[] for i in range(len(years))]

# Pandas-Element als Datenbank
data = pd.DataFrame(columns=[COL_DATE,COL_VALUES])

# Schleife über alle Jahre
for year in years:

	# Anzahl der Tage im Februar in einem Schaltjahr anpassen
	daysPerMonth[1] = 29 if (year%4 == 0) else 28		

	# Die Daten fuer alle Monate des Jahres finden
	currDataDir = DATA_DIR + '\\' + str(year)
	dataFileNames = findValidDataFiles(currDataDir,monthNames,Monatsnamen,year)

	# Schleife über alle Monate
	for m in range(12):

		# Pruefen, ob fuer den ersten Monat eine Datei vorhanden ist
		if len(dataFileNames[m]) == 0:
			continue

		#### Daten des Monats laden
		# Datum
		days = [datetime(year,m+1,d+1) for d in range(daysPerMonth[m])]

		# Zählerstände
		filename = DATA_DIR + '\\' + str(year) + '\\' + dataFileNames[m]
		with open(filename) as file:
			res = file.readlines()
		# In jeder Zeile '\n' und ' ' entfernen
		res = [res[i].rstrip('\n') for i in range(len(res))]
		values = [res[i].rstrip(' ') for i in range(len(res))]

		# Liste der Zählerstände mit leeren Strings auffüllen, wenn in dem TXT-File zu wenig Einträge waren
		if len(values) < len(days):
			for i in range(len(days)-len(values)):
				values.append('')
		elif len(values) > len(days):
			print('+++ Im ' + Monatsnamen[m] + ' sind mehr Einträge vorhanden, als der Monat Tage hat. +++')
		

		# DataFrame fuer Pandas-Tabelle erstellen
		dFrame = []
		for i in range(len(days)):
			if values[i] == '':
				dFrame.append([days[i],values[i]])
			else:
				dFrame.append([days[i],int(values[i])])

		# Daten zur Tabelle hinzufuegen
		newdata = pd.DataFrame(dFrame,columns=[COL_DATE,COL_VALUES])
		data = data.append(newdata,ignore_index=True)



def getNextValueWithIndex(currIndex,maxIndex):
	for index in range(currIndex+1,maxIndex):
		value = data.iloc[index,:][COL_VALUES]
		if value != '':
			return [int(value),index]

	# Wenn kein neuer Wert bis zum Ende gefunden wurde, dann gibt es nicht mehr Datenpunkte
	# Demnach ist keine Interpolation möglich
	return ['','']


# Überprüfung aller Werte und
# Interolation fehlender Datenpunkte
items = len(data)
for i in range(1,items):
	rawValue = data.iloc[i,:][COL_VALUES]
	lastValue = int(data.iloc[i-1,:][COL_VALUES])

	# Wenn ein Eintrag leer ist, dann werden die Daten interpoliert
	if rawValue == '':
		[nextValue,nextIndex] = getNextValueWithIndex(i,items)	
		if nextValue == '' and nextIndex == '':
			data.drop(data.index[[x for x in range(i,items)]],inplace=True)
			break
		interpolatedValue = lastValue + (nextValue-lastValue)/(nextIndex-i+1)
		data.at[i, COL_VALUES] = int(interpolatedValue)
		rawValue = interpolatedValue

	if int(rawValue) - lastValue < 0:
		print('* Fehler für den Wert vom '  + str(data.iloc[i,:][COL_DATE]))


#
data[COL_DATE] = pd.to_datetime(data[COL_DATE], format='%Y.%m.%d') # format='%d%b%Y:%H:%M:%S.%f'
data['Tag'] = pd.DatetimeIndex(data[COL_DATE]).day
data['Monat'] = pd.DatetimeIndex(data[COL_DATE]).month
data['Jahr'] = pd.DatetimeIndex(data[COL_DATE]).year
Jahre = len(years)

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

plotdata = [[] for i in range(Jahre)]
date = [[] for i in range(Jahre)]
# Den Verlauf des Zaehlerstands plotten
fig, ax = plt.subplots()
for i in range(len(years)):
	dataCurrYear = data.loc[data['Jahr'] == years[i]]
	plotdata[i] = dataCurrYear.iloc[:,1]
	date[i] = dataCurrYear.iloc[:,0]
	ax.plot(dataCurrYear.iloc[:,0],dataCurrYear.iloc[:,1],label=str(years[i]))

ax.legend(loc='upper left')
plt.grid()
plt.xlim((data.iloc[0,0],data.iloc[-1,0]))
plt.xlabel('Tag')
plt.ylabel('Zählerstand in kWh')
plt.xticks(rotation=45)
plt.title('Stromproduktion der Photovoltaikanlage')
fig.tight_layout()
pdf.savefig()
fig.clf()

# Vergleich der Daten im Jahresverlauf
dateCompare = [[] for i in range(Jahre)]
dataCompare = [[] for i in range(Jahre)]
for i in range(len(years)):
	dataCurrYear = data.loc[data['Jahr'] == years[i]]
	for j in range(len(dataCurrYear)):
		dateCompare[i].append(datetime(2016,dataCurrYear.iloc[j,3],dataCurrYear.iloc[j,2]))
		dataCompare[i].append(dataCurrYear.iloc[j,1]-dataCurrYear.iloc[0,1])

# Einen Vergleich der ausgewaehlten Jahre plotten
fig, ax = plt.subplots()
for i in range(len(years)):
	# Daten jahresweise plotten
	# Neuere Daten liegen im Diagramm ueber aelteren Daten
	ax.plot(dateCompare[i],dataCompare[i],label=str(years[i]))

ax.legend(loc='upper left')
plt.grid()
myFmt = mdates.DateFormatter('%m-%d')
ax.xaxis.set_major_formatter(myFmt)
plt.xlim((dateCompare[0][0], dateCompare[-2][-1]))
plt.xlabel('Monat-Tag')
ax.set_ylim(bottom=0)
plt.ylabel('Strompoduktion seit Jahresbeginn in kWh')
plt.xticks(rotation=45)
plt.title('Vergleich der Stromproduktion im Jahresverlauf')
fig.tight_layout()
pdf.savefig()
fig.clf()


# Vegleiche die Monate jahresweise
for i in range(len(Monatsnamen)):
	dataCurrMonth = data.loc[data['Monat'] == i+1]
	fig, ax = plt.subplots()
	print(Monatsnamen[i])
	for j in range(Jahre):
		dataCurrMonthYear = dataCurrMonth.loc[data['Jahr'] == years[j]]
		dateCompare = [k+1 for k in range(len(dataCurrMonthYear))]
		dataCompare = [k-dataCurrMonthYear.iloc[0,1] for k in dataCurrMonthYear.iloc[:,1]]
		ax.plot(dateCompare,dataCompare,label=str(years[j]))

	ax.legend(loc='upper left')	
	plt.grid(which='major')
	plt.grid(b=True, which='minor', color='r', linestyle='--')
	
	plt.xlim((1, 31))
	plt.xlabel('Tag')
	ax.set_ylim(bottom=0, top=5000)
	plt.ylabel('Strompoduktion seit Monatsbeginn in kWh')
	plt.title('Vergleich der Stromproduktion im Monat ' + Monatsnamen[i])
	fig.tight_layout()
	pdf.savefig()
	fig.clf()


pdf.close()
print('PDF mit Ergebnissen wurde erstellt!')
print('Datei: ' + pdf_filename  + '\n')
