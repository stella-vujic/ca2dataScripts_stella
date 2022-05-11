# Preprocessing widefield calcium imaging data: a step-by-step guide
The purpose of this pipeline is to perform some basic quality control and preprocessing on data generated by a two-wavelength widefield calcium imaging experiment. The things you'll need to get started are:
- Raw imaging data from your experiment, in the form of .tif files and their corresponding .smr (trigger) files
- Basic knowledge of linux commands
- Access to a computing cluster (probably)

Before proceeding with the instructions, download this repository to the location in which you are planning to run the pipeline. You can do this easily by cloning the repository onto your desired machine (see directions [here](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)).

## Setting up your software environment
This pipeline uses Python. It is also heavily integrated with [BioImage Suite](https://bioimagesuiteweb.github.io/webapp/) (BIS), a biomedical image analysis software. To run this pipeline, we will need to set up your software environment to be compatible with running Python scripts and BIS.  

### Python environment
The easiest way to use Python on your machine is to first install miniconda. You can find and install the appropriate version for your machine [here](https://docs.conda.io/en/latest/miniconda.html). 

Once miniconda is succesfully installed, we can use the "environment2.yml" file to create an environment for running the pipeline. From the directory containing "environment2.yml", run the command
```
conda env create --file environment2.yml
```

This command simply creates an environment by installing the packages listed in environment.yml. It also names the environment 'ca2Python'. 

Once the environment is created, we need to activate it with the command
```
conda activate ca2Python
```

You are now ready to run the Python scripts! This environment must be activated prior to every use of the pipeline. Once the pipeline has finished, you can exit the environment with the command
```
conda deactivate
```

### Singularity container for BIS integration
Currently, the most convenient way to uses the pipeline entails the use of a Singularity container. Singularity essentially allows for the creation of a portable stack (called a "container") that contains all of the dependencies you need to run a particular piece of software. You can read more about them on this page from [Yale's Center for Research Computing](https://docs.ycrc.yale.edu/clusters-at-yale/guides/singularity/).

If you're not running the pipeline on a cluster that already has Singularity installed, you can install it [here](https://singularity.hpcng.org/user-docs/master/quick_start.html).

A singularity "image" is the collection of files needed for a container. For this pipeline, you can obtain the image in one of two ways: 
- Download the [image](https://drive.google.com/file/d/1H7PIvLk06wPqgDPYvIvD4HHfqPf2lkAm/view?usp=sharing) (1.7GB, md5sum = dcb254e8aa6c86bcd1f57f876b54a60e) to wherever you're running the pipeline
- Build the image using the specification file in install/thing.txt and run the following command:
```
singularity build ubuntuBIS.sif ../biswebSing.recipe
```

## Running the pipeline
Now that your environment is set up, you're ready to run the pipeline! The steps outlined in greater detail below are as follows:
1. Correctly format your raw data files and directories
2. Separate the two wavelengths and convert them to NIfTI files, then verify the data was split correctly
3. Preprocess the images

### Formatting raw input data
Currently, the preprocessing script only supports files organized into a highly specfic directory hierarchy. To format your data in this way, run the following command ***in the directory where you want the organized data to reside*** (any number of raw data directories can be input):
```
python formatDirs.py  /path/to/raw/animal05 /path/to/raw/animal06 --dataset <name> --sesType <name> --imgType ca2 --ratio 3
```
Given the folders containing the raw session data, formatDirs.py creates an organized directory hierarchy that looks something like this:
```
SLC/
SLC/ses-2
SLC/ses-2/animal06
SLC/ses-2/animal06/ca2
SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI1_REST_part-00.tif
SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI1_REST_part-01.tif
SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI1_REST_part-02.tif
SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI2_LED_part-00.tif
SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI2_LED_part-01.tif
SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI2_LED_part-02.tif
SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI3_REST_part-00.tif
SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI3_REST_part-01.tif
SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI3_REST_part-02.tif
SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17-16-06-51_619.smr
SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17-16-35-57_621.smr
SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17-16-58-16_623.smr
```

The files are all symbolic links pointing to the original location of the raw data. The --ratio flag specifies how many parts the TIF files are broken into, due to their often large file size. The default value is 3. The formating for TIF files is:
```
{datasetName}/ses-{sessionType}/{ID}/ca2/{datasetName}_{ID}_ses-{sessionType}_{date}_{runNumber}_{taskLabel}_part-{partNumber}.tif
```
and for electrical recording (smr) files: 
```
{datasetName}/ses-{sessionLabel}/{subID}/ca2/{datasetName}_{subID}_ses-{sessionLabel}_{dateAndTime}.smr
```
The 'ID' will match the original name of the folder containing the raw data (ex. animal06). The date and time are filled in with a dummy variable at the moment due to other code dependencies.

### Separating wavelengths and converting data to NIfTI format

Now that the raw data is correctly organized, you can begin to preprocess the data. For each .smr file, a .csv file describing the trigger timing (or alternation of cyan and UV images)  will be generated. For each .tif file, the wavelengths will be split into two NIfTI files, corresponding to raw signal (cyan) and raw noise (UV).
To accomplish this, run the following command:
```
python genTrigsNii.py organizedData/ preprocDir/ qcFigs/ triggerFix.csv
```
The organizedData/ directory corresponds to the home directory in which you ran formatDirs.py above. 

The preprocDir/ is where the NIfTI and .csv files will reside. Upon a successful run of the code, the data in preprocDir will be organized in the following format: 
```
preprocDir/SLC
preprocDir/SLC/ses-2
preprocDir/SLC/ses-2/animal06
preprocDir/SLC/ses-2/animal06/ca2
preprocDir/SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI1_REST
preprocDir/SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI1_REST/part-00
preprocDir/SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI1_REST/part-00/OpticalOrder.csv
preprocDir/SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI1_REST/part-00/rawsignl.nii.gz
preprocDir/SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI1_REST/part-00/rawnoise.nii.gz
preprocDir/SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI1_REST/part-01
preprocDir/SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI1_REST/part-01/OpticalOrder.csv
preprocDir/SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI1_REST/part-01/rawsignl.nii.gz
preprocDir/SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI1_REST/part-01/rawnoise.nii.gz
preprocDir/SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI1_REST/part-02
preprocDir/SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI1_REST/part-02/OpticalOrder.csv
preprocDir/SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI1_REST/part-02/rawsignl.nii.gz
preprocDir/SLC/ses-2/animal06/ca2/SLC_animal06_ses-2_2019-01-17_EPI1_REST/part-02/rawnoise.nii.gz
```

The qcFigs/ directory refers to where the quality control figures will be output. These figures should be evaluated to ensure that the automatic split makes sense. Below are two examples--one correct and one incorrect--of "successfully" split data. If the figure looks like the incorrect example, you should use the semi automated functions described next to correct the splitting.

Correct           |  Incorrect
:-------------------------:|:-------------------------:
![](figs/correct.png)  |  ![](figs/incorrect.png)

When you first run genTrigsNii, there will not be any corresponding NIfTI files in the output directory if the image cannot be automatically split.
If this is the case, check out the .csv file you specified in the input (called "triggerFix.csv") in this case. The spreadsheet will be populated with the names of the files in your input directory automatically, and will look something like this:

| Img                                             |   CrossedTrigs |   autoFix |   simpFix |   sdFlag |   sdVal |   writeImgs |   manualOverwrite |   splitMethod |   dbscanEps |
|:------------------------------------------------|---------------:|----------:|----------:|---------:|--------:|------------:|------------------:|--------------:|------------:|
| SLC_animal06_ses-2_2019-01-17_EPI1_REST_part-00 |                |           |           |          |         |             |                   |               |             |
| SLC_animal06_ses-2_2019-01-17_EPI1_REST_part-01 |                |           |           |          |         |             |                   |               |             |
| SLC_animal06_ses-2_2019-01-17_EPI1_REST_part-02 |                |           |           |          |         |             |                   |               |             |
| SLC_animal06_ses-2_2019-01-17_EPI2_LED_part-00  |                |           |           |          |         |             |                   |               |             |
| SLC_animal06_ses-2_2019-01-17_EPI2_LED_part-01  |                |           |           |          |         |             |                   |               |             |
| SLC_animal06_ses-2_2019-01-17_EPI2_LED_part-02  |                |           |           |          |         |             |                   |               |             |
| SLC_animal06_ses-2_2019-01-17_EPI3_REST_part-00 |                |           |           |          |         |             |                   |               |             |
| SLC_animal06_ses-2_2019-01-17_EPI3_REST_part-01 |                |           |           |          |         |             |                   |               |             |
| SLC_animal06_ses-2_2019-01-17_EPI3_REST_part-02 |                |           |           |          |         |             |                   |               |             |

You can edit this spreadsheet to help fix the data. 
- For any data that could not be split automatically the code will put a "1" in the "CrossedTrigs" column next to the filename. 
- The code will generate a first pass at two different methods for generating wavelegnth labels for the data based on the mean timeseries of the tif file. 
  - The "simpFix" method assumes that the wavelengths were acquired in a simple interleaved fashion, without any error: cyan,uv,cyan,uv.... etc. 
  - The second method (autoFix) is useful in the case that there is a skipped frame at some point (in which case the order of the wavelengths will swap at some point). It is based on the mean intensity of each frame, and assumes that there are two distributions of data (cyan and uv) with significantly different means. In this case it will assign all frames in the distribution with the higher mean intensity to cyan, and the lower inensity to uv. 
- The code will generate plots of both methods applied to the data and deposit them in the quality control directory, in this case called qcFigs/triggerFix/ (autogenerated). 
- You can look at these and if either the auto fix or the simp fix gives satisfactory results you can then put a "1" in the "writeImgs" column in the spreadsheet, rerun the code and the nifti files will be written to the output directory.

Data with dropped trigger:

![](figs/droppedTrigs.png) 

Proposed fixes (autoFix vs simpFix):

![](figs/droppedTrigsFix.png)


For example in the above image, if you are happy with the autoFix solution, you can edit the csv file like so:

|    | Img                                             |   CrossedTrigs |   autoFix |   simpFix |   sdFlag |   sdVal |   writeImgs |   manualOverwrite |   splitMethod |   dbscanEps |
|---:|:------------------------------------------------|---------------:|----------:|----------:|---------:|--------:|------------:|------------------:|--------------:|------------:|
|  0 | SLC_animal06_ses-2_2019-01-17_EPI1_REST_part-00 |        1       |     1     |           |          |         |     1       |                   |               |             |

Then rerun the code, and the data will output with the correct split of cyan and uv. 

Addional notes:
- Four files can be produced in the qcFigs/triggerFix directory. The will have the same name as the tif file, along with a suffix. They are:
  - imageNameBeforeTSWithTrigs.png: This is the label assignment prior to any fix being applied
  - imageNameTSOnly.png: This is the mean timeseries without labelling
  - imageNamemeanTSAuto.png: This is the plot with the proposed fixes as shown above
  - imageNameAfterTSWithTrigs.png: This is the label assignment after the fix is applied. This will only be generated after the data is split.


- The autoFix method works off of the distribution of the data, but can be thrown off if the cyan and uv distributions are far in terms of mean magnitude and artifactual frame is relatively close, or vice versa. In one of these cases you can put a "1" in the sdFlag column, and then enter a value in the sdVal column. The default sdVal is 8, a higher value will include artifactual frames which have relatively high/low magnitudes, and a lower value will exlcude those with magnitudes closer to the non-artifactual data.

-If the data is too challenging to split using the above methods, it is possible to manually create a trigger file. You can put it is the qcFigs/triggerReplace (autogenerated) directory. Under the directory the folder structure should be similar to the output directory. In this case the file will be copied into the output directory, provided there is a one in the "manualOverwrite" column.

- The splitMethod and dbscanEps columns are part of a function that is under development, please ignore. 

- If you run the code multiple times in order to tweak how the data is split you will need to delete the qc figures, as they do not get overwritten.

### Preprocessing the files

The preprocessing code is currenty best used as a singularity container. It is available for download [here](https://drive.google.com/file/d/1H7PIvLk06wPqgDPYvIvD4HHfqPf2lkAm/view?usp=sharing) (1.7GB, md5sum = dcb254e8aa6c86bcd1f57f876b54a60e)

The pipeline will perform the functions detailed in the figure below:

![](figs/preproc.png)


1) Inputs are two nifti images, corresponding to two wavelengths, the signal sensitive cyan, and the signal insensitive ultraviolet. 
2) Initially it performs a heavy smoothing operation (16 FWHM) on both images, and then motion correction on the heavily smoothed images. This is to avoid the motion correction picking up on small image artifacts that may bias the linear registration algorithm. 
3) It then does a lighter smooth on the input data (4 FWHM), discarding the heavily smoothed data. 
4) It applies the motion correction parameters from the heavily smoothed to the lightly smoothed data, and downsample by a factor of two in the process. 
5) It corrects for an exponential decay in the data, caused by photobleaching, using an exponential trend calculated from the mean time series. 
6) Finally it regresses the UV timeseries from the Cyan timeseries at the pixel level, in order to remove non-signal artifact. 

