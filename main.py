import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / "src"))
import Equirectangular as E2P
import Perspective as P2E
import cv2
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert between equirectangular panorama and perspective images."
    )
    parser.add_argument(
        "--fov", type=float, default=90, help="Field of view in degrees"
    )
    parser.add_argument(
        "--theta", type=float, default=50, help="Horizontal viewing angle"
    )
    parser.add_argument("--phi", type=float, default=30, help="Vertical viewing angle")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Load panorama/
    panorama = E2P.Equirectangular("images/image.jpg")
    # Generate perspective image.
    perspective_img = panorama.get_perspective(
        args.fov, args.theta, args.phi, 720, 1080
    )
    # Save.
    cv2.imwrite("images/perspective.png", perspective_img)

    # Load perspective image.
    perspective = P2E.Perspective("images/perspective.png")
    _, height, width = panorama.get_original_image()
    # Generate panorama reconstruction.
    panorama_img = perspective.get_panorama(
        args.fov, args.theta, args.phi, height, width
    )
    # Save.
    cv2.imwrite("images/panorama.png", panorama_img)
