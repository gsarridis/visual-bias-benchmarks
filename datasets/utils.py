import torch
import os
import zipfile
import requests
from tqdm import tqdm
import gdown
import tarfile


class TwoCropTransform:
    """Create two crops of the same image"""

    def __init__(self, transform):
        self.transform = transform

    def __call__(self, x):
        return [self.transform(x), self.transform(x)]


def get_confusion_matrix(num_classes, targets, biases):
    confusion_matrix_org = torch.zeros(num_classes, num_classes)
    confusion_matrix_org_by = torch.zeros(num_classes, num_classes)
    for t, p in zip(targets, biases):
        confusion_matrix_org[p.long(), t.long()] += 1
        confusion_matrix_org_by[t.long(), p.long()] += 1

    confusion_matrix = confusion_matrix_org / confusion_matrix_org.sum(1).unsqueeze(1)
    confusion_matrix_by = confusion_matrix_org_by / confusion_matrix_org_by.sum(
        1
    ).unsqueeze(1)
    # confusion_matrix = confusion_matrix_org / confusion_matrix_org.sum()
    return confusion_matrix_org, confusion_matrix, confusion_matrix_by


def get_unsup_confusion_matrix(num_classes, targets, biases, marginals):
    confusion_matrix_org = torch.zeros(num_classes, num_classes).float()
    confusion_matrix_cnt = torch.zeros(num_classes, num_classes).float()
    for t, p, m in zip(targets, biases, marginals):
        confusion_matrix_org[p.long(), t.long()] += m
        confusion_matrix_cnt[p.long(), t.long()] += 1

    zero_idx = confusion_matrix_org == 0
    confusion_matrix_cnt[confusion_matrix_cnt == 0] = 1
    confusion_matrix_org = confusion_matrix_org / confusion_matrix_cnt
    confusion_matrix_org[zero_idx] = 1
    confusion_matrix_org = 1 / confusion_matrix_org
    confusion_matrix_org[zero_idx] = 0

    confusion_matrix = confusion_matrix_org / confusion_matrix_org.sum(1).unsqueeze(1)
    # confusion_matrix = confusion_matrix_org / confusion_matrix_org.sum()
    return confusion_matrix_org, confusion_matrix


