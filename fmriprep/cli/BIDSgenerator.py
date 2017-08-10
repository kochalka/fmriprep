import os
import os.path as op
import shutil
import sys 
import nibabel as nib
import json
import numpy as np

def createBIDS(projDir, pid, visitNum, sessionNum, runName = None):
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
    if runName is None:
        root, tasks, files = next(os.walk(fromDir + '/fmri'))
        for task in tasks:
            for subRoot, dirs, files in os.walk(os.path.join(root, task, 'unnormalized')):
                repTime = 0
                for file in files:
                    if(file.endswith('.json')):
                        with open(os.path.join(subRoot, file)) as f:    
                            data = json.load(f)
                        repTime = data['RepetitionTime']
                        fileName = ('sub-%s_task-' % subStr) + task + '_bold.json'
                        shutil.copyfile(os.path.join(subRoot, file), toDir + '/func/' + fileName)  

                for file in files:
                    if(file.endswith('.nii.gz')):
                        fileName = ('sub-%s_task-' % subStr) + task + '_bold.nii.gz'
                        shutil.copyfile(os.path.join(subRoot, file), toDir + '/func/' + fileName)
                        toFile = toDir + '/func/' + fileName
                        img = nib.load(toFile)
                        hdr = img.get_header()
                        hdr['pixdim'][4] = repTime
                        img.to_filename(img.get_filename())

                        ''' Make sure repetition time was saved to nifti file '''
                        img = nib.load(toFile)
                        assert(img.get_header()['pixdim'][4] == repTime)     

    else:
        for root, dirs, files in os.walk(fromDir + '/fmri/' + runName + '/unnormalized'):
            repTime = 0
            for file in files:
                if(file.endswith('.json')):
                    with open(os.path.join(root, file)) as f:    
                        data = json.load(f)
                    repTime = data['RepetitionTime']
                    fileName = ('sub-%s_' % subStr) + runName + '.json'
                    shutil.copyfile(os.path.join(root, file), toDir + '/func/' + fileName)  

            for file in files:
                if(file.endswith('.nii.gz')):
                    fileName = ('sub-%s_' % subStr) + runName + '.nii.gz'
                    shutil.copyfile(os.path.join(root, file), toDir + '/func/' + fileName)
                    toFile = toDir + '/func/' + fileName
                    img = nib.load(toFile)
                    hdr = img.get_header()
                    hdr['pixdim'][4] = repTime
                    img.to_filename(img.get_filename())

                    ''' Make sure repetition time was saved to nifti file '''
                    img = nib.load(toFile)
                    assert np.allclose(img.get_header()['pixdim'][4],repTime), 'image header TR=%f, sidecar TR=%f' % (img.header['pixdim'][4],repTime)

    return toDirRoot, subStr


def moveToProject(projDir, pid, visitNum, sessionNum, processedDir):
    subStr = '%s%s%s' % (pid,visitNum,sessionNum)
    fromDir = op.join(processedDir, 'fmriprep', 'sub-' + subStr, 'func')

    toDir = op.join(projDir,'data', 'imaging', 'participants', pid, 'visit%s' % visitNum,'session%s' % sessionNum, 'fmri', runName, 'preprocessed')
    if not os.path.exists(toDir):
        #os.makedirs('my_dataset')
        os.makedirs(toDir)

    for root, dirs, files in os.walk(fromDir):
        for file in files:
            if(file.endswith('.nii.gz')):
                start = 'sub-%s_task-' % subStr
                end = '_bold'
                fileName = file.split('.')[0]
                taskName = (file.split(start))[1].split(end)[0]
                toSubDir = op.join(toDir, taskName, 'preprocessed')
                if not os.path.exists(toSubDir):
                    os.makedirs(toSubDir)
                if 'brainmask' in fileName:
                    shutil.copyfile(os.path.join(root, file), toSubDir +  '/brainmask.nii.gz')   
                elif 'preproc' in fileName:
                    shutil.copyfile(os.path.join(root, file), toSubDir + '/I_preproc.nii.gz') 
