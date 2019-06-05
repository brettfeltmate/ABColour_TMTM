# ABColour_TMTM

This experiment is intended to provide a modified tool to measure the attentional blink (see the project description on the OSF at https://osf.io/34sqx/ for detailed explanation of the blink). The important distinction here is that in addition to the typical 'discrete' task used to report targets (i.e., which number from 1-9), a secondary 'continuous' task is employed (i.e., what colour?).

In this design, participants are asked to complete a series of trials wherein they report some dimension (numerical identity, colouring) of two targets presented in rapid sequence. 

Within a trial, four items are presented: T1 (1-9, randomly coloured), a mask (an array of randomly coloured squares), T2 (identity & colouring unique from T1), and a second mask. The time between onset of T1 & T2 is randomly selected from 5 TTOAs (target-target onset asychrony): 120, 240, 360, 480, & 600ms. At the end of the sequence, the participant is probed to make their response.

Participants complete two blocks of 360 trials, for one block they are asked to report the numerical identites of each target, and their colouring the other block. Identity is reported by pressing the appropriate number key, colouring is reported by selecting within a colour wheel by means of mouse click. Prior to each of these blocks, participants complete a practice block wherein only one target is presented. During practice, participant performance is monitored by the program, and stimulus durations of the target, and its mask, are adjusted to make the task easier (to avoid 'floor' effects) or harder (to avoid 'ceiling' effects). Once performance stablizes between 20% & 80% response accuracy, the practice block is terminated and the final stimulus durations are used for both targets (and their masks) within the experimental block. 

In order to run the experiment, you will first need to download & install KLibs with which this experiment is written. KLibs is open-source and can be found at https://github.com/a-hurst/klibs. This experiment needs no equipement to be run, short of a standard computer setup including mouse and keyboard. 

Those with 'fancy' monitors should take note that stimulus durations are specified in units of the display computer's screen refresh rate. Most monitors refresh at a rate of 60Hz (1 refresh every 16.7ms), and this experiment is coded with that in mind. If your monitor refreshes at a faster or slower rate, stimulus durations will need to be adjusted (within experiment.py) to compensate for this. 

Once KLibs has been installed, the experiment is run using terminal. First, change the directory to that of the experiment (ex. cd path/to/experiment/folder/) then by using the command 'klibs run ##' where ## is replaced by the display size (i.e., 21.5). In the event that you want to simply demo the experiment, without saving trial data, add '-d' to the end of the run command to run the experiment in 'development' mode. You MUST be within the experiment folder for this command to work.

In order to export the saved data, run 'klibs export' in terminal (again, in the experiment directory), and a data folder will be created (if not already present) populated with all of the data files (one for each experiment run). Because KLibs saves all data in a database, even when deleted the files can be repopulated by running the export command. The caveat being that KLibs will always export ALL the data, which means that it will create duplicates of files already present. So, for sanity, it's best to export sparingly.

PS: If there is any information that would have been helpful to include in this document, please let me know and I'll update it accordingly.
