import numpy as np


def cartesian_to_spherical(xyz):
    """
    Converts 3D Cartesian coordinates into spherical longitude/latitude coordinates theta/phi.

    Args:
        xyz (np.ndarray): Array of 3D vectors containing coordinates [x, y, z] with values in [0,1].

    Returns:
        np.ndarray: Array of longitude/latitude pairs [lon, lat] in radians
    """
    atan2 = np.arctan2
    asin = np.arcsin

    # Normalise all vectors to = 1.
    norm = np.linalg.norm(xyz, axis=-1, keepdims=True)
    xyz_norm = xyz / norm
    # Extract x, y, z
    x = xyz_norm[..., 0:1]
    y = xyz_norm[..., 1:2]
    z = xyz_norm[..., 2:]

    # Transform to spherical coords
    lon = atan2(x, z)  # lon = theta
    lat = asin(y)  # lat = phi
    lst = [lon, lat]

    out = np.concatenate(lst, axis=-1)
    return out


def spherical_to_cartesian(lonlat):
    """
    Converts spherical longitude/latitude coordinates into 3D Cartesian coordinates.

    Args:
        lonlat (np.ndarray): Array of [longitude, latitude] coordinates in radians.

    Returns:
        np.ndarray: Array of 3D unit vectors [x, y, z].
    """
    lon = lonlat[..., 0]
    lat = lonlat[..., 1]

    x = np.cos(lat) * np.sin(lon)
    y = np.sin(lat)
    z = np.cos(lat) * np.cos(lon)

    return np.stack([x, y, z], axis=-1)


def spherical_to_panorama(lonlat, shape):
    """
    Converts spherical coordinates into pixel coordinates for an equirectangular panorama image.
    Theta coordinates range from [-pi,pi] and are mapped to x coords from left to right [0,image_width].
    Phi coordinates range from [-pi/2,pi/2] and are mapped to y coords from top to bottom [0,image_height].

    Args:
        lonlat (np.ndarray): Array of spherical coordinates [longitude, latitude] in radians.
        shape (tuple): Shape of the panorama image in the form (height, width, channels).

    Returns:
        np.ndarray: Array of image coordinates [X, Y] pixel coordinates.
    """
    # Map lon/theta values along x axis, normalise from [-pi,+pi] to [0,1], translate by 0.5 and multiply by image width.
    X = (lonlat[..., 0:1] / (2 * np.pi) + 0.5) * (shape[1] - 1)
    # Map lat/phi values along y axis, normalise from [-pi/2,+pi/2] to [0,1], translate by 0.5 and multiply by image height.
    Y = (lonlat[..., 1:] / (np.pi) + 0.5) * (shape[0] - 1)
    lst = [X, Y]
    out = np.concatenate(lst, axis=-1)

    return out


def panorama_to_spherical(XY, shape):
    """
    Converts equirectangular panorama image pixels into longitude/latitude coordinates.

    Args:
        XY (np.ndarray): Array of [X, Y] image coordinates in pixels.
        shape (tuple): Panorama image shape (height, width, channels).

    Returns:
        np.ndarray: Array of [longitude, latitude] coordinates in radians.
    """
    # Normalise pixel coordinates to [0,1] range, translate by 0.5 so that center value = 0, then convert to radians.
    lon = ((XY[..., 0:1] / (shape[1] - 1)) - 0.5) * 2 * np.pi
    # Normalise pixel coordinates to [0,1] range, translate by 0.5 so that center value = 0, then convert to radians.
    lat = ((XY[..., 1:2] / (shape[0] - 1)) - 0.5) * np.pi

    return np.concatenate([lon, lat], axis=-1)
