import os
import shutil
import subprocess
import json
import glob

'''
Peter Goodin, Dec 2016
'''

def sabr_dcm2niix_check():
    fnull = open(os.devnull, 'w')
    try:
        retcode = subprocess.call('dcm2niix', stdout = fnull, stderr = subprocess.STDOUT)
        if retcode == 0:
            print('\n***dcm2niix installed! Continuing with conversion.***\n')
    except:
        raise Exception('\n***ERROR! DCM2NIIX NOT PRESENT!***\nPlease place executable in the /bin directory\n')



def sabr_dcm2niix_convert(subj_deid_main_dir, subj_nii_outdir, participant_id, scan_df, n_sessions):
    #First, check the de-id dicom directoy exists
    if os.path.isdir(subj_deid_main_dir) == 0:
        raise Exception('\n***ERROR! DE-IDENTIFIED DICOM DIRECTORY DOES NOT EXIST!***\nPlease rerun SABR.')

    #Next, copy de-id folder structure to nii folder
    try:
        shutil.copytree(subj_deid_main_dir, subj_nii_outdir, ignore = shutil.ignore_patterns('*.nii', '*.nii.gz', '*.mgh')) #Ignore anything with extensions .nii(.gz), .mgh, etc. ADD YOUR OWN IF NEEDED!
    except:
        print('***\nWARNING! NII OUTPUT DIRECTORY ALREADY EXISTS!***\nOverwriting.')
        shutil.rmtree(subj_nii_outdir)
        shutil.copytree(subj_deid_main_dir, subj_nii_outdir, ignore = shutil.ignore_patterns('*.nii', '*.nii.gz', '*.mgh'))

    if n_sessions == 1:
        for scanNo, scan_type in enumerate(scan_df['scan_type']):
            nii_out_path = os.path.join(subj_nii_outdir, 'ses-01', scan_type)
            convert_path = os.path.join(subj_nii_outdir, 'ses-01', scan_type, scan_df['scan_filename'].iloc[scanNo])

            if scan_type == 'func':
                output_fn = participant_id + '_ses-01_task-' + scan_df['scan_filename'].iloc[scanNo] + '_bold'
                output_json_fn = os.path.join(nii_out_path, output_fn + '.json')
                print('\n{}\n'.format(output_json_fn))

                os.system('dcm2niix -z y -b y -f ' + output_fn + ' -o ' + nii_out_path + ' '  + convert_path)

                try:
                    print('Injecting TaskName information into json file.')

                    taskname_dict = {'TaskName': str(scan_df['scan_filename'].iloc[scanNo])}

                    with open(output_json_fn) as f:
                        data = json.load(f)

                    data.update(taskname_dict)

                    with open(output_json_fn, 'w') as f:
                        json.dump(data, f)
                except:
                    print('Scan not present. Moving to next')

            else:
                output_fn = participant_id + '_ses-01_' + scan_df['scan_filename'].iloc[scanNo]

                print('\n{}\n'.format(convert_path))
                print('{}\n'.format(output_fn))
                os.system('dcm2niix -z y -b y -f ' + output_fn + ' -o ' + nii_out_path + ' '  + convert_path)

            #Clean file name to remove dcm2niix adding echo number (e_n) to end of filename.
            im_json_fn = glob.glob(os.path.join(nii_out_path, output_fn.split('.')[0] + '*'))
            test_fn = os.path.split(im_json_fn[0])[-1].split('.')
            if not test_fn[0] is output_fn:

                for rename_fn in im_json_fn:
                    print('Removing echo information from file {}'.format(rename_fn))
                    suffix = '.'.join(rename_fn.split('.')[1:])
                    os.rename(rename_fn, os.path.join(nii_out_path, '.'.join([output_fn, suffix])))


          #Remove dicom directory
            try:
               shutil.rmtree(convert_path)
            except:
               print('\n***WARNING! {} not present for {}***\nMoving to next sequence.'.format(participant_id, scan_df['scan_filename'].iloc[scanNo]))

    elif n_sessions > 1:
        sessions = os.listdir(subj_nii_outdir) #Get directory names of sessions
        for sess in sessions:
            for scanNo, scan_type in enumerate(scan_df['scan_type']):
                nii_out_path = os.path.join(subj_nii_outdir, sess, scan_type)
                convert_path = os.path.join('./', subj_nii_outdir, sess, scan_type, scan_df['scan_filename'].iloc[scanNo])
                print('\n{}\n'.format(convert_path))

                if scan_type == 'func':
                    output_fn = participant_id + '_' + sess + '_task-' + scan_df['scan_filename'].iloc[scanNo]  + '_bold'
                    output_json_fn = os.path.join(nii_out_path, output_fn + '.json')
                    print('\n{}\n'.format(output_json_fn))

                    os.system('dcm2niix -z y -b y -f ' + output_fn + ' -o ' + nii_out_path + ' '  + convert_path)

                    try:
                        print('Injecting TaskName information into json file.')

                        taskname_dict = {'TaskName': str(scan_df['scan_filename'].iloc[scanNo])}

                        with open(output_json_fn) as f:
                            data = json.load(f)

                        data.update(taskname_dict)

                        with open(output_json_fn, 'w') as f:
                            json.dump(data, f)
                    except:
                        print('Scan not present. Moving to next')

                else:
                    output_fn = participant_id + '_' + sess + '_' + scan_df['scan_filename'].iloc[scanNo]
                    os.system('dcm2niix -z y -b y -f ' + output_fn + ' -o ' + nii_out_path + ' '  + convert_path)


                #Clean file name to remove dcm2niix adding echo number (e_n) to end of filename.
                im_json_fn = glob.glob(os.path.join(nii_out_path, output_fn.split('.')[0] + '*'))
                test_fn = os.path.split(im_json_fn[0])[-1].split('.')
                if not test_fn[0] is output_fn:

                    for rename_fn in im_json_fn:
                        print('Removing echo information from file {}'.format(rename_fn))
                        suffix = '.'.join(rename_fn.split('.')[1:])
                        os.rename(rename_fn, os.path.join(nii_out_path, '.'.join([output_fn, suffix])))

                #Remove dicom directory
                try:
                   shutil.rmtree(convert_path)
                except:
                   print('\n***WARNING! {} not present for {}***\nMoving to next sequence.'.format(participant_id, scan_df['scan_filename'].iloc[scanNo]))

    else:
        raise Exception('\n***ERROR! UNABLE TO FIND DE-IDENTIFIED DICOMS!***\nPlease re-run SABR\n')
