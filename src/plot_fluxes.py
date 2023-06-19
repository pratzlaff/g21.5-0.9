import argparse
import astropy.io.fits
import glob as gl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import re

# glob flux files
# foreach flux file
#  - get PI file, read instrument and date
#  - save flux CI
# plot

def plot(data, args):

    rows = { 'HRC-S' : 0, 'HRC-I' : 1 }
    cols = { 'plerion' : 0, 'halo' : 1 }
    titles = { 0 : 'G21.5-0.9 PWN: HRC-S', 1 : 'HRC-I' }

    fig, axs = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(8.5, 11))
    for det in rows:
        for src in 'plerion', : 

            x = data[det][src]['date']
            y = data[det][src]['flux']
            errlo = data[det][src]['errlo']
            errhi = data[det][src]['errhi']

            row, col = rows[det], cols[src]
            ax = axs[row]#, col]
            ax.errorbar(x, y, yerr=[errlo, errhi], fmt='o')
            ax.set_title(titles[row], loc='right')
            if col==0:
                ax.set_ylabel('Flux')

            if row==1:
                ax.set_xlabel('Date')
                
    #fig.suptitle('G21.5-0.9')

    plt.tight_layout()
    if (args.outfile):
        plt.savefig(args.outfile)
    else:
        plt.show()
    plt.close()

def read_obsid_det_date(f):
    hdulist = astropy.io.fits.open(f)
    header = hdulist[1].header
    obsid = header['obs_id']
    detnam = header['detnam']
    mjd = header['mjd-obs']

    hdulist.close()

    date = 1998 + (mjd-50814)/365.2425

    return obsid, detnam, date

def get_pifiles_info(files):
    obsids, dets, dates, srcs = [], [], [], []
    for f in files:
        obsid, det, date = read_obsid_det_date(f)
        obsids.append(obsid)
        dets.append(det)
        dates.append(date)
        srcs.append(re.findall('/\d+_(\w+)_0001', f)[0])
    return obsids, dets, dates, srcs

def pifile_from_fluxfile(fluxfile):
    return fluxfile[:-10]+'_0001.pi'

def get_files(globs):
    fluxfiles = []
    pifiles = []
    for glob in globs:
        fluxfiles_ = gl.glob(glob)
        pifiles_ = [pifile_from_fluxfile(f) for f in fluxfiles_]
        fluxfiles.extend(fluxfiles_)
        pifiles.extend(pifiles_)
    return fluxfiles, pifiles

def mk_data_struct(fluxfiles, obsids, dets, dates, srcs):
    data = { }
    for det in dets:
        data[det] = { }
        for src in srcs:
            data[det][src] = {
                'obsid' : [],
                'flux' : [],
                'errlo' : [],
                'errhi' : [],
                'date' : []
            }

    for i in range(len(fluxfiles)):
        fluxfile = fluxfiles[i]
        obsid = obsids[i]
        det = dets[i]
        date = dates[i]
        src = srcs[i]
        try:
            flux, errlo, errhi = read_fluxes(fluxfile)
            data[det][src]['obsid'].append(obsid)
            data[det][src]['flux'].append(flux)
            data[det][src]['errlo'].append(errlo)
            data[det][src]['errhi'].append(errhi)
            data[det][src]['date'].append(date)
        except:
            pass
    for det in data:
        for src in data[det]:
            for key in data[det][src]:
                data[det][src][key] = np.array(data[det][src][key])

    return data

def read_fluxes(fluxfile):
    hdulist = astropy.io.fits.open(fluxfile)
    data = hdulist[1].data
    flux = data.field('net_mflux_aper')[0]
    errlo = flux - data.field('net_mflux_aper_lo')[0]
    errhi = data.field('net_mflux_aper_hi')[0] - flux
    hdulist.close()
    return flux, errlo, errhi

def main():
    parser = argparse.ArgumentParser(
        description='Plot fluxes from HRC G21.5-0.9 observatinos'
    )
    parser.add_argument('-o', '--outfile', help='Output file name.')
    parser.add_argument('-g', '--globs', default='./srcflux/i/*.flux', nargs='+', help='Flux filenames globs.')
    args = parser.parse_args()

    print(args.globs)
    fluxfiles, pifiles = get_files(args.globs)
    print(fluxfiles, pifiles)
    obsids, dets, dates, srcs = get_pifiles_info(pifiles)
    sorti = sorted(range(len(dates)), key=lambda ix: dates[ix])

    fluxfiles = [fluxfiles[i] for i in sorti]
    pifiles = [pifiles[i] for i in sorti]
    obsids = [obsids[i] for i in sorti]
    dets = [dets[i] for i in sorti]
    dates = [dates[i] for i in sorti]
    srcs = [srcs[i] for i in sorti]

    data = mk_data_struct(fluxfiles, obsids, dets, dates, srcs)
    print(data)
    plot(data, args)

if __name__ == '__main__':
    main()
