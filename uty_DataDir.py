import os, sys, re

DATA_DIR = 'Daten'

##### Pruefung, ob Daten vorhanden sind #####
# returns: List mit zwei Elementen
#          - Wahrheitswert, ob die Datenstruktur in Ordnung ist
#          - List mit den Ordnernamen, die Daten enthalten
def checkDataDir():
    # Pruefung, ob ein Ordner mit dem Namen "Daten" im aktuellen Verzeichnis vorhanden ist
    if not os.path.isdir(DATA_DIR):
        print('Keine Daten vorhanden. Es muss ein Ordner "' + DATA_DIR + '" vorhanden sein.\nSkript beendet.')
        return [False,[]]

    # Pruefung, ob der Ordner "Daten" weiter Ordner mit Jahreszahlen enthaelt
    data_content = os.listdir(DATA_DIR)
    annual_dirs = [x for x in data_content if os.path.isdir(DATA_DIR + '/' + x)]
    if len(annual_dirs) == 0:
        print('Der Ordner ' + DATA_DIR + ' enthält keine weiteren Ordner.\nSkript beendet.')
        return [False,[]]

    years = []
    for folderName in annual_dirs:
        try:
            # Wenn der Ordnername ein Integer repraesentiert, dann wird er spaeter noch verwendet
            int(folderName)
            years.append(folderName)
        except ValueError:
            # Odner, der keine Jahreszahl enthaelt
            print('Der Ordner "' + DATA_DIR + '\\' + folderName + '" enthält keine Jahreszahl und wird deshalb nicht berücksichtigt.')

    # Wenn keine Ordner mit Jahreszahlen gefunden worden sind, dann wird das Skript beendet
    if len(years) == 0:
        print('Der Ordner "' + DATA_DIR + '" enthält keine Ordner mit einer Jahreszahl, wie z.B. "' + DATA_DIR + '\\2019".\nSkript beendet.')
        return [False,[]]

    # Pruefung, ob die Ordner mit den Jahreszahlen passende Dateien enthalten
    for i in range(len(years)):
        filesInDir = os.listdir(DATA_DIR + '\\' + years[i])
        dataFiles = getDataFiles(filesInDir)
        if len(dataFiles) == 0:
            years.pop(i)

    # Pruefung, ob keiner der Ordner Daten enthält
    if len(years) == 0:
        print('Die Ordner im Verzeichnis "' + DATA_DIR + '" enthalten keine TXT-Files.\nSkript beendet.')
        return [False,[]]

    # Wenn alle Pruefungen bestanden worden sind, dann sind Daten vorhanden
    return [True,years]


def getDataFiles(files):
    dataFiles = [f for f in files if len(re.findall(r"\w+\.txt$", f)) > 0]
    return dataFiles


def findValidDataFiles(directory,monthNames,Monatsnamen,year):
	allFiles = os.listdir(directory)
	dataFiles = getDataFiles(allFiles)
	dataFileNames = ['' for i in range(12)]
	for m in range(12):
		fileNames = []
		for f in dataFiles:
			fileCheck = re.findall('.*' + monthNames[m] + '.*\\.txt', f)
			if len(fileCheck) != 0:
				fileNames.append(fileCheck)
		if len(fileNames) == 0:
			print('* Für den Monat ' + Monatsnamen[m] + ' ' + str(year) + ' gibt es keine TXT-Datei mit Daten.')
		elif len(fileNames) > 1:
			print('* Für den Monat ' + Monatsnamen[m] + ' ' + str(year) + ' wurden mehrere TXT-Dateien gefunden.')
			print(str(fileNames))
			print('* Es wird nur die Datei ' + fileNames[0] + ' verwendet')
			dataFileNames[m] = fileNames[0][0]
		else:
			dataFileNames[m] = fileNames[0][0]	

	return dataFileNames