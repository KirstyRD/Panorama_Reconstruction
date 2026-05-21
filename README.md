# Perspective Image to Equirectangular Panorama Reconstruction.
## Introduction
The following document provides a walk through of steps taken to complete this assignment as well as assumptions and resources. This is followed by running instructions for the code in this repo.



## Approach

I began by doing some reading on the equirectangular panorama and how it maps to a 2D projection. The following example resources were useful in understanding the code in [`Equirec2Perspec`](https://github.com/fuenwang/Equirec2Perspec):

- https://medium.com/check-visit-computer-vision/understanding-360-images-8e0fcf0ee861
- https://deerajmanjaray.medium.com/understanding-the-linear-camera-model-in-camera-calibration-c08a18dbb0f9 

In order to reverse the process I needed to understand the main steps taken. As I read through these resources, I added comments to the original algorithm in order to better understand the steps taken to transform from an equirectangular panorama to a 2D perspective image. I changed a few variable names to make the code easier to understand. The following provides a high-level summary:
1. Create a uniform grid which represents the pixels in the desired output image.
2. Construct an intrinsic matrix which can be used to transform a 3D point in the camera coordinate frame to its corresponding 2D point on the output image plane.
3. Generate homogeneous camera coordinates for each pixel in the output image using the inverse of the intrinsic matrix. The homogeneous camera coordinates are cartesian points with a fictitious extra coordinate. It's now possible to apply transformations such as rotations using matrix multiplication.
5. Rotate according to the input parameters, $\theta$ and $\phi$ which represent horizontal and vertical rotation respectively. This selects a sample of the panorama image to transform.
6. Convert from cartesian to spherical coordinates, with the camera as the center. These can be easily mapped to the coordinates (pixels) in the panorama.
7. Using spherical coordinates, sample the pixels from the panorama which map to each point in the grid. The colour of these pixels is used to "fill in" the grid, generating a 2D output image.

Once I understood the process, I was able to reverse it by working backwards, paying careful attention to the order of any translations such as rotations and matrix multiplications.

1. Create a grid corresponding to the panorama pixels.
2. Map the panorama pixels to spherical coordinates.
3. Convert to homogeneous camera coordinates.
4. Apply the rotations in the opposite order and direction.
5. Apply the intrinsic matrix, which is the inverse of the matrix used in the original algorithm. This transfors from 3D camera coordinates to 2D image coordinates.
6. Normalise by z, our fictitious coordinate. Remove any points that would be behind the camera in this coordinate system.
8. Sample the pixels from the 2D perspective that correspond to each point in the grid.

I debugged my code by saving the output image to file and checking it for errors. Finally, I tidied up the codebase and added a main module.

### Evaluating the solution

When transforming from panorama to 2D perspective, most of the pixels from the original image are lost. Performing the transformation in reverse will only reconstruct a subset of the original image. I made the decision to overlay the reconstructed segment onto a black background, in the location where the original segment of the panorama would have been. In order to evaluate the reconstruction, I simply added a mask over the rest of the original panorama image and checked how "similar" this image was to the reconstruction.

I created a simple test script which uses a basic Mean Squared Error test to check how "different" these two images are. I added a small threshold to account for small compression artifacts and the edge of the mask. This was coupled with a visual reconstruction of the difference between the two images which can be used to debug.

### Other resources
- I used Copilot to generate the below running instructions in this readme. I chose not to use it while developing the solution to ensure a pure evaluation of my technical skills.
- I used the OpenCV and Numpy docs to check syntax.


## Running Instructions
This project uses

- [`uv`](https://github.com/astral-sh/uv) for package management, with a local virtual environment located at `.venv`.
- `pytest` for testing.

### 1. Install uv

#### Linux / macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify installation:

```bash
uv --version
```
---

### 2. Create the virtual environment and install dependencies

From the project root:

```bash
uv sync
```

This will:

- create `.venv/` automatically
- install all dependencies from `pyproject.toml`
- install locked versions from `uv.lock` if present

---


### 3. Activate the virtual environment

#### Linux / macOS

```bash
source .venv/bin/activate
```

#### Windows (PowerShell)

```powershell
.venv\Scripts\Activate.ps1
```

---

### 4. Running the Application

Run the main panorama conversion script using:

```bash
uv run python main.py
```

This will:

1. Load the panorama image from:

```text
images/image.jpg
```

2. Generate a perspective projection image:

```text
images/perspective.png
```

3. Reconstruct a panorama image from the perspective projection:

```text
images/panorama.png
```

---

### Command Line Arguments

You can customize the projection parameters using command line arguments.

Example:

```bash
uv run python main.py \
    --fov 120 \
    --theta 45 \
    --phi 10 
```

---

### Available Arguments

| Argument | Description | Default |
|---|---|---|
| `--fov` | Field of view in degrees | `90` |
| `--theta` | Horizontal viewing angle | `50` |
| `--phi` | Vertical viewing angle | `30` |

---

### Example

```bash
uv run python main.py --fov 90 --theta 0 --phi 0
```

This generates a perspective image centered on the panorama with a 90° field of view.




### 4. Run the tests

Run all tests:

```bash
uv run pytest
```

Run with console output enabled:

```bash
uv run pytest -s
```