It can be used as follows:

```
singularity exec ubuntuBIS.simg python3 calciumPreprocess2.py --signal rawsignl.nii.gz --noise rawnoise.nii.gz --signalout signl_out.nii.gz --noiseout dnoise_out.nii.gz --debug True --workdir workdir/ --runoption spatial --createmask False --createmcref True --mask mask.nii.gz
```

The arguments are detailed here:

| Argument    | Required                                      | Type    | Description                                                                                                |
|:------------|:----------------------------------------------|:--------|:-----------------------------------------------------------------------------------------------------------|
| signal      | True                                          | String  | Cyan nifti file                                                                                            |
| noise       | True                                          | String  | UV nifti file                                                                                              |
| signalout   | True                                          | String  | Output filepath for preprocessed cyan                                                                      |
| noiseout    | True                                          | String  | Output filepath for preprocessed uv                                                                        |
| debug       | False                                         | Boolean | If True, will output all intermediate files                                                                |
| workdir     | True                                          | String  | Path to put intermediate files                                                                             |
| runoption   | True                                          | String  | Can be one of “spatial”, “temporal” or “both”                                                              |
| createmask  | True                                          | Boolean | If True will try automated creation of mask                                                                |
| createmcref | True                                          | Boolean | If True will take middle frame of raw cyan as motion correction reference                                  |
| mask        | True if createmask is false; otherwise false  | String  | If createmask is False, give path to other mask. Not needed if runoption is only spatial                   |
| mcrefsignal | True if createmcref is false; otherwise false | String  | If createmcref is False, give path to nifti file with frame to use as motion correction reference for cyan |
| mcrefnoise  | True if createmcref is false; otherwise false | String  | If createmcref is False, give path to nifti file with frame to use as motion correction reference for uv   |

