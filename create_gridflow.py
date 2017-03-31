#!/usr/bin/python

import os
import sys
import subprocess

def extract_frames(path):
    root = os.path.splitext(path)[0]
    if not os.path.isdir(root):
        os.mkdir(root)

    frame_dir = os.path.join(root, "frames")
    if not os.path.isdir(frame_dir):
        os.mkdir(frame_dir)

    fps = 15
    cmd = "ffmpeg -i {0} -q:v 1 -vf fps={1} {2}/%d.jpg".format(path, fps, frame_dir)
    subprocess.Popen(cmd, shell=True).wait()
    return root

def compute_flow(root):
    flow_dir = os.path.join(root, "flow")
    if not os.path.isdir(flow_dir):
        os.mkdir(flow_dir)
    cmd = "matlab -nodisplay -nodesktop -nosplash -r \"computeflow(\'{0}\'); exit;\"".format(root)
    subprocess.Popen(cmd, shell=True).wait()

def create_gridflow(root):
    flow_dir = os.path.join(root, "flow")
    frames = []
    for flow in os.listdir(flow_dir):
        frame, ext = os.path.splitext(flow)
        if ext != ".flo":
            continue
        frames.append(int(frame))

    flow_list = os.path.join(root, "flowlist.txt")
    with open(flow_list, 'w') as fout:
        for frame in sorted(frames):
            frame_path = os.path.join(flow_dir, "{}.flo".format(frame))
            fout.write("{}\n".format(frame_path))

    gridx = 16
    gridy = 12

    exe = "gridflow"
    output_path = os.path.join(root, "gridflow_{0}x{1}.txt".format(gridx, gridy))
    cmd = "{0} {1} {2} {3} > {4}".format(exe, flow_list, gridx, gridy, output_path)
    subprocess.Popen(cmd, shell=True).wait()

if __name__ == "__main__":
    path = sys.argv[1]
    root = os.path.splitext(path)[0]
    extract_frames(path)
    compute_flow(root)
    create_gridflow(root)


