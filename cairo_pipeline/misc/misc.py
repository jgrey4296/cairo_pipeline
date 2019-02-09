def tick(dc, i):
    """ Simple Perlin Noise Use """
    r = 0
    g = 0
    b = 0
    if i == 0:
        r = 1
    if i == 1:
        g = 1
    if i == 2:
        b = 1

    for x in range(0, SIZE, 25):
        for y in range(0, SIZE, 25):
            v = dc.newVertex(x,y)
            v.data[VertE.STROKE] = np.array([r * snoise2(x * SCALER, y * SCALER, base=0, octaves=3, repeatx=200, repeaty=200, persistence=1),
                                    g * snoise2(x * SCALER, y * SCALER, base=0, octaves=5, repeatx=200, repeaty=200, persistence=1),
                                    b * snoise2(x * SCALER, y * SCALER, base=0, octaves=10, repeatx=200, repeaty=200, persistence=1),
                                    1]) + np.array([r * 0.2, g * 0.2, b * 0.2, 0])
            v.data[VertE.RADIUS] = 10

    return dc


def tick(dc, i):
    """ Perlin Noise Heightmap, followed by filtering to try to get edges
    Doesn't work, but saving for posterity
    """
    r = 0
    g = 0
    b = 0
    if i == 0:
        r = 1
    if i == 1:
        g = 1
    if i == 2:
        b = 1

    if i == 0:
        for x in range(0, SIZE, 25):
            for y in range(0, SIZE, 25):
                xs = x * SCALER
                ys = y * SCALER
                v = dc.newVertex(x,y)
                v.data[VertE.STROKE] = np.array([r * snoise2(xs, ys, octaves=5),
                                                 g * snoise2(xs, ys, octaves=5),
                                                 b * snoise2(xs, ys, octaves=10),
                                                 1]) + np.array([r * 0.3, g * 0.3, b * 0.3, 0])
                v.data[VertE.RADIUS] = 10

    vertex_distance = 50
    colour_quant = 5

    if i == 0:
        logging.info("Quantizing")
        #Quantize
        for v in dc.vertices:
            col = np.array(v.data[VertE.STROKE])
            upscaled = col * colour_quant
            to_int = np.array(upscaled, dtype=np.int)
            downscaled = to_int / colour_quant
            v.data[VertE.STROKE] = downscaled

    vertex_lookup = {}
    if i == 1:
        logging.info("Low PAss")
        #low pass filter
        for v in dc.vertices:
            nearby = v.get_nearby_vertices(e=vertex_distance)
            colours = np.array([np.array(x.data[VertE.STROKE]) for x in nearby])
            avg_c = colours.sum(axis=0) / len(colours)
            v.data['old'] = v.data[VertE.STROKE]
            v.data['avg'] = avg_c
            v.data[VertE.STROKE] = avg_c

    if i == 2:
        logging.info("High Pass")
        #high pass filter:
        for v in dc.vertices:
            v.data[VertE.STROKE] = (v.data['old'] - (v.data[VertE.STROKE])).clip(0,1)
            v.data[VertE.STROKE][-1] = 1

    if i == 3:
        logging.info("Hi pass 2")
        for v in dc.vertices:
            v.data[VertE.STROKE] = (v.data['old'] - v.data[VertE.STROKE]).clip(0, 1)
            v.data[VertE.STROKE][-1] = 1


    if i == 4:
        logging.info("Quantizing")
        #quantize hi pass:
        for v in dc.vertices:
            col = np.array(v.data[VertE.STROKE])
            upscaled = col * 100
            greater_than = upscaled > 25
            to_int = 100 * greater_than
            downscaled = to_int / colour_quant
            v.data[VertE.STROKE] = downscaled

    if i == 5:
        logging.info("Layering Quantized hi pass over top")
        for v in dc.vertices:
            v.data[VertE.STROKE] += v.data['old']


    return dc

def tick(dc, i):
    """ A Working edge detection for perlin noise, using
    scipi's generic_filter convolution function
    """
    r = 0
    g = 0
    b = 0
    if i == 0:
        r = 1
    if i == 1:
        g = 1
    if i == 2:
        b = 1

    if i == 0:
        for x in range(0, SIZE, INC_AMNT):
            for y in range(0, SIZE, INC_AMNT):
                xs = x * SCALER
                ys = y * SCALER
                v = dc.newVertex(x,y)
                v.data[VertE.STROKE] = np.array([r * snoise2(xs, ys, octaves=5),
                                                 g * snoise2(xs, ys, octaves=5),
                                                 b * snoise2(xs, ys, octaves=10),
                                                 1]) + np.array([r * 0.3, g * 0.3, b * 0.3, 0])
                v.data[VertE.RADIUS] = 10

    vertex_distance = 50
    colour_quant = 5

    #pad the size a bit
    matrix_size = int(SIZE / INC_AMNT) + 3
    normal = 1 / INC_AMNT
    matrix = np.zeros((matrix_size, matrix_size))
    edges = np.zeros((matrix_size, matrix_size))
    if i == 0:
        logging.info("Quantizing")
        #Quantize
        for v in dc.vertices:
            col = np.array(v.data[VertE.STROKE])
            upscaled = col * colour_quant
            to_int = np.array(upscaled, dtype=np.int)
            downscaled = to_int / colour_quant
            v.data[VertE.STROKE] = downscaled
            matrix[(int(v.x  * normal), int(v.y * normal))] = to_int[0]


        #For each level of quantization:
        for layer_val in [(colour_quant - 1) - x for x in range(colour_quant)]:
            if layer_val == 0:
                continue
            #merge with layers above and filter
            use_matrix = matrix * (matrix >= layer_val)
            filter_mat = generic_filter(use_matrix, partial(filter_func, layer_val), size=2)
            #aggregate:
            edges += filter_mat


        #then recolour the nodes that reflect those edges:
        for v in dc.vertices:
            pos = (int(v.x * normal), int(v.y * normal))
            if edges[pos] > 0:
                v.data[VertE.STROKE][1] = 1


    return dc

def filter_func(max_val, arr):
    return 0 in arr and any(arr >= max_val)



def tick(dc, i):
    """ Expanding from an edge test """
    #create the end
    e = dc.createEdge([200, 200], [400, 200])

    curr = e
    vertsToConnect = []
    #split, and expand forwards at 30 degrees, and at a 90 degree angle
    for x in range(10):
        vertsToConnect.append(curr.origin)
        newVert, subEdge = curr.split_by_ratio(0.5)
        vertsToConnect.append(newVert)
        curr.extend(rotate=radians(90), d=100)
        newEdge = subEdge.extend(rotate=radians(-30), d=300)
        curr = newEdge


    avg = np.array([x.toArray() for x in vertsToConnect]).sum(axis=0) / len(vertsToConnect)
    centreVert= dc.newVertex(*avg)

    for v in vertsToConnect:
        dc.newEdge(v, centreVert)


    for edge in dc.halfEdges:
        edge.data[EdgeE.STROKE] = [0, 1, 0, 1]
        edge.data[EdgeE.WIDTH] = 20

    for v in dc.vertices:
        v.data[VertE.STROKE] = [0, 0, 1, 1]
        v.data[VertE.RADIUS] = 30

    return dc
