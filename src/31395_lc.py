from pycrates import read_file
import matplotlib.pylab as plt
import numpy as np

plt.subplots(4,1,sharex=True)

plt.subplot(4,1,1)
tab = read_file("31395_src.fits")
dt = tab.get_column("dt")
rate = tab.get_column("count_rate")
erate = tab.get_column("count_rate_err")
plt.errorbar(dt.values, rate.values, yerr=erate.values, marker="o", color="red", mfc="black",mec="black", ecolor="grey")
plt.ylabel('Source')
src = rate.values
srcerr = erate.values

plt.subplot(4,1,2)
tab = read_file("31395_bg.fits")
dt = tab.get_column("dt")
rate = tab.get_column("count_rate")
erate = tab.get_column("count_rate_err")
plt.errorbar(dt.values, rate.values, yerr=erate.values, marker="o", color="red", mfc="black",mec="black", ecolor="grey")
plt.ylabel('Background')
bg = rate.values
bgerr = erate.values

plt.subplot(4,1,3)
x = dt.values
y = src - bg
yerr = np.sqrt(srcerr**2 + bgerr**2)
plt.errorbar(x, y, yerr=yerr, marker="o", color="red", mfc="black",mec="black", ecolor="grey")
plt.ylabel("Net")

plt.subplot(4,1,4)
ee = tab.get_column("EXPOSURE")
plt.plot(dt.values, ee.values, marker="o", color="red", mfc="black",mec="black")
plt.xlabel(r"$\Delta$ T (s)")
plt.ylabel("Exposure")

plt.tight_layout()
plt.show()
