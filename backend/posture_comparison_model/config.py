scale_search = [0.5]
standard_image_shape = 368
boxsize = 256
stride = 8
padValue = 128
thre1 = 0.1
thre2 = 0.05

limbSeq = [[2, 3], [2, 6], [3, 4], [4, 5], [6, 7], [7, 8], [2, 9], [9, 10], \
    [10, 11], [2, 12], [12, 13], [13, 14], [2, 1], [1, 15], [15, 17], \
    [1, 16], [16, 18], [3, 17], [6, 18]]

joinName = {
    1: "Head",
    2: "Neck",
    3: "Right Shoulder",
    4: "Right Elbow",
    5: "Right Wrist",
    6: "Left Shoulder",
    7: "Left Elbow",
    8: "Left Wrist",
    9: "Right Hip",
    10: "Right Knee",
    11: "Right Ankle",
    12: "Left Hip",
    13: "Left Knee",
    14: "Left Ankle",
    15: "Right Eye",
    16: "Left Eye",
    17: "Right Ear",
    18: "Left Ear",   
}
mapIdx = [[31, 32], [39, 40], [33, 34], [35, 36], [41, 42], [43, 44], [19, 20], [21, 22], \
            [23, 24], [25, 26], [27, 28], [29, 30], [47, 48], [49, 50], [53, 54], [51, 52], \
            [55, 56], [37, 38], [45, 46]]

colors = [[255, 0, 0], [255, 85, 0], [255, 170, 0], [255, 255, 0], [170, 255, 0], [85, 255, 0], [0, 255, 0], \
        [0, 255, 85], [0, 255, 170], [0, 255, 255], [0, 170, 255], [0, 85, 255], [0, 0, 255], [85, 0, 255], \
        [170, 0, 255], [255, 0, 255], [255, 0, 170], [255, 0, 85]]


limbSeqToCompare = [[2, 3], [2, 6], [3, 4], [4, 5], [6, 7], [7, 8], [2, 9], [9, 10], \
            [10, 11], [2, 12], [12, 13], [13, 14], [2, 1]]