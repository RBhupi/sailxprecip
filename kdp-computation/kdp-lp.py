#
# The `run_kdp_to_nc` is the main function for the KDP processing. 
# It calls the `kdp_lp` function to compute the KDP and PHIDP and
# then calls `write_kdp_to_nc` to write the data to a NetCDF file.

# Imports the libraries for the KDP processing.
import pyart
import numpy as np

import sys
import os
import glob

import argparse



def run_kdp_to_nc(radar_fname, args):
    """
    Main function to run the KDP process and save output.
    """
    try:
        radar = kdp_lp(radar_fname, args)
    except OSError:
        print(f"Error processing {radar_fname}. Skipped!")
    else:
        write_kdp_to_nc(radar_fname, radar, args)


def read_radar(radar_fname, sweeps=[]):
    """
    Reads PyART radar data object and extracts sweeps.
    """
    radar = pyart.io.read(radar_fname)

    # Extract given sweeps 
    if sweeps:
        radar = radar.extract_sweeps(sweeps)
    return radar


def kdp_lp(radar_fname, args):
    """
    Comput KDP using Scott Giangrande's LP method. 

    Saves corrected PHIDP and KDP.
    """ 

    radar = read_radar(radar_fname, args.sweeps)
    
    PHIDP_LP, KDP_LP = pyart.correct.phase_proc_lp(radar, 0.0,
                                                   ncp_field='NCP',
                                                   refl_field='DBZ',
                                                   rhv_field='RHOHV',
                                                   phidp_field='PHIDP')

    radar.fields['PHIDP_LP']=PHIDP_LP
    radar.fields['KDP_LP']=KDP_LP
    
    return radar



def texture(radar):
    """
    Comput velocity and PHIDP texture, not used.
    """
    nyquist_value = radar.fields['VEL']['data'].max()
    vel_texture = pyart.retrieve.calculate_velocity_texture(radar,
                                                        vel_field='VEL',
                                                        nyq=nyquist_value)

    radar.add_field('velocity_texture', vel_texture, replace_existing=True)

    phidp_texture = pyart.retrieve.texture_of_complex_phase(radar, phidp_field='PHIDP', phidp_texture_field='phidp_texture')

    radar.add_field('phidp_texture', phidp_texture, replace_existing=True)
    return radar


def write_kdp_to_nc(radar_fname, radar, args):
    #remove all unwanted fields
    radar.fields.pop('VEL')
    radar.fields.pop('WIDTH')
    radar.fields.pop('PHIDP')
    radar.fields.pop('unfolded_differential_phase')
    #radar.fields.pop('DBZhv')
    
    cfrad_fname = os.path.basename(radar_fname.replace('.b1.nc', '.b1_kdp-lp.nc'))
    odir = args.out_dir
    cfrad_fname = odir + cfrad_fname
    print(f"Processed {radar_fname}. \n Writting output in {cfrad_fname}")
    pyart.io.write_cfradial(cfrad_fname, radar)



def main(args):
    """
    Run KDP processing for all files in the directory.
    """
    
    if not os.path.exists(args.out_dir):
        # Create a new directory
        os.makedirs(args.out_dir)
        print(f"The out_dir is created! \n {args.out_dir}")


    files = sorted(glob.glob(args.glob_str))
    print(len(files))
    
    for radar_fname in files:
        print(f"Processing {radar_fname} ...")
        run_kdp_to_nc(radar_fname, args)
        break


# Argument Parser
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--glob",
        type=str,
        dest="glob_str",
        default='/gpfs/wolf/atm124/proj-shared/gucxprecipradarcmacS2.c1/ppi/*/*.nc',
        help="wildcard string for searching files",
    )
    parser.add_argument(
        "--out",
        dest="out_dir",
        type=str, 
        default= '/ccsopen/home/braut/output/kdp_lp-test1/',
        help="output path"
        )

    parser.add_argument(
        "--sweeps",
        type=int,
        dest="sweeps",
        default=[],
        nargs="+",
        help="select sweeps",
    )

    args = parser.parse_args()
    main(args)


