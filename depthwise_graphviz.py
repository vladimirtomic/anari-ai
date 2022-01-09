##############################################
#                                            #
#        Depthwise convolutional layer       #
#                                            #
##############################################

# Implort pygears types
from pygears import gear, datagear, sim, find, reg

# Import pygears types
from pygears.typing import Array, Fixp, Queue, Tuple, Uint

# Import pygears built-in modules
from pygears.lib import accum, ccat, collect, czip, dreg, drv, flatten, mul, qdeal, qrange, qround, queuemap, replicate, saturate, sdp, when

# Packages used for verification and visualization
import matplotlib.image as mpimg
import numpy as np
import matplotlib.pyplot as plt
import pygearsviz

reg['gear/memoize'] = False

##############################################
#                                            #
#                   Design                   #
#                                            #
##############################################


# Dot product implementation with saturation and rounding
@gear
def dot(din):
    return din \
        | queuemap(f=mul) \
        | accum(init=Fixp[10, 18](0)) \
        | qround \
        | saturate(t=Uint[8])


# Reorganizes data on the bus for proper distribution among 3 dot product
# modules
@datagear
def reorder(din: Queue[Tuple['pixel', 'weight']]
            ) -> Array[Queue[Tuple['pixel[0]', 'weight[0]']], 3]:
    p = din.data[0]
    w = din.data[1]

    return (
        ((p[0], w[0]), din.eot),
        ((p[1], w[1]), din.eot),
        ((p[2], w[2]), din.eot),
    )


# Generates write addresses based on filter weights stream. This is used for
# caching of filter weights.
@gear(hdl={'compile': True})
async def wr_req(weights: Queue) -> Tuple[Uint[4], 'weights.data']:
    cnt = Uint[4](0)
    async for w, last in weights:
        yield cnt, w
        cnt += 1


# Implements:
#     1. filter weights caching for a single CNN filter
#     2. filter weights readout synchronized with the input image segment
#     3. 3 dot product modules in operating in parallel on different slices
#        along the image segment depth
#     4. outputs the result as a vector of 3 output feature map elements
@gear
def filter(
        img: Queue[Array[Uint, 3]],  # Image segment stream
        weights: Queue,  # Filter weights stream
) -> b'img.data':

    # - Performs the readout of the cached filter weights out of a simple
    #   dual-port (sdp) memory
    # - Before readout waits for the last of the filter weigts to be streamed in
    #   "weights['eot']"
    # - Kernel weights will be read out 30*30=900 times for each of the image
    #   segments
    w = when(weights['eot'] | dreg, 9) \
        | replicate(30 * 30) \
        | flatten \
        | qrange \
        | flatten \
        | sdp(wr_req(weights))

    # Pair up corresponding slices of the kernel and image segment and send
    # them for processing to a set of "dot" modules, one for each slice along
    # the tensor depth
    res = [dot(d) for d in reorder(czip(img, w))]

    # Synchronize outputs of the "dot" modules and combine them into a vector
    return ccat(*res)


# Top level design module - distributes image segments for processing on "num"
# filters in parallel
@gear
def depthwise(
        img,  # Image segment stream
        weights,  # Filter weights stream
        *,
        num,  # Number of parallel filters available
):
    res = [filter(img, w) for w in qdeal(weights, num=num, lvl=1)]

    return ccat(*res)


##############################################
#                                            #
#                 Simulation                 #
#                                            #
##############################################

res = []

# Driver that outputs image segments
img_drv = drv(t=Queue[Array[Uint[8], 3]], seq=[])
# Driver that outputs filter weights
w_drv = drv(t=Queue[Array[Fixp[3, 8], 3]], seq=[])

# Top level connection between drivers, dut and a monitor
#  - "depthwise" module will be first converted to SystemVerilog and simulated
#    using "verilator" HDL simulator

depthwise(img_drv, w_drv, num=2) \
    | Array[Array[int, 3], 2] \
    | collect(result=res)

##############################################
#                                            #
#     Graphviz hierarchy visualization       #
#                                            #
##############################################

top = find('/')

# Traverse hierarchy starting from the 'top' and generate graphviz graph
pygearsviz.render_hierarchy_tree(gear=top, name='depthwise', format='svg')
