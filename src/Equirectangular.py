import cv2
import numpy as np
from transformations import cartesian_to_spherical, spherical_to_panorama


class Equirectangular:
    def __init__(self, img_name):
        """
        Load an equirectangular panorama image.

        Args:
            img_name (str): Path to the panorama image file.
        """

        self._img = cv2.imread(img_name, cv2.IMREAD_COLOR)
        [self._height, self._width, _] = self._img.shape

    def get_original_image(self):
        return self._img, self._height, self._width

    def get_perspective(self, FOV, THETA, PHI, height, width):
        """
        Generate a perspective projection from the equirectangular panorama by simulating a pinhole camera.
        1. Construct pinhole camera intrinsic matrix.
        2. Generate homogeneous camera coordinates for each pixel.
        3. Rotate camera coordinates according to THETA and PHI.
        4. Convert to spherical coordinates.
        5. Map spherical coordinates to panorama pixels coordinates.
        6. Extract the pixels from panorama.
        7. Output the perspective image.

        NOTE: Arguments are in degrees for user-friendliness.

        Args:
            FOV (float): Horizontal field of view in degrees.
            THETA (float): Horizontal viewing angle (yaw) in degrees.
            PHI (float): Vertical viewing angle (pitch) in degrees.
            height (int): Height of the output perspective image.
            width (int): Width of the output perspective image.

        Returns:
            np.ndarray: Perspective image.
        """

        # Compute focal length from FOV
        f = 0.5 * width * 1 / np.tan(0.5 * FOV / 180.0 * np.pi)
        # Compute horizontal and vertical image center.
        cx = (width - 1) / 2.0
        cy = (height - 1) / 2.0
        # Construct pinhole camera intrinsic matrix.
        K = np.array(
            [
                [f, 0, cx],
                [0, f, cy],
                [0, 0, 1],
            ],
            np.float32,
        )
        # Inverse matrix, will be used to convert image pixels into homogeneous camera coordinates.
        K_inv = np.linalg.inv(K)

        x = np.arange(width)
        y = np.arange(height)
        # Create grid of pixel coordinates.
        x, y = np.meshgrid(x, y)

        z = np.ones_like(x)
        xyz = np.concatenate([x[..., None], y[..., None], z[..., None]], axis=-1)
        # Convert pixel coords to homogeneous camera coordinates.
        xyz = xyz @ K_inv.T

        # Rotation vectors for y and x axis
        y_axis = np.array([0.0, 1.0, 0.0], np.float32)
        x_axis = np.array([1.0, 0.0, 0.0], np.float32)

        # Rotate camera around y axis (horizontally)
        R1, _ = cv2.Rodrigues(y_axis * np.radians(THETA))
        # Rotate camera around x axis (vertically) (correct order is yaw then pitch)
        R2, _ = cv2.Rodrigues(np.dot(R1, x_axis) * np.radians(PHI))
        # Combine to get rotation matrix
        R = R2 @ R1
        # Apply chosen rotations to camera coordinates.
        xyz = xyz @ R.T

        # Convert to spherical coordinates.
        lonlat = cartesian_to_spherical(xyz)
        # Get the corresponding panorama pixels.
        XY = spherical_to_panorama(lonlat, shape=self._img.shape).astype(np.float32)
        # Sample the pixels from panorama to create perspective image.
        perspective = cv2.remap(
            self._img,
            XY[..., 0],
            XY[..., 1],
            cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_WRAP,
        )

        return perspective
