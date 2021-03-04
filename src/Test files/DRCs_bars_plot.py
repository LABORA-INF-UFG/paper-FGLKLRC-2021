import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def plot_dsg_number():
    x = ['LCR1', 'RCR1', 'HCR1', ' ', 'LCF1', 'RCF1', 'HCF1']
    colors_list = ["", "darkgoldenrod", "gold", "black", "midnightblue", "blue", "royalblue", "cornflowerblue", "darkgray", "lightgray", "brown"]

    y = {}

    y[5] = [0, 0, 0, 0, 0, 0, 9] #DSG 1 - 1
    y[4] = [0, 17, 66, 0, 0, 21, 60] # DSG 2 - 2
    y[7] = [0, 0, 0, 0, 14, 0, 0] # DSG 4 - 7
    y[6] = [15, 15, 0, 0, 15, 18, 0] # DSG 5 - 8
    y[9] = [0, 6, 0, 0, 17, 5, 4] # DSG 6 - 12
    y[8] = [78, 45, 25, 0, 65, 47, 15] # DSG 7 - 13
    y[10] = [8, 0, 0, 0, 15, 4, 0] # DSG 8 - DRAN
    y[1] = [0, 9, 10, 0, 0, 18, 32] # DSG 9 - 18 - CRAN
    y[2] = [0, 9, 0, 0, 0, 13, 6] # DSG 10 - 17 - CRAN

    peso = [0, 1, 4, 0, 5, 6, 7, 8, 9, 10, 25]

    for count in range(0, 6):
        sum_peso = 0
        for i in y:
            list = y[i]
            sum_peso += list[count]*peso[i]

        print(sum_peso)

    prev = {}

    for i in [1, 2, 4, 5, 6, 7, 8, 9, 10]:
        if i == 1:
            prev[1] = [0, 0, 0, 0, 0, 0, 0]
        else:
            aux_prev = prev[ant]
            aux_y = y[ant]
            new = []
            for c in range(0, len(aux_prev)):
                new.append(aux_prev[c] + aux_y[c])
            prev[i] = new
        ant = i

    fig, ax = plt.subplots()
    plt.ylim(0, 160)

    for i in y:
        ax.bar(x, y[i], width=.7, color=colors_list[i], bottom=prev[i])

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(17)

    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(20)

    #ax.set_ylabel('DRCs (#)', fontsize=18)

    #ax.set_title('Scores by group and gender')

    plt.rcParams.update({'font.size': 13})

    legend_elements = [Line2D([0], [0], color='b', lw=4, label='NG-RAN (3)'),
                       Line2D([0], [0], color='gray', lw=4, label='NG-RAN (2)'),
                       Line2D([0], [0], color='darkgoldenrod', lw=4, label='C-RAN'),
                       Line2D([0], [0], color='brown', lw=4, label='D-RAN')]

    ax.legend(handles=legend_elements, loc="upper left")
    ax.yaxis.grid(color='gray', linestyle='--', linewidth=0.5)

    plt.savefig("DRCs_128.png")
    plt.show()


def plot_dsg_by_tam():

    x = ['LCR1', 'RCR1', 'HCR1', 'LCF1', 'RCF1', 'HCF1']
    colors_list = ["brown", "navy", "green", "brown", "navy", "green", "white"]

    y = [19.65, 44.017, 67.52, 19.73, 44.85, 70.06]

    fig, ax = plt.subplots()

    ax.bar(x, y, color = colors_list)

    ax.set_ylabel('Aggregation Level (%)')
    #ax.set_title('Scores by group and gender')

    legend_elements = [Line2D([0], [0], color='brown', lw=4, label='Low Capacity (LC)'),
                       Line2D([0], [0], color='navy', lw=4, label='Random Capacity (RC)'),
                       Line2D([0], [0], color='green', lw=4, label='High Capacity (HC)')]

    ax.legend(handles=legend_elements, loc="upper left")

    plt.ylim(0, 100)

    plt.savefig("agg_lvl_128.png")
    plt.show()


if __name__ == '__main__':
    plot_dsg_number()
    # plot_dsg_by_tam()