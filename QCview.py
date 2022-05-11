### QCview.py: iterates through the qcFigs/triggerFix directory and shows the user each figure one at at a time. The user can choose which figure,
### if any, looks like a correct split. The program then updates the triggerFix.csv file accordingly
### usage: python QCview.py path/to/qcFigs/triggerFix path/to/triggerFix.csv

### NOTE: in order for this code to work properly, a graphical interface must be enabled, such as X11 for Mac. For more information on installing,
### visit https://docs.ycrc.yale.edu/clusters-at-yale/access/x11/
import pandas as pd
import os
import argparse
import PIL
from PIL import Image

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='automate trigger fixes in spreadsheet for qcFig output')
	parser.add_argument('qcDir', help='full path to directory containing qcFigs output from first run of genTrigsNii')
	parser.add_argument('qcSheet', help='csv where autofix vs simpfix is specified')

	args=parser.parse_args()
	
	qcDir = args.qcDir
	sheet = args.qcSheet
	
	qcDF = pd.read_csv(sheet, index_col = 'Img')
	os.chdir(qcDir)
	for file in os.scandir():
		name, ext = os.path.splitext(file)
		if ext == '.png' and name.endswith('Auto'):
			rowName = file.name.split('mean')[0]
			print('opening qcFig for: ', rowName)
			fig = Image.open(file.path)
			fig.show()
			method = input('Select simpfix, autofix, or none for this figure: ')
			if method == 'simpfix':
				qcDF.at[rowName, 'simpFix'] = 1
				qcDF.at[rowName, 'writeImgs'] = 1
			if method == 'autofix':
				qcDF.at[rowName, 'autoFix'] = 1
				qcDF.at[rowName, 'writeImgs'] = 1
			closeWindow = input('Press enter to continue the program after closing the image window')
	qcDF.to_csv(sheet)