And here is a description of the outputs:

| File                                              | Group                     | Description                                           |
|:--------------------------------------------------|:--------------------------|:------------------------------------------------------|
| rawsignl.nii.gz                                   | Raw Data                  | Raw cyan data                                         |
| rawnoise.nii.gz                                   | Raw Data                  | Raw uv data                                           |
| opticalOrder.csv                                  | Raw Data                  | Trigger timing                                        |
| rawsignl_moco_refimg.nii.gz                       | Raw Data                  | Middle frame from raw cyan                            |
| rawsignl_smooth16.nii.gz                          | Spatial Operation Output  | Cyan data smoothed with median kernel of size 16      |
| rawnoise_smooth16.nii.gz                          | Spatial Operation Output  | Uv data smoothed with median kernel of size 16        |
| rawsignl_smooth4.nii.gz                           | Spatial Operation Output  | Cyan data smoothed with median kernel of size 4       |
| rawnoise_smooth4.nii.gz                           | Spatial Operation Output  | Uv data smoothed with median kernel of size 4         |
| rawsignl_smooth16_moco.nii.gz                     | Spatial Operation Output  | Motion corrected smooth16 data                        |
| rawsignl_smooth16_moco_refimg.nii.gz              | Spatial Operation Output  | Middle frame from motion corrected smooth16 data      |
| rawsignl_smooth16_moco_xfm.npy                    | Spatial Operation Output  | Motion correction parameters                          |
| rawnoise_smooth16_moco.nii.gz                     | Spatial Operation Output  | Motion corrected smooth16 data                        |
| rawnoise_smooth16_moco_refimg.nii.gz              | Spatial Operation Output  | Middle frame from motion corrected smooth16 data      |
| rawnoise_smooth16_moco_xfm.npy                    | Spatial Operation Output  | Motion correction parameters                          |
| rawsignl_smooth4_mococombo.nii.gz                 | Spatial Operation Output  | Motion correction parameters applied to smooth4 data  |
| rawnoise_smooth4_mococombo.nii.gz                 | Spatial Operation Output  | Motion correction parameters applied to smooth4 data  |
| signl_out.nii.gz                                  | Spatial Operation Output  | Output of spatial operations                          |
| noise_out.nii.gz                                  | Spatial Operation Output  | Output of spatial operations                          |
| rawsignl_smooth4_mococombo_threeparts.nii.gz      | Spatial Operation Output  | The stitched together data from three parts of an EPI |
| rawnoise_smooth4_mococombo_threeparts.nii.gz      | Spatial Operation Output  | The stitched together data from three parts of an EPI |
| rawsignl_smooth4_mococombo_photob.nii.gz          | Temporal Operation Output | Photobleach corrected cyan                            |
| rawnoise_smooth4_mococombo_photob.nii.gz          | Temporal Operation Output | Photobleach corrected uv                              |
| rawsignl_smooth4_mococombo_photob_wvlthreg.nii.gz | Temporal Operation Output | Cyan with uv regressed out                            |
| signl_out.nii.gz                                  | Temporal Operation Output | Output of temporal operations                         |
| noise_out.nii.gz                                  | Temporal Operation Output | Output of temporal operations                         |

There is a script cal runPreproc.py to provide easy preprocessing of the bids like directory output from genTrigs.py. It requires the following:

- An preprocessing directory setup like above.
- A path to premade masks. The files should be named like: {datasetName}_{subID}_ses-{sessionLabel}_RotOptical_maskRPI.nii.gz
- The singularity image file


And can be used like so:

```
python3 runPreproc.py preprocDir/ maskDir/ ubuntuBIS.sif
```

The way the data is setup at the moment, it is required that we do spatial prepreprocessing first, then stitch together three image parts, and do temporal processing. This script will perform these operations sequentially. If you want to run on a HPC/Cluster you can pass a flag to the command and instead of running the pipeline, it will print all the commands to a file called "joblist.txt" in your current directory. This can then be passed to a scheduler.

```
python3 runPreproc.py preprocDir/ maskDir/ ubuntuBIS.sif --hpc 1
```


