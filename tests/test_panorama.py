import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import cv2
import numpy as np
import Equirectangular as E2P
import Perspective as P2E


def mse(img1, img2):
    return np.mean((img1.astype("float") - img2.astype("float")) ** 2)


def projection_similarity(fov, theta, phi):
    """
    Test how well the reconstruction matches the original panorama.
    Generates a visual check which shows differences between real and expected result on a black background.
    """
    panorama = E2P.Equirectangular("images/image.jpg")
    perspective_img = panorama.get_perspective(fov, theta, phi, 720, 1080)
    cv2.imwrite(f"tests/images/perspective_{fov}_{theta}_{phi}.png", perspective_img)
    original_panorama, panorama_height, panorama_width = panorama.get_original_image()

    perspective = P2E.Perspective(f"tests/images/perspective_{fov}_{theta}_{phi}.png")
    panorama_img = perspective.get_panorama(
        fov, theta, phi, panorama_height, panorama_width
    )
    cv2.imwrite(f"tests/images/panorama_{fov}_{theta}_{phi}.png", panorama_img)

    # Check (MSE threshold)

    # Add mask to original panorama to match black background of reconstruction.
    gray = cv2.cvtColor(panorama_img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    masked_original = original_panorama.copy()
    masked_original = cv2.bitwise_and(masked_original, masked_original, mask=mask)

    # Calculate difference between the 2 images.
    error = mse(masked_original, panorama_img)
    print(f"MSE: {error:.4f}")

    # Visual check to see why the image passed/failed.
    diff = cv2.absdiff(masked_original, panorama_img)
    cv2.imwrite(f"tests/images/test_image_difference_{fov}_{theta}_{phi}.png", diff)
    # cv2.imwrite(f"images/masked_original_{fov}_{theta}_{phi}.png", masked_original)

    assert error < 10, f"Images are too different, MSE={error}"


def test_projection_similarity_90_0_0():
    projection_similarity(90, 0, 0)


def test_projection_similarity_90_30_0():
    projection_similarity(90, 30, 0)


def test_projection_similarity_90_30_30():
    projection_similarity(90, 30, 30)


def test_projection_similarity_90_45_30():
    projection_similarity(90, 45, 30)
