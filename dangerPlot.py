import os
from Utilities.Plotting import plot_preformatted


def replot_all():
    graphs = []
    for(dp, dn, fns) in os.walk("output"):
        graphs = dn
        break

    for x in graphs:
        subdirs = next(os.walk("output/{}".format(x)))[1]
        for subdir in subdirs:
            datadir = "output/{}/{}/data/".format(x, subdir)
            files = {
                "g_path": x,
                "g_r_path": "output/{}/{}".format(x, subdir),
                "js_name": "output/{}/{}.json".format(x, x),
                "g_r_path_zone": datadir + "zones.txt",
                "g_r_path_path": datadir + "paths.txt",
                "r": float(subdir.split("_")[-1])
            }
            plot_preformatted(files)


replot_all()