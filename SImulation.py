# -*- coding: utf-8 -*-
"""
Created on Mon May 25 23:40:34 2020

@author: TBE7
"""

import numpy as np
import scipy 
import scipy.integrate as si
from functools import partial
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams['animation.ffmpeg_path']  = "C:\\Users\\tbe7\\Downloads\\addons\\ffmpeg-20200523-26b4509-win64-static\\bin\\ffmpeg.exe"
import matplotlib.animation as animation
from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)

#%%    
def integrandforpd2(x,y,t):
    xminus = x - 1
    return scipy.special.erfc((-xminus + 4*t)/2/np.sqrt(t)) * np.exp(4*t - y**2/4/t)/np.sqrt(t) 

def evaluateintegralpd2(x,y,t):
    partialintegrandpd2 = partial(integrandforpd2, x, y )
    return si.quad(partialintegrandpd2, 0, t)[0]

def evaluatePD2(x,y,t):
    xminus = x - 1    
    return np.exp(-2*xminus)/(2*np.sqrt(np.pi))  * evaluateintegralpd2(x,y,t)

#%%
def integrandforpd1(x,y,t):
    xplus = x + 1
    return scipy.special.erfc((xplus + 4*t)/2/np.sqrt(t)) * np.exp(4*t - y**2/4/t) /np.sqrt(t) 

def evaluateintegralpd1(x,y,t):
    partialintegrandpd1 = partial(integrandforpd1, x, y )
    return si.quad(partialintegrandpd1, 0, t)[0]


def evaluatePD1(x,y,t):
    xstar = np.abs(x-1)
    xplus = x + 1
    arg1 = (xstar**2 + y**2)/4/t
    arg2 = (xplus**2 + y**2)/4/t
    out = -0.5*(scipy.special.expi(-arg1) + \
                scipy.special.expi(-arg2)) - np.exp(2*xplus)/np.sqrt(np.pi)*evaluateintegralpd1(x,y,t) 
    return out 

#%% Bringing the above two cells together

Nx = 61
Ny = 61
Ntlog = 71
Ntlin = 30
Nt = Ntlog + Ntlin

x = np.linspace(-2,2,Nx)
y = np.linspace(-1,1,Ny)
#t = np.logspace(-4, 2, Ntlog)
t = np.concatenate( ( np.logspace(-4, 1, Ntlog), np.linspace(12, 100, Ntlin)) )

PD  = np.empty((Nx, Ny, Nt))
PD1  = np.empty((Nx, Ny, Nt))
PD2 = np.empty((Nx, Ny, Nt))

for k, tcurr in enumerate(t):
    for j, ycurr in enumerate(y):
        for i, xcurr in enumerate(x):
            # PD1[i,j,k] = evaluatePD1(xcurr,ycurr,tcurr)
            # PD2[i,j,k] = evaluatePD2(xcurr,ycurr,tcurr)
            if xcurr < 0:
                PD[i,j,k] = evaluatePD2(xcurr,ycurr,tcurr)
            else:
                PD[i,j,k] = evaluatePD1(xcurr,ycurr,tcurr)


PD[PD>7.2] = 7.2


#%% Plot some figs
fig, axs = plt.subplots(3, 3, constrained_layout=True)

