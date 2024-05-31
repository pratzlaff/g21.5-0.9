import argparse
import astropy.io.fits
from braceexpand import braceexpand
import glob as gl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from pprint import pprint;
import re

plt.rcParams.update({'font.size' : 14})

def braced_glob(path):
    l = []
    for x in braceexpand(path):
        l.extend(gl.glob(x))

    return l

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
        srcs.append(re.findall(r'/\d+_(\w+)_0001', f)[0])
    return obsids, dets, dates, srcs

def pifile_from_fluxfile(fluxfile):
    return fluxfile[:-10]+'_0001.pi'

def get_files(globs):
    fluxfiles = []
    pifiles = []
    for glob in globs:
        fluxfiles_ = braced_glob(glob)
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

            # special case, correction from Vinay, from 2020-06-04 email
            # "divide by (1-[0.373,0.445]) to get corrected flux"
            if int(obsid) == 22855:
                factor_lo = 1/(1-.337)
                factor_hi = 1/(1-.445)
                factor = 0.5*(factor_hi+factor_lo)
                factor_err = 0.5*(factor_hi-factor_lo)
                flux_new = flux * factor
                errlo_new = np.sqrt(flux_new**2*((errlo/flux)**2 + (factor_err/factor)**2))
                errhi_new = np.sqrt(flux_new**2*((errhi/flux)**2 + (factor_err/factor)**2))
                print(factor, factor_err, flux,  errlo, errhi)
                flux, errlo, errhi = flux_new, errlo_new, errhi_new

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
    flux = data.field('net_umflux_aper')[0]
    errlo = flux - data.field('net_umflux_aper_lo')[0]
    errhi = data.field('net_umflux_aper_hi')[0] - flux
    hdulist.close()
    return flux, errlo, errhi

