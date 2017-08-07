import os
import os.path as op
import shutil
import sys 
import nibabel as nib
import json


def createBIDS(projDir, pid, visitNum, sessionNum):
    fromDir = op.join(projDir,'data', 'imaging', 'participants', pid, 'visit%i' % visitNum,'session%i' % sessionNum)
    toDirRoot =  op.join(projDir, 'data', 'imaging', 'BIDS')
    subStr = '%i%i%i' % (pid,visitNum,sessionNum)
    toDir = op.join(toDirRoot, 'sub-' + subStr)
    if not os.path.exists(toDir):
        os.makedirs(toDir)
        os.makedirs(toDir + '/anat')
        os.makedirs(toDir + '/func')
        os.makedirs(toDir + '/dwi')

    ''' Copy over anat '''
    shutil.copyfile(fromDir + '/anatomical/T1w-0_defaced.nii.gz', toDir + '/anat/sub-%s_T1w.nii.gz' % subStr)

    ''' Copy over dwi (incomplete -- missing 2 files)'''
    # shutil.copyfile(fromDir + '/dwi/dwi_raw.nii.gz', toDir + '/dwi/sub-01_dwi.nii.gz')
    # shutil.copyfile(fromDir + '/dwi/dwi_raw.json', toDir + '/dwi/sub-01_dwi.json')


    ''' Copy over func '''
    for root, dirs, files in os.walk(fromDir + '/fmri'):
        taskName = ''
        repTime = 0
        flag = False
        for file in files:
            if(file.endswith('.json')):
                taskName = file.split('.')[0]
                with open(os.path.join(root, file)) as f:    
                    data = json.load(f)
                repTime = data['RepetitionTime']
            if(file == 'task-rest_bold.json'):
                flag = True

        for file in files:
            if(not flag):
                break
            if(file.endswith('.nii.gz')):
                fileName = 'sub-01_' + taskName + '.nii.gz'
                shutil.copyfile(os.path.join(root, file), toDir + '/func/' + fileName)
                toFile = toDir + '/func/' + fileName
                img = nib.load(toFile)
                hdr = img.get_header()
                hdr['pixdim'][4] = repTime
                img.to_filename(img.get_filename())

                ''' Make sure repetition time was saved to nifti file '''
                img = nib.load(toFile)
                assert(img.get_header()['pixdim'][4] == repTime)

            elif(file.endswith('.json')):
                fileName = 'sub-01_' + taskName + '.json'
                shutil.copyfile(os.path.join(root, file), toDir + '/func/' + fileName)              


    ''' Delete the .DS_Store files '''
    # for root, dirs, files in os.walk(toDir):
    #     for file in files:
    #         if(file == '.DS_Store'):
    #             os.remove(os.path.join(root, file))

    return toDirRoot, subStr


#if(len(sys.argv) == 5):
#    createBIDS(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