tplotid = (0, -7, -1) # this is for Nt = 21 and just logspace, for animation , we have part logspace part linspace
yplotid = np.tile( np.array([0,(Ny-1)//2,-1]), [3])
plottitles = \
    (r'$t  =  10^{-4}, y = -1$', r'$t  =  10^{-4}, y = 0$', r'$t  =  10^{-4}, y = 1$', \
     r'$t  =  1, y = -1$', r'$t  =  1, y = 0$', r'$t  =  1, y = 1$', \
         r'$t  =  100, y = -1$', r'$t  =  100, y = 0$', r'$t  =  100, y = 1$' )
        
for ax, plotid in zip(axs.ravel(), (i for i in range(9)) ):
    ax.plot(x[x>=0], PD[20:,yplotid[plotid], tplotid[plotid//3] ], c = 'r', ls = '-')
    ax.set_title(plottitles[plotid])
    ax.set_xlabel(r'$x$')
    ax.set_ylabel(r'$PD1$')

fig.savefig('plt33faultPD1_.pdf', dpi = 600)

# repeat same for PD2
fig, axs = plt.subplots(3, 3, constrained_layout=True)


plottitles = \
    (r'$t  =  10^{-4}, y = -1$', r'$t  =  10^{-4}, y = 0$', r'$t  =  10^{-4}, y = 1$', \
     r'$t  =  1, y = -1$', r'$t  =  1, y = 0$', r'$t  =  1, y = 1$', \
         r'$t  =  100, y = -1$', r'$t  =  100, y = 0$', r'$t  =  100, y = 1$' )
        
for ax, plotid in zip(axs.ravel(), (i for i in range(9)) ):
    ax.plot(x[x<0], PD[:20,yplotid[plotid], tplotid[plotid//3] ], c = 'b', ls = '-')
    ax.set_title(plottitles[plotid])
    ax.set_xlabel(r'$x$')
    ax.set_ylabel(r'$PD2$')

fig.savefig('plt33faultPD2_.pdf', dpi = 600)


#%%
# Set up formatting for the movie files
Writer = animation.writers['ffmpeg']
writer = Writer(fps=1, metadata=dict(artist='Me'), bitrate=-1)


xmesh,ymesh = np.meshgrid(x,y)
fig = plt.figure()
ax = plt.axes(xlim=(x[0], x[-1]), ylim=(y[0], y[-1]))  

# animation function
def animate(k): 
    cont = plt.contourf(xmesh, ymesh, PD[:,:,k].T, 100)
    plt.title(r't = %1.2e' % i )
    
    return cont  

fig.colorbar(animate(0))
anim = animation.FuncAnimation(fig, animate, frames=Nt)
#plt.show()
anim.save('animationfault.mp4', writer = writer, dpi = 600)


#%% How about a surface plot instead?
from mpl_toolkits.mplot3d import axes3d
xmesh,ymesh = np.meshgrid(x,y)
fig = plt.figure()
ax = fig.add_subplot(111, projection = '3d')
#ax = plt.axes(xlim=(x[0], x[-1]), ylim=(y[0], y[-1])) 
cmap=plt.get_cmap('gist_earth')
mappable = matplotlib.cm.ScalarMappable(cmap = "magma") #" magma ", plt.get_cmap('gist_earth')
mappable.set_array(PD[:,:,0].T)
plot = [ax.plot_surface(xmesh, ymesh, PD[:,:,0].T, cmap = mappable.cmap, cstride = 10, rstride = 1)] 
#ax.view_init(elev=40, azim=10.5)
fps = 10 # frame per sec
frn = Nt # frame number of the animation

# Set up formatting for the movie files
Writer = animation.writers['ffmpeg']
writer = Writer(fps=fps, metadata=dict(artist='Me'), bitrate=-1)

ax.set_xlabel(r'$x$')
ax.set_ylabel(r'$y$')
ax.set_zlabel(r'$\Delta P$')
ax.set_xticks(np.arange(-2, 2.1, step=1))
ax.set_yticks(np.arange(-1, 1.5, step=0.5))
ax.set_zticks(np.arange(0., 9.0, step=1))

ax.set_xticklabels([ '$'+str(i)+'$' for i in np.arange(-2, 2.1, step=1)])
ax.set_yticklabels([ '$'+str(i)+'$' for i in np.arange(-1, 1.5, step=0.5)])

currtext = ax.text2D(0.05, 0.95, 'time', transform=ax.transAxes)

# animation function
def update_plot(frame_number, zarray, plot): 
    plot[0].remove()
    plot[0] = ax.plot_surface(xmesh, ymesh, zarray[:,:,frame_number].T, cmap= mappable.cmap, cstride = 1, rstride = 1 ) #plt.get_cmap('gist_earth')
    tstr = '{:.4f}'.format(t[frame_number]) 
    tstr = '$ \mathrm{time = }' + tstr + '\mathrm{s} $'
    currtext.set_text(tstr )

fig.colorbar(mappable)
ax.set_zlim(0,7.5)
ani = animation.FuncAnimation(fig, update_plot, frn, fargs=(PD, plot), interval=1000/fps)
ani.save('animationfaultsurface___.mp4', writer = writer, dpi = 800)
