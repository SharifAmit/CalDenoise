'''
4SM/model.py Copyright (C) 2021 Sharif Amit Kamran, Hussein Moghnieh

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
'''

import matplotlib.pyplot as plt
import seaborn as sns
PLOT_TITLE_FONT_S=12
PLOT_LABEL_FONT_S=10


def size_plot(plt, scale = 1):
    N = scale
    plt.gca().margins(x=0)
    plt.gcf().canvas.draw()
    tl = plt.gca().get_xticklabels()
    maxsize = max([t.get_window_extent().width for t in tl])
    m = 0.2 # inch margin
    s = maxsize/plt.gcf().dpi*N+2*m
    margin = m/plt.gcf().get_size_inches()[0]

    plt.gcf().subplots_adjust(left=margin, right=1.-margin)
    plt.gcf().set_size_inches(s, plt.gcf().get_size_inches()[1])


def stats(global_quant_df):
    stats_df = global_quant_df.groupby(by=["Image"]).agg(['mean', 'count'])
    stats_df = stats_df.reset_index()
    stats_df.columns = [c[0] + "_" + c[1] for c in stats_df.columns]
    return stats_df

def generate_plot_cat(df, y, title, ylabel, file_name):
    scale = 1 if len(df['category'].unique()) == 1 else len(df['category'].unique()) * 0.5
    ax = sns.catplot(x="category", y=y, kind="swarm", data=df, s=13, marker="$\circ$")
    sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, offset=None, trim=False)
    size_plot(plt, scale)
    if len(df) == 1:
        ax.set(xticks=[])
    ax.set_xticklabels(rotation = 30)
    ax.set( xlabel = "", ylabel = ylabel)
    plt.title(title, fontsize=PLOT_TITLE_FONT_S)

    if file_name is not None:
        plt.savefig(file_name, bbox_inches='tight')
    else:
        plt.show(bbox_inches='tight')


