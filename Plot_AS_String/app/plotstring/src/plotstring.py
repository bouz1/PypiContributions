import pyperclip
import pandas as pd
import numpy as np

def plot(df=None, Nx=80,Ny=32,title='Title' ,
                         xlabel=None, ylabel=None, print_str=True, 
                         return_str=True,copy_out_clipbrd=True, 
                         markers='*',N_grid=2,bar=False,x_int=False):
    
    """Create a plot of the data in the clipboard AS STRING.
    The plot can be used as a normal string in comments, bloc-notes, ... 

    :param df: DataFrame, optional
        The DataFrame to plot. If not provided, the function reads from the clipboard.
    :param Nx: int, optional
        The number of horizontal pixels in the plot.
    :param Ny: int, optional
        The number of vertical pixels in the plot.
    :param title: str, optional
        The title of the plot.
    :param xlabel: str, optional
        The label for the x-axis. if not provided, the function will use df columns.
    :param ylabel: str, optional
        The label for the y-axis. if not provided, the function will use df columns.
    :param print_str: bool, optional
        Whether to print the plot as a string.
    :param return_str: bool, optional
        Whether to return the plot as a string.
    :param copy_out_clipbrd: bool, optional
        Whether to copy the plot to the clipboard.
    :param markers: str, optional
        The marker to use for the plot.
    :param N_grid: int, optional
        The number of grid lines to use.
    :param bar: bool, optional
        Whether to use a bar plot instead of a line plot.
    :param x_int: bool, optional
        Whether the x is an integer or not.
    :return: None or str
        If `print_str` is True, the plot is printed as a string. If `return_str` is True, the plot is returned as a string. Otherwise, None is returned.

    """
   
    
    # Read the data from the clipboard if no DataFrame is provided
    if df is None: 
        df=pd.read_clipboard()  
        
    # Attempt to convert the DataFrame to float
    try:
        df=df.astype(float)
        df_is_float=True
    except: 
        df_is_float=False
        
    # Check if the input DataFrame is valid
    if not (type(df)==pd.core.frame.DataFrame and df.shape[0]>=1 and  \
    df.shape[1]>=2 and df_is_float): 
        print('error in the input dataFrame')
        return None
    
    # Extract the x and y data from the DataFrame
    x=df.iloc[:,0].astype('float32')
    y=df.iloc[:,1].astype('float32')
    
    # Set the x and y labels if not provided
    if xlabel is None: 
        xlabel= df.columns[0]
    if ylabel is None: 
        ylabel= df.columns[1]
        
    # Normalize the y data
    maxy=y.max()
    miny=y.min()
    ys=(y-miny)/(maxy-miny)
    ys=(ys*Ny)

    # Normalize the x data
    maxx=x.max()
    minx=x.min()
    xs=(x-minx)/(maxx-minx)
    xs=(xs*Nx)

    # Combine the x and y data into a DataFrame
    dfs=pd.concat([xs.to_frame(), ys.to_frame()],axis=1)
    dfs=dfs.drop_duplicates()
    dfs.sort_values(dfs.columns[1],ascending=False,inplace=True)
    dfs=dfs.round(0).astype(int).dropna()
    xy=dfs.iloc[:,0:2].values
    
    # Create the x-axis labels
    #X values are integer
    if x_int:
        i0='¦'+str(int((maxx-minx)*(0)+minx)) # label for 0%
        i25='¦'+str(int((maxx-minx)*(0.25)+minx)) # label for 25%
        i50='¦'+str(int((maxx-minx)*(0.5)+minx)) # label for 50%
        i75='¦'+str(int((maxx-minx)*0.75+minx)) # label for 75%
        i100='¦'+str(int((maxx-minx)+minx)) # label for 100%
    #X values are float
    else:
        i0='¦'+'{:.2e}'.format((maxx-minx)*(0)+minx) # label for 0%
        i25='¦'+'{:.2e}'.format((maxx-minx)*(0.25)+minx) # label for 25%
        i50='¦'+'{:.2e}'.format((maxx-minx)*(0.5)+minx) # label for 50%
        i75='¦'+'{:.2e}'.format((maxx-minx)*0.75+minx) # label for 75%
        i100='¦'+'{:.2e}'.format((maxx-minx)+minx) # label for 100%
    
    # Convert x-axis labels to string
    s=[' ']*Nx
    s[0:len(i0)]=i0
    s[int(Nx*0.25):int(Nx*0.25)+len(i25)]=i25
    s[int(Nx*0.5):int(Nx*0.5)+len(i25)]=i50
    s[int(Nx*0.75):int(Nx*0.75)+len(i75)]=i75
    s=''.join(s)+i100
    
    # Create the title and y-axis label
    N_title=(Nx-len(title))//2
    title= ' '*N_title+title+' '*N_title
    st=title+'\n'
    st+=' '*Nx+ylabel+'\n'
    
    # Create the bar plot if needed
    bar_arr=np.zeros(Nx+1)
    
    # Main loop 
    '''
    for j in range(Ny,-1,-1):
        for i in range(Nx+1):
            if str(i)+','+str(j) in [str(u[0])+','+str(u[1]) for u in xy]:
                st+=markers
                bar_arr[i]=1
            elif bar and bar_arr[i]:
                st+=markers
            else:
                if j%(Ny//N_grid)==0 :
                    st+='-'
                elif i%(Nx//N_grid)==0 and i < Nx:
                    st+='|'
                else: 
                    st+=' '
                   
        js=(maxy-miny)*(j/Ny)+miny
        
        js='{:.2e}'.format(js)
        if j%(Ny//4)==0 :
            st+='|'+js+'\n'
        else: 
            st+='|\n'
        

    st+=s+'\n'
    st+=xlabel
    '''
    # Start a loop that goes from Ny to -1 with a step of -1
    for j in range(Ny,-1,-1):
        # Start a loop that goes from 0 to Nx with a step of 1
        for i in range(Nx+1):
            # Check if the string representation of the current coordinates (i, j) is in the list of xy coordinates
            if str(i)+','+str(j) in [str(u[0])+','+str(u[1]) for u in xy]:
                # If it is, add the marker to the string and set the corresponding bar_arr index to 1
                st+=markers
                bar_arr[i]=1
            # If the bar is true and the corresponding bar_arr index is 1
            elif bar and bar_arr[i]:
                # Add the marker to the string
                st+=markers
            else:
                # If j is a multiple of the integer division of Ny by N_grid
                if j%(Ny//N_grid)==0 :
                    # Add a '-' to the string
                    st+='-'
                # If i is a multiple of the integer division of Nx by N_grid and i is less than Nx
                elif i%(Nx//N_grid)==0 and i < Nx:
                    # Add a '|' to the string
                    st+='|'
                else: 
                    # Otherwise, add a space to the string
                    st+=' '

        # Calculate the value of js based on the current value of j
        js=(maxy-miny)*(j/Ny)+miny

        # Format js to scientific notation with 2 decimal places
        js='{:.2e}'.format(js)
        # If j is a multiple of the integer division of Ny by 4
        if j%(Ny//4)==0 :
            # Add a '|' and the value of js to the string, then start a new line
            st+='|'+js+'\n'
        else: 
            # Otherwise, just add a '|' to the string and start a new line
            st+='|\n'

    # Add the value of s to the string and start a new line
    st+=s+'\n'
    # Add the value of xlabel to the string
    st+=xlabel

        
    # Print the plot as a string if requested
    if print_str:
        print(st)
        
    # Copy the plot to the clipboard if requested
    if copy_out_clipbrd:
        pyperclip.copy(st)

    # Return the plot as a string if requested
    if return_str:
        return st