def download_celeba(root):
    """
    Downloads the CelebA dataset and extracts it to the directory `root/celeba`.

    Args:
        root (str): Root directory where the CelebA dataset will be extracted.

    Raises:
        Exception: If the download or extraction fails.
    """
    # Define URLs and paths
    dataset_url = (
        "https://www.kaggle.com/api/v1/datasets/download/jessicali9530/celeba-dataset"
    )
    download_path = os.path.join(root, "celeba.zip")
    extract_path = root

    # Ensure the root directory exists
    os.makedirs(root, exist_ok=True)

    try:
        # Download the dataset with a progress bar
        print("Downloading CelebA dataset...")
        response = requests.get(dataset_url, stream=True)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

        # Get the total size from headers
        total_size = int(response.headers.get("content-length", 0))
        chunk_size = 1024
        num_chunks = total_size // chunk_size + 1

        # Write the dataset to a file with a progress bar
        with open(download_path, "wb") as file, tqdm(
            desc="Downloading",
            unit="KB",
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
                    pbar.update(len(chunk))
        print(f"Downloaded CelebA dataset to {download_path}.")

        # Extract the dataset
        print(f"Extracting CelebA dataset to {extract_path}...")
        with zipfile.ZipFile(download_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        extracted_dir = os.path.join(extract_path, "img_align_celeba")
        final_path = os.path.join(root, "celeba")
        if os.path.exists(extracted_dir):
            os.rename(extracted_dir, final_path)
        print(f"Extraction complete. Dataset available at {final_path}.")

        # Optionally delete the zip file
        os.remove(download_path)
        print(f"Deleted the downloaded zip file: {download_path}.")

    except requests.exceptions.RequestException as e:
        print(f"Failed to download the dataset: {e}")
        raise
    except zipfile.BadZipFile as e:
        print(f"Failed to extract the dataset: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise


def download_utkface(root):
    """
    Downloads the UTKFace dataset and extracts it to the directory `root/utk_face`.

    Args:
        root (str): Root directory where the UTKFace dataset will be extracted.

    Raises:
        Exception: If the download or extraction fails.
    """
    # Define URLs and paths
    dataset_url = "https://www.kaggle.com/api/v1/datasets/download/jangedoo/utkface-new"
    download_path = os.path.join(root, "utkface.zip")
    extract_path = root

    # Ensure the root directory exists
    os.makedirs(root, exist_ok=True)

    try:
        # Download the dataset with a progress bar
        print("Downloading UTKFace dataset...")
        response = requests.get(dataset_url, stream=True)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

        # Get the total size from headers
        total_size = int(response.headers.get("content-length", 0))
        chunk_size = 1024
        num_chunks = total_size // chunk_size + 1

        # Write the dataset to a file with a progress bar
        with open(download_path, "wb") as file, tqdm(
            desc="Downloading",
            unit="KB",
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
                    pbar.update(len(chunk))
        print(f"Downloaded UTKFace dataset to {download_path}.")

        # Extract the dataset
        print(f"Extracting UTKFace dataset to {extract_path}...")
        with zipfile.ZipFile(download_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        # Optionally delete the zip file
        os.remove(download_path)
        print(f"Deleted the downloaded zip file: {download_path}.")

    except requests.exceptions.RequestException as e:
        print(f"Failed to download the dataset: {e}")
        raise
    except zipfile.BadZipFile as e:
        print(f"Failed to extract the dataset: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise


def download_waterbirds(root):

    extract_path = root
    download_path = os.path.join(root, "waterbirds.zip")
    data_url = "https://drive.google.com/uc?id=1xPNYQskEXuPhuqT5Hj4hXPeJa9jh7liL"
    # Ensure the directory exists
    os.makedirs(root, exist_ok=True)

    try:
        # Download the data file from Google Drive
        gdown.download(data_url, download_path, quiet=False)
        print(f"Downloaded data to {download_path}.")

        # Extract the dataset
        print(f"Extracting UTKFace dataset to {extract_path}...")
        with zipfile.ZipFile(download_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        # Optionally delete the zip file
        os.remove(download_path)
        print(f"Deleted the downloaded zip file: {download_path}.")
    except zipfile.BadZipFile as e:
        print(f"Failed to extract the dataset: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise


def download_imagenet9(root):
    """
    Downloads the Imagenet9 background challenge dataset and extracts it to the directory `root/imagenet9`.

    Args:
        root (str): Root directory where the Imagenet9 dataset will be extracted.

    Raises:
        Exception: If the download or extraction fails.
    """
    # Define URLs and paths
    dataset_url = "https://github.com/MadryLab/backgrounds_challenge/releases/download/data/backgrounds_challenge_data.tar.gz"
    download_path = os.path.join(root, "imagenet9.zip")
    extract_path = root

    # Ensure the root directory exists
    os.makedirs(root, exist_ok=True)

    try:
        # Download the dataset with a progress bar
        print("Downloading Imagenet9 dataset...")
        response = requests.get(dataset_url, stream=True)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

        # Get the total size from headers
        total_size = int(response.headers.get("content-length", 0))
        chunk_size = 1024
        num_chunks = total_size // chunk_size + 1

        # Write the dataset to a file with a progress bar
        with open(download_path, "wb") as file, tqdm(
            desc="Downloading",
            unit="KB",
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
                    pbar.update(len(chunk))
        print(f"Downloaded Imagenet9 dataset to {download_path}.")

        # Extract the dataset
        print(f"Extracting Imagenet9 dataset to {extract_path}...")
        with tarfile.open(download_path, "r:gz") as tar:
            tar.extractall(path=extract_path)
        print(f"Extraction complete!")

        # Optionally delete the zip file
        os.remove(download_path)
        print(f"Deleted the downloaded zip file: {download_path}.")

    except requests.exceptions.RequestException as e:
        print(f"Failed to download the dataset: {e}")
        raise
    except zipfile.BadZipFile as e:
        print(f"Failed to extract the dataset: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise
