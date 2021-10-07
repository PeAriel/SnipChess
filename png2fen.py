#!/Library/Frameworks/Python.framework/Versions/3.9/bin/python3

'''
This should be the main output of the DL part.

Thoughts:
1. As for now, the default square size (after inflation is 80 pixels). For a faster
   selective-search consider deflate the png after reading it from the user to get the squares,
   and only than inflate to classify. This may be a bit problematic - TEST the inflatet square!!!
'''
from model import ChessConvNet

import cv2
from time import time
import numpy as np
import os
import torch
import sys


PIECES = "RBNQKPrbnqkp"
PIECES_DICT = {("b" if i.islower() else "w") + i.lower(): i for i in PIECES}
PIECES_DICT['e'] = 'e'
LABELS_DICT = {'e': 0,
               'br': 1,
               'bb': 2,
               'bn': 3,
               'bq': 4,
               'bk': 5,
               'bp': 6,
               'wr': 7,
               'wb': 8,
               'wn': 9,
               'wq': 10,
               'wk': 11,
               'wp': 12}
LABELS_LIST = [k for k, v in LABELS_DICT.items()]
MODEL_PATH = 'parameters.pt'


def ss_regions(cvimage, verbosity=True):

    # speed-up using multithreads
    cv2.setUseOptimized(True)
    cv2.setNumThreads(4)

    ss = cv2.ximgproc.segmentation.createSelectiveSearchSegmentation()
    ss.setBaseImage(cvimage)
    ss.switchToSelectiveSearchFast()

    # run selective search on the input image
    start = time()
    rects = ss.process()
    end = time()

    if verbosity:
        print("selective search took {:.4f} seconds".format(end - start))
        print("{} total region proposals".format(len(rects)))

    new_rects = []
    for i, rect in enumerate(rects):
        x, y, w, h = rect
        if (w - h) < 3 and w <= cvimage.shape[0] // 8 and h <= cvimage.shape[0] // 8:
            new_rects.append([x, y, w, h])
    new_rects = np.array(new_rects)

    fixed_rects = np.array([[0 for _ in range(4)] for _ in range(64)])

    min_indices = np.argmin(new_rects, axis=0)
    xp, _, wp, hp = new_rects[min_indices[0]]  # Here I (arbitrarily) use x as the min. Could use y instead.
    box_size = max(wp, hp)

    idx = 0
    while True:
        condition = xp + box_size * 8 - (cvimage.shape[0] - xp)
        if abs(condition) > 3:
            box_size -= 1 * np.sign(condition)
            idx += 1
            if idx % 10 == 0:
                xp += 2
            if verbosity:
                print('Margin deviation = %d. Now box size = %d' % (condition, box_size))
                if idx % 10 == 0:
                    print('Reached %d iterations. Now xp = %d' % (idx, xp))
            continue
        else:
            break
        # Now construct the new 64 fixed rects
    idx = 0
    for i in range(8):
        for j in range(8):
            fixed_rects[idx] = [xp + box_size * j, xp + box_size * i, box_size, box_size]
            idx += 1
    return fixed_rects

def visualize_regions(cvimage, regions):
    while True:
        # create a copy of original image
        imOut = cvimage.copy()

        # itereate over all the region proposals
        for i, rect in enumerate(regions):
            # draw rectangle for region proposal till numShowRects
            x, y, w, h = rect
            cv2.rectangle(imOut, (x, y), (x + w, y + h), (0, 255, 0), 1, cv2.LINE_AA)

        # show output
        cv2.imshow("Output", imOut)

        # record key press
        k = cv2.waitKey(0) & 0xFF
        # q is pressed
        if k == 113:
            break
    # close image show window
    cv2.destroyAllWindows()

def regions2squares(cvimage, regions, square_size=80, grayscale=True):
    if grayscale:
        cvimage = cv2.cvtColor(cvimage, cv2.COLOR_BGR2GRAY)
        cvimage = np.array([cvimage, cvimage, cvimage])
        cvimage = np.moveaxis(cvimage, 0, -1)

    squares = np.zeros([64, square_size, square_size, 3], dtype=np.uint8)
    for i in range(64):
        imOut = cvimage.copy()
        x, y, w, h = regions[i]
        squares[i, :, :] = cv2.resize(imOut[y:y+w, x:x+w, :], (square_size, square_size))

    return squares

def evaluate(img, resizing=350, square_vis=None):
    """
    The functions that converts the board to its fen representation
    :param img_path: the path to the board image
    :param resizeing: int. the smaller image size for faster square identification. later it will
                      be inflated, so use with caution. Also, this optional argument may be erased
                      once this parameter is tuned.
    :param square_vis: number of square to be visualized
                       (to see that the inflation wasn't exaggerated). May be deleted afterwards.
    """
    model = ChessConvNet()
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
    model.eval()

    img = cv2.resize(img, (resizing, resizing))
    regions = ss_regions(img, verbosity=False)
    squares = regions2squares(img, regions, square_size=80)
    if square_vis:
        while True:
            imOut = squares[square_vis].copy()
            cv2.imshow("Output", imOut)

            # record key press
            k = cv2.waitKey(0) & 0xFF
            # q is pressed
            if k == 113:
                break
        # close image show window
        cv2.destroyAllWindows()

    pred_board = ['' for _ in range(64)]
    idx = 0
    ecount = 0
    for i in range(64):
        if i % 8 == 0 and i != 0:
            pred_board[idx] = '/'
            idx += 1

        square = np.moveaxis(squares[i], -1, 0)
        pred_square = model(torch.FloatTensor(square).unsqueeze(0))
        pred_square = PIECES_DICT.get(LABELS_LIST[torch.argmax(pred_square, dim=1)])
        if pred_square != 'e':
            if ecount != 0:
                pred_board[idx] = str(ecount)
                idx += 1
                ecount = 0
            pred_board[idx] = pred_square
            idx += 1
        else:
            ecount += 1
            if i % 8 == 7:
                pred_board[idx] = str(ecount)
                idx += 1
                ecount = 0

    fen = ''.join(list(filter(None, pred_board)))
    return fen