def main():
    parser = argparse.ArgumentParser(
        description='Plot fluxes from HRC G21.5-0.9 observatinos',
    )
    parser.add_argument('-o', '--outfile', help='Output file name.')
    parser.add_argument('--isuffix', help='Brace expansion addition to I glob.')
    parser.add_argument('-v', '--vlk', action='store_true', help='Use srcflux output when run with Vinay\'s regions.')
    parser.add_argument('-l', '--latest', action='store_true', help='Use only the latest QE.')
    parser.add_argument('--noi', help='Do not plot I fluxes.', action='store_true')
    parser.add_argument('--nos', help='Do not plot S fluxes.', action='store_true')
    args = parser.parse_args()

    if args.noi or args.nos:
        nrows = 1
        figsize = (11, 8.5)
    else:
        nrows = 2
        figsize = (8.5, 11)

    fig, axes = plt.subplots(nrows=nrows, ncols=1, sharex=True, figsize=figsize)

    if not args.nos:
        ax = axes
        if not args.noi:
            ax = axes[0]
        ax.set_ylabel(r'Flux $(\mathregular{erg\;cm^{-2}\;s^{-1}})$')
        ax.set_title('G21.5-0.9 Plerion')
        ax.set_title('HRC-S', loc='right')

        qe_s = ['N0014', 'N0015', 'N0016']
        label_s = { 'N0014' : 'QE N0014',
                    'N0015' : 'QE N0015',
                    'N0016' : 'QE N0016',
                   }
        fmt_s = { 'N0014' : '^',
                  'N0015' : 'o',
                  'N0016' : 's',
                 }

        if args.latest:
            qe_s = [qe_s[0], qe_s[-1]]
            fmt_s = { qe_s[0]:'^c', qe_s[1]:'^c' }

        for qe in qe_s:
            glob = '/data/legs/rpete/flight/g21.5-0.9/srcflux{}/qe_{}_qeu_N001[45678]/*.flux'.format('/vlk' if args.vlk else '', qe)

            fluxfiles, pifiles = get_files((glob,))
            obsids, dets, dates, srcs = get_pifiles_info(pifiles)
            sorti = sorted(range(len(dates)), key=lambda ix: dates[ix])

            fluxfiles = [fluxfiles[i] for i in sorti]
            print(glob)
            print(fluxfiles)
            pifiles = [pifiles[i] for i in sorti]
            obsids = [obsids[i] for i in sorti]
            dets = [dets[i] for i in sorti]
            dates = [dates[i] for i in sorti]
            srcs = [srcs[i] for i in sorti]

            data = mk_data_struct(fluxfiles, obsids, dets, dates, srcs)

            det, src = 'HRC-S', 'plerion'
            x = data[det][src]['date']
            y = data[det][src]['flux']
            errlo = data[det][src]['errlo']
            errhi = data[det][src]['errhi']

            mask = x > 1998

            if qe == 'N0014' and args.latest:
                mask = x < 2010

            if qe > 'N0014':
                mask = x > 2010

            ax.errorbar(x[mask], y[mask],
                        yerr=[errlo[mask], errhi[mask]],
                        fmt=fmt_s[qe], label=label_s[qe])

            if qe == 'N0014':
                mask = x < 2010
                mean = np.mean(y[mask])
                std = np.std(y[mask])
                ax.axhline(mean, color='k', ls='--')
                eb = ax.errorbar((0.5*(x[0]+x[-1]),), (mean,), (std,), fmt='', ecolor='k', capsize=12)
                eb[-1][0].set_linestyle('--')

        if not args.latest:
            ax.legend(loc='upper left')

    if not args.noi:
        ax = axes
        if not args.nos:
            ax = axes[1]
        else:
            ax.set_title('G21.5-0.9 Plerion')

        qe_i = ['N0011', 'N0012', 'N0013', 'N0014', 'N0015']
        fmt_i = { 'N0011':'^', 'N0012':'o', 'N0013':'s', 'N0014':'v', 'N0015':'P' }

        if args.latest:
            qe_i = [qe_i[0], qe_i[-1]]
            fmt_i = { qe_i[0]:'^c', qe_i[1]:'^c' }

        ax.set_title('HRC-I', loc='right')
        ax.set_ylabel(r'Flux $(\mathregular{erg\;cm^{-2}\;s^{-1}})$')
        ax.set_xlabel('Date')

        det, src = 'HRC-I', 'plerion'
        for qe in qe_i:
            brace = ''
            if args.isuffix and qe == 'N0015':
                brace = '{{,{}}}'.format(args.isuffix)
                brace = args.isuffix
            glob = '/data/legs/rpete/flight/g21.5-0.9/srcflux{}/i_qe_{}{}/*.flux'.format('/vlk' if args.vlk else '', qe, brace)
            print(glob)
            fluxfiles, pifiles = get_files((glob,))
            print(fluxfiles)
            obsids, dets, dates, srcs = get_pifiles_info(pifiles)
            sorti = sorted(range(len(dates)), key=lambda ix: dates[ix])

            fluxfiles = [fluxfiles[i] for i in sorti]
            pifiles = [pifiles[i] for i in sorti]
            obsids = [obsids[i] for i in sorti]
            dets = [dets[i] for i in sorti]
            dates = [dates[i] for i in sorti]
            srcs = [srcs[i] for i in sorti]

            data = mk_data_struct(fluxfiles, obsids, dets, dates, srcs)

            x = data[det][src]['date']
            y = data[det][src]['flux']
            errlo = data[det][src]['errlo']
            errhi = data[det][src]['errhi']

            mask = x > 1998

            if qe == 'N0011' and args.latest:
                mask = x < 2016

            if qe > 'N0011':
                mask = x > 2016

            ilabel = f'QE {qe}'
            if args.isuffix and qe == 'N0015':
                ilabel += args.isuffix
            print(qe, x[mask], y[mask])
            ax.errorbar(x[mask], y[mask],
                        yerr=[errlo[mask], errhi[mask]],
                        fmt=fmt_i[qe], label=ilabel)

            if qe == 'N0011':
                mask = x < 2016
                mean = np.mean(y[mask])
                std = np.std(y[mask])
                ax.axhline(mean, color='k', ls='--')
                eb = ax.errorbar((0.5*(x[0]+x[-1]),), (mean,), (std,), fmt='', ecolor='k', capsize=12)
                eb[-1][0].set_linestyle('--')

        if not args.latest:
            ax.legend(loc='upper left')

    plt.tight_layout()
    if (args.outfile):
        plt.savefig(args.outfile)
    else:
        plt.show()

    plt.close()

if __name__ == '__main__':
    main()
