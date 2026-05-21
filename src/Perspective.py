import cv2
import numpy as np
from transformations import panorama_to_spherical, spherical_to_cartesian


class Perspective:
    def __init__(self, img_name):
        """
        Load a perspective image.

        Args:
            img_name (str): Path to the perspective image.
            panorama_img_name (str): Path to the original panorama image.
        """
        self._img = cv2.imread(img_name, cv2.IMREAD_COLOR)
        self._height, self._width = self._img.shape[:2]

    def get_panorama(
        self,
        FOV,
        THETA,
        PHI,
        panorama_height,
        panorama_width,
    ):
        """
        Reproject a perspective image back into equirectangular space.
        1. Create a grid corresponding to the panorama image pixels.
        2. Convert panorama pixels to spherical coordinates.
        3. Convert spherical coordinates to homogeneous camera coordinates.
        4. Rotate in the opposite direction and order according to THETA and PHI.
        5. Map to perspective pixel coordinates.
        6. Sample pixels from perspective image.

        Args:
            FOV (float): Horizontal field of view in degrees.
            THETA (float): Horizontal viewing angle (yaw) in degrees.
            PHI (float): Vertical viewing angle (pitch) in degrees.
            panorama_height (int): Height of output equirectangular panorama image.
            panorama_width (int): Width of output equirectangular panorama image.

        Returns:
            np.ndarray: Equirectangular reprojection image.
        """

        # Create coordinate grid for equirectangular panorama pixels.
        x = np.arange(panorama_width)
        y = np.arange(panorama_height)
        x, y = np.meshgrid(x, y)
        # Build grid of coordinate pairs for output panorama pixels
        XY = np.stack([x, y], axis=-1).astype(np.float32)

        # Convert to spherical coordinates
        lonlat = panorama_to_spherical(XY, (panorama_height, panorama_width, 3))

        # Convert to 3D camera coordinates
        xyz = spherical_to_cartesian(lonlat)

        # Rotation vectors for y and x axis
        y_axis = np.array([0.0, 1.0, 0.0], np.float32)
        x_axis = np.array([1.0, 0.0, 0.0], np.float32)
        # Rotate the camera in the opposite direction and opposite order from original transformation.
        R1, _ = cv2.Rodrigues(y_axis * np.radians(THETA))
        R2, _ = cv2.Rodrigues(np.dot(R1, x_axis) * np.radians(PHI))
        # Combine to get rotation matrix
        R = R2 @ R1

        # Apply rotation to camera coordinates, to return to original panorama space.
        xyz = xyz @ R

        x = xyz[..., 0]
        y = xyz[..., 1]
        z = xyz[..., 2]

        # Compute focal length from FOV
        f = 0.5 * self._width / np.tan(0.5 * np.radians(FOV))
        # Compute horizontal and vertical image center.
        cx = (self._width - 1) / 2.0
        cy = (self._height - 1) / 2.0
        # Apply the pinhole camera intrinsic matrix and normalise by z.
        map_x = f * (x / z) + cx
        map_y = f * (y / z) + cy

        map_x = map_x.astype(np.float32)
        map_y = map_y.astype(np.float32)

        # Make sure to remove points that are behind the camera view.
        valid = z > 0

        panorama = np.zeros((panorama_height, panorama_width, 3), dtype=np.uint8)

        # Sample the pixels from the perspective image into panorama pixel space.
        sampled = cv2.remap(
            self._img,
            map_x,
            map_y,
            interpolation=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_CONSTANT,
        )

        panorama[valid] = sampled[valid]

        return panorama
