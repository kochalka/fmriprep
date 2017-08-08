import os
import os.path as op
import shutil
import sys 
import nibabel as nib
import json


def createBIDS(projDir, pid, visitNum, sessionNum, runName):
    fromDir = op.join(projDir,'data', 'imaging', 'participants', pid, 'visit%s' % visitNum,'session%s' % sessionNum)
    toDirRoot =  op.join(projDir, 'data', 'imaging', 'BIDS')
    subStr = '%s%s%s' % (pid,visitNum,sessionNum)
    toDir = op.join(toDirRoot, 'sub-' + subStr)
    if not os.path.exists(toDir):
        os.makedirs(toDir)
        os.makedirs(toDir + '/anat')
        os.makedirs(toDir + '/func')

    ''' Copy over anat '''
    shutil.copyfile(fromDir + '/anatomical/T1w-0_defaced.nii.gz', toDir + '/anat/sub-%s_T1w.nii.gz' % subStr)

    ''' Copy over func '''
    for root, dirs, files in os.walk(fromDir + '/fmri/' + runName + '/unnormalized'):
        taskName = ''
        repTime = 0
        for file in files:
            if(file.endswith('.json')):
                taskName = file.split('.')[0]
                with open(os.path.join(root, file)) as f:    
                    data = json.load(f)
                repTime = data['RepetitionTime']
                fileName = 'sub-01_' + taskName + '.json'
                shutil.copyfile(os.path.join(root, file), toDir + '/func/' + fileName)  

        for file in files:
            if(file.endswith('.nii.gz')):
                fileName = ('sub-%s_' % subStr) + taskName + '.nii.gz'
                shutil.copyfile(os.path.join(root, file), toDir + '/func/' + fileName)
                toFile = toDir + '/func/' + fileName
                img = nib.load(toFile)
                hdr = img.get_header()
                hdr['pixdim'][4] = repTime
                img.to_filename(img.get_filename())

                ''' Make sure repetition time was saved to nifti file '''
                img = nib.load(toFile)
                assert(img.get_header()['pixdim'][4] == repTime)         

    return toDirRoot, subStr


def moveToProject(projDir, pid, visitNum, sessionNum, runName, processedDir):
    subStr = '%s%s%s' % (pid,visitNum,sessionNum)
    fromDir = op.join(processedDir, 'fmriprep', 'sub-' + subStr, 'func')
    toDir = op.join(projDir,'data', 'imaging', 'participants', pid, 'visit%s' % visitNum,'session%s' % sessionNum, 'fmri', runName, 'preprocessed)
    if not os.path.exists(toDir):
        #os.makedirs('my_dataset')
        os.makedirs(toDir)
    for root, dirs, files in os.walk(fromDir):
        for file in files:
            if(file.endswith('.nii.gz')):
                fileName = file.split('.')[0]
                if 'brainmask' in fileName:
                    shutil.copyfile(os.path.join(root, file), toDir + '/brainmask.nii.gz')   
                elif 'preproc' in fileName:
                    shutil.copyfile(os.path.join(root, file), toDir + '/I_preproc.nii.gz')  
