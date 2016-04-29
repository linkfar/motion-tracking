"""A script for parsing the Alov bounding box `.ann` files."""

import sys
import os
import itertools
import shutil
import pandas as pd

def parse_file(bbox_dir, filename): 
    """Parse an individual `.ann` file and output the relevant elements.

    Args: 
    ----
        bbox_dir: str
            Holds the directory path to the `.ann` file. 
        filename: str
            Holds the name of the `.ann` file. 

    Output: 
    ------
        output_lst: list of lists 
            Holds the elements grabbed from the `.ann` file. 
    """

    parsed_df = pd.read_table(bbox_dir + filename, sep=' ', header=None)
    parsed_df['filename'] = filename
    parsed_df['directory'] = parsed_df['filename'].apply(lambda fn: fn.split('_')[0])

    return parsed_df

def cp_files(filepaths_df, input_dir, output_dir): 
    """Copy over the files given by the attributes in the dataframe. 

    Args: 
    -----
        filepaths_df: pandas DataFrame
            Holds 3 columns, each of which holds a piece that 
            determines the input filepaths. We'll copy the files 
            at these filepaths to the output_dir.
        input_dir: str
            Holds the first part of the input directory path, used 
            for obtaining the full path pointing to the files to copy. 
        output_dir: str
            Holds the directory of where to copy the file. 
    """
    
    # The video numbers are zero padded on the left. 
    filepaths_df['vid_num'] = filepaths_df['frame'].astype(str).apply(lambda 
            frame: frame.zfill(8))

    # Need to replace the filename ext. in the DataFrame with `.jpg` and 
    # provide the full relative path point to what to move. 
    filepaths_df['filename'] = filepaths_df['filename'].apply(lambda filename: 
            filename.replace('.ann', ''))
    filepaths_df['input_filepath'] = input_dir + \
            filepaths_df['directory_path'] + '/' + filepaths_df['filename'] + \
            '/' + filepaths_df['vid_num'] + '.jpg'

    # Need to provide the full relative output path to point to where to move. 
    # The `filename` is being used as part of what to save so that images 
    # can be identified (there are lot with the same number, so we need an
    # identifying feature). 
    filepaths_df['output_filepath'] = output_dir + filepaths_df['filename'] + \
            '_' + filepaths_df['vid_num'] + '.jpg'

    for input_fp, output_fp in zip(filepath_df['input_filepath'], 
            filepath_df['output_filepath']): 
        shutil.copy(input_fp, output_fp)

if __name__ == '__main__': 
    input_dir = sys.argv[1]
    output_filepath = sys.argv[2]
    output_dir = sys.argv[3]

    bbox_dir = input_dir + 'bb/'
    ann_files_by_dir = (i[2] for i in os.walk(bbox_dir))
    bbox_ann_filenames = itertools.chain(*ann_files_by_dir)


    cols = ['frame', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'x4', 
            'y4', 'filename', 'directory_path']
    parsed_df = pd.concat(parse_file(bbox_dir, filename) for 
            filename in bbox_ann_filenames)
    parsed_df.columns = cols
    parsed_df.to_csv(output_filepath, index=False)

    frames_dir = input_dir + 'frames/'
    filepath_cols = ['directory_path', 'filename', 'frame']
    filepath_df = parsed_df[filepath_cols]
    cp_files(filepath_df, frames_dir, output_dir)