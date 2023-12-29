# import key modules
# import matplotlib
from matplotlib import pyplot as plt
import numpy as np

# main function

def plot_onion_rings(data,labels,basecolormap="tab10",plot_threshold = 0.02):
    """
    Plots onion rings based on hierachical data represented by a balanced tree
    Unbalanced tree will be handled in future versions
    
    Input:
      - data: nested list in which each level of nesting corresponds to a node/leaf in the tree.
              only the leafs should be populated, the numbers are automatically aggregated
      - labels: nested list containing the labels to be used at each level
      - basecolormap (optional): base colors to be used to plot the data (default is "tab10") see https://matplotlib.org/stable/users/explain/colors/colormaps.html
      - plot_threshold (optional): threshold (percentage, e.g. 0.02) below which labels are not included (default is 0.02)
    
    Example: tree of depth three with two leaves in each branch (8 leaves total)
      data = [[[1,3],[1,1]],[[4,5],[1,1]]]
      labels = [['L11','L12'],['L21','L22'],['L31','L32']]

      plot_onion_rings(data,labels)
    """
    
    basemap = plt.colormaps["tab10"] #loads base colormap
    NUMBER_BASE = basemap.N # number of lements in the colormap
    
    data_array = np.array(data) # converts data in numpy array form
    NUMBER_ITEMS_PER_LEVEL = np.array(np.shape(data_array)) # number of nodes at each level of the tree
    NUMBER_LEVELS = NUMBER_ITEMS_PER_LEVEL.size # number of levels

    # Creation of colors to be used at each level of the onion ring
    # Each nesting levels decreases the alpha
    my_map = []
    for i in np.arange(NUMBER_ITEMS_PER_LEVEL[0]):
        my_map.append(list(basemap(np.mod(i,NUMBER_BASE)))) # adds base colors to the map, cycling if necessary

    alpha_range = [[1.0,0.4]] # range of alpha to split in the new colormap
    low_alpha_range = alpha_range[0][1] # lowest end of alphas to use ()
    
    alpha_per_level = [[1]] # initialization of list of alphas per level
    
    for level in np.arange(1,NUMBER_LEVELS): # creating list of alphas per level
        nb_items = NUMBER_ITEMS_PER_LEVEL[level]
        level_alpha = []
        for i in np.arange(0,len(alpha_range[level-1])):
            # The following splits the range of alphas at the previous level in the appropriate number of items
            if alpha_range[level-1][i] >low_alpha_range:
                delta = (alpha_range[level-1][i]-alpha_range[level-1][i+1])/(nb_items+1)
                new_alphas = list(alpha_range[level-1][i] - delta*np.arange(1,nb_items+2))
                alpha_range.append(new_alphas)
                for new_alpha in new_alphas[0:-1]:
                    level_alpha.append(new_alpha)
        alpha_per_level.append(level_alpha)
    
    # Creation of color map
    my_level_map = []
    NUMBER_CUM_ITEMS_PER_LEVEL = np.cumprod(NUMBER_ITEMS_PER_LEVEL)/NUMBER_ITEMS_PER_LEVEL[0] # Computes the indexing in the colormap
    
    for level in np.arange(NUMBER_LEVELS):
        for base_color in my_map: 
            if level==0:
                my_level_map.append(base_color) # appends base colors to first level
            else:
                for item in np.arange(int(NUMBER_CUM_ITEMS_PER_LEVEL[level])): # adds modified alphas to the color map using alpha_per_level
                    new_color = base_color[0:3]
                    alpha = alpha_per_level[level][item]
                    new_color.append(alpha)
                    my_level_map.append(new_color)


    # Creation of polar plot to represent data
    # Credit where it's due: https://matplotlib.org/stable/gallery/pie_and_polar_charts/nested_pie.html
                    
    fig, ax = plt.subplots(subplot_kw=dict(projection="polar")) # figure and axes
    SIZE = 1/(NUMBER_LEVELS+1) # width of onion ring (using +1 leaves a nice hold in the middle)

    values_normalized = data_array/np.sum(data_array) # Normalize data_array values to [0,1]
    values_in_angles = values_normalized*2*np.pi # Normalize data_array values to [0,2pi]

    # Computes boundaries and values of different levels
    # This is merely data re-formatting to ensure that we can read all required value sequentially in a list per level
    width_values_at_level = []
    original_values_at_level = []
    percent_values_at_level = []
    edge_values_at_level = []
    for level in np.arange(NUMBER_LEVELS-1,-1,-1):
        if level == NUMBER_LEVELS-1:
            hierachical_values_in_angle = values_in_angles
            hierarchical_original_values = data_array
            hierarchical_percent_values = values_normalized
        else:
            hierachical_values_in_angle = hierachical_values_in_angle.sum(axis=level+1)
            hierarchical_original_values = hierarchical_original_values.sum(axis=level+1)
            hierarchical_percent_values = hierarchical_percent_values.sum(axis=level+1)
        edge_values_at_level.insert(0,np.cumsum(np.append(0, hierachical_values_in_angle.flatten()[:-1])))
        width_values_at_level.insert(0,hierachical_values_in_angle.flatten())
        original_values_at_level.insert(0,hierarchical_original_values.flatten())
        percent_values_at_level.insert(0,hierarchical_percent_values.flatten())

    # Plots layers of the onion
    for level in np.arange(NUMBER_LEVELS):
        # Extracts the colormap for the level
        if level ==0 :
            start_color_index = 0
            stop_color_index = start_color_index + NUMBER_ITEMS_PER_LEVEL[level]
        else:
            start_color_index = stop_color_index
            stop_color_index  = start_color_index + np.prod(np.array(NUMBER_ITEMS_PER_LEVEL)[0:level+1])
        colors_level = my_level_map[start_color_index:stop_color_index]
        # Plots the layer
        ax.bar(x=edge_values_at_level[level], 
                width=width_values_at_level[level], 
                bottom=2*SIZE+level*2*SIZE, 
                height=2*SIZE, 
                color=colors_level, 
                edgecolor='w', 
                linewidth=1, 
                align="edge") 

        # Prints labels
        region_edges = edge_values_at_level[level]
        for i in np.arange(len(region_edges)):
            if i< len(region_edges)-1:
                angle = (region_edges[i]+region_edges[i+1])*0.5  
            else:
                angle = (region_edges[len(region_edges)-1]+2*np.pi)*0.5
            if angle>np.pi:
                text_rotation=0
            else:
                text_rotation = angle+180
            if percent_values_at_level[level][i]>plot_threshold:
                current_label = labels[level][np.mod(i,NUMBER_ITEMS_PER_LEVEL[level])] + "\n"+str(np.round(percent_values_at_level[level][i]*100,1))+"%\n({})".format(original_values_at_level[level][i])
                plt.text(angle,3*SIZE+level*2*SIZE,current_label,size=7,ha='center',va='center',color='white',weight='bold',rotation=text_rotation, rotation_mode='anchor',transform_rotates_text=True)

    ax.set_axis_off()

    return(fig,ax)