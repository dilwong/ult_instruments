'''
Python Node in LabVIEW VI 'gate sts.vi' for gate-sweep Bias Spectroscopy.
Takes a filename, the header attributes, the data channels, and the numerical data, 
and saves this information as a HDF5 file.

Tested in Python 3.6.0 and LabVIEW 2021 (32-bit version).
'''

import sys
import time
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category = FutureWarning)
    import h5py

def saveBiasSpectroscopyasHDF5(filename, attributes, channels, data):
    if sys.version_info.major == 2:
        FileInUseError = IOError
    elif sys.version_info.major == 3:
        FileInUseError = BlockingIOError
    while True:
        try:
            with h5py.File(filename, 'a') as f:
                if 'data' not in f.keys():
                    f.create_group('data')
                    f.attrs['index'] = 0
                    f.attrs['size'] = 0
                dataindex = f.attrs['index'] + 1
                while ('%09d' % dataindex) in f['data'].keys():
                    dataindex += 1
                dataname = '%09d' % dataindex
                f['data'].create_dataset(dataname, data = data.T)
                for attr in attributes:
                    f['data'][dataname].attrs[ attr[0] ] = attr[1]
                f['data'][dataname].attrs['channels'] = '||'.join(channels)
                f.attrs['size'] = len(f['data'])
                f.attrs['index'] = dataindex
        except FileInUseError:
            time.sleep(0.1)
            continue
        break
    return dataname