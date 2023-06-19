from sherpa.astro.ui import *
from sherpa_contrib.utils import *
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

nh = { 'plerion' : 3.2, 'halo' : 2.4 }
phoindex = { 'plerion' : 1.8, 'halo' : 2.1 }
norm = { 'plerion' : 1.8e-2, 'halo' : 4.4e-3 }
titles = { 'plerion' : 'Plerion', 'halo' : 'Halo' }

for type in ('plerion', 'halo'):
    #set_analysis("wave")
    set_xsabund("wilm")
    set_source(type, xstbabs.tbabs * xspowerlaw.pl)
    tbabs.nh = nh[type]
    pl.phoindex = phoindex[type]
    pl.norm = norm[type]
    dataspace1d(0.06, 10.0, 0.025, id=type)
    plot_source(type)
    plt.xscale('log')
    plt.xlabel('Energy (keV)')
    plt.ylabel('Counts/sec/keV')
    plt.xlim(1, 10)
    #plt.title('G21.5-0.9 Spectral Model: {}'.format(titles[type]))
    plt.title('')
    plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%g'))
    plt.gca().xaxis.set_minor_formatter(FormatStrFormatter('%g'))
    #plt.gca().ticklabel_format(axis='both', style='plain', useOffset=False)
    plt.tight_layout()
    plt.savefig('spectrum_{}.pdf'.format(type))
    plt.savefig('spectrum_{}.png'.format(type))
    save_instmap_weights(type, 'spectrum_{}_erg.txt'.format(type), fluxtype="erg")
    save_instmap_weights(type, 'spectrum_{}_ph.txt'.format(type))
