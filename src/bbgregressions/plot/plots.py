import matplotlib.pyplot as plt

def coefplot(results: dict,
            config: dict,
            main_vars: list,
            coeff_vars: list,
            pdf) -> None:
    """
    
    """

    fig, axs = plt.subplots(config["nrows"], config["ncols"],
                        figsize = (config["fig_width"], config["fig_height"]),
                        sharey = True)
    plt.suptitle(config["main_title"], fontsize = 14)
    
    for main_var, ax in zip(main_vars, axs.flat):

        for i, coeff_var in enumerate(coeff_vars):

            # check whether the coeff is significant to highlight the point in black
            if results["sign"].loc[main_var][coeff_var] < config["sign_thres"]:
                edgecolors = "black"
            else:
                edgecolors = "face"

            # plot dot + confidence interval
            ax.scatter(results["coeff"].loc[main_var][coeff_var], i, 
                    color = config["colors"][coeff_var],
                    s = config["coeffdot_size"], edgecolors = edgecolors, 
                    linewidths = config["coeffdot_linewidth"])
            ax.hlines(i, 
                    results["low_ci"].loc[main_var][coeff_var],
                    results["high_ci"].loc[main_var][coeff_var],
                    color = config["colors"][coeff_var])

        # add labels
        y_ticks = [i for i in range(len(coeff_vars))]
        y_labels = [config["names"][coeff_var] for coeff_var in coeff_vars]
        ax.set_yticks(y_ticks, y_labels)

        # set zero effect 
        ax.vlines(0, -1, len(coeff_vars)+0.3, ls = '--', color = 'grey')

        # subplot config
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_xlabel('Effect size')
        ax.set_ylim(-1, len(coeff_vars.keys())+0.5)
        ax.set_title(config["titles"][main_var])

    plt.tight_layout()
    pdf.savefig()  # saves the current figure into a pdf page
    plt.show()
    plt.close() 