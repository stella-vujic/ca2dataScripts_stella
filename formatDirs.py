### formatDirs.py: create directory hierarchy for raw data and filename conventions for running ca2 preproc pipeline
### this program should be run from whichever directory you would like the organized data to reside in
### assumptions:
###		the raw data is organized in folders by scanning session, and there can be multiple runs per session
###		the files are named in such a way that "natsort" module will return the order in which the data was collected
###			examples: (firstSessionA, firstSessionB, firstSessionC) or (run1.tif, run1@0001.tif, run1@0001.tif)
###		the rawDirs inputs are absolute file paths
### usage: python formatDirs.py /path/to/rawdata/animal01 /path/to/rawdata/animal02 --dataset SLC --sesType awake --imgType ca2
import natsort
import os
import argparse

### mkLinks: create symbolic links inside the abs. path dstpath that point to .tif and .smr files contained in tifs and smrs
def mkLinks(tifs, smrs, dstpath, dataset, session, animalName, image, ratio):
	os.chdir(dstpath)
	start = 0
	for trig in smrs:
		# smr symlink name format: {datasetName}_{ID}_ses-{sessionType}_{dateAndTime}.smr
		# for now, date is a dummy var
		smrFormat = dataset + '_' + animalName + '_' + session + '_' + '2022-05-06' + '_' + str(start) + '.smr'
		smrDstFile = os.path.join(dstpath, smrFormat)
		os.symlink(trig, smrDstFile)
		startInd = start * ratio
		endInd = startInd + ratio
		partnum = 0
		for img in tifs[startInd:endInd]:
			# tif symlink format: {datasetName}_{ID}_ses-{sessionType}_{date}_{runNumber}_{taskLabel}_part-{partNumber}.tif
			# for now, tasklabel is just REST
			tifFormat = dataset + '_' + animalName + '_' + session + '_' + '2022-05-06' + '_' 'EPI' + str(start) + '_' + 'REST' + '_' + 'part' + '-' + str(partnum) + '.tif'
			tifDstFile = os.path.join(dstpath, tifFormat)
			os.symlink(img, tifDstFile)
			partnum += 1
		start += 1

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='organize raw ca2 wavelengths into hierarchical directory format for preprocessing')
	parser.add_argument('rawDirs', nargs='+', help='full paths to all directories containing raw data, tail corresponds to animalIDs i.e. 3rd dirname')
	parser.add_argument('--dataset', help='top directory, name of dataset')
	parser.add_argument('--sesType', help='second directory, session type; ie "awake"')
	parser.add_argument('--imgType', help='lowest directory, type of imaging i.e. ca2')
	parser.add_argument('--ratio', type=int, help='number of .tif files per .smr file', default=3)

	args=parser.parse_args()
	
	rawDirs = args.rawDirs
	dataset = args.dataset
	session = 'ses' + '-' + args.sesType
	image = args.imgType
	ratio = args.ratio
	
	homedir = os.getcwd()
	pathList = []
	for animal in rawDirs:
		p, animalName = os.path.split(animal)
		path = os.path.join(homedir, dataset, session, animalName, image)
		pathList.append(path)
	for path in pathList:
		os.makedirs(path, exist_ok = True)

	for animal in rawDirs:
		os.chdir(animal)	
		tifs = []
		smrs = []
		for file in os.scandir():
			name, ext = os.path.splitext(file)
			if ext == '.tif':
				tifs.append(os.path.join(animal, file.name))
			if ext == '.smr':
				smrs.append(os.path.join(animal, file.name))
		tifs = natsort.natsorted(tifs)
		smrs = natsort.natsorted(smrs)
		p, animalName = os.path.split(animal)
		path = os.path.join(homedir, dataset, session, animalName, image)
		mkLinks(tifs, smrs, path, dataset, session, animalName, image, ratio)
